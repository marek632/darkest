"""Heuristic hero AI, parameterized by a Strategy's knobs.

The policy enumerates every legal (skill, target) pair — from the hero's
current position AND from adjacent positions reachable with the turn's move
action — scores each with expected-value heuristics, and plays the best.
Strategy knobs shift those scores (targeting focus, heal thresholds, stun
affinity), so different strategies genuinely play differently.
"""

from __future__ import annotations

from dataclasses import dataclass

from .combat import Action, Battle, clamp


@dataclass(frozen=True)
class PolicyParams:
    focus: str = "threat"  # threat | stress_first | backline | lowest_hp
    heal_threshold: float = 0.6  # heal allies below this fraction of max hp
    stress_heal_at: int = 5  # consider stress heals at or above this stress
    stun_weight: float = 1.0
    kill_bonus: float = 14.0


def _target_priority(battle: Battle, enemy, params: PolicyParams):
    """How much do we want this enemy dead, per point of expected damage."""
    w = 1.0 + enemy.threat / 8.0
    tags = enemy.etype.tags
    if params.focus == "stress_first" and "stress" in tags:
        w *= 2.2
    elif params.focus == "backline":
        w *= 1.0 + 0.35 * (battle.rank_of(enemy) - 1)
    elif params.focus == "lowest_hp":
        w *= 1.0 + 1.5 * (1.0 - enemy.hp / enemy.max_hp)
    # nearly-dead enemies are always attractive
    if enemy.hp <= enemy.max_hp * 0.35:
        w *= 1.3
    return w


def _expected_attack_value(battle: Battle, hero, skill, targets, params: PolicyParams):
    total = 0.0
    for t in targets:
        hit = clamp(skill.acc + hero.stat("acc") - t.stat("dodge"), 1, 9) / 10.0
        if skill.dmg_mod is not None:
            lo, hi = hero.dmg
            avg = (lo + hi) / 2 * skill.dmg_mod
            mult = hero.stat("dmg_mult")
            if t.marked > 0:
                mult += skill.vs_marked
            if t.stunned:
                mult += skill.vs_stunned
            avg *= max(0.0, mult)
            avg *= 1.0 - clamp(t.stat("prot"), 0, 90) / 100.0
        else:
            avg = 0.0
        if skill.dot is not None:
            dot_p = clamp(skill.dot.chance - t.stat(f"{skill.dot.kind}_resist"), 0, 100) / 100.0
            expected_ticks = min(skill.dot.duration, max(1, t.hp // max(1, skill.dot.dpr)))
            avg += dot_p * skill.dot.dpr * expected_ticks
        val = hit * avg
        if hit * avg >= t.hp * 0.9:
            val += params.kill_bonus
        val *= _target_priority(battle, t, params)
        # stun value: shutting down a dangerous, un-stunned enemy
        if skill.stun is not None and not t.stunned:
            land = clamp(skill.stun - t.stat("stun_resist"), 0, 100) / 100.0
            val += land * t.threat * 1.4 * params.stun_weight
        # marks are only worth it if someone can exploit them
        if skill.mark and t.marked == 0 and t.hp > t.max_hp * 0.5:
            exploiters = sum(
                1 for h in battle.alive_heroes()
                for s in h.skills if s.vs_marked > 0
            )
            val += 6.0 * exploiters
        if skill.target_debuffs and t.hp > t.max_hp * 0.4:
            val += 3.0
        total += val
    return total


def _support_value(battle: Battle, hero, skill, targets, params: PolicyParams):
    total = 0.0
    for t in targets:
        if skill.heal is not None:
            missing = t.max_hp - t.hp
            avg_heal = sum(skill.heal) / 2
            effective = min(missing, avg_heal)
            val = effective * 1.6
            frac = t.hp / t.max_hp
            if t.at_deaths_door:
                val += 60.0
            elif frac < 0.33:
                val += 12.0
            elif frac >= params.heal_threshold:
                val = effective * 0.2  # topping off is low value
            total += val
        if skill.stress_heal is not None:
            if t.stress >= params.stress_heal_at:
                avg = sum(skill.stress_heal) / 2
                val = min(t.stress, avg) * 6.0
                if t.stress >= 8 and not t.resolve_tested:
                    val += 25.0  # prevent an imminent resolve check
                total += val
        for b in skill.target_buffs:
            total += 2.0
        if skill.cure_dots and t.has_dot():
            total += sum(d[1] * d[2] for d in t.dots) * 1.2
    # self-buff skills get a small flat value so they're used when idle
    if skill.target_type == "self" and skill.self_buffs:
        total += 3.0
    return total


def _score(battle, hero, action, params):
    sk = action.skill
    if sk.target_type == "enemy":
        score = _expected_attack_value(battle, hero, sk, action.targets, params)
    else:
        score = _support_value(battle, hero, sk, action.targets, params)
    # small penalty for wasteful self-moves that break formation
    if sk.self_move and sk.target_type != "enemy":
        score -= 2.0
    return score


def choose_action(battle: Battle, hero, params: PolicyParams):
    best, best_score = None, -1.0
    for action in battle.legal_actions(hero):
        score = _score(battle, hero, action, params)
        if score > best_score:
            best, best_score = action, score

    # two actions per turn: consider stepping one rank, then using a skill
    # that is NOT legal from the current rank (move-then-strike)
    rank = battle.rank_of(hero)
    n = len(battle.alive_heroes())
    current_names = set()
    for a in battle.legal_actions(hero):
        current_names.add(a.skill.name)
    for delta in (-1, 1):
        new_rank = clamp(rank + delta, 1, n)
        if new_rank == rank:
            continue
        for action in battle.legal_actions(hero, from_rank=new_rank):
            if action.skill.name in current_names:
                continue
            score = _score(battle, hero, action, params) - 1.0  # cost of the step
            if score > best_score:
                best = Action("move_skill", skill=action.skill,
                              targets=action.targets, move=delta)
                best_score = score

    if best is not None and best_score > 0.5:
        return best
    # nothing useful: move toward the ranks our skills want
    desired = _desired_rank(hero)
    if rank != desired:
        return Action("move", move=-1 if desired < rank else 1)
    return best if best is not None else Action("pass")


def _desired_rank(hero):
    counts = {r: 0 for r in (1, 2, 3, 4)}
    for s in hero.skills:
        for r in s.launch:
            counts[r] += 1
    return max(counts, key=lambda r: (counts[r], -r))


def make_policy(params: PolicyParams):
    def policy(battle, hero):
        return choose_action(battle, hero, params)
    return policy
