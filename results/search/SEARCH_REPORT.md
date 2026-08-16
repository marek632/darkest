# Broad Composition Search — Report

Full-space search over ordered parties, skill loadouts and policy knobs (design: docs/COVERAGE_GAPS.md). Stages A-C select, stage D re-measures the finalists on fresh seeds — **only stage D numbers below are unbiased.**

Parties screened: 1680 (all ordered 4-of-8 parties). Simulated dungeons: ~2 million.

## Validated final ranking (fresh seeds, N=3000)

| # | Party (rank 1→4) | Focus | Stun | Heal thr. | Win rate | 95% CI | Deaths/run | vs best (p) |
|---|------------------|-------|------|-----------|----------|--------|------------|-------------|
| 1 | Crusader / Hellion / Highwayman / Plague Doctor | threat | 1.0 | 0.45 | **98.0%** | 97.4%–98.4% | 0.12 | — |
| 2 | Crusader / Highwayman / Plague Doctor / Hellion | backline | 0.6 | 0.45 | **97.3%** | 96.7%–97.9% | 0.16 | p=0.087 |
| 3 | Highwayman / Crusader / Plague Doctor / Hellion | stress_first | 1.0 | 0.45 | **96.9%** | 96.2%–97.5% | 0.17 | p=0.007 * |
| 4 | Crusader / Hellion / Highwayman / Grave Robber | stress_first | 0.6 | 0.45 | **96.4%** | 95.6%–97.0% | 0.22 | p<0.001 * |
| 5 | Crusader / Vestal / Highwayman / Plague Doctor | stress_first | 1.0 | 0.45 | **96.2%** | 95.5%–96.8% | 0.23 | p<0.001 * |
| 6 | Highwayman / Crusader / Grave Robber / Plague Doctor | threat | 1.0 | 0.45 | **95.5%** | 94.7%–96.2% | 0.24 | p<0.001 * |
| 7 | Hellion / Crusader / Plague Doctor / Highwayman | backline | 0.6 | 0.45 | **95.5%** | 94.7%–96.2% | 0.26 | p<0.001 * |
| 8 | Crusader / Vestal / Highwayman / Grave Robber | stress_first | 0.6 | 0.45 | **95.2%** | 94.4%–95.9% | 0.29 | p<0.001 * |
| 9 | Vestal / Crusader / Highwayman / Grave Robber | stress_first | 1.6 | 0.75 | **95.2%** | 94.4%–95.9% | 0.26 | p<0.001 * |
| 10 | Grave Robber / Vestal / Highwayman / Plague Doctor | threat | 1.0 | 0.45 | **95.1%** | 94.3%–95.8% | 0.29 | p<0.001 * |
| 11 | Crusader / Highwayman / Plague Doctor / Grave Robber | backline | 0.6 | 0.45 | **95.1%** | 94.2%–95.8% | 0.26 | p<0.001 * |
| 12 | Bounty Hunter / Crusader / Highwayman / Plague Doctor | stress_first | 0.6 | 0.45 | **94.9%** | 94.0%–95.6% | 0.27 | p<0.001 * |
| 13 | Hellion / Crusader / Highwayman / Plague Doctor | backline | 1.0 | 0.45 | **94.7%** | 93.9%–95.5% | 0.28 | p<0.001 * |
| 14 | Highwayman / Crusader / Grave Robber / Vestal | threat | 0.6 | 0.45 | **94.6%** | 93.7%–95.4% | 0.22 | p<0.001 * |
| 15 | Vestal / Crusader / Highwayman / Plague Doctor | stress_first | 1.6 | 0.45 | **94.0%** | 93.1%–94.8% | 0.32 | p<0.001 * |
| 16 | Highwayman / Vestal / Grave Robber / Plague Doctor | backline | 0.6 | 0.45 | **93.8%** | 92.8%–94.6% | 0.37 | p<0.001 * |
| 17 | baseline:all_damage_no_healer | lowest_hp | 1.0 | 0.3 | **76.2%** | 74.6%–77.7% | 1.09 | p<0.001 * |

