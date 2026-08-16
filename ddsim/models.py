"""Core data model for the Darkest Dungeon board-game simulator.

Conventions
-----------
* Hero party is a list; index 0 is rank 1 (the front, adjacent to enemies).
  Enemy group likewise: index 0 is their rank 1 (their front).
* Hero skill ``launch`` ranks refer to the hero's own rank; ``targets`` refer
  to enemy ranks (or ally ranks for support skills).
* ``self_move``: negative moves toward rank 1 (front), positive toward the back.
  ``target_move``: positive pushes the target toward its own back ranks.
* All chances are percentages (0-100).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Buff:
    """A temporary stat modifier. ``stat`` is one of:
    acc, dodge, prot, spd, crit, dmg_mult, stun_resist, bleed_resist,
    blight_resist, debuff_resist."""

    stat: str
    amount: float
    duration: int  # rounds


@dataclass(frozen=True)
class Dot:
    kind: str  # 'bleed' | 'blight'
    chance: float  # base application chance, reduced by target resist
    dpr: int  # damage per round
    duration: int  # rounds


@dataclass(frozen=True)
class Skill:
    name: str
    launch: tuple  # ranks the user may act from, e.g. (1, 2)
    targets: tuple  # ranks that can be targeted
    target_type: str = "enemy"  # enemy | ally | self | party (all allies)
    aoe: bool = False  # hits every legal target rank at once
    acc: float = 0.0  # base accuracy (attacks only)
    dmg_mod: Optional[float] = None  # None = no damage component; scales class dmg
    dmg_range: Optional[tuple] = None  # enemies: absolute damage range
    crit_mod: float = 0.0
    heal: Optional[tuple] = None  # (min, max) hp restored
    stress_heal: Optional[tuple] = None  # (min, max) stress removed (heroes)
    stress_dmg: Optional[tuple] = None  # (min, max) stress inflicted (enemies)
    stun: Optional[float] = None  # base stun chance
    dot: Optional[Dot] = None
    mark: int = 0  # rounds of Mark applied to target
    cure_dots: bool = False
    self_move: int = 0
    target_move: int = 0
    vs_marked: float = 0.0  # extra dmg multiplier vs marked targets
    vs_stunned: float = 0.0  # extra dmg multiplier vs stunned targets
    vs_family: Optional[tuple] = None  # (family, bonus) e.g. ("unholy", 0.15)
    vs_blighted: float = 0.0  # extra dmg multiplier vs blighted targets
    ignore_prot: bool = False  # armor piercing
    self_heal: Optional[tuple] = None  # hp restored to the user on cast
    riposte: Optional[tuple] = None  # (rounds, dmg_mult): counter when hit
    summon: Optional[str] = None  # enemy type spawned on use (monsters)
    self_buffs: tuple = ()
    target_buffs: tuple = ()  # beneficial, applied to allies (no resist)
    target_debuffs: tuple = ()  # hostile, resisted by debuff resist
    debuff_chance: float = 100.0
    limit: int = 0  # uses per battle; 0 = unlimited


@dataclass(frozen=True)
class Resists:
    stun: float = 40
    bleed: float = 30
    blight: float = 30
    debuff: float = 30
    move: float = 40
    deathblow: float = 67  # chance to SURVIVE a hit at death's door


@dataclass(frozen=True)
class HeroClass:
    name: str
    hp: int
    dodge: float
    spd: int
    dmg: tuple  # weapon damage range (min, max)
    crit: float
    resists: Resists
    skills: dict  # skill name -> Skill
    acc_mod: float = 0.0


@dataclass(frozen=True)
class EnemyType:
    name: str
    hp: int
    dodge: float
    prot: float
    spd: int
    crit: float
    resists: Resists
    skills: tuple  # of Skill
    weights: tuple  # selection weight per skill
    prefer: str = "random"  # random | back | front | stress | weak | marked
    tags: tuple = ()  # e.g. ('stress',), ('tank',), ('ranged',)
    family: str = "human"  # unholy | human | eldritch | beast (vs_family bonuses)
    is_boss: bool = False


class Combatant:
    """Mutable battle state shared by heroes and enemies."""

    def __init__(self, name, max_hp, dodge, prot, spd, crit, dmg, acc_mod, resists):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.base_dodge = dodge
        self.base_prot = prot
        self.base_spd = spd
        self.base_crit = crit
        self.dmg = dmg
        self.acc_mod = acc_mod
        self.resists = resists
        self.alive = True
        self.stunned = False
        self.marked = 0  # rounds remaining
        self.riposte = None  # [rounds_left, dmg_mult] while active
        self.buffs = []  # list of [stat, amount, rounds_left]
        self.dots = []  # list of [kind, dpr, rounds_left]
        self.skill_uses = {}

    # -- stats -------------------------------------------------------------
    def stat(self, name):
        base = {
            "dodge": self.base_dodge,
            "prot": self.base_prot,
            "spd": self.base_spd,
            "crit": self.base_crit,
            "acc": self.acc_mod,
            "dmg_mult": 1.0,
            "stun_resist": self.resists.stun,
            "bleed_resist": self.resists.bleed,
            "blight_resist": self.resists.blight,
            "debuff_resist": self.resists.debuff,
        }[name]
        return base + sum(b[1] for b in self.buffs if b[0] == name)

    def add_buff(self, stat, amount, duration):
        self.buffs.append([stat, amount, duration])

    def has_dot(self):
        return bool(self.dots)

    def battle_reset(self):
        """Clear transient battle state between encounters (keep permanent
        virtue/affliction modifiers, which use duration >= 900)."""
        self.stunned = False
        self.marked = 0
        self.riposte = None
        self.buffs = [b for b in self.buffs if b[2] >= 900]
        self.dots = []
        self.skill_uses = {}

    @property
    def is_hero(self):
        return isinstance(self, Hero)


class Hero(Combatant):
    def __init__(self, cls: HeroClass, skill_names):
        super().__init__(
            cls.name, cls.hp, cls.dodge, 0, cls.spd, cls.crit, cls.dmg,
            cls.acc_mod, cls.resists,
        )
        self.cls = cls
        unknown = [s for s in skill_names if s not in cls.skills]
        if unknown:
            raise ValueError(f"{cls.name} has no skill(s) {unknown}")
        if len(skill_names) != 3:
            # official rules: "pick three level one skills from the hero's deck"
            raise ValueError(f"{cls.name}: exactly 3 skills required, got {len(skill_names)}")
        self.skills = [cls.skills[s] for s in skill_names]
        self.stress = 0
        self.resolve_tested = False
        self.afflicted = False
        self.virtuous = False

    @property
    def at_deaths_door(self):
        return self.alive and self.hp <= 0


class Enemy(Combatant):
    def __init__(self, etype: EnemyType):
        from .tuning import ENEMY_HP_MULT

        super().__init__(
            etype.name, round(etype.hp * ENEMY_HP_MULT), etype.dodge, etype.prot,
            etype.spd, etype.crit, (0, 0), 0.0, etype.resists,
        )
        self.etype = etype

    @property
    def threat(self):
        """Rough danger estimate used by hero targeting AI."""
        total = 0.0
        for sk, w in zip(self.etype.skills, self.etype.weights):
            v = 0.0
            if sk.dmg_range:
                v += (sk.dmg_range[0] + sk.dmg_range[1]) / 2 * (min(sk.acc, 9) / 10.0)
            if sk.stress_dmg:
                # stress is on the short 0-10 track: a point of stress is worth
                # roughly a point of hp x9 in threat terms
                v += (sk.stress_dmg[0] + sk.stress_dmg[1]) / 2 * 9.0
            if sk.stun is not None:
                v += 2.0
            total += v * w
        total /= sum(self.etype.weights)
        return total
