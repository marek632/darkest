"""Training loop: advantage-actor-critic (REINFORCE + shared value
baseline + entropy bonus) over full dungeon runs.

Usage:
    python -m ddsim.rl.train --episodes 4000 --party classic_balanced \
        --save models/rl_policy.pt
    python -m ddsim.rl.train --eval-only --load models/rl_policy.pt \
        --party classic_balanced --eval-runs 500

The trained policy is compared against the heuristic policy on a
held-out seed block (identical dungeons for both).
"""

from __future__ import annotations

import argparse
import os
import random
import time

import torch

from .agent import RLAgent, make_rl_policy
from .model import DDPolicyNet
from ..dungeon import run_dungeon
from ..policy import PolicyParams
from ..stats import two_proportion_z, wilson_ci
from ..strategies import STRATEGY_INDEX

TRAIN_SEED_BASE = 610_000_000
EVAL_SEED_BASE = 620_000_000  # held out from training
GAMMA = 0.99


def episode(net, party, seed):
    agent = RLAgent(net)
    result = run_dungeon(party, PolicyParams(), seed,
                         policy=agent.policy, on_event=agent.on_event)
    return agent.finish(), result


def batch_loss(trajs, ent_coef):
    policy_terms, value_terms, entropy_terms = [], [], []
    advantages = []
    returns_all = []
    for t in trajs:
        ret, rets = 0.0, []
        for r in reversed(t.rewards):
            ret = r + GAMMA * ret
            rets.append(ret)
        rets.reverse()
        returns_all.append(torch.tensor(rets))
    flat_ret = torch.cat(returns_all)
    flat_val = torch.stack([v for t in trajs for v in t.values])
    adv = flat_ret - flat_val.detach()
    adv = (adv - adv.mean()) / (adv.std() + 1e-6)
    flat_logp = torch.stack([lp for t in trajs for lp in t.logps])
    flat_ent = torch.stack([e for t in trajs for e in t.entropies])
    policy_loss = -(flat_logp * adv).mean()
    value_loss = torch.nn.functional.mse_loss(flat_val, flat_ret)
    entropy = flat_ent.mean()
    return policy_loss + 0.5 * value_loss - ent_coef * entropy, entropy


def evaluate(net, party, n_runs, seed_base=EVAL_SEED_BASE):
    """Greedy RL policy vs heuristic policy on identical held-out seeds."""
    rl_policy = make_rl_policy(net, greedy=True)
    rl_wins = heur_wins = 0
    rl_deaths = heur_deaths = 0.0
    for i in range(n_runs):
        r = run_dungeon(party, PolicyParams(), seed_base + i, policy=rl_policy)
        rl_wins += int(r.win)
        rl_deaths += r.deaths
        h = run_dungeon(party, PolicyParams(), seed_base + i)
        heur_wins += int(h.win)
        heur_deaths += h.deaths
    return {
        "rl_wins": rl_wins, "heur_wins": heur_wins, "n": n_runs,
        "rl_deaths": rl_deaths / n_runs, "heur_deaths": heur_deaths / n_runs,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=4000)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--ent", type=float, default=0.01)
    ap.add_argument("--ent-final", type=float, default=0.001)
    ap.add_argument("--party", default="classic_balanced")
    ap.add_argument("--save", default="models/rl_policy.pt")
    ap.add_argument("--load", default=None)
    ap.add_argument("--eval-runs", type=int, default=400)
    ap.add_argument("--eval-only", action="store_true")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    random.seed(args.seed)
    torch.set_num_threads(os.cpu_count() or 4)

    party = STRATEGY_INDEX[args.party].party
    net = DDPolicyNet()
    if args.load:
        net.load_state_dict(torch.load(args.load, weights_only=True))
        print(f"loaded {args.load}")

    if args.eval_only:
        stats = evaluate(net, party, args.eval_runs)
        report(stats)
        return

    opt = torch.optim.Adam(net.parameters(), lr=args.lr)
    t0 = time.time()
    ep_done = 0
    recent_wins = []
    while ep_done < args.episodes:
        trajs = []
        batch_wins = 0
        for b in range(args.batch):
            seed = TRAIN_SEED_BASE + ep_done + b
            traj, result = episode(net, party, seed)
            if traj.logps:
                trajs.append(traj)
            batch_wins += int(result.win)
        ep_done += args.batch
        frac = ep_done / args.episodes
        ent_coef = args.ent + (args.ent_final - args.ent) * frac
        loss, entropy = batch_loss(trajs, ent_coef)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
        opt.step()
        recent_wins.append(batch_wins / args.batch)
        recent_wins = recent_wins[-20:]
        if (ep_done // args.batch) % 10 == 0:
            wr = sum(recent_wins) / len(recent_wins)
            print(f"  ep {ep_done}/{args.episodes} "
                  f"train-win(sampling)={wr:.2f} "
                  f"H={entropy.item():.2f} ({time.time() - t0:.0f}s)",
                  flush=True)
        if args.save and (ep_done // args.batch) % 50 == 0:
            os.makedirs(os.path.dirname(args.save), exist_ok=True)
            torch.save(net.state_dict(), args.save)

    if args.save:
        os.makedirs(os.path.dirname(args.save), exist_ok=True)
        torch.save(net.state_dict(), args.save)
        print(f"saved {args.save}")
    stats = evaluate(net, party, args.eval_runs)
    report(stats)


def report(stats):
    n = stats["n"]
    rl, he = stats["rl_wins"], stats["heur_wins"]
    rl_lo, rl_hi = wilson_ci(rl, n)
    he_lo, he_hi = wilson_ci(he, n)
    _, p = two_proportion_z(rl, n, he, n)
    print(f"\nheld-out eval ({n} identical dungeons):")
    print(f"  RL (greedy):  {rl / n:.1%}  CI {rl_lo:.1%}-{rl_hi:.1%}  "
          f"deaths/run {stats['rl_deaths']:.2f}")
    print(f"  heuristic:    {he / n:.1%}  CI {he_lo:.1%}-{he_hi:.1%}  "
          f"deaths/run {stats['heur_deaths']:.2f}")
    print(f"  two-proportion z-test p={p:.4f}")


if __name__ == "__main__":
    main()
