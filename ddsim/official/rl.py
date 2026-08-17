"""RL v2 for the official engine.

Everything the user asked the policy to see is a token with trainable
embeddings, and attention decides what matters:
  * one token per combatant: type embedding + stance embedding + area
    embedding + numeric features + mean embedding of ITS OWN skill cards
    (so the policy knows what allies and enemies can do),
  * one token per room area (capacity, occupancy, distance),
  * a global token (round, light, totals).
Actions (skill+targets / move / stance swap / pass) are scored by a
per-class policy head from [actor, state, action-embedding, targets].
A shared value head scores the state for all heroes.
"""

from __future__ import annotations

import torch
import torch.nn as nn

from .battle import Action
from .board import MAX_AREAS, TILES
from .cards import HERO_CLASSES
from .monsters import BOSSES, MONSTERS

TYPE_VOCAB = {}
for _n in sorted(HERO_CLASSES):
    TYPE_VOCAB[_n] = len(TYPE_VOCAB)
for _n in sorted(MONSTERS) + sorted(BOSSES):
    TYPE_VOCAB.setdefault(_n, len(TYPE_VOCAB))
N_TYPES = len(TYPE_VOCAB)

SKILL_VOCAB = {}
for _n in sorted(HERO_CLASSES):
    for _s in sorted(HERO_CLASSES[_n].skills):
        SKILL_VOCAB.setdefault(_s, len(SKILL_VOCAB))
for _d in (MONSTERS, BOSSES):
    for _n in sorted(_d):
        for _s in _d[_n].skills:
            SKILL_VOCAB.setdefault(_s.name, len(SKILL_VOCAB))
for _sp in ("<move>", "<swap+>", "<swap->", "<pass>"):
    SKILL_VOCAB[_sp] = len(SKILL_VOCAB)
N_SKILLS = len(SKILL_VOCAB)

N_STANCES = 5          # A D Z W + none
ENT_FEATS = 20
AREA_FEATS = 7
GLOB_FEATS = 8
ACT_FEATS = 12
STANCE_IDX = {"A": 0, "D": 1, "Z": 2, "W": 3}


def _ent_feats(battle, f, actor):
    return [
        1.0 if f.is_hero else 0.0,
        1.0 if f is actor else 0.0,
        f.hp / max(1, f.max_hp),
        f.max_hp / 20.0,
        (f.stress / 10.0) if f.is_hero else 0.0,
        1.0 if f.dd else 0.0,
        f.n_stacks("stun") / 2.0,
        f.dot_amt("krwotok") / 5.0,
        f.dot_amt("zaraza") / 5.0,
        f.n_stacks("wzmoc") / 2.0,
        f.n_stacks("oslab") / 2.0,
        f.n_stacks("nazn") / 2.0,
        1.0 if f.has("riposta") else 0.0,
        1.0 if f.has("garda") else 0.0,
        1.0 if f.has("ochrona") else 0.0,
        battle.tile.dist(actor.area, f.area) / 4.0,
        (f.size - 1.0),
        f.base_unik / 3.0,
        f.speed / 4.0,
        1.0 if (f.is_hero and f.form == "bestia") else 0.0,
    ]


