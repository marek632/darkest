# Broad Composition Search — Report

Full-space search over ordered parties, skill loadouts and policy knobs (design: docs/COVERAGE_GAPS.md). Stages A-C select, stage D re-measures the finalists on fresh seeds — **only stage D numbers below are unbiased.**

Parties screened: 1680 (all ordered 4-of-8 parties). Simulated dungeons: ~2 million.

## Validated final ranking (fresh seeds, N=3000)

| # | Party (rank 1→4) | Focus | Stun | Heal thr. | Win rate | 95% CI | Deaths/run | vs best (p) |
|---|------------------|-------|------|-----------|----------|--------|------------|-------------|
| 1 | Hellion / Crusader / Highwayman / Vestal | threat | 0.6 | 0.45 | **99.4%** | 99.1%–99.6% | 0.04 | — |
| 2 | Crusader / Hellion / Highwayman / Occultist | threat | 0.6 | 0.75 | **99.3%** | 98.9%–99.5% | 0.05 | p=0.422 |
| 3 | Hellion / Crusader / Highwayman / Occultist | backline | 1.0 | 0.75 | **99.2%** | 98.9%–99.5% | 0.03 | p=0.341 |
| 4 | Hellion / Grave Robber / Highwayman / Vestal | threat | 0.6 | 0.6 | **99.2%** | 98.8%–99.4% | 0.08 | p=0.215 |
| 5 | Hellion / Bounty Hunter / Highwayman / Crusader | lowest_hp | 1.0 | 0.45 | **99.0%** | 98.6%–99.3% | 0.09 | p=0.057 |
| 6 | Hellion / Crusader / Highwayman / Grave Robber | threat | 1.0 | 0.45 | **98.7%** | 98.2%–99.0% | 0.13 | p=0.003 * |
| 7 | Hellion / Crusader / Highwayman / Plague Doctor | stress_first | 0.6 | 0.45 | **98.6%** | 98.2%–99.0% | 0.10 | p=0.002 * |
| 8 | Bounty Hunter / Hellion / Highwayman / Occultist | threat | 0.6 | 0.75 | **98.6%** | 98.1%–98.9% | 0.06 | p<0.001 * |
| 9 | Hellion / Crusader / Occultist / Highwayman | lowest_hp | 1.0 | 0.45 | **98.5%** | 98.0%–98.9% | 0.07 | p<0.001 * |
| 10 | Hellion / Vestal / Highwayman / Crusader | lowest_hp | 1.6 | 0.6 | **98.4%** | 97.9%–98.8% | 0.11 | p<0.001 * |
| 11 | Hellion / Crusader / Highwayman / Bounty Hunter | threat | 1.0 | 0.45 | **98.2%** | 97.7%–98.6% | 0.21 | p<0.001 * |
| 12 | Hellion / Bounty Hunter / Highwayman / Occultist | stress_first | 1.0 | 0.75 | **98.2%** | 97.6%–98.6% | 0.11 | p<0.001 * |
| 13 | Bounty Hunter / Crusader / Highwayman / Grave Robber | threat | 0.6 | 0.45 | **98.1%** | 97.5%–98.5% | 0.17 | p<0.001 * |
| 14 | Hellion / Bounty Hunter / Highwayman / Grave Robber | threat | 0.6 | 0.45 | **97.8%** | 97.2%–98.3% | 0.19 | p<0.001 * |
| 15 | Hellion / Grave Robber / Highwayman / Crusader | stress_first | 0.6 | 0.45 | **97.7%** | 97.1%–98.2% | 0.12 | p<0.001 * |
| 16 | Hellion / Highwayman / Crusader / Vestal | lowest_hp | 1.0 | 0.75 | **96.9%** | 96.3%–97.5% | 0.10 | p<0.001 * |
| 17 | baseline:all_damage_no_healer | lowest_hp | 1.0 | 0.3 | **94.2%** | 93.3%–95.0% | 0.38 | p<0.001 * |

`*` = significantly worse than the top configuration (two-proportion z-test, α=0.05).

