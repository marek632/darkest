"""RL agent: wraps the network as a hero policy and records trajectories.

Dense reward shaping is computed by diffing battle state between the
agent's consecutive decisions (damage dealt, party damage/stress taken,
deaths), plus dungeon-level events (room cleared, run win/loss) delivered
through run_dungeon's on_event callback.
"""

from __future__ import annotations

import torch

from .features import action_features, candidate_actions, encode_state
from .model import DDPolicyNet

# reward shaping weights
R_ENEMY_HP = 0.6      # per fraction of an enemy's max hp removed... scaled below
R_HERO_HP = -0.4
R_HERO_STRESS = -0.03
R_HERO_DEATH = -0.5
R_ROOM = 0.25
R_WIN = 1.0


class Trajectory:
    __slots__ = ("logps", "values", "entropies", "rewards")

    def __init__(self):
        self.logps = []
        self.values = []
        self.entropies = []
        self.rewards = []


class RLAgent:
    def __init__(self, net: DDPolicyNet, greedy=False, record=True):
        self.net = net
        self.greedy = greedy
        self.record = record
        self.traj = Trajectory()
        self._last_battle_id = None
        self._snap = None

    # -- reward bookkeeping -------------------------------------------------
    def _snapshot(self, battle):
        return {
            "enemy_hp": sum(e.hp / max(1, e.max_hp)
                            for e in battle.alive_enemies()),
            "n_enemies": len(battle.alive_enemies()),
            "hero_hp": sum(h.hp / max(1, h.max_hp)
                           for h in battle.alive_heroes()),
            "stress": sum(h.stress for h in battle.alive_heroes()),
            "n_heroes": len(battle.alive_heroes()),
        }

    def _accrue(self, battle):
        """Reward for the PREVIOUS decision = what changed since then."""
        snap = self._snapshot(battle)
        if self._last_battle_id == id(battle) and self._snap is not None:
            prev = self._snap
            killed = (prev["enemy_hp"] - snap["enemy_hp"]) \
                + (prev["n_enemies"] - snap["n_enemies"])
            r = R_ENEMY_HP * max(0.0, killed) / 4.0
            r += R_HERO_HP * max(0.0, prev["hero_hp"] - snap["hero_hp"]) / 4.0
            r += R_HERO_STRESS * max(0.0, snap["stress"] - prev["stress"])
            r += R_HERO_DEATH * max(0, prev["n_heroes"] - snap["n_heroes"])
            if self.traj.rewards:
                self.traj.rewards[-1] += r
        self._last_battle_id = id(battle)
        self._snap = snap

    def on_event(self, kind, payload):
        if not self.traj.rewards:
            return
        if kind == "room_cleared":
            self.traj.rewards[-1] += R_ROOM
        elif kind == "run_end":
            if payload.win:
                self.traj.rewards[-1] += R_WIN

    # -- policy interface ---------------------------------------------------
    def policy(self, battle, hero):
        if self.record:
            self._accrue(battle)
        type_ids, ent_feats, glob_feats, tok_of = encode_state(battle, hero)
        acts = candidate_actions(battle, hero)
        enc = []
        for a in acts:
            sid, nums, tgts = action_features(battle, hero, a, tok_of)
            enc.append((sid, torch.tensor(nums), torch.tensor(tgts)))
        tokens = self.net.encode(type_ids, ent_feats, glob_feats)
        logits = self.net.action_logits(hero.name, tokens,
                                        tok_of[id(hero)], enc)
        dist = torch.distributions.Categorical(logits=logits)
        if self.greedy:
            idx = int(torch.argmax(logits))
        else:
            idx = int(dist.sample())
        if self.record:
            self.traj.logps.append(dist.log_prob(torch.tensor(idx)))
            self.traj.entropies.append(dist.entropy())
            self.traj.values.append(self.net.state_value(tokens))
            self.traj.rewards.append(0.0)
        return acts[idx]

    def finish(self):
        """Return the completed trajectory and reset."""
        t = self.traj
        self.traj = Trajectory()
        self._last_battle_id = None
        self._snap = None
        return t


def make_rl_policy(net, greedy=True):
    """Inference-only policy function (no recording, no grad)."""
    agent = RLAgent(net, greedy=greedy, record=False)

    def policy(battle, hero):
        with torch.no_grad():
            return agent.policy(battle, hero)

    return policy
