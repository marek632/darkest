"""Joint class + skill-loadout optimization.

Full space: C(10,4)=210 class combos x 35^4 loadout vectors ~ 315M
teams — brute force impossible. Staged search with one generalist RL
model (trained on random classes AND random loadouts) as evaluator:

  A. screen all 210 class combos, marginalizing over random loadouts
     (common quest seeds across combos),
  B. coordinate ascent for the top combos (+ box party): for each hero
     in turn try all 35 loadouts with the rest fixed, on a common seed
     block; repeat until no improvement (max 3 passes),
  C. validate finalists (optimized + default loadouts) on a fresh seed
     block with Wilson CIs.

Usage:
    python -m ddsim.official.optimize --load models/rl_skills.pt
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import time
import zlib

import torch

from ..stats import wilson_ci
from .cards import BOX_PARTY, DEFAULT_LOADOUT
from .quest import LOADOUTS, PARTY_POOL, run_quest
from .rl import DDNet2, make_rl_policy

SCREEN_SEED = 750_000_000
CLIMB_SEED = 760_000_000
VALID_SEED = 770_000_000


def block(spec, policy, seed_base, n):
    """-> (wins, rooms_cleared, deaths) over n paired quests."""
    w = rc = d = 0
    for i in range(n):
        r = run_quest(spec, seed_base + i, policy=policy)
        w += int(r.win)
        rc += r.rooms_cleared
        d += r.deaths
    return w, rc, d


def score(t):
    w, rc, d = t
    return (w, rc, -d)


def screen(policy, runs):
    combos = list(itertools.combinations(PARTY_POOL, 4))
    out = []
    t0 = time.time()
    for k, combo in enumerate(combos):
        w = rc = d = 0
        for i in range(runs):
            lrng = random.Random(
                zlib.crc32(f"{'+'.join(combo)}|{i}".encode()))
            spec = [(n, lrng.choice(LOADOUTS[n])) for n in combo]
            r = run_quest(spec, SCREEN_SEED + i, policy=policy)
            w += int(r.win)
            rc += r.rooms_cleared
            d += r.deaths
        out.append({"party": combo, "wins": w, "rooms": rc, "deaths": d})
        if (k + 1) % 30 == 0:
            print(f"  screen {k + 1}/{len(combos)} "
                  f"({time.time() - t0:.0f}s)", flush=True)
    out.sort(key=lambda r: (-r["wins"], -r["rooms"], r["deaths"]))
    return out


def climb(combo, policy, runs, max_passes=3):
    cur = {n: tuple(sorted(DEFAULT_LOADOUT[n])) for n in combo}

    def spec():
        return [(n, cur[n]) for n in combo]

    cur_s = score(block(spec(), policy, CLIMB_SEED, runs))
    for p in range(max_passes):
        improved = False
        for n in combo:
            best_lo, best_s = cur[n], cur_s
            for lo in LOADOUTS[n]:
                if lo == cur[n]:
                    continue
                trial = [(m, lo if m == n else cur[m]) for m in combo]
                s = score(block(trial, policy, CLIMB_SEED, runs))
                if s > best_s:
                    best_lo, best_s = lo, s
            if best_lo != cur[n]:
                cur[n] = best_lo
                cur_s = best_s
                improved = True
        print(f"    pass {p + 1}: wins {cur_s[0]}/{runs} "
              f"rooms {cur_s[1]}", flush=True)
        if not improved:
            break
    return cur, cur_s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--load", default="models/rl_skills.pt")
    ap.add_argument("--screen-runs", type=int, default=30)
    ap.add_argument("--climb-runs", type=int, default=24)
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--valid-runs", type=int, default=300)
    ap.add_argument("--out", default="results/official_skills.json")
    args = ap.parse_args()

    net = DDNet2(unified=True)
    net.load_state_dict(torch.load(args.load, weights_only=True))
    policy = make_rl_policy(net, greedy=True)

    print(f"A. screening 210 combos x {args.screen_runs} "
          "(random loadouts, common seeds)")
    scr = screen(policy, args.screen_runs)

    chosen = [tuple(r["party"]) for r in scr[:args.top]]
    box = tuple(sorted(BOX_PARTY))
    if box not in chosen:
        chosen.append(box)

    print(f"B. coordinate ascent over loadouts for {len(chosen)} combos "
          f"({args.climb_runs} common seeds)")
    t0 = time.time()
    finalists = []
    for combo in chosen:
        print(f"  {'+'.join(combo)}", flush=True)
        best, s = climb(combo, policy, args.climb_runs)
        finalists.append({"party": combo, "loadouts": best,
                          "climb_score": s})
        print(f"    done ({time.time() - t0:.0f}s)", flush=True)

    print(f"C. validating {len(finalists)} finalists x {args.valid_runs} "
          "fresh quests (optimized vs default loadouts)")
    for f in finalists:
        spec_o = [(n, f["loadouts"][n]) for n in f["party"]]
        w, rc, d = block(spec_o, policy, VALID_SEED, args.valid_runs)
        lo, hi = wilson_ci(w, args.valid_runs)
        f["valid"] = {"wins": w, "n": args.valid_runs, "ci": [lo, hi],
                      "deaths": d}
        w2, _, d2 = block(list(f["party"]), policy, VALID_SEED,
                          args.valid_runs)
        f["valid_default"] = {"wins": w2, "deaths": d2}
        print(f"  {'+'.join(f['party'])}: opt {w / args.valid_runs:.1%} "
              f"({lo:.1%}-{hi:.1%})  default {w2 / args.valid_runs:.1%}",
              flush=True)
    finalists.sort(key=lambda f: -f["valid"]["wins"])

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump({"screen": scr, "finalists": finalists}, fh,
                  ensure_ascii=False, indent=1)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
