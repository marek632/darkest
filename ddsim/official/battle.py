"""Battle engine on official rules: formation stances + room tile areas,
2 actions per hero turn (repeats allowed), fixed card damage with K10
to-hit, status token stacks, initiative deck, monster stance AI.

Assumptions carried from docs (flagged there): monster speed 2, boss
actions 2, timeout after round 4 = forced retreat (+1 stress each).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .board import TILES
from .cards import STANCES, SkillCard
from .monsters import ENCOUNTER_DECK, MONSTERS, MSkill

DEATH_DIE = 0.3          # 3/10 czaszek (potwierdzone przez właściciela)
STRESS_CAP = 10
ROOM_ROUNDS = 4


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


@dataclass
class Action:
    kind: str                    # skill | move | swap | pass
    card: object = None          # SkillCard
    targets: tuple = ()
    area: int | None = None      # move destination
    move: int = 0                # swap direction -1/+1


class Fighter:
    def __init__(self, cls=None, loadout=None, mcard=None):
        if mcard is not None:
            self.is_hero = False
            self.card = mcard
            self.name = mcard.name
            self.max_hp = mcard.hp
            self.speed = mcard.speed
            self.base_unik = mcard.unik
            self.odp = set(mcard.odp)
            self.niewr = set(mcard.niewr)
            self.size = mcard.size
            self.skills = list(mcard.skills)
            self.actions = mcard.actions
            self.family = mcard.family
        else:
            self.is_hero = True
            self.cls = cls
            self.name = cls.name
            self.max_hp = cls.hp
            self.speed = cls.speed
            self.base_unik = cls.unik
            self.odp = set(cls.odp)
            self.niewr = set()
            self.size = 1
            names = list(loadout)
            if cls.forms:
                for t in ("Transformacja w Bestię",
                          "Transformacja w człowieka"):
                    if t not in names:
                        names.append(t)
            self.skills = [cls.skills[n] for n in names]
            self.actions = 1
            self.family = "czlowiek"
        self.hp = self.max_hp
        self.stress = 0
        self.form = "czlowiek"
        self.slot = None
        self.area = None
        self.dd = False
        self.dead = False
        self.affl = None            # None | "cnota" | "udreka"
        self.stacks = []            # [kind, amt_or_None, turns]
        # per-round bookkeeping
        self.acted = False
        self.actions_left = 0
        self.ticked = False

    # -- status helpers ---------------------------------------------------
    def n_stacks(self, kind):
        return sum(1 for s in self.stacks if s[0] == kind)

    def dot_amt(self, kind):
        return sum(s[1] for s in self.stacks if s[0] == kind and s[1])

    def has(self, kind):
        return self.n_stacks(kind) > 0

    def remove_kind(self, kinds):
        self.stacks = [s for s in self.stacks if s[0] not in kinds]

    def battle_reset(self):
        self.stacks = []
        self.acted = False
        self.ticked = False
        self.dd = self.dd and self.hp <= 0

    def __repr__(self):
        return f"<{self.name} hp={self.hp}/{self.max_hp}>"


class Battle:
    def __init__(self, heroes, monsters, tile_name, light, rng,
                 policy=None, on_event=None):
        from .heuristic import heuristic_policy
        self.tile = TILES[tile_name]
        self.light = light
        self.rng = rng
        self.policy = policy or heuristic_policy
        self.on_event = on_event
        self.heroes = list(heroes)
        self.monsters = list(monsters)
        self.round_no = 0
        self.boss = any((not f.is_hero) and f.card.boss for f in monsters)
        self.hero_slots = [None] * 4
        self.mon_slots = [None] * 4
        self._place()

    # -- setup ------------------------------------------------------------
    def _place(self):
        for i, h in enumerate(self.heroes):
            h.slot = i
            self.hero_slots[i] = h
            start = self.tile.hero_start[0 if i < 2 else 1]
            h.area = self._fit_area(start, h.size)
        for m in self.monsters:
            self._place_monster(m)

    def _fit_area(self, want, size):
        if self.free_space(want) >= size:
            return want
        order = sorted(range(self.tile.n),
                       key=lambda a: self.tile.dist(want, a))
        for a in order:
            if self.free_space(a) >= size:
                return a
        return want  # overcrowded fallback

    def _place_monster(self, m):
        slots = self.mon_slots
        idxs = (range(4) if m.card.row == "front" else range(3, -1, -1))
        placed = False
        for i in idxs:
            if m.size == 1:
                if slots[i] is None:
                    slots[i] = m
                    m.slot = i
                    placed = True
                    break
            else:
                j = i + 1 if m.card.row == "front" else i - 1
                if 0 <= j < 4 and slots[i] is None and slots[j] is None:
                    slots[i] = slots[j] = m
                    m.slot = min(i, j)
                    placed = True
                    break
        if not placed:
            for i in range(4):
                if slots[i] is None:
                    slots[i] = m
                    m.slot = i
                    placed = True
                    break
        start = self.tile.monster_start[0 if m.card.row == "front" else 1]
        m.area = self._fit_area(start, m.size)

    # -- queries ----------------------------------------------------------
    def alive_heroes(self):
        return [h for h in self.heroes if not h.dead]

    def alive_monsters(self):
        return [m for m in self.monsters if not m.dead]

    def occupants(self, area):
        return [f for f in self.alive_heroes() + self.alive_monsters()
                if f.area == area]

    def free_space(self, area):
        used = sum(f.size for f in self.occupants(area))
        return self.tile.caps[area] - used

    def dist(self, a, b):
        return self.tile.dist(a.area, b.area)

    def stance_of(self, f):
        return STANCES[f.slot] if f.slot is not None else "A"

    def eff_unik(self, f):
        u = f.base_unik
        if f.is_hero and self.light == 5:
            u += 1
        if not f.is_hero and self.light == 0:
            u += 1
        return u

    # -- stress / wounds --------------------------------------------------
    def add_stress(self, h, n):
        if not h.is_hero or h.dead:
            return
        if n <= 0:
            h.stress = max(0, h.stress + n)
            return
        if self.light <= 2:
            n += 1
        h.stress = min(STRESS_CAP, h.stress + n)
        if h.stress >= STRESS_CAP:
            if h.affl is None:
                roll = self.rng.randint(1, 10)
                h.affl = "cnota" if roll <= 2 else "udreka"
                h.stress = 0
            else:
                self._die(h)   # atak serca

    def wound_hero(self, h, n):
        if n <= 0 or h.dead:
            return
        if h.dd:
            if self.rng.random() < DEATH_DIE:
                self._die(h)
        else:
            h.hp -= n
            if h.hp <= 0:
                h.hp = 0
                h.dd = True

    def heal_fighter(self, f, n):
        if n <= 0 or f.dead:
            return
        f.hp = min(f.max_hp, f.hp + n)
        if f.is_hero and f.dd and f.hp > 0:
            f.dd = False

    def damage_monster(self, m, n, attacker=None):
        if n <= 0 or m.dead:
            return
        m.hp -= n
        if m.card.retaliate and attacker is not None and attacker.is_hero:
            for fx in m.card.retaliate:
                if fx.startswith("heal:"):
                    self.heal_fighter(m, int(fx.split(":")[1]))
                else:
                    self.apply_effect(m, attacker, fx)
        if m.hp <= 0:
            m.dead = True
            for i in range(4):
                if self.mon_slots[i] is m:
                    self.mon_slots[i] = None

    def _die(self, h):
        h.dead = True
        if h.slot is not None and self.hero_slots[h.slot] is h:
            self.hero_slots[h.slot] = None

    # -- statuses ---------------------------------------------------------
    def inflict(self, source, target, kind, turns, amt=None):
        if target.dead:
            return
        if kind in target.niewr:
            return
        if kind in target.odp:
            turns -= 1
        if turns <= 0:
            return
        target.stacks.append([kind, amt, turns])

    def apply_effect(self, actor, target, fx):
        parts = fx.split(":")
        kind = parts[0]
        if kind in ("krwotok", "zaraza"):
            self.inflict(actor, target, kind, int(parts[2]), int(parts[1]))
        elif kind in ("stun", "wzmoc", "oslab", "nazn", "riposta",
                      "ochrona", "garda"):
            self.inflict(actor, target, kind, int(parts[1]))
        elif kind == "push":
            self.shove(target, actor.area, int(parts[1]), away=True)
        elif kind == "pull":
            self.shove(target, actor.area, int(parts[1]), away=False)
        elif kind == "push_self":
            ref = self._nearest_opponent_area(actor)
            self.shove(actor, ref, int(parts[1]), away=True, forced=False)
        elif kind == "pull_self":
            ref = self._nearest_opponent_area(actor)
            self.shove(actor, ref, int(parts[1]), away=False, forced=False)
        elif kind == "stress":
            self.add_stress(target, int(parts[1]))
        elif kind == "light":
            self.light = clamp(self.light + int(parts[1]), 0, 5)
        elif kind == "heal":
            self.heal_fighter(actor, int(parts[1]))
        elif kind == "rany_self":
            self.wound_hero(actor, int(parts[1]))
        elif kind == "usun":
            target.remove_kind(set(parts[1].split(",")))
        elif kind == "transform":
            actor.form = parts[1]
        elif kind == "shuffle_stances":
            self._shuffle_hero_stances()

    def _nearest_opponent_area(self, f):
        opps = self.alive_monsters() if f.is_hero else self.alive_heroes()
        if not opps:
            return f.area
        return min(opps, key=lambda o: self.dist(f, o)).area

    def shove(self, target, ref_area, n, away, forced=True):
        """Move target n areas away from / toward ref_area."""
        if forced and "przesuwanie" in target.niewr:
            return
        if forced and "przesuwanie" in target.odp:
            n -= 1
        for _ in range(max(0, n)):
            d0 = self.tile.dist(ref_area, target.area)
            best = None
            for nb in self.tile.neighbors(target.area):
                d1 = self.tile.dist(ref_area, nb)
                good = d1 > d0 if away else d1 < d0
                if good and self.free_space(nb) >= target.size:
                    best = nb
                    break
            if best is None:
                return
            target.area = best

    def _shuffle_hero_stances(self):
        alive = self.alive_heroes()
        slots = [h.slot for h in alive]
        self.rng.shuffle(slots)
        self.hero_slots = [None] * 4
        for h, s in zip(alive, slots):
            h.slot = s
            self.hero_slots[s] = h

    # -- attack resolution ------------------------------------------------
    def resolve_attack(self, actor, card, target):
        """Returns wounds dealt (heals return negative-ish semantics)."""
        heal = getattr(card, "heal", False)
        if card.acc is None:
            if heal:
                self.heal_fighter(target, card.dmg)
            for fx in card.fx:
                self.apply_effect(actor, target, fx)
            return 0
        crit_eff = card.crit + actor.n_stacks("wzmoc")
        if not heal:
            crit_eff += target.n_stacks("oslab")
        if self.light <= 4:
            crit_eff += 1
        acc_eff = card.acc - self.eff_unik(target) \
            + target.n_stacks("nazn")
        if not actor.is_hero and self.light == 0:
            acc_eff += 1
        roll = self.rng.randint(1, 10)
        crit = roll <= crit_eff
        hit = crit or roll <= acc_eff
        if not hit:
            return 0
        amount = card.cdmg if crit else card.dmg
        if heal:
            self.heal_fighter(target, amount)
            for fx in card.fx:
                self.apply_effect(actor, target, fx)
            return 0
        for key, extra in getattr(card, "bonus", ()):
            if key == target.family or \
               (key in ("nazn", "zaraza", "stun") and target.has(key)):
                amount += extra
        if target.has("ochrona") and not getattr(card, "ignore_ochrona",
                                                 False):
            amount = math.ceil(amount / 2)
        dealt = amount
        if target.is_hero:
            self.wound_hero(target, dealt)
            if crit and not target.dead:
                self.add_stress(target, 1)
                for other in self.alive_heroes():
                    if other is not target and other.area == target.area:
                        self.add_stress(other, 1)
        else:
            self.damage_monster(target, dealt, attacker=actor)
        if not target.dead:
            for fx in card.fx:
                self.apply_effect(actor, target, fx)
        if target.has("riposta") and not actor.dead:
            back = math.ceil(dealt / 2)
            if actor.is_hero:
                self.wound_hero(actor, back)
            else:
                self.damage_monster(actor, back, attacker=target)
        return dealt

    # -- hero actions -----------------------------------------------------
    def reachable(self, f):
        seen = {f.area: 0}
        frontier = [f.area]
        for step in range(f.speed):
            nxt = []
            for a in frontier:
                for nb in self.tile.neighbors(a):
                    if nb not in seen:
                        seen[nb] = step + 1
                        nxt.append(nb)
            frontier = nxt
        return [a for a in seen
                if a != f.area and self.free_space(a) >= f.size]

    def legal_actions(self, hero):
        acts = []
        stance = self.stance_of(hero)
        allies = self.alive_heroes()
        enemies = self.alive_monsters()
        for card in hero.skills:
            if card.form and hero.form != card.form:
                continue
            if stance not in card.stances:
                continue
            lo, hi = card.rng
            if card.tgt == "self":
                acts.append(Action("skill", card, (hero,)))
            elif card.tgt == "allies_all":
                others = tuple(a for a in allies if a is not hero)
                acts.append(Action("skill", card, others))
            else:
                if card.tgt in ("ally", "any"):
                    pool = [a for a in allies
                            if lo <= self.tile.dist(hero.area, a.area) <= hi]
                    if card.n == 1:
                        acts += [Action("skill", card, (a,)) for a in pool]
                    elif pool:
                        pool.sort(key=lambda a: a.hp / a.max_hp)
                        acts.append(Action("skill", card,
                                           tuple(pool[:card.n])))
                if card.tgt in ("enemy", "any"):
                    pool = [e for e in enemies
                            if lo <= self.tile.dist(hero.area, e.area) <= hi]
                    if card.n == 1 or card.tgt == "any":
                        acts += [Action("skill", card, (e,)) for e in pool]
                    else:
                        for area in {e.area for e in pool}:
                            grp = [e for e in pool if e.area == area]
                            grp.sort(key=lambda e: e.hp)
                            acts.append(Action("skill", card,
                                               tuple(grp[:card.n])))
        for area in self.reachable(hero):
            acts.append(Action("move", area=area))
        for d in (-1, 1):
            if 0 <= hero.slot + d <= 3:
                acts.append(Action("swap", move=d))
        acts.append(Action("pass"))
        return acts

    def apply_action(self, hero, act):
        if act.kind == "pass":
            return
        if act.kind == "move":
            if self.free_space(act.area) >= hero.size:
                hero.area = act.area
            return
        if act.kind == "swap":
            new = hero.slot + act.move
            other = self.hero_slots[new]
            self.hero_slots[hero.slot] = other
            if other is not None:
                other.slot = hero.slot
            self.hero_slots[new] = hero
            hero.slot = new
            return
        card = act.card
        for t in act.targets:
            if t.dead:
                continue
            if t.is_hero and t is not hero and card.tgt == "any":
                for fx in card.ally_fx:
                    self.apply_effect(hero, t, fx)
            elif card.tgt == "allies_all":
                for fx in card.ally_fx:
                    self.apply_effect(hero, t, fx)
            else:
                self.resolve_attack(hero, card, t)
        for fx in card.self_fx:
            self.apply_effect(hero, hero, fx)

    # -- turn / round flow ------------------------------------------------
    def tick_statuses(self, f):
        batch = 0
        keep = []
        stun_stacks = 0
        for s in f.stacks:
            kind, amt, turns = s
            if kind in ("krwotok", "zaraza"):
                batch += amt
            elif kind == "stun":
                stun_stacks += 1
            s[2] -= 1
            if s[2] > 0:
                keep.append(s)
        f.stacks = keep
        if batch:
            if f.is_hero:
                self.wound_hero(f, batch)
            else:
                self.damage_monster(f, batch)
        return stun_stacks

    def hero_turn(self, hero):
        hero.acted = True
        stun = self.tick_statuses(hero)
        if hero.dead:
            return
        if hero.affl == "cnota" and self.rng.randint(1, 10) <= 5:
            self.inflict(hero, hero, "wzmoc", 2)
        elif hero.affl == "udreka" and self.rng.randint(1, 10) <= 4:
            self.inflict(hero, hero, "oslab", 1)
        actions = max(0, 2 - stun)
        while actions > 0 and self.alive_monsters() and not hero.dead:
            act = self.policy(self, hero)
            if act.kind == "pass":
                break
            self.apply_action(hero, act)
            actions -= 1

    # -- monster AI -------------------------------------------------------
    def _garda_pool(self):
        pool = self.alive_heroes()
        guards = [h for h in pool if h.has("garda")]
        return guards or pool

    def _choose_mskill(self, m):
        entry = m.card.stance_map[m.slot if m.slot is not None else 0]
        if isinstance(entry, int):
            return m.skills[entry]
        roll = self.rng.randint(1, 10)
        for lo, hi, idx in entry:
            if lo <= roll <= hi:
                return m.skills[idx]
        return m.skills[0]

    def _mtargets(self, m, sk):
        pool = self._garda_pool()
        if not pool:
            return []
        if sk.rule == "zatloczony":
            areas = {}
            for h in pool:
                areas.setdefault(h.area, []).append(h)
            area = max(areas, key=lambda a: len(areas[a]))
            return areas[area][:sk.n]
        if sk.rule == "specjalna":
            areas = sorted({h.area for h in pool})
            area = self.rng.choice(areas)
            return [h for h in pool if h.area == area][:sk.n]
        if sk.rule == "zestresowany":
            return [max(pool, key=lambda h: h.stress)]
        if sk.rule in ("nazn_najdalszy", "nazn_najblizszy"):
            marked = [h for h in pool if h.has("nazn")]
            if marked:
                key = (lambda h: self.dist(m, h))
                pick = min(marked, key=key)
                return [pick]
            far = sk.rule == "nazn_najdalszy"
            f = (max if far else min)(pool, key=lambda h: self.dist(m, h))
            return [f]
        if sk.rule == "najdalszy":
            return [max(pool, key=lambda h: self.dist(m, h))]
        return [min(pool, key=lambda h: self.dist(m, h))]

    def monster_action(self, m):
        if not m.ticked:
            m.ticked = True
            stun = self.tick_statuses(m)
            if stun:
                m.actions_left = max(0, m.actions_left - stun + 1)
                if m.dead:
                    return
                return  # this action consumed by stun
            if m.dead:
                return
        sk = self._choose_mskill(m)
        if sk.rule == "summon":
            self._summon()
            return
        targets = self._mtargets(m, sk)
        if not targets:
            return
        lo, hi = sk.rng
        primary = targets[0]
        d = self.dist(m, primary)
        if d > hi:
            steps = m.speed
            while steps > 0 and self.tile.dist(m.area, primary.area) > hi:
                cur = self.tile.dist(m.area, primary.area)
                nxt = None
                for nb in self.tile.neighbors(m.area):
                    if self.tile.dist(nb, primary.area) < cur and \
                            self.free_space(nb) >= m.size:
                        nxt = nb
                        break
                if nxt is None:
                    break
                m.area = nxt
                steps -= 1
            d = self.dist(m, primary)
        if not (lo <= d <= hi):
            return
        for t in targets:
            if self.tile.dist(m.area, t.area) <= hi and not t.dead:
                self.resolve_attack(m, sk, t)
        for fx in sk.self_fx:
            self.apply_effect(m, m, fx)

    def _summon(self):
        free = sum(1 for s in self.mon_slots if s is None)
        if free < 1:
            return
        names = [n for n, w in ENCOUNTER_DECK for _ in range(w)
                 if MONSTERS[n].size == 1]
        card = MONSTERS[self.rng.choice(names)]
        f = Fighter(mcard=card)
        self.monsters.append(f)
        self._place_monster(f)

    # -- main loop --------------------------------------------------------
    def run_round(self):
        self.round_no += 1
        if not self.boss and self.round_no > ROOM_ROUNDS:
            return "timeout"
        for h in self.alive_heroes():
            h.acted = False
        for m in self.alive_monsters():
            m.actions_left = m.actions
            m.ticked = False
        deck = ["H"] * len(self.alive_heroes()) + \
               ["M"] * sum(m.actions for m in self.alive_monsters())
        self.rng.shuffle(deck)
        for side in deck:
            if not self.alive_monsters():
                return "win"
            if not self.alive_heroes():
                return "loss"
            if side == "H":
                nxt = [h for h in self.alive_heroes() if not h.acted]
                nxt.sort(key=lambda h: h.slot)
                if nxt:
                    self.hero_turn(nxt[0])
            else:
                nxt = [m for m in self.alive_monsters()
                       if m.actions_left > 0]
                nxt.sort(key=lambda m: m.slot)
                if nxt:
                    nxt[0].actions_left -= 1
                    self.monster_action(nxt[0])
        if not self.alive_monsters():
            return "win"
        if not self.alive_heroes():
            return "loss"
        return None

    def run(self):
        result = None
        while result is None:
            result = self.run_round()
        if result == "timeout":
            for h in self.alive_heroes():
                self.add_stress(h, 1)
        return result
