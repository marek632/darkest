# Broad Composition Search — Report

Full-space search over ordered parties, skill loadouts and policy knobs (design: docs/COVERAGE_GAPS.md). Stages A-C select, stage D re-measures the finalists on fresh seeds — **only stage D numbers below are unbiased.**

Parties screened: 1680 (all ordered 4-of-8 parties). Simulated dungeons: ~2 million.

## Validated final ranking (fresh seeds, N=3000)

| # | Party (rank 1→4) | Focus | Stun | Heal thr. | Win rate | 95% CI | Deaths/run | vs best (p) |
|---|------------------|-------|------|-----------|----------|--------|------------|-------------|
| 1 | Crusader / Vestal / Highwayman / Plague Doctor | stress_first | 0.6 | 0.45 | **96.8%** | 96.1%–97.4% | 0.20 | — |
| 2 | Crusader / Hellion / Highwayman / Plague Doctor | lowest_hp | 0.6 | 0.45 | **96.6%** | 95.9%–97.2% | 0.17 | p=0.563 |
| 3 | Crusader / Hellion / Highwayman / Grave Robber | stress_first | 1.0 | 0.45 | **96.1%** | 95.3%–96.7% | 0.23 | p=0.124 |
| 4 | Crusader / Highwayman / Hellion / Plague Doctor | backline | 0.6 | 0.45 | **95.9%** | 95.1%–96.5% | 0.23 | p=0.046 * |
| 5 | Crusader / Highwayman / Plague Doctor / Hellion | backline | 0.6 | 0.45 | **95.8%** | 95.1%–96.5% | 0.22 | p=0.039 * |
| 6 | Highwayman / Crusader / Vestal / Plague Doctor | threat | 0.6 | 0.45 | **95.7%** | 94.9%–96.4% | 0.24 | p=0.024 * |
| 7 | Vestal / Crusader / Highwayman / Plague Doctor | stress_first | 1.0 | 0.45 | **95.7%** | 94.9%–96.4% | 0.24 | p=0.021 * |
| 8 | Highwayman / Crusader / Hellion / Plague Doctor | stress_first | 0.6 | 0.45 | **95.6%** | 94.8%–96.3% | 0.24 | p=0.012 * |
| 9 | Grave Robber / Vestal / Highwayman / Plague Doctor | threat | 0.6 | 0.45 | **95.4%** | 94.6%–96.1% | 0.29 | p=0.005 * |
| 10 | Vestal / Crusader / Highwayman / Grave Robber | stress_first | 1.6 | 0.75 | **94.8%** | 93.9%–95.5% | 0.30 | p<0.001 * |
| 11 | Bounty Hunter / Crusader / Highwayman / Plague Doctor | stress_first | 0.6 | 0.45 | **94.7%** | 93.8%–95.4% | 0.29 | p<0.001 * |
| 12 | Crusader / Bounty Hunter / Highwayman / Plague Doctor | stress_first | 0.6 | 0.45 | **94.4%** | 93.5%–95.1% | 0.29 | p<0.001 * |
| 13 | Grave Robber / Crusader / Plague Doctor / Highwayman | stress_first | 1.6 | 0.45 | **94.4%** | 93.5%–95.1% | 0.32 | p<0.001 * |
| 14 | Highwayman / Crusader / Grave Robber / Vestal | stress_first | 0.6 | 0.75 | **94.2%** | 93.3%–95.0% | 0.28 | p<0.001 * |
| 15 | Highwayman / Crusader / Grave Robber / Plague Doctor | threat | 1.0 | 0.45 | **94.2%** | 93.3%–95.0% | 0.30 | p<0.001 * |
| 16 | Crusader / Vestal / Highwayman / Grave Robber | stress_first | 1.6 | 0.45 | **93.9%** | 93.0%–94.7% | 0.35 | p<0.001 * |
| 17 | baseline:all_damage_no_healer | lowest_hp | 1.0 | 0.3 | **75.8%** | 74.2%–77.3% | 1.13 | p<0.001 * |

`*` = significantly worse than the top configuration (two-proportion z-test, α=0.05).

## Winning loadouts

**Crusader / Vestal / Highwayman / Plague Doctor**
- Crusader: Holy Lance, Stunning Blow, Zealous Accusation
- Vestal: Hand of Light, Dazzling Light, Mace Bash
- Highwayman: Duelist's Advance, Grapeshot Blast, Point Blank Shot
- Plague Doctor: Noxious Blast, Plague Grenade, Blinding Gas

**Crusader / Hellion / Highwayman / Plague Doctor**
- Crusader: Holy Lance, Smite, Zealous Accusation
- Hellion: Barbaric YAWP, Breakthrough, Wicked Hack
- Highwayman: Duelist's Advance, Grapeshot Blast, Point Blank Shot
- Plague Doctor: Battlefield Medicine, Noxious Blast, Plague Grenade

**Crusader / Hellion / Highwayman / Grave Robber**
- Crusader: Zealous Accusation, Smite, Stunning Blow
- Hellion: Bleed Out, Breakthrough, Wicked Hack
- Highwayman: Duelist's Advance, Grapeshot Blast, Point Blank Shot
- Grave Robber: Lunge, Pick to the Face, Poison Dart

**Crusader / Highwayman / Hellion / Plague Doctor**
- Crusader: Holy Lance, Smite, Zealous Accusation
- Highwayman: Duelist's Advance, Pistol Shot, Point Blank Shot
- Hellion: Barbaric YAWP, Iron Swan, Wicked Hack
- Plague Doctor: Noxious Blast, Plague Grenade, Blinding Gas

**Crusader / Highwayman / Plague Doctor / Hellion**
- Crusader: Holy Lance, Smite, Zealous Accusation
- Highwayman: Open Vein, Point Blank Shot, Wicked Slice
- Plague Doctor: Blinding Gas, Emboldening Vapours, Noxious Blast
- Hellion: Barbaric YAWP, Breakthrough, Wicked Hack


## Findings (corrected light model)

1. **Validated champion: Crusader / Vestal / Highwayman / Plague Doctor**
   (stress_first focus) at **96.8%** (CI 96.1–97.4%), 0.20 deaths/run. The
   top three are statistically indistinguishable (96.1–96.8%, p ≥ 0.124);
   all share the Crusader + Highwayman + Plague Doctor core with a
   flexible fourth slot (Vestal, Hellion, or Grave Robber).
2. **Even the Vestal wins by attacking.** The champion's Vestal carries
   Hand of Light, Dazzling Light and Mace Bash — anti-Unholy damage and a
   stun, zero healing skills. Damage-plus-rationed-utility remains the
   optimal shape even when the failure mode is attrition rather than a
   clock.
3. **Highwayman and Plague Doctor remain the load-bearing pair** (86/100
   each in the top-100 screened parties; Bounty Hunter 93/100 and
   Occultist 89/100 of the bottom-100).
4. **Under the corrected light rules, losing parties die, they don't time
   out.** The weakest tournament strategies now average ~4 hero deaths
   per run while fighting on in darkness (+10–25% monster damage at low
   light); win rates barely moved versus the timer model, confirming the
   ranking was not an artifact of the invented light-failure bound.
5. **The pure-damage baseline stays last** (75.8%, −21 points vs the
   champion, p < 0.001).
