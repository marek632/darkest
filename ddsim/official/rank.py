"""Composition tournament with a single generalist RL model.

Compositions are UNORDERED combinations of 4 distinct classes out of the
10-class pool (Wynaturzenie excluded) — permutations are not
distinguished, because heroes can rearrange the formation in play.

Stages:
  1. screening: all C(10,4)=210 combos on the same seed block (common
     random numbers),
  2. validation: top-K on a fresh, larger seed block with Wilson CIs.

Usage:
    python -m ddsim.official.rank --load models/rl_unified.pt --unified
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import time

import torch

from ..stats import wilson_ci
from .quest import PARTY_POOL, run_quest
from .rl import DDNet2, make_rl_policy

SCREEN_SEED_BASE = 730_000_000
VALID_SEED_BASE = 740_000_000


def run_block(party, policy, seed_base, n):
    wins = deaths = 0
    for i in range(n):
        r = run_quest(list(party), seed_base + i, policy=policy)
        wins += int(r.win)
        deaths += r.deaths
    return wins, deaths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--load", default="models/rl_unified.pt")
    ap.add_argument("--unified", action="store_true", default=True)
    ap.add_argument("--screen-runs", type=int, default=30)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--valid-runs", type=int, default=200)
    ap.add_argument("--out", default="results/official_rank.json")
    args = ap.parse_args()

    net = DDNet2(unified=args.unified)
    net.load_state_dict(torch.load(args.load, weights_only=True))
    policy = make_rl_policy(net, greedy=True)

    combos = list(itertools.combinations(PARTY_POOL, 4))
    print(f"screening {len(combos)} combos x {args.screen_runs} quests")
    t0 = time.time()
    screen = []
    for k, combo in enumerate(combos):
        w, d = run_block(combo, policy, SCREEN_SEED_BASE, args.screen_runs)
        screen.append({"party": combo, "wins": w, "n": args.screen_runs,
                       "deaths": d})
        if (k + 1) % 20 == 0:
            print(f"  {k + 1}/{len(combos)} ({time.time() - t0:.0f}s)",
                  flush=True)
    screen.sort(key=lambda r: (-r["wins"], r["deaths"]))

    top = screen[:args.top]
    print(f"validating top {len(top)} x {args.valid_runs} fresh quests")
    for r in top:
        w, d = run_block(r["party"], policy, VALID_SEED_BASE,
                         args.valid_runs)
        lo, hi = wilson_ci(w, args.valid_runs)
        r["valid"] = {"wins": w, "n": args.valid_runs, "deaths": d,
                      "ci": [lo, hi]}
        print(f"  {'+'.join(r['party'])}: {w / args.valid_runs:.1%} "
              f"({lo:.1%}-{hi:.1%}) deaths {d / args.valid_runs:.2f}",
              flush=True)
    top.sort(key=lambda r: -r["valid"]["wins"])

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({"screen": screen, "top": top}, f,
                  ensure_ascii=False, indent=1)
    print(f"wrote {args.out} ({time.time() - t0:.0f}s total)")


if __name__ == "__main__":
    main()