def encode_state(battle, actor):
    """-> dict of tensors + token index maps."""
    fighters = battle.alive_heroes() + battle.alive_monsters()
    type_ids, stance_ids, area_ids, feats = [], [], [], []
    tok_of = {}
    for f in fighters:
        tok_of[id(f)] = len(type_ids) + 1     # 0 = global token
        type_ids.append(TYPE_VOCAB[f.name])
        stance_ids.append(STANCE_IDX.get(battle.stance_of(f), 4)
                          if f.slot is not None else 4)
        area_ids.append(f.area)
        feats.append(_ent_feats(battle, f, actor))
    skill_ids = [[SKILL_VOCAB[getattr(s, "name", s)] for s in f.skills]
                 for f in fighters]
    n_ent = len(fighters)
    area_tok_of = {}
    a_ids, a_feats = [], []
    for a in range(battle.tile.n):
        area_tok_of[a] = 1 + n_ent + len(a_ids)
        occ = battle.occupants(a)
        a_ids.append(a)
        a_feats.append([
            battle.tile.caps[a] / 4.0,
            battle.free_space(a) / 4.0,
            sum(1 for o in occ if o.is_hero) / 4.0,
            sum(1 for o in occ if not o.is_hero) / 4.0,
            battle.tile.dist(actor.area, a) / 4.0,
            1.0 if a == actor.area else 0.0,
            1.0 if a in battle.tile.monster_start else 0.0,
        ])
    glob = [
        battle.round_no / 4.0,
        battle.light / 5.0,
        len(battle.alive_heroes()) / 4.0,
        len(battle.alive_monsters()) / 4.0,
        sum(h.hp for h in battle.alive_heroes())
        / max(1, sum(h.max_hp for h in battle.alive_heroes())),
        sum(m.hp for m in battle.alive_monsters())
        / max(1, sum(m.max_hp for m in battle.alive_monsters())),
        1.0 if battle.boss else 0.0,
        sum(h.stress for h in battle.alive_heroes()) / 40.0,
    ]
    return {
        "type_ids": torch.tensor(type_ids, dtype=torch.long),
        "stance_ids": torch.tensor(stance_ids, dtype=torch.long),
        "area_ids": torch.tensor(area_ids, dtype=torch.long),
        "ent_feats": torch.tensor(feats, dtype=torch.float32),
        "skill_ids": skill_ids,
        "a_ids": torch.tensor(a_ids, dtype=torch.long),
        "a_feats": torch.tensor(a_feats, dtype=torch.float32),
        "glob": torch.tensor(glob, dtype=torch.float32),
        "tok_of": tok_of,
        "area_tok_of": area_tok_of,
    }


def action_features(battle, hero, act, tok_of, area_tok_of):
    if act.kind == "pass":
        return SKILL_VOCAB["<pass>"], [0.0] * ACT_FEATS, [0]
    if act.kind == "swap":
        sid = SKILL_VOCAB["<swap+>" if act.move > 0 else "<swap->"]
        nums = [0.0] * ACT_FEATS
        nums[1] = 1.0
        return sid, nums, [tok_of[id(hero)]]
    if act.kind == "move":
        sid = SKILL_VOCAB["<move>"]
        nums = [0.0] * ACT_FEATS
        nums[2] = 1.0
        nums[3] = battle.tile.dist(hero.area, act.area) / 4.0
        return sid, nums, [area_tok_of[act.area]]
    card = act.card
    sid = SKILL_VOCAB[card.name]
    dmg = getattr(card, "dmg", 0)
    nums = [
        1.0, 0.0, 0.0, 0.0,
        len(act.targets) / 4.0,
        (battle.tile.dist(hero.area, act.targets[0].area) / 4.0
         if act.targets else 0.0),
        dmg / 15.0,
        1.0 if getattr(card, "heal", False) else 0.0,
        1.0 if any(f.startswith("stun") for f in card.fx) else 0.0,
        1.0 if any(f.startswith(("krwotok", "zaraza"))
                   for f in card.fx) else 0.0,
        1.0 if any(f.startswith(("push", "pull"))
                   for f in card.fx + card.self_fx) else 0.0,
        getattr(card, "crit", 0) / 5.0,
    ]
    tgts = [tok_of[id(t)] for t in act.targets if id(t) in tok_of] or [0]
    return sid, nums, tgts


class DDNet2(nn.Module):
    def __init__(self, d=64, heads=4, layers=2, ff=128):
        super().__init__()
        self.d = d
        self.type_emb = nn.Embedding(N_TYPES, d)
        self.skill_emb = nn.Embedding(N_SKILLS, d)
        self.stance_emb = nn.Embedding(N_STANCES, d)
        self.area_emb = nn.Embedding(MAX_AREAS, d)
        self.ent_proj = nn.Linear(ENT_FEATS, d)
        self.area_proj = nn.Linear(AREA_FEATS, d)
        self.glob_proj = nn.Linear(GLOB_FEATS, d)
        self.act_proj = nn.Linear(ACT_FEATS, d)
        layer = nn.TransformerEncoderLayer(
            d, heads, dim_feedforward=ff, dropout=0.0,
            batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, layers)
        self.value_head = nn.Sequential(
            nn.Linear(d, 64), nn.ReLU(), nn.Linear(64, 1))
        self.policy_heads = nn.ModuleDict({
            cls: nn.Sequential(
                nn.Linear(4 * d, 128), nn.ReLU(), nn.Linear(128, 1))
            for cls in sorted(HERO_CLASSES)})

    def encode(self, st):
        ent = (self.type_emb(st["type_ids"])
               + self.stance_emb(st["stance_ids"])
               + self.area_emb(st["area_ids"])
               + self.ent_proj(st["ent_feats"]))
        skill_means = torch.stack([
            self.skill_emb(torch.tensor(ids, dtype=torch.long)).mean(0)
            for ids in st["skill_ids"]])
        ent = ent + skill_means
        areas = self.area_emb(st["a_ids"]) + self.area_proj(st["a_feats"])
        glob = self.glob_proj(st["glob"]).unsqueeze(0)
        seq = torch.cat([glob, ent, areas], dim=0).unsqueeze(0)
        return self.encoder(seq)

    def state_value(self, tokens):
        return self.value_head(tokens[0, 0]).squeeze(-1)

    def action_logits(self, cls_name, tokens, actor_tok, actions_enc):
        t = tokens[0]
        actor = t[actor_tok]
        state = t[0]
        head = self.policy_heads[cls_name]
        rows = []
        for sid, nums, tgt_idx in actions_enc:
            a_emb = self.skill_emb.weight[sid] + self.act_proj(nums)
            tgt = t[tgt_idx].mean(dim=0)
            rows.append(torch.cat([actor, state, a_emb, tgt]))
        return head(torch.stack(rows)).squeeze(-1)