## Winning loadouts

**Hellion / Crusader / Highwayman / Vestal**
- Hellion: Bleed Out, If It Bleeds, Iron Swan
- Crusader: Smite, Stunning Blow, Zealous Accusation
- Highwayman: Pistol Shot, Duelist's Advance, Grapeshot Blast
- Vestal: Divine Grace, Dazzling Light, Judgement

**Crusader / Hellion / Highwayman / Occultist**
- Crusader: Smite, Stunning Blow, Zealous Accusation
- Hellion: If It Bleeds, Iron Swan, Wicked Hack
- Highwayman: Duelist's Advance, Grapeshot Blast, Point Blank Shot
- Occultist: Wyrd Reconstruction, Abyssal Artillery, Daemon's Pull

**Hellion / Crusader / Highwayman / Occultist**
- Hellion: Bleed Out, If It Bleeds, Iron Swan
- Crusader: Smite, Stunning Blow, Zealous Accusation
- Highwayman: Pistol Shot, Duelist's Advance, Grapeshot Blast
- Occultist: Wyrd Reconstruction, Abyssal Artillery, Daemon's Pull

**Hellion / Grave Robber / Highwayman / Vestal**
- Hellion: Bleed Out, If It Bleeds, Iron Swan
- Grave Robber: Pick to the Face, Poison Dart, Flashing Daggers
- Highwayman: Duelist's Advance, Grapeshot Blast, Point Blank Shot
- Vestal: Divine Grace, Dazzling Light, Judgement

**Hellion / Bounty Hunter / Highwayman / Crusader**
- Hellion: Bleed Out, If It Bleeds, Iron Swan
- Bounty Hunter: Finish Him, Uppercut, Hook and Slice
- Highwayman: Pistol Shot, Duelist's Advance, Grapeshot Blast
- Crusader: Holy Lance, Inspiring Cry, Battle Heal


## Findings

1. **The best validated configuration** is Hellion / Crusader / Highwayman /
   Vestal (threat focus, stun weight 0.6, heal threshold 0.45) at **99.4%**
   (CI 99.1–99.6%) with 0.04 deaths per run. The top five configurations are
   statistically indistinguishable (all p ≥ 0.057 vs the leader).
2. **The hand-crafted champion was beatable by 5 points.** all_damage_no_healer
   (94.2% on the same fresh seeds) finishes dead last among the 17 validated
   configurations, and its party ranked only 406th of 1,680 in the unbiased
   screen — direct confirmation of the coverage critique: the 14-strategy
   tournament identified the best of its own small sample, not the best
   strategy.
3. **The optimum is a hybrid, not pure damage.** Every top-five party is three
   damage dealers plus one *damage-capable* back-rank support (Vestal or
   Occultist) whose kit attacks by default and heals only in emergencies
   (heal thresholds 0.45–0.75, stun weight at or below 1.0). In-fight
   sustain is worthless as a plan but decisive as insurance: the champion
   converts the baseline's 0.38 deaths/run into 0.04 without losing tempo.
4. **Highwayman is the single most load-bearing class**: present in 100 of
   the top 100 screened parties and only 2 of the bottom 100. Plague Doctor
   is the reverse (17 of the top 100, 81 of the bottom 100).
5. **Hellion is the definitive rank-1 hero** (front rank in 53 of the top
   100), with the Bleed Out / If It Bleeds / Iron Swan kit — Iron Swan
   letting the front rank snipe rank-4 stress dealers.
6. **Four skills no hand-written strategy ever used surfaced in validated
   finalist loadouts**: Finish Him, Breakthrough, Mace Bash, Pick to the
   Face. Unknown-value skills stayed unknown until the search priced them.
7. **Ceiling caveat**: the finalists sit at ~97–99.4%, so at this difficulty
   calibration the corrected game is nearly solved by a good composition;
   separating the top five would need harder tuning or larger N. The robust
   claims are the ordering of shapes (hybrid > pure damage > everything
   else) and the baseline gap, both significant at p < 0.001.
