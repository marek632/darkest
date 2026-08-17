"""Simple scripted baseline policy for the official engine.

Greedy: heal when someone is badly hurt, otherwise best expected damage;
if no attack is legal, move toward the enemy; otherwise pass.
"""

from __future__ import annotations


def _exp_damage(battle, hero, act):
    card = act.card
    total = 0.0
    for t in act.targets:
        if t.is_hero:
            continue
        if card.acc is None:
            p_hit, p_crit = 1.0, 0.0
        else:
            acc = card.acc - battle.eff_unik(t) + t.n_stacks("nazn")
            crit = card.crit + hero.n_stacks("wzmoc") + t.n_stacks("oslab")
            if battle.light <= 4:
                crit += 1
            p_hit = max(0.0, min(1.0, acc / 10.0))
            p_crit = max(0.0, min(p_hit, crit / 10.0))
        dmg = card.dmg * (p_hit - p_crit) + card.cdmg * p_crit
        dmg += 0.4 * (1 if card.fx else 0)
        total += min(dmg, t.hp + 2)
    return total


def heuristic_policy(battle, hero):
    acts = battle.legal_actions(hero)
    skills = [a for a in acts if a.kind == "skill"]
    heals = [a for a in skills if getattr(a.card, "heal", False)
             and a.targets and all(t.is_hero for t in a.targets)]
    hurt = [h for h in battle.alive_heroes()
            if h.dd or h.hp <= h.max_hp * 0.35]
    if hurt and heals:
        best = max(heals, key=lambda a: sum(
            1 for t in a.targets if t in hurt))
        if any(t in hurt for t in best.targets):
            return best
    attacks = [a for a in skills
               if a.targets and any(not t.is_hero for t in a.targets)]
    if attacks:
        return max(attacks, key=lambda a: _exp_damage(battle, hero, a))
    moves = [a for a in acts if a.kind == "move"]
    if moves and battle.alive_monsters():
        near = min(battle.alive_monsters(),
                   key=lambda m: battle.dist(hero, m))
        best = min(moves, key=lambda a: battle.tile.dist(a.area, near.area))
        if battle.tile.dist(best.area, near.area) < \
                battle.tile.dist(hero.area, near.area):
            return best
    others = [a for a in skills if a not in attacks]
    if others:
        return others[0]
    return acts[-1]  # pass
