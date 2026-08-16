# Coverage Critique: What the 14-Strategy Tournament Did NOT Test

The tournament in `results/REPORT.md` compared 14 hand-written strategies.
That answers "which of these 14 is best," not "which strategy is best." This
document quantifies the gap between those questions, and specifies the
broad search (`ddsim/search.py`) built to close it.

## The space

With the official rules (one copy of each hero; a party of 4 in rank
order; 3 skills chosen per hero; a targeting policy):

| Dimension | Size |
|---|---|
| Class subsets (8 choose 4) | 70 |
| Ordered parties (× 4! orderings) | 1,680 |
| Skill loadouts per party (C(7,3)³ × C(6,3) or C(7,3)⁴) | ~0.86–1.5 million |
| Policy knobs (focus × stun weight × heal threshold) | dozens |
| **Total configurations** | **~10⁹** |

## Measured coverage of the 14-strategy set

* **9 of 1,680 ordered parties tested — 0.5%.** (Several strategies share a
  party and differ only in loadout/policy.)
* **9 of 70 class subsets tested — 13%.** 61 four-class combinations were
  never simulated at all.
* **Every tested subset appeared in exactly one rank ordering.** Nobody
  ever asked whether the Crusader belongs in rank 2, or the Hellion in
  rank 3. Six of eight classes were never tested in rank 1; four were
  never tested in rank 4.
* **9 of 55 skills never appeared in any loadout** (e.g. Finish Him,
  Take Aim, Emboldening Vapours, Incision, Mace Bash). Their value is
  simply unknown.
* **~1 loadout per party out of ~1 million.** Loadouts were hand-picked to
  match each strategy's theme, so loadout quality is confounded with
  party quality.

## Structural biases, not just gaps

1. **Author priors.** The 14 strategies were designed under v1
   (video-game-style) intuitions — healer-centric, sustain-friendly. The
   rules audit then showed those intuitions were wrong (the v1 champion
   fell to 7th). A strategy set authored by a biased prior almost
   certainly misses the optimum of the corrected game.
2. **Policy confounded with composition.** Stun-heavy knobs were only
   attached to stun comps, backline focus only to mark comps, etc. When
   `stun_wall` loses, we cannot say whether the comp, the loadout, or the
   policy lost. The search must vary these independently.
3. **Themed loadouts.** Hand-picked kits are internally "pure" (all-bleed,
   all-stun). Mixed kits — e.g. two damage skills plus one utility — were
   never explored, and the v2 result (tempo dominates) suggests hybrids
   near the damage-maximum are exactly where the optimum lives.
4. **Winner's curse at larger scale.** Screening thousands of configs and
   reporting the best screening score overstates it (selection on noise).
   The search must re-validate finalists on *fresh seeds* that played no
   part in selection.

## Search design (implemented in `ddsim/search.py`)

Staged screen-and-refine, ~2 million simulated dungeons, all stages using
common random numbers (identical seed blocks within a stage) so
comparisons are paired and fair:

* **Stage A — screen every ordered party (1,680).** Each gets an
  automatically built "greedy" loadout (best rank-legal skills by a
  static value heuristic) and the default policy. N=160 runs each.
  Keep the top 40 parties.
  *Known limitation: the greedy loadout is damage-leaning, so
  support-dependent parties get a slight handicap at this stage; the
  refinement stage lets every survivor re-discover support skills if
  they help.*
* **Stage B — refine survivors.** For each surviving party: pick the best
  of the 4 targeting focuses (N=320 paired runs), then hill-climb the
  loadout — try every single-skill swap for every hero, accept swaps that
  improve paired wins by a noise margin, repeat up to 2 passes
  (~45 swap evaluations × 320 runs per pass).
* **Stage C — policy grid on the top 16.** Stun weight × heal threshold
  grid (9 cells × 400 runs) around the chosen focus.
* **Stage D — validation on fresh seeds.** Top 16 configurations plus the
  hand-crafted champion (`all_damage_no_healer`) as baseline: 3,000 runs
  each on a seed block never used during search. Wilson 95% intervals and
  two-proportion z-tests. **Stage D numbers are the only unbiased
  estimates; stage A–C scores are selection-inflated by construction.**

## Deliberately out of scope (documented assumptions)

* **No duplicate classes** — the physical game has one miniature/board per
  hero.
* Secondary policy constants (kill bonus, stress-heal trigger) stay fixed;
  they shape all strategies equally and the finalist grid covers the two
  knobs with the largest observed effect.
* The hero AI itself is fixed. The search finds the best *composition
  under this AI*; a better AI could reorder close finishers (documented
  caveat in the final report).
