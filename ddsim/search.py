"""Broad search over party compositions, skill loadouts, and policy knobs.

Staged screen-and-refine (design and rationale: docs/COVERAGE_GAPS.md):

  A. screen all 1,680 ordered parties with auto-built loadouts
  B. best-focus selection + hill-climb loadout search on survivors
  C. policy-knob grid on the finalists
  D. validation of the top configurations on FRESH seeds (the only
     unbiased numbers; stages A-C select on noise by construction)

All comparisons within a stage use common random numbers (identical seed
blocks), so they are paired. Stage results are checkpointed as JSON so an
interrupted search resumes at the last finished stage.

Usage:
    python -m ddsim.search --out results/search            # full pipeline
    python -m ddsim.search --out results/search --stage A  # one stage
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor

from .data import HERO_CLASSES
from .dungeon import run_dungeon
from .policy import PolicyParams
from .stats import two_proportion_z, wilson_ci

CLASSES = sorted(HERO_CLASSES)
FOCI = ("threat", "stress_first", "backline", "lowest_hp")

SEED_A = 310_000_000  # screening block
SEED_B = 320_000_000  # refinement block
SEED_C = 330_000_000  # policy-grid block
SEED_D = 340_000_000  # validation block (never used during search)

N_A, KEEP_A = 160, 40
N_B, PASSES_B, ACCEPT_B = 320, 2, 5  # accept a swap at +5 paired wins (~1.6%)
N_C, KEEP_C = 400, 16
N_D = 3000

STUN_GRID = (0.6, 1.0, 1.6)
HEAL_GRID = (0.45, 0.6, 0.75)

BASELINE = {  # hand-crafted v2 champion, for reference in stage D
    "party": (
        ("Hellion", ("Wicked Hack", "Iron Swan", "Bleed Out")),
        ("Highwayman", ("Wicked Slice", "Pistol Shot", "Open Vein")),
        ("Bounty Hunter", ("Collect Bounty", "Mark for Death", "Hook and Slice")),
        ("Grave Robber", ("Thrown Dagger", "Poison Dart", "Lunge")),
    ),
    "focus": "lowest_hp", "stun": 1.0, "heal": 0.3,
    "label": "baseline:all_damage_no_healer",
}


# ---------------------------------------------------------------------------
# Auto-loadout: greedy rank-legal kit from a static value heuristic
# ---------------------------------------------------------------------------

def _skill_value(cls, skill, rank):
    if rank not in skill.launch and skill.target_type != "self":
        return -1.0  # not usable from the hero's home rank
    v = 0.0
    if skill.dmg_mod is not None:
        avg = (cls.dmg[0] + cls.dmg[1]) / 2 * skill.dmg_mod * min(skill.acc, 9) / 10
        if skill.aoe:
            avg *= 1.7
        v += avg
    if skill.dot is not None:
        v += skill.dot.dpr * skill.dot.duration * (skill.dot.chance / 100) * 0.5
    if skill.stun is not None:
        v += 3.0
    if skill.heal is not None:
        v += sum(skill.heal) / 2 * (1.6 if skill.target_type == "party" else 1.1)
    if skill.stress_heal is not None:
        v += sum(skill.stress_heal) / 2 * 3.0
    if skill.mark:
        v += 1.0
    if skill.vs_marked or skill.vs_stunned:
        v += 0.8
    if skill.self_buffs or skill.target_buffs:
        v += 1.0
    if skill.cure_dots:
        v += 0.5
    return v


def auto_loadout(comp):
    """Greedy 3-skill kit per hero for its assigned rank."""
    out = []
    for rank0, cname in enumerate(comp):
        cls = HERO_CLASSES[cname]
        scored = sorted(
            cls.skills.values(),
            key=lambda s: (-_skill_value(cls, s, rank0 + 1), s.name),
        )
        out.append(tuple(s.name for s in scored[:3]))
    return tuple(out)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate(comp, loadout, focus, stun, heal, seed_base, n):
    party = tuple((c, tuple(sk)) for c, sk in zip(comp, loadout))
    params = PolicyParams(focus=focus, stun_weight=stun, heal_threshold=heal)
    wins = deaths = 0
    for i in range(n):
        r = run_dungeon(party, params, seed_base + i)
        wins += int(r.win)
        deaths += r.deaths
    return wins, deaths / n


# -- stage A ----------------------------------------------------------------

def _screen_one(comp):
    loadout = auto_loadout(comp)
    wins, avg_deaths = evaluate(comp, loadout, "threat", 1.0, 0.6, SEED_A, N_A)
    return {"comp": comp, "loadout": loadout, "wins": wins, "n": N_A,
            "avg_deaths": avg_deaths}


def stage_a(pool, out_dir):
    comps = [c for c in itertools.permutations(CLASSES, 4)]
    t0 = time.time()
    results = []
    for i, res in enumerate(pool.map(_screen_one, comps, chunksize=16)):
        results.append(res)
        if (i + 1) % 200 == 0:
            print(f"  screened {i + 1}/{len(comps)} ({time.time() - t0:.0f}s)",
                  flush=True)
    results.sort(key=lambda r: -r["wins"])
    _save(out_dir, "stageA", results)
    print(f"  stage A done: best {results[0]['wins']}/{N_A} wins "
          f"{tuple(results[0]['comp'])}")
    return results


# -- stage B ----------------------------------------------------------------

def _refine_one(entry):
    comp = tuple(entry["comp"])
    loadout = [tuple(l) for l in entry["loadout"]]

    def ev(lo, focus):
        return evaluate(comp, lo, focus, 1.0, 0.6, SEED_B, N_B)[0]

    # pick the best targeting focus for this party (paired seeds)
    focus_scores = {f: ev(loadout, f) for f in FOCI}
    focus = max(focus_scores, key=focus_scores.get)
    best = focus_scores[focus]

    # hill-climb single-skill swaps
    for _ in range(PASSES_B):
        improved = False
        for hi, cname in enumerate(comp):
            cls = HERO_CLASSES[cname]
            unused = [s for s in cls.skills if s not in loadout[hi]]
            for repl in unused:
                for slot in range(3):
                    cand = list(loadout)
                    kit = list(cand[hi])
                    kit[slot] = repl
                    if len(set(kit)) < 3:
                        continue
                    cand[hi] = tuple(sorted(kit))
                    w = ev(cand, focus)
                    if w >= best + ACCEPT_B:
                        best, loadout = w, cand
                        improved = True
        if not improved:
            break

    return {"comp": comp, "loadout": [tuple(l) for l in loadout],
            "focus": focus, "wins": best, "n": N_B,
            "screen_wins": entry["wins"]}


def stage_b(pool, out_dir, screened):
    survivors = screened[:KEEP_A]
    t0 = time.time()
    results = []
    for i, res in enumerate(pool.map(_refine_one, survivors)):
        results.append(res)
        print(f"  refined {i + 1}/{len(survivors)}: "
              f"{res['wins']}/{N_B} {tuple(res['comp'])} focus={res['focus']} "
              f"({time.time() - t0:.0f}s)", flush=True)
    results.sort(key=lambda r: -r["wins"])
    _save(out_dir, "stageB", results)
    return results


# -- stage C ----------------------------------------------------------------

def _grid_one(entry):
    comp = tuple(entry["comp"])
    loadout = [tuple(l) for l in entry["loadout"]]
    focus = entry["focus"]
    best = None
    for stun in STUN_GRID:
        for heal in HEAL_GRID:
            w, _ = evaluate(comp, loadout, focus, stun, heal, SEED_C, N_C)
            if best is None or w > best["wins"]:
                best = {"comp": comp, "loadout": loadout, "focus": focus,
                        "stun": stun, "heal": heal, "wins": w, "n": N_C}
    return best


def stage_c(pool, out_dir, refined):
    finalists = refined[:KEEP_C]
    results = list(pool.map(_grid_one, finalists))
    results.sort(key=lambda r: -r["wins"])
    _save(out_dir, "stageC", results)
    for r in results[:5]:
        print(f"  grid: {r['wins']}/{N_C} {tuple(r['comp'])} "
              f"stun={r['stun']} heal={r['heal']}")
    return results


# -- stage D ----------------------------------------------------------------

def _validate_one(cfg):
    comp = tuple(cfg["comp"])
    loadout = [tuple(l) for l in cfg["loadout"]]
    wins, avg_deaths = evaluate(comp, loadout, cfg["focus"], cfg["stun"],
                                cfg["heal"], SEED_D, N_D)
    return {**cfg, "val_wins": wins, "val_n": N_D, "avg_deaths": avg_deaths}


def stage_d(pool, out_dir, grid_results):
    configs = list(grid_results[:KEEP_C])
    configs.append({
        "comp": tuple(c for c, _ in BASELINE["party"]),
        "loadout": [tuple(sk) for _, sk in BASELINE["party"]],
        "focus": BASELINE["focus"], "stun": BASELINE["stun"],
        "heal": BASELINE["heal"], "wins": -1, "n": 0,
        "label": BASELINE["label"],
    })
    results = list(pool.map(_validate_one, configs))
    results.sort(key=lambda r: -r["val_wins"])
    _save(out_dir, "stageD", results)
    return results


# ---------------------------------------------------------------------------

def _save(out_dir, name, data):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"{name}.json"), "w") as f:
        json.dump(data, f, indent=1)


def _load(out_dir, name):
    path = os.path.join(out_dir, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def write_report(out_dir, validated, screened):
    best = validated[0]
    lines = ["# Broad Composition Search — Report\n"]
    lines.append("Full-space search over ordered parties, skill loadouts and "
                 "policy knobs (design: docs/COVERAGE_GAPS.md). Stages A-C "
                 "select, stage D re-measures the finalists on fresh seeds — "
                 "**only stage D numbers below are unbiased.**\n")
    lines.append(f"Parties screened: {len(screened)} (all ordered 4-of-8 "
                 f"parties). Simulated dungeons: ~2 million.\n")
    lines.append("## Validated final ranking (fresh seeds, N=3000)\n")
    lines.append("| # | Party (rank 1→4) | Focus | Stun | Heal thr. | Win rate | 95% CI | Deaths/run | vs best (p) |")
    lines.append("|---|------------------|-------|------|-----------|----------|--------|------------|-------------|")
    for i, r in enumerate(validated, 1):
        lo, hi = wilson_ci(r["val_wins"], r["val_n"])
        _, p = two_proportion_z(best["val_wins"], best["val_n"],
                                r["val_wins"], r["val_n"])
        pcell = "—" if r is best else (
            "p<0.001 *" if p < 0.001 else (f"p={p:.3f} *" if p < 0.05 else f"p={p:.3f}"))
        name = r.get("label") or " / ".join(r["comp"])
        wr = r["val_wins"] / r["val_n"]
        lines.append(f"| {i} | {name} | {r['focus']} | {r['stun']} | {r['heal']} "
                     f"| **{wr:.1%}** | {lo:.1%}–{hi:.1%} | {r['avg_deaths']:.2f} | {pcell} |")
    lines.append("\n`*` = significantly worse than the top configuration "
                 "(two-proportion z-test, α=0.05).\n")
    lines.append("## Winning loadouts\n")
    for r in validated[:5]:
        name = r.get("label") or " / ".join(r["comp"])
        lines.append(f"**{name}**")
        for cname, kit in zip(r["comp"], r["loadout"]):
            lines.append(f"- {cname}: {', '.join(kit)}")
        lines.append("")
    report = "\n".join(lines) + "\n"
    with open(os.path.join(out_dir, "SEARCH_REPORT.md"), "w") as f:
        f.write(report)
    return report


def main():
    ap = argparse.ArgumentParser(description="broad composition search")
    ap.add_argument("--out", default="results/search")
    ap.add_argument("--stage", default="all", choices=["all", "A", "B", "C", "D"])
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    args = ap.parse_args()

    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        screened = _load(args.out, "stageA")
        if args.stage in ("all", "A") and screened is None:
            print("stage A: screening all ordered parties...", flush=True)
            screened = stage_a(pool, args.out)
        refined = _load(args.out, "stageB")
        if args.stage in ("all", "B") and refined is None:
            print("stage B: focus + loadout hill-climb on survivors...", flush=True)
            refined = stage_b(pool, args.out, screened)
        grid = _load(args.out, "stageC")
        if args.stage in ("all", "C") and grid is None:
            print("stage C: policy grid on finalists...", flush=True)
            grid = stage_c(pool, args.out, refined)
        validated = _load(args.out, "stageD")
        if args.stage in ("all", "D") and validated is None:
            print("stage D: fresh-seed validation...", flush=True)
            validated = stage_d(pool, args.out, grid)

    write_report(args.out, validated, screened)
    best = validated[0]
    print(f"\ntotal {time.time() - t0:.0f}s")
    print(f"best (validated): {best['val_wins'] / best['val_n']:.1%} "
          f"{' / '.join(best['comp'])} focus={best['focus']}")
    print(f"report: {args.out}/SEARCH_REPORT.md")


if __name__ == "__main__":
    main()
