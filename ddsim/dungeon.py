"""A full dungeon run: 4 rooms drawn from the encounter table.

Board-game structure (see docs/RULES_AUDIT.md):
* Each room's battle lasts at most 4 rounds. An uncleared room forces a
  retreat: heroes keep their wounds, gain stress, the light tracker drops,
  and the room refills to a full monster group for the next attempt.
* The light tracker starts at 5 and never ends the quest: low light makes
  monsters stronger (damage/crit/stress per the source game's light-meter
  table). Failure comes from attrition — party wipes, stress spirals — or
  a generous simulation safety cap on total battles.
* Clearing a room grants a fixed pool of rest points, each restoring a flat
  amount of HP or stress — independent of anyone's skill kit.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .combat import Battle
from .data import ENCOUNTER_TABLE, ENEMY_TYPES, HERO_CLASSES
from .models import Enemy, Hero
from .policy import PolicyParams, make_policy

LIGHT_START = 5
REST_POINTS = 4       # per cleared room (not after the final room)
REST_HEAL_HP = 3      # hp restored by one rest point
REST_HEAL_STRESS = 2  # stress removed by one rest point
RETREAT_STRESS = 1    # per hero, on a forced retreat
MAX_BATTLES = 20      # simulation safety cap only; darkness never ends a quest


@dataclass
class RunResult:
    win: bool = False
    encounters_cleared: int = 0
    deaths: int = 0
    rounds: int = 0
    retreats: int = 0
    light_remaining: int = 0
    afflictions: int = 0
    heart_attacks: int = 0
    end_stress: float = 0.0  # mean stress of survivors
    survivors: int = 0
    log: list = field(default_factory=list)


def build_party(party_spec):
    """party_spec: sequence of (class_name, [3 skill names]), rank 1 first."""
    return [Hero(HERO_CLASSES[cls], skills) for cls, skills in party_spec]


def build_encounter(rng, slot):
    template = rng.choice(ENCOUNTER_TABLE[slot])
    return [Enemy(ENEMY_TYPES[n]) for n in template]


def rest_phase(heroes, log=None):
    """Camp after clearing a room: spend rest points on hp or stress."""
    for h in heroes:
        h.battle_reset()
    alive = [h for h in heroes if h.alive]
    for _ in range(REST_POINTS):
        best, best_score, best_kind = None, 1.0, None
        for h in alive:
            missing = h.max_hp - h.hp
            heal_score = min(missing, REST_HEAL_HP) * 1.5 + (20 if h.hp == 0 else 0)
            if heal_score > best_score:
                best, best_score, best_kind = h, heal_score, "hp"
            stress_score = min(h.stress, REST_HEAL_STRESS) * 3.0
            if h.stress >= 8 and not h.resolve_tested:
                stress_score += 15
            if stress_score > best_score:
                best, best_score, best_kind = h, stress_score, "stress"
        if best is None:
            break
        if best_kind == "hp":
            best.hp = min(best.max_hp, best.hp + REST_HEAL_HP)
        else:
            best.stress = max(0, best.stress - REST_HEAL_STRESS)
        if log is not None:
            log.append(f"camp: {best.name} recovers {best_kind}")


def run_dungeon(party_spec, policy_params: PolicyParams, seed, keep_log=False):
    rng = random.Random(seed)
    heroes = build_party(party_spec)
    policy = make_policy(policy_params)
    result = RunResult()
    log = [] if keep_log else None
    light = LIGHT_START
    battles = 0

    for slot in range(len(ENCOUNTER_TABLE)):
        cleared = False
        while not cleared and battles < MAX_BATTLES:
            alive = [h for h in heroes if h.alive]
            if not alive:
                break
            for h in alive:
                h.battle_reset()
            if log is not None:
                log.append(f"--- Room {slot + 1} (light {light}) ---")
            # each attempt faces a full monster group (reinforcements);
            # low light makes them hit harder and stress more (never ends
            # the quest — official light rules are penalties, not failure)
            enemies = build_encounter(rng, slot)
            battle = Battle(alive, enemies, rng, policy, log=log, light=light)
            battles += 1
            cleared = battle.run()
            result.rounds += battle.round
            result.afflictions += battle.stats["afflictions"]
            result.heart_attacks += battle.stats["heart_attacks"]
            heroes = [h for h in heroes if h.alive]
            if not cleared:
                if not battle.alive_heroes():
                    break  # party wiped
                # forced retreat after 4 rounds: stress, and the wasted time
                # burns light (adaptation — see docs/RULES_AUDIT.md ledger)
                result.retreats += 1
                light = max(0, light - 1)
                if log is not None:
                    log.append("retreat! the room refills with monsters")
                for h in battle.alive_heroes():
                    battle.add_stress(h, RETREAT_STRESS)
                heroes = [h for h in heroes if h.alive]
        if not cleared:
            break
        result.encounters_cleared += 1
        if slot < len(ENCOUNTER_TABLE) - 1:
            rest_phase(heroes, log=log)

    survivors = [h for h in heroes if h.alive]
    result.win = result.encounters_cleared == len(ENCOUNTER_TABLE) and bool(survivors)
    result.deaths = 4 - len(survivors)
    result.survivors = len(survivors)
    result.light_remaining = max(0, light)
    result.end_stress = (
        sum(h.stress for h in survivors) / len(survivors) if survivors else 10.0
    )
    if log is not None:
        result.log = log
    return result