`*` = significantly worse than the top configuration (two-proportion z-test, α=0.05).

## Winning loadouts

**Crusader / Hellion / Highwayman / Plague Doctor**
- Crusader: Holy Lance, Smite, Zealous Accusation
- Hellion: Breakthrough, Iron Swan, Wicked Hack
- Highwayman: Duelist's Advance, Grapeshot Blast, Point Blank Shot
- Plague Doctor: Blinding Gas, Disorienting Blast, Noxious Blast

**Crusader / Highwayman / Plague Doctor / Hellion**
- Crusader: Zealous Accusation, Smite, Stunning Blow
- Highwayman: Duelist's Advance, Pistol Shot, Point Blank Shot
- Plague Doctor: Noxious Blast, Plague Grenade, Blinding Gas
- Hellion: Barbaric YAWP, Breakthrough, Wicked Hack

**Highwayman / Crusader / Plague Doctor / Hellion**
- Highwayman: Duelist's Advance, Point Blank Shot, Wicked Slice
- Crusader: Zealous Accusation, Smite, Stunning Blow
- Plague Doctor: Noxious Blast, Plague Grenade, Blinding Gas
- Hellion: Barbaric YAWP, Breakthrough, Wicked Hack

**Crusader / Hellion / Highwayman / Grave Robber**
- Crusader: Zealous Accusation, Smite, Stunning Blow
- Hellion: Bleed Out, Breakthrough, Wicked Hack
- Highwayman: Duelist's Advance, Grapeshot Blast, Point Blank Shot
- Grave Robber: Lunge, Pick to the Face, Poison Dart

**Crusader / Vestal / Highwayman / Plague Doctor**
- Crusader: Zealous Accusation, Smite, Stunning Blow
- Vestal: Hand of Light, Dazzling Light, Mace Bash
- Highwayman: Duelist's Advance, Grapeshot Blast, Point Blank Shot
- Plague Doctor: Noxious Blast, Plague Grenade, Blinding Gas


## Findings (grounded-stats run)

1. **New validated champion: Crusader / Hellion / Highwayman / Plague
   Doctor** (threat focus) at **98.0%** (CI 97.4–98.4%), 0.12 deaths/run;
   statistically tied only with its own reordering (#2, p=0.087).
2. **Grounding the stats rehabilitated the Plague Doctor.** With invented
   stats she was the worst class in the game (17 of the top-100 screened
   parties, 81 of the bottom-100). With her official kit — Noxious Blast's
   blight 5/round and a three-use, 100%-chance Blinding Gas — she sits in
   four of the top five validated parties. Conclusions at this level are
   very sensitive to stat fidelity, which is why this grounding pass
   mattered.
3. **The pure-damage baseline collapsed from champion to −22 points.**
   all_damage_no_healer: 94% under v2 rules with invented stats, 76.2% now
   vs the 98.0% champion. With official numbers, rule-accurate utility
   (limited but reliable stuns, strong blight, riposte) beats raw damage.
4. **Stun-spam is now structurally impossible, matching the official
   cards.** Blinding Gas is 3 uses/battle and YAWP self-debuffs;
   classic_stunlock fell from 34.1% to 1.6% in the tournament. The stun
   *rationed as a tool* (in the champion's kit) is excellent; the stun as
   a *strategy* is dead.
5. **Bleed comps crashed** (bleed_party 60.7% → 19.4%): the Highwayman's
   corrected 5–10 weapon damage removed the engine that used to carry
   them, and skeleton immunity now bites a weaker kit much harder.
6. **Winning kits exploit the two-action turn**: the champion's Crusader
   carries Holy Lance (a back-rank launcher) in rank 1 and its Hellion
   carries Breakthrough in rank 2 — loadouts that convert forced shuffles
   into damage instead of wasted turns. This tech depends on the official
   move-then-strike action economy implemented in the rules audit.
