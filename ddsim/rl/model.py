"""Transformer policy/value network.

* Shared trunk: entity-token transformer encoder (the state reader).
* Shared value head: scores the game state — one model for all heroes.
* Per-class policy heads: each hero class owns the MLP that turns
  (its own embedding, the state summary, an action's description, the
  action's target embedding) into a logit for that action.
"""

from __future__ import annotations

import torch
import torch.nn as nn

from .features import ACT_FEATS, ENT_FEATS, GLOB_FEATS, N_SKILLS, N_TYPES
from ..data import HERO_CLASSES


class DDPolicyNet(nn.Module):
    def __init__(self, d_model=64, n_heads=4, n_layers=2, ff=128):
        super().__init__()
        self.d = d_model
        self.type_emb = nn.Embedding(N_TYPES, d_model)
        self.ent_proj = nn.Linear(ENT_FEATS, d_model)
        self.glob_proj = nn.Linear(GLOB_FEATS, d_model)
        layer = nn.TransformerEncoderLayer(
            d_model, n_heads, dim_feedforward=ff, dropout=0.0,
            batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, n_layers)
        self.skill_emb = nn.Embedding(N_SKILLS, d_model)
        self.act_proj = nn.Linear(ACT_FEATS, d_model)
        # shared game-state scorer
        self.value_head = nn.Sequential(
            nn.Linear(d_model, 64), nn.ReLU(), nn.Linear(64, 1),
        )
        # one policy head per hero class
        self.policy_heads = nn.ModuleDict({
            cls: nn.Sequential(
                nn.Linear(4 * d_model, 128), nn.ReLU(), nn.Linear(128, 1),
            )
            for cls in sorted(HERO_CLASSES)
        })

    def encode(self, type_ids, ent_feats, glob_feats):
        """-> (tokens [1, T, d]) with token 0 = global summary."""
        ent = self.type_emb(type_ids) + self.ent_proj(ent_feats)  # [E, d]
        glob = self.glob_proj(glob_feats).unsqueeze(0)  # [1, d]
        seq = torch.cat([glob, ent], dim=0).unsqueeze(0)  # [1, T, d]
        return self.encoder(seq)

    def state_value(self, tokens):
        return self.value_head(tokens[0, 0]).squeeze(-1)

    def action_logits(self, cls_name, tokens, actor_token_idx, actions_enc):
        """actions_enc: list of (skill_id, nums_tensor, target_token_indices).
        Returns logits over the candidate actions."""
        t = tokens[0]  # [T, d]
        actor_emb = t[actor_token_idx]
        state_emb = t[0]
        head = self.policy_heads[cls_name]
        feats = []
        for sid, nums, tgt_idx in actions_enc:
            a_emb = self.skill_emb.weight[sid] + self.act_proj(nums)
            tgt_emb = t[tgt_idx].mean(dim=0)
            feats.append(torch.cat([actor_emb, state_emb, a_emb, tgt_emb]))
        return head(torch.stack(feats)).squeeze(-1)  # [A]
