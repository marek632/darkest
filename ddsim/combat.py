"""Battle resolution engine."""

from __future__ import annotations

import random

from .models import Combatant, Enemy, Hero, Skill

MAX_ROUNDS = 40
STRESS_VIRTUE_CHANCE = 25  # % on resolve test
STRESS_CAP = 200
CRIT_STRESS_SELF_HEAL = 3   # hero landing a crit
CRIT_STRESS_ON_VICTIM = 8   # hero being crit
DEATHS_DOOR_STRESS = 10     # stress on reaching death's door


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class Action:
    __slots__ = ("kind", "skill", "targets", "move")

    def __init__(self, kind, skill=None, targets=(), move=0):
        self.kind = kind  # 'skill' | 'move' | 'pass'
        self.skill = skill
        self.targets = list(targets)
        self.move = move


class Battle:
    def __init__(self, heroes, enemies, rng: random.Random, hero_policy, log=None):
        self.heroes = [h for h in heroes if h.alive]
        self.enemies = enemies
        self.rng = rng
        self.hero_policy = hero_policy
        self.log = log
        self.round = 0
        self.stats = {"crits_taken": 0, "afflictions": 0, "heart_attacks": 0}

    # -- helpers -----------------------------------------------------------
    def say(self, msg):
        if self.log is not None:
            self.log.append(f"R{self.round}: {msg}")

    def rank_of(self, c):
        side = self.heroes if c.is_hero else self.enemies
        return side.index(c) + 1

    def side_of(self, c):
        return self.heroes if c.is_hero else self.enemies

    def foes_of(self, c):
        return self.enemies if c.is_hero else self.heroes

    def alive_heroes(self):
        return [h for h in self.heroes if h.alive]

    def alive_enemies(self):
        return [e for e in self.enemies if e.alive]

    def over(self):
        return not self.alive_heroes() or not self.alive_enemies()

    def won(self):
        return bool(self.alive_heroes()) and not self.alive_enemies()

    # -- stress / death ----------------------------------------------------
    def add_stress(self, hero: Hero, amount):
        if not hero.alive or amount <= 0:
            return
        before = hero.stress
        hero.stress = min(STRESS_CAP, hero.stress + amount)
        if before < 100 <= hero.stress and not hero.resolve_tested:
            hero.resolve_tested = True
            if self.rng.uniform(0, 100) < STRESS_VIRTUE_CHANCE:
                hero.virtuous = True
                hero.stress = 45
                hero.add_buff("acc", 10, 9999)
                hero.add_buff("dmg_mult", 0.15, 9999)
                self.say(f"{hero.name} is VIRTUOUS")
            else:
                hero.afflicted = True
                hero.add_buff("acc", -5, 9999)
                hero.add_buff("dodge", -5, 9999)
                self.stats["afflictions"] += 1
                self.say(f"{hero.name} is AFFLICTED")
        if hero.stress >= STRESS_CAP:
            self.stats["heart_attacks"] += 1
            hero.stress = 170
            if hero.at_deaths_door:
                self.kill_hero(hero, "heart attack")
            else:
                hero.hp = 0
                self.add_stress_on_deaths_door(hero)
                self.say(f"{hero.name} suffers a HEART ATTACK -> death's door")

    def relieve_stress(self, hero: Hero, amount):
        hero.stress = max(0, hero.stress - amount)

    def add_stress_on_deaths_door(self, hero):
        # party sees a comrade fall to death's door
        for h in self.alive_heroes():
            if h is not hero:
                self.add_stress(h, 4)

    def kill_hero(self, hero: Hero, cause):
        hero.alive = False
        hero.hp = 0
        self.say(f"{hero.name} DIES ({cause})")
        for h in self.alive_heroes():
            self.add_stress(h, 10)
        if hero in self.heroes:
            self.heroes.remove(hero)

    def damage_hero(self, hero: Hero, dmg, cause="attack"):
        if not hero.alive:
            return
        if hero.at_deaths_door:
            # any damage at death's door forces a death blow check
            if self.rng.uniform(0, 100) >= hero.resists.deathblow:
                self.kill_hero(hero, f"death blow ({cause})")
            return
        hero.hp -= dmg
        if hero.hp <= 0:
            hero.hp = 0
            self.add_stress(hero, DEATHS_DOOR_STRESS)
            self.add_stress_on_deaths_door(hero)
            self.say(f"{hero.name} is at DEATH'S DOOR")

    def damage_enemy(self, enemy: Enemy, dmg):
        if not enemy.alive:
            return
        enemy.hp -= dmg
        if enemy.hp <= 0:
            enemy.alive = False
            enemy.hp = 0
            self.say(f"{enemy.name} destroyed")
            if enemy in self.enemies:
                self.enemies.remove(enemy)

    def apply_damage(self, target, dmg, cause="attack"):
        if target.is_hero:
            self.damage_hero(target, dmg, cause)
        else:
            self.damage_enemy(target, dmg)

    # -- movement ----------------------------------------------------------
    def move_combatant(self, c, delta):
        """delta < 0 -> toward rank 1 (front)."""
        side = self.side_of(c)
        if c not in side or len(side) < 2:
            return
        i = side.index(c)
        j = clamp(i + delta, 0, len(side) - 1)
        if i != j:
            side.pop(i)
            side.insert(j, c)

    # -- attack resolution -------------------------------------------------
    def roll_damage(self, actor, skill: Skill, target):
        if skill.dmg_range is not None:  # enemy attack
            from .tuning import ENEMY_DMG_MULT

            lo = skill.dmg_range[0] * ENEMY_DMG_MULT
            hi = skill.dmg_range[1] * ENEMY_DMG_MULT
        else:
            lo = actor.dmg[0] * skill.dmg_mod
            hi = actor.dmg[1] * skill.dmg_mod
        dmg = self.rng.uniform(lo, hi)
        mult = actor.stat("dmg_mult")
        if target.marked > 0:
            mult += skill.vs_marked
        if target.stunned:
            mult += skill.vs_stunned
        dmg *= max(0.0, mult)
        return dmg, hi * max(0.0, mult)

    def resolve_attack(self, actor, skill: Skill, target):
        """One attack roll against one target. Returns 'miss'|'hit'|'crit'|'dead'."""
        if not target.alive:
            return "dead"
        hit_chance = clamp(skill.acc + actor.stat("acc") - target.stat("dodge"), 5, 95)
        if self.rng.uniform(0, 100) >= hit_chance:
            self.say(f"{actor.name} {skill.name} misses {target.name}")
            return "miss"

        crit = False
        result = "hit"
        deals_damage = skill.dmg_mod is not None or skill.dmg_range is not None
        if deals_damage:
            dmg, max_dmg = self.roll_damage(actor, skill, target)
            crit_chance = actor.stat("crit") + skill.crit_mod
            if self.rng.uniform(0, 100) < crit_chance:
                crit = True
                result = "crit"
                dmg = max_dmg * 1.5
            dmg *= 1.0 - clamp(target.stat("prot"), 0, 90) / 100.0
            dmg = max(1, round(dmg))
            self.apply_damage(target, dmg, cause=skill.name)
            if crit:
                if actor.is_hero:
                    self.relieve_stress(actor, CRIT_STRESS_SELF_HEAL)
                if target.is_hero and target.alive:
                    self.stats["crits_taken"] += 1
                    self.add_stress(target, CRIT_STRESS_ON_VICTIM)
            self.say(f"{actor.name} {skill.name} {'CRITS' if crit else 'hits'} "
                     f"{target.name} for {dmg}")

        if not target.alive:
            return "crit" if crit else "hit"

        if skill.stress_dmg is not None and target.is_hero:
            from .tuning import ENEMY_STRESS_MULT

            amt = round(self.rng.randint(*skill.stress_dmg) * ENEMY_STRESS_MULT)
            if crit:
                amt = round(amt * 1.5)
            self.add_stress(target, amt)
            self.say(f"{target.name} suffers {amt} stress")

        if skill.stun is not None:
            chance = skill.stun - target.stat("stun_resist")
            if self.rng.uniform(0, 100) < chance:
                target.stunned = True
                self.say(f"{target.name} is stunned")

        if skill.dot is not None:
            resist = target.stat(f"{skill.dot.kind}_resist")
            if self.rng.uniform(0, 100) < skill.dot.chance - resist:
                target.dots.append([skill.dot.kind, skill.dot.dpr, skill.dot.duration])
                self.say(f"{target.name} suffers {skill.dot.kind}")

        if skill.mark:
            target.marked = max(target.marked, skill.mark)

        if skill.target_debuffs:
            if self.rng.uniform(0, 100) < skill.debuff_chance - target.stat("debuff_resist"):
                for b in skill.target_debuffs:
                    target.add_buff(b.stat, b.amount, b.duration)

        if skill.target_move and target.alive:
            self.move_combatant(target, skill.target_move)

        return result

    def resolve_support(self, actor, skill: Skill, target):
        """Heals, stress heals, ally buffs (no accuracy roll)."""
        if not target.alive:
            return
        if skill.heal is not None:
            amt = self.rng.randint(*skill.heal)
            crit_chance = 5 + skill.crit_mod
            if self.rng.uniform(0, 100) < crit_chance:
                amt = round(amt * 1.5)
            was_at_door = target.is_hero and target.at_deaths_door
            target.hp = min(target.max_hp, target.hp + max(0 if skill.heal[0] == 0 else 1, amt))
            if was_at_door and target.hp > 0:
                self.say(f"{target.name} recovers from death's door")
            self.say(f"{actor.name} {skill.name} heals {target.name} for {amt}")
        if skill.stress_heal is not None and target.is_hero:
            amt = self.rng.randint(*skill.stress_heal)
            self.relieve_stress(target, amt)
        if skill.cure_dots:
            target.dots = []
        if skill.dot is not None:  # risky heals (Wyrd Reconstruction)
            resist = target.stat(f"{skill.dot.kind}_resist")
            if self.rng.uniform(0, 100) < skill.dot.chance - resist:
                target.dots.append([skill.dot.kind, skill.dot.dpr, skill.dot.duration])
        for b in skill.target_buffs:
            target.add_buff(b.stat, b.amount, b.duration)

    def execute(self, actor, action: Action):
        if action.kind == "pass":
            return
        if action.kind == "move":
            self.move_combatant(actor, action.move)
            return
        skill = action.skill
        uses = actor.skill_uses.get(skill.name, 0)
        actor.skill_uses[skill.name] = uses + 1
        for target in list(action.targets):
            if skill.target_type == "enemy":
                self.resolve_attack(actor, skill, target)
            else:
                self.resolve_support(actor, skill, target)
        for b in skill.self_buffs:
            actor.add_buff(b.stat, b.amount, b.duration)
        if skill.mark and skill.target_type == "self":
            actor.marked = max(actor.marked, skill.mark)
        if skill.self_move:
            self.move_combatant(actor, skill.self_move)

    # -- legality ----------------------------------------------------------
    def legal_targets(self, actor, skill: Skill):
        """Return list of target-lists. Single-target: one list per candidate.
        AOE/party: a single list containing everyone hit."""
        if skill.target_type == "self":
            return [[actor]]
        if skill.target_type in ("ally", "party"):
            allies = self.alive_heroes() if actor.is_hero else self.alive_enemies()
            pool = [a for a in allies if self.rank_of(a) in skill.targets]
            if skill.target_type == "party":
                return [pool] if pool else []
            return [[a] for a in pool]
        foes = self.foes_of(actor)
        pool = [f for f in foes if f.alive and self.rank_of(f) in skill.targets]
        if not pool:
            return []
        if skill.aoe:
            return [pool]
        return [[f] for f in pool]

    def legal_actions(self, actor):
        acts = []
        for skill in (actor.skills if actor.is_hero else actor.etype.skills):
            if self.rank_of(actor) not in skill.launch and skill.target_type != "self":
                continue
            if skill.limit and actor.skill_uses.get(skill.name, 0) >= skill.limit:
                continue
            for tl in self.legal_targets(actor, skill):
                acts.append(Action("skill", skill=skill, targets=tl))
        return acts

    # -- enemy AI ----------------------------------------------------------
    def enemy_choose(self, enemy: Enemy):
        legal = self.legal_actions(enemy)
        if not legal:
            return Action("move", move=-1)
        # weight actions by their skill's configured weight
        wmap = {s.name: w for s, w in zip(enemy.etype.skills, enemy.etype.weights)}
        prefer = enemy.etype.prefer
        weights = []
        for a in legal:
            w = wmap.get(a.skill.name, 0.1)
            if len(a.targets) == 1 and a.targets[0].is_hero:
                t = a.targets[0]
                if prefer == "back":
                    w *= 1.0 + 0.5 * (self.rank_of(t) - 1)
                elif prefer == "stress":
                    w *= 1.0 + t.stress / 60.0
                elif prefer == "weak":
                    w *= 1.0 + 2.0 * (1.0 - t.hp / t.max_hp)
                if t.marked > 0:
                    w *= 1.6
            weights.append(max(w, 0.01))
        return self.rng.choices(legal, weights=weights, k=1)[0]

    # -- round loop --------------------------------------------------------
    def tick_dots(self, c):
        total = 0
        for d in c.dots:
            total += d[1]
            d[2] -= 1
        c.dots = [d for d in c.dots if d[2] > 0]
        if total > 0:
            self.say(f"{c.name} takes {total} from DoTs")
            self.apply_damage(c, total, cause="dot")

    def afflicted_act_out(self, hero):
        """Afflicted heroes sometimes refuse to act and stress the party."""
        if hero.afflicted and self.rng.uniform(0, 100) < 20:
            for h in self.alive_heroes():
                if h is not hero:
                    self.add_stress(h, 2)
            self.say(f"{hero.name} acts out (afflicted)")
            return True
        return False

    def take_turn(self, actor):
        if not actor.alive or self.over():
            return
        self.tick_dots(actor)
        if not actor.alive or self.over():
            return
        if actor.stunned:
            actor.stunned = False
            actor.add_buff("stun_resist", 50, 2)
            self.say(f"{actor.name} shakes off stun")
            return
        if actor.is_hero:
            if self.afflicted_act_out(actor):
                return
            action = self.hero_policy(self, actor)
        else:
            action = self.enemy_choose(actor)
        self.execute(actor, action)

    def end_round(self):
        for c in self.alive_heroes() + self.alive_enemies():
            for b in c.buffs:
                b[2] -= 1
            c.buffs = [b for b in c.buffs if b[2] > 0]
            if c.marked > 0:
                c.marked -= 1

    def run(self):
        while not self.over() and self.round < MAX_ROUNDS:
            self.round += 1
            order = sorted(
                self.alive_heroes() + self.alive_enemies(),
                key=lambda c: c.stat("spd") + self.rng.uniform(1, 8),
                reverse=True,
            )
            for actor in order:
                self.take_turn(actor)
                if self.over():
                    break
            self.end_round()
        return self.won()
