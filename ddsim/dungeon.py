"""A full dungeon run: 4 encounters drawn from the encounter table."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .combat import Battle
from .data import ENCOUNTER_TABLE, ENEMY_TYPES, HERO_CLASSES
from .models import Enemy, Hero
from .policy import PolicyParams, make_policy

RECOVERY_CASTS = 3  # free support casts after each victorious encounter


@dataclass
class RunResult:
    win: bool = False
    encounters_cleared: int = 0
    deaths: int = 0
    rounds: int = 0
    afflictions: int = 0
    heart_attacks: int = 0
    end_stress: float = 0.0  # mean stress of survivors
    survivors: int = 0
    log: list = field(default_factory=list)


def build_party(party_spec):
    """party_spec: sequence of (class_name, [4 skill names]), rank 1 first."""
    return [Hero(HERO_CLASSES[cls], skills) for cls, skills in party_spec]


def build_encounter(rng, slot):
    template = rng.choice(ENCOUNTER_TABLE[slot])
    return [Enemy(ENEMY_TYPES[n]) for n in template]


def recovery_phase(heroes, rng, policy_params, log=None):
    """Post-victory breather: emulates stalling — a few free support casts."""
    from .policy import _support_value  # local import to avoid cycle

    for h in heroes:
        h.battle_reset()
    battle = Battle(heroes, [], rng, hero_policy=None, log=log)
    for _ in range(RECOVERY_CASTS):
        best, best_score = None, 4.0  # only worthwhile casts
        for h in battle.alive_heroes():
            for skill in h.skills:
                if skill.target_type not in ("ally", "party", "self"):
                    continue
                if skill.heal is None and skill.stress_heal is None:
                    continue
                for tl in battle.legal_targets(h, skill):
                    score = _support_value(battle, h, skill, tl, policy_params)
                    if score > best_score:
                        best, best_score = (h, skill, tl), score
        if best is None:
            break
        h, skill, tl = best
        for t in tl:
            battle.resolve_support(h, skill, t)
    for h in heroes:
        h.buffs = [b for b in h.buffs if b[2] >= 90]  # keep virtue/affliction only


def run_dungeon(party_spec, policy_params: PolicyParams, seed, keep_log=False):
    rng = random.Random(seed)
    heroes = build_party(party_spec)
    policy = make_policy(policy_params)
    result = RunResult()
    log = [] if keep_log else None

    for slot in range(len(ENCOUNTER_TABLE)):
        for h in heroes:
            h.battle_reset()
        alive = [h for h in heroes if h.alive]
        if not alive:
            break
        if log is not None:
            log.append(f"--- Encounter {slot + 1} ---")
        enemies = build_encounter(rng, slot)
        battle = Battle(alive, enemies, rng, policy, log=log)
        won = battle.run()
        result.rounds += battle.round
        result.afflictions += battle.stats["afflictions"]
        result.heart_attacks += battle.stats["heart_attacks"]
        heroes = [h for h in heroes if h.alive]
        if not won:
            break
        result.encounters_cleared += 1
        if slot < len(ENCOUNTER_TABLE) - 1:
            recovery_phase(heroes, rng, policy_params, log=log)

    survivors = [h for h in heroes if h.alive]
    result.win = result.encounters_cleared == len(ENCOUNTER_TABLE) and bool(survivors)
    result.deaths = 4 - len(survivors)
    result.survivors = len(survivors)
    result.end_stress = (
        sum(h.stress for h in survivors) / len(survivors) if survivors else 200.0
    )
    if log is not None:
        result.log = log
    return result
