"""Trainer for RL v2 on the official engine.

Usage:
    python -m ddsim.official.train --episodes 3000 \
        --save models/rl_official.pt --eval-runs 400
"""

from __future__ import annotations

import argparse
import os
import random
import time

import torch

from ..stats import two_proportion_z, wilson_ci
from .quest import run_quest, sample_party, sample_party_loadouts
from .rl import DDNet2, RLAgent, make_rl_policy

TRAIN_SEED_BASE = 710_000_000
EVAL_SEED_BASE = 720_000_000
GAMMA = 0.99


def episode(net, party, seed, boss=None):
    agent = RLAgent(net)
    result = run_quest(party, seed, policy=agent.policy,
                       on_event=agent.on_event, boss=boss)
    return agent.finish(), result


def party_for_seed(seed, mixed, skills=False):
    if not mixed:
        return None  # BOX_PARTY
    rng = random.Random(seed * 2654435761 % (2 ** 31))
    if skills:
        return sample_party_loadouts(rng)
    return sample_party(rng)


def batch_loss(trajs, ent_coef):
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


def evaluate(net, party, n_runs, seed_base=EVAL_SEED_BASE, boss=None,
             mixed=False, skills=False):
    rl_policy = make_rl_policy(net, greedy=True)
    rl_w = he_w = 0
    rl_d = he_d = 0.0
    for i in range(n_runs):
        p = party_for_seed(seed_base + i, mixed, skills) if mixed else party
        r = run_quest(p, seed_base + i, policy=rl_policy, boss=boss)
        rl_w += int(r.win)
        rl_d += r.deaths
        h = run_quest(p, seed_base + i, boss=boss)
        he_w += int(h.win)
        he_d += h.deaths
    return {"rl": rl_w, "he": he_w, "n": n_runs,
            "rl_d": rl_d / n_runs, "he_d": he_d / n_runs}


def report(s):
    n = s["n"]
    rl_lo, rl_hi = wilson_ci(s["rl"], n)
    he_lo, he_hi = wilson_ci(s["he"], n)
    _, p = two_proportion_z(s["rl"], n, s["he"], n)
    print(f"\nheld-out eval ({n} identical quests):")
    print(f"  RL (greedy):  {s['rl'] / n:.1%}  CI {rl_lo:.1%}-{rl_hi:.1%}"
          f"  deaths/run {s['rl_d']:.2f}")
    print(f"  heuristic:    {s['he'] / n:.1%}  CI {he_lo:.1%}-{he_hi:.1%}"
          f"  deaths/run {s['he_d']:.2f}")
    print(f"  two-proportion z-test p={p:.4f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=3000)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--ent", type=float, default=0.01)
    ap.add_argument("--ent-final", type=float, default=0.001)
    ap.add_argument("--save", default="models/rl_official.pt")
    ap.add_argument("--load", default=None)
    ap.add_argument("--eval-runs", type=int, default=400)
    ap.add_argument("--eval-only", action="store_true")
    ap.add_argument("--boss", default=None)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--mixed", action="store_true",
                    help="losowy skład 4/10 klas w każdym epizodzie")
    ap.add_argument("--skills", action="store_true",
                    help="losowe zestawy 3/7 umiejętności (implikuje --mixed)")
    ap.add_argument("--unified", action="store_true",
                    help="jedna wspólna głowa polityki dla wszystkich klas")
    args = ap.parse_args()
    if args.skills:
        args.mixed = True

    torch.manual_seed(args.seed)
    random.seed(args.seed)
    torch.set_num_threads(os.cpu_count() or 4)

    party = None  # BOX_PARTY default
    net = DDNet2(unified=args.unified)
    n_par = sum(p.numel() for p in net.parameters())
    print(f"model parameters: {n_par}")
    if args.load:
        net.load_state_dict(torch.load(args.load, weights_only=True))
        print(f"loaded {args.load}")
    if args.eval_only:
        report(evaluate(net, party, args.eval_runs, boss=args.boss,
                        mixed=args.mixed, skills=args.skills))
        return

    opt = torch.optim.Adam(net.parameters(), lr=args.lr)
    t0 = time.time()
    ep_done = 0
    recent = []
    while ep_done < args.episodes:
        trajs = []
        wins = 0
        for b in range(args.batch):
            seed = TRAIN_SEED_BASE + ep_done + b
            traj, result = episode(
                net, party_for_seed(seed, args.mixed, args.skills),
                seed, boss=args.boss)
            if traj.logps:
                trajs.append(traj)
            wins += int(result.win)
        ep_done += args.batch
        frac = ep_done / args.episodes
        ent_coef = args.ent + (args.ent_final - args.ent) * frac
        loss, entropy = batch_loss(trajs, ent_coef)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
        opt.step()
        recent.append(wins / args.batch)
        recent = recent[-20:]
        if (ep_done // args.batch) % 10 == 0:
            wr = sum(recent) / len(recent)
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
    report(evaluate(net, party, args.eval_runs, boss=args.boss,
                    mixed=args.mixed, skills=args.skills))


if __name__ == "__main__":
    main()
