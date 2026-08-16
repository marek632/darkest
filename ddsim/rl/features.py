"""State and action featurization for the RL policy.

The battle state becomes a token sequence:
  [global token] [hero tokens in rank order] [enemy tokens in rank order]
Each token = learned type embedding (class/monster identity) + projected
numeric features (hp, stress, rank, statuses...). Candidate actions are
described by a skill-vocabulary embedding + numeric flags + the indices
of their target tokens, so the policy head can attend to whom it is about
to hit.
"""

from __future__ import annotations

import torch

from ..combat import Action, clamp
from ..data import ENEMY_TYPES, HERO_CLASSES

HERO_NAMES = sorted(HERO_CLASSES)
ENEMY_NAMES = sorted(ENEMY_TYPES)
TYPE_VOCAB = {n: i for i, n in enumerate(HERO_NAMES + ENEMY_NAMES)}
N_TYPES = len(TYPE_VOCAB)

# skill vocabulary: every hero skill + synthetic actions
SKILL_VOCAB = {}
for _cls in HERO_NAMES:
    for _sk in sorted(HERO_CLASSES[_cls].skills):
        SKILL_VOCAB.setdefault(_sk, len(SKILL_VOCAB))
for _special in ("<move_fwd>", "<move_back>", "<pass>"):
    SKILL_VOCAB[_special] = len(SKILL_VOCAB)
N_SKILLS = len(SKILL_VOCAB)

ENT_FEATS = 16
GLOB_FEATS = 8
ACT_FEATS = 10
MAX_TOKENS = 1 + 4 + 6  # global + heroes + enemies


def entity_features(battle, c, actor):
    """Numeric feature vector for one combatant token."""
    rank = battle.rank_of(c)
    bleed = sum(d[1] for d in c.dots if d[0] == "bleed")
    blight = sum(d[1] for d in c.dots if d[0] == "blight")
    return [
        1.0 if c.is_hero else 0.0,
        1.0 if c is actor else 0.0,
        c.hp / max(1, c.max_hp),
        c.max_hp / 40.0,
        (c.stress / 10.0) if c.is_hero else 0.0,
        1.0 if rank == 1 else 0.0,
        1.0 if rank == 2 else 0.0,
        1.0 if rank == 3 else 0.0,
        1.0 if rank == 4 else 0.0,
        1.0 if c.stunned else 0.0,
        min(c.marked, 3) / 3.0,
        1.0 if c.riposte else 0.0,
        clamp(c.stat("prot"), 0, 90) / 90.0,
        bleed / 5.0,
        blight / 5.0,
        1.0 if (c.is_hero and c.at_deaths_door) else 0.0,
    ]


def global_features(battle):
    return [
        battle.round / 4.0,
        len(battle.alive_heroes()) / 4.0,
        len(battle.alive_enemies()) / 6.0,
        battle.dark_dmg - 1.0,           # darkness tier proxies
        battle.dark_stress - 1.0,
        battle.dark_crit / 5.0,
        sum(h.hp for h in battle.alive_heroes())
        / max(1, sum(h.max_hp for h in battle.alive_heroes())),
        sum(e.hp for e in battle.alive_enemies())
        / max(1, sum(e.max_hp for e in battle.alive_enemies())),
    ]


def encode_state(battle, actor):
    """Returns (type_ids, ent_feats, glob_feats, token_index_of) where
    token_index_of maps id(combatant) -> token position (0 = global)."""
    entities = list(battle.alive_heroes()) + list(battle.alive_enemies())
    entities = entities[: MAX_TOKENS - 1]
    type_ids, feats = [], []
    token_index_of = {}
    for i, c in enumerate(entities):
        name = c.name if c.is_hero else c.etype.name
        type_ids.append(TYPE_VOCAB[name])
        feats.append(entity_features(battle, c, actor))
        token_index_of[id(c)] = i + 1  # position 0 is the global token
    return (
        torch.tensor(type_ids, dtype=torch.long),
        torch.tensor(feats, dtype=torch.float32),
        torch.tensor(global_features(battle), dtype=torch.float32),
        token_index_of,
    )


def candidate_actions(battle, hero):
    """Unified action space: legal skill actions from the current rank,
    move-then-strike combos for skills only reachable after a step, plain
    moves, and pass. Mirrors the heuristic policy's action space so the
    two AIs are compared fairly."""
    acts = list(battle.legal_actions(hero))
    current = {a.skill.name for a in acts}
    rank = battle.rank_of(hero)
    n = len(battle.alive_heroes())
    for delta in (-1, 1):
        new_rank = clamp(rank + delta, 1, n)
        if new_rank == rank:
            continue
        for a in battle.legal_actions(hero, from_rank=new_rank):
            if a.skill.name in current:
                continue
            acts.append(Action("move_skill", skill=a.skill, targets=a.targets,
                               move=delta))
    if n > 1:
        if rank > 1:
            acts.append(Action("move", move=-1))
        if rank < n:
            acts.append(Action("move", move=1))
    acts.append(Action("pass"))
    return acts


def action_features(battle, hero, action, token_index_of):
    """(skill_vocab_id, numeric features, target token indices)."""
    if action.kind == "pass":
        sid = SKILL_VOCAB["<pass>"]
        return sid, [0.0] * ACT_FEATS, [0]
    if action.kind == "move":
        sid = SKILL_VOCAB["<move_fwd>" if action.move < 0 else "<move_back>"]
        nums = [0.0] * ACT_FEATS
        nums[0] = 1.0
        nums[1] = action.move / 2.0
        return sid, nums, [0]
    sk = action.skill
    sid = SKILL_VOCAB[sk.name]
    nums = [
        0.0,
        (action.move / 2.0) if action.kind == "move_skill" else 0.0,
        1.0 if action.kind == "move_skill" else 0.0,
        1.0 if sk.target_type == "enemy" else 0.0,
        1.0 if sk.heal is not None or sk.stress_heal is not None else 0.0,
        1.0 if sk.aoe or sk.target_type == "party" else 0.0,
        len(action.targets) / 4.0,
        1.0 if sk.stun is not None else 0.0,
        1.0 if sk.dot is not None else 0.0,
        1.0 if sk.target_type == "self" else 0.0,
    ]
    targets = [token_index_of.get(id(t), 0) for t in action.targets] or [0]
    return sid, nums, targets
