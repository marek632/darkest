# Darkest Dungeon Simulator — Strategy Report

*14 strategies x 2000 runs each (28,000 simulated dungeons, 50s).*

A run is a fixed 4-encounter dungeon (random draws from the encounter table); **win** = clear all 4 encounters with at least one hero alive. Seeds are deterministic, so every strategy faces the same distribution of dungeons.

## Ranking

| # | Strategy | Win rate | 95% CI | Deathless | Avg deaths | Avg rounds | Avg afflictions | Survivor stress | vs best (p) |
|---|----------|----------|--------|-----------|------------|------------|-----------------|-----------------|-------------|
| 1 | bleed_party | **82.0%** | 80.2%–83.6% | 52.5% | 1.08 | 24.0 | 0.56 | 65 | — |
| 2 | classic_balanced | **81.8%** | 80.1%–83.5% | 69.5% | 0.87 | 25.6 | 0.70 | 67 | p=0.935 |
| 3 | shuffle_bruisers | **80.8%** | 79.0%–82.4% | 62.9% | 0.99 | 24.0 | 0.61 | 64 | p=0.330 |
| 4 | mark_backline_purge | **77.1%** | 75.3%–78.9% | 65.0% | 1.04 | 30.4 | 0.96 | 73 | p<0.001 * |
| 5 | classic_stunlock | **77.0%** | 75.1%–78.8% | 68.3% | 1.02 | 28.3 | 0.75 | 63 | p<0.001 * |
| 6 | classic_stress_first | **76.8%** | 74.9%–78.6% | 65.9% | 1.06 | 26.0 | 0.71 | 65 | p<0.001 * |
| 7 | classic_aoe | **76.1%** | 74.2%–78.0% | 60.6% | 1.15 | 21.5 | 0.64 | 66 | p<0.001 * |
| 8 | glass_cannon_rush | **72.5%** | 70.5%–74.4% | 45.1% | 1.44 | 25.1 | 1.12 | 88 | p<0.001 * |
| 9 | backline_artillery | **70.2%** | 68.1%–72.1% | 61.6% | 1.28 | 29.8 | 1.48 | 82 | p<0.001 * |
| 10 | mark_execute | **63.9%** | 61.8%–66.0% | 51.7% | 1.59 | 31.8 | 1.50 | 88 | p<0.001 * |
| 11 | double_healer_turtle | **63.8%** | 61.7%–65.9% | 53.0% | 1.58 | 32.8 | 1.26 | 73 | p<0.001 * |
| 12 | blight_party | **62.5%** | 60.3%–64.5% | 49.2% | 1.65 | 33.7 | 1.64 | 95 | p<0.001 * |
| 13 | stun_wall | **57.4%** | 55.2%–59.5% | 46.2% | 1.84 | 32.2 | 1.82 | 94 | p<0.001 * |
| 14 | all_damage_no_healer | **34.8%** | 32.7%–36.9% | 4.2% | 3.17 | 18.8 | 0.11 | 56 | p<0.001 * |

`*` = significantly worse than the top strategy (two-proportion z-test, α=0.05).

## Strategy descriptions

- **bleed_party** — Hellion / Highwayman / Grave Robber / Occultist. Bleed-heavy comp. Expected to struggle vs bleed-immune skeletons.
- **classic_balanced** — Crusader / Highwayman / Plague Doctor / Vestal. The tutorial party: tank/dps/support/healer, balanced loadouts.
- **shuffle_bruisers** — Crusader / Highwayman / Grave Robber / Vestal. Movement-skill bruisers over a Vestal anchor.
- **mark_backline_purge** — Crusader / Bounty Hunter / Occultist / Vestal. Drag the backline forward and beat it to death at the front.
- **classic_stunlock** — Crusader / Highwayman / Plague Doctor / Vestal. Classic comp, but every stun in the kit and a policy that loves them.
- **classic_stress_first** — Crusader / Highwayman / Plague Doctor / Vestal. Classic comp; kill stress dealers before anything else.
- **classic_aoe** — Crusader / Highwayman / Plague Doctor / Vestal. Classic comp leaning on AOE clears and group healing.
- **glass_cannon_rush** — Hellion / Highwayman / Grave Robber / Plague Doctor. No dedicated healer; race the damage clock, snipe the backline.
- **backline_artillery** — Crusader / Hellion / Plague Doctor / Occultist. Two frontliners hold while the back rains AOE on the enemy rear.
- **mark_execute** — Crusader / Bounty Hunter / Occultist / Vestal. Mark synergy: Occultist hexes, Bounty Hunter collects.
- **double_healer_turtle** — Crusader / Bounty Hunter / Occultist / Vestal. Two healers, a marked tank, and patience.
- **blight_party** — Hellion / Grave Robber / Plague Doctor / Occultist. Blight-heavy comp: strong into skeletons' low blight resist.
- **stun_wall** — Hellion / Bounty Hunter / Plague Doctor / Vestal. Maximum stun coverage across all four ranks.
- **all_damage_no_healer** — Hellion / Highwayman / Bounty Hunter / Grave Robber. Deliberate baseline: zero sustain, pure damage.
