# RL Policy Report — Transformer Hero AI

## Architecture

* **Shared transformer trunk** (2 layers, 4 heads, d=64; ~343k params
  total): battle state as entity tokens — one per living hero and
  monster (identity embedding + numeric features: hp, stress, rank,
  stun/mark/riposte/prot, DOTs, death's door) plus a global token
  (round, darkness tier, both sides' health pools).
* **Shared value head** on the global token scores the game state for
  all heroes (the common state-scoring model).
* **Per-class policy heads** (`ModuleDict`): each hero class owns the
  MLP that scores its candidate actions from
  [actor embedding ⊕ state summary ⊕ skill embedding + action flags ⊕
  attended target embedding]. Action space mirrors the heuristic's
  (skills, move-then-strike, moves, pass) for a fair comparison.
* Training: REINFORCE with shared value baseline, entropy annealing
  (0.01 → 0.001), grad clipping; dense reward shaping from state diffs
  between the agent's decisions (enemy hp removed, party hp/stress lost,
  deaths) plus events (room cleared +0.25, win +1.0), γ=0.99.

## Training run (classic_balanced party, 4800 episodes, ~33 min CPU)

Sampling win rate during training: 0.06 → 0.38 (ep 1440) → 0.66
(ep 1920) → 0.86 (ep 4800); entropy annealed 2.1 → 0.69. Smooth,
monotone learning; no collapse.

## Held-out evaluation (400 identical dungeons, seeds never trained on)

| Policy | Win rate | 95% CI | Deaths/run |
|---|---|---|---|
| **RL (greedy)** | **89.5%** | 86.1–92.1% | 0.53 |
| Heuristic | 51.2% | 46.4–56.1% | 1.96 |

Two-proportion z-test p < 0.0001. **+38 points over the heuristic on the
same party and the same dungeons.**

## What it learned (behavioral profile, 120 fresh runs)

* Each hero converged to essentially one attack skill: Crusader → Smite,
  Highwayman → Open Vein, Plague Doctor → Noxious Blast, Vestal →
  Judgement (~100% of skill uses each). The policy plays **zero heals,
  zero stress heals, zero stuns** with this party.
* It also acts more efficiently: ~5.6k hero actions across 120 runs vs
  ~8.4k for the heuristic (fewer, shorter battles), with far fewer
  wasted repositioning turns.
* The win-rate gap therefore comes from (a) refusing all low-tempo
  support actions and (b) learned target selection through attention —
  the skill mix alone is close to what a "pure damage" heuristic would
  do, but the heuristic with the same skills wins half as often.

## Interpretation and caveats

* This strongly confirms the earlier suspicion that **AI quality was a
  binding constraint** on strategy conclusions: the classic party under
  learned play (89.5%) approaches the best searched parties under
  heuristic play (96.8%).
* The policy is trained per party (classic_balanced); it specializes.
  Training across many parties (or per-party fine-tuning) is the next
  step for search integration.
* The current engine is the rank-based grounded-stats model; the
  architecture (entity tokens + per-class heads) transfers unchanged to
  the upcoming official card engine — retraining required, code reuse
  full.

## Reproduction

```bash
python -m ddsim.rl.train --episodes 4800 --party classic_balanced \
    --save models/rl_classic.pt --eval-runs 400
python -m ddsim.rl.train --eval-only --load models/rl_classic.pt \
    --party classic_balanced --eval-runs 400
```