# ----------------------------- agent ------------------------------------

R_ENEMY_HP = 0.6
R_HERO_HP = -0.4
R_HERO_STRESS = -0.03
R_HERO_DEATH = -0.5
R_ROOM = 0.25
R_WIN = 1.0
R_TIMEOUT = -0.25


class Trajectory:
    __slots__ = ("logps", "values", "entropies", "rewards")

    def __init__(self):
        self.logps, self.values = [], []
        self.entropies, self.rewards = [], []


class RLAgent:
    def __init__(self, net, greedy=False, record=True):
        self.net = net
        self.greedy = greedy
        self.record = record
        self.traj = Trajectory()
        self._bid = None
        self._snap = None

    def _snapshot(self, b):
        return {
            "ehp": sum(m.hp / max(1, m.max_hp) for m in b.alive_monsters()),
            "nm": len(b.alive_monsters()),
            "hhp": sum(h.hp / max(1, h.max_hp) for h in b.alive_heroes()),
            "st": sum(h.stress for h in b.alive_heroes()),
            "nh": len(b.alive_heroes()),
        }

    def _accrue(self, b):
        s = self._snapshot(b)
        if self._bid == id(b) and self._snap is not None:
            p = self._snap
            killed = (p["ehp"] - s["ehp"]) + (p["nm"] - s["nm"])
            r = R_ENEMY_HP * max(0.0, killed) / 4.0
            r += R_HERO_HP * max(0.0, p["hhp"] - s["hhp"]) / 4.0
            r += R_HERO_STRESS * max(0, s["st"] - p["st"])
            r += R_HERO_DEATH * max(0, p["nh"] - s["nh"])
            if self.traj.rewards:
                self.traj.rewards[-1] += r
        self._bid = id(b)
        self._snap = s

    def on_event(self, kind, payload):
        if not self.traj.rewards:
            return
        if kind == "room_cleared":
            self.traj.rewards[-1] += R_ROOM
        elif kind == "run_end":
            if payload.win:
                self.traj.rewards[-1] += R_WIN
            elif payload.timeout:
                self.traj.rewards[-1] += R_TIMEOUT

    def policy(self, battle, hero):
        if self.record:
            self._accrue(battle)
        st = encode_state(battle, hero)
        acts = battle.legal_actions(hero)
        enc = []
        for a in acts:
            sid, nums, tgts = action_features(
                battle, hero, a, st["tok_of"], st["area_tok_of"])
            enc.append((sid, torch.tensor(nums), torch.tensor(tgts)))
        tokens = self.net.encode(st)
        logits = self.net.action_logits(
            hero.name, tokens, st["tok_of"][id(hero)], enc)
        dist = torch.distributions.Categorical(logits=logits)
        idx = int(torch.argmax(logits)) if self.greedy else int(dist.sample())
        if self.record:
            self.traj.logps.append(dist.log_prob(torch.tensor(idx)))
            self.traj.entropies.append(dist.entropy())
            self.traj.values.append(self.net.state_value(tokens))
            self.traj.rewards.append(0.0)
        return acts[idx]

    def finish(self):
        t = self.traj
        self.traj = Trajectory()
        self._bid = None
        self._snap = None
        return t


def make_rl_policy(net, greedy=True):
    agent = RLAgent(net, greedy=greedy, record=False)

    def policy(battle, hero):
        with torch.no_grad():
            return agent.policy(battle, hero)

    return policy
