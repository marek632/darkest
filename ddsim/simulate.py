"""Monte Carlo simulation runner and report generator.

Usage:
    python -m ddsim.simulate --runs 1500 --out results
    python -m ddsim.simulate --strategy classic_balanced --runs 200
    python -m ddsim.simulate --demo            # one narrated run
"""

from __future__ import annotations

import argparse
import csv
import os
import time
from concurrent.futures import ProcessPoolExecutor

from .dungeon import run_dungeon
from .stats import mean_std, two_proportion_z, wilson_ci
from .strategies import STRATEGIES, STRATEGY_INDEX

BASE_SEED = 990_000_000


def simulate_strategy(args):
    """Run N dungeons for one strategy. Seeds are deterministic per strategy."""
    strat_idx, runs = args
    strat = STRATEGIES[strat_idx]
    rows = []
    for i in range(runs):
        seed = BASE_SEED + strat_idx * 1_000_000 + i
        r = run_dungeon(strat.party, strat.params, seed)
        rows.append((
            int(r.win), r.encounters_cleared, r.deaths, r.rounds,
            r.afflictions, r.heart_attacks, r.end_stress, r.survivors,
        ))
    return strat.name, rows


def summarize(name, rows):
    n = len(rows)
    wins = sum(r[0] for r in rows)
    lo, hi = wilson_ci(wins, n)
    deaths_m, deaths_s = mean_std([r[2] for r in rows])
    enc_m, _ = mean_std([r[1] for r in rows])
    rounds_m, _ = mean_std([r[3] for r in rows])
    affl_m, _ = mean_std([r[4] for r in rows])
    stress_m, _ = mean_std([r[6] for r in rows if r[7] > 0])
    deathless = sum(1 for r in rows if r[0] and r[2] == 0)
    return {
        "strategy": name, "runs": n, "wins": wins,
        "win_rate": wins / n if n else 0.0,
        "ci_lo": lo, "ci_hi": hi,
        "deathless_rate": deathless / n if n else 0.0,
        "avg_deaths": deaths_m, "sd_deaths": deaths_s,
        "avg_encounters": enc_m, "avg_rounds": rounds_m,
        "avg_afflictions": affl_m, "avg_survivor_stress": stress_m,
    }


def write_report(summaries, out_dir, runs, elapsed):
    summaries = sorted(summaries, key=lambda s: (-s["win_rate"], s["avg_deaths"]))
    best = summaries[0]

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
        w.writeheader()
        w.writerows(summaries)

    lines = []
    lines.append("# Darkest Dungeon Simulator — Strategy Report\n")
    lines.append(f"*{len(summaries)} strategies x {runs} runs each "
                 f"({len(summaries) * runs:,} simulated dungeons, {elapsed:.0f}s).*\n")
    lines.append("A run is a fixed 4-encounter dungeon (random draws from the "
                 "encounter table); **win** = clear all 4 encounters with at "
                 "least one hero alive. Seeds are deterministic, so every "
                 "strategy faces the same distribution of dungeons.\n")
    lines.append("## Ranking\n")
    lines.append("| # | Strategy | Win rate | 95% CI | Deathless | Avg deaths "
                 "| Avg rounds | Avg afflictions | Survivor stress | vs best (p) |")
    lines.append("|---|----------|----------|--------|-----------|------------"
                 "|------------|-----------------|-----------------|-------------|")
    for i, s in enumerate(summaries, 1):
        _, p = two_proportion_z(best["wins"], best["runs"], s["wins"], s["runs"])
        if s is best:
            pcell = "—"
        elif p < 0.001:
            pcell = "p<0.001 *"
        elif p < 0.05:
            pcell = f"p={p:.3f} *"
        else:
            pcell = f"p={p:.3f}"
        lines.append(
            f"| {i} | {s['strategy']} | **{s['win_rate']:.1%}** "
            f"| {s['ci_lo']:.1%}–{s['ci_hi']:.1%} | {s['deathless_rate']:.1%} "
            f"| {s['avg_deaths']:.2f} | {s['avg_rounds']:.1f} "
            f"| {s['avg_afflictions']:.2f} | {s['avg_survivor_stress']:.0f} | {pcell} |"
        )
    lines.append("\n`*` = significantly worse than the top strategy "
                 "(two-proportion z-test, α=0.05).\n")

    lines.append("## Strategy descriptions\n")
    for s in summaries:
        strat = STRATEGY_INDEX[s["strategy"]]
        party = " / ".join(f"{cls}" for cls, _ in strat.party)
        lines.append(f"- **{s['strategy']}** — {party}. {strat.desc}")

    report = "\n".join(lines) + "\n"
    with open(os.path.join(out_dir, "REPORT.md"), "w") as f:
        f.write(report)
    return report, summaries


def main():
    ap = argparse.ArgumentParser(description="Darkest Dungeon strategy simulator")
    ap.add_argument("--runs", type=int, default=1500, help="runs per strategy")
    ap.add_argument("--out", default="results", help="output directory")
    ap.add_argument("--strategy", help="run a single strategy by name")
    ap.add_argument("--demo", action="store_true", help="print one narrated run")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    args = ap.parse_args()

    if args.demo:
        strat = STRATEGY_INDEX[args.strategy or "classic_balanced"]
        r = run_dungeon(strat.party, strat.params, seed=BASE_SEED + 7, keep_log=True)
        print("\n".join(r.log))
        print(f"\nwin={r.win} cleared={r.encounters_cleared} deaths={r.deaths} "
              f"stress={r.end_stress:.0f}")
        return

    chosen = (
        [STRATEGIES.index(STRATEGY_INDEX[args.strategy])]
        if args.strategy else range(len(STRATEGIES))
    )
    t0 = time.time()
    work = [(i, args.runs) for i in chosen]
    summaries = []
    if args.jobs > 1 and len(work) > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            for name, rows in ex.map(simulate_strategy, work):
                summaries.append(summarize(name, rows))
                print(f"  {name}: {summaries[-1]['win_rate']:.1%} win", flush=True)
    else:
        for w in work:
            name, rows = simulate_strategy(w)
            summaries.append(summarize(name, rows))
            print(f"  {name}: {summaries[-1]['win_rate']:.1%} win", flush=True)
    elapsed = time.time() - t0

    report, ranked = write_report(summaries, args.out, args.runs, elapsed)
    top = ranked[0]
    print(f"\nBest strategy: {top['strategy']} "
          f"({top['win_rate']:.1%}, CI {top['ci_lo']:.1%}-{top['ci_hi']:.1%})")
    print(f"Report written to {args.out}/REPORT.md")


if __name__ == "__main__":
    main()
