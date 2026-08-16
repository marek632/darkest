# Darkest Dungeon Simulator — Strategy Report

*14 strategies x 2000 runs each (28,000 simulated dungeons, 56s).*

A run is a 4-room dungeon (random draws from the encounter table) under board-game rules: rooms last at most 4 rounds, an uncleared room forces a retreat (stress, -1 light, full monster reinforcements), and the quest fails when the light tracker (start 5) hits 0. **Win** = clear all 4 rooms with at least one hero alive. Seeds are deterministic, so every strategy faces the same distribution of dungeons.

## Ranking

| # | Strategy | Win rate | 95% CI | Deathless | Avg deaths | Avg rounds | Retreats | Avg afflictions | Survivor stress | vs best (p) |
|---|----------|----------|--------|-----------|------------|------------|----------|-----------------|-----------------|-------------|
| 1 | shuffle_bruisers | **80.0%** | 78.2%–81.7% | 78.0% | 0.53 | 15.3 | 1.35 | 0.44 | 3.1 | — |
| 2 | all_damage_no_healer | **78.0%** | 76.2%–79.8% | 65.5% | 1.01 | 15.2 | 1.09 | 0.34 | 2.8 | p=0.130 |
| 3 | glass_cannon_rush | **71.0%** | 69.0%–73.0% | 66.0% | 1.15 | 16.6 | 1.39 | 0.62 | 2.9 | p<0.001 * |
| 4 | classic_stress_first | **54.9%** | 52.7%–57.0% | 53.9% | 1.04 | 20.1 | 2.34 | 0.82 | 4.1 | p<0.001 * |
| 5 | classic_aoe | **52.5%** | 50.4%–54.7% | 51.0% | 1.41 | 20.5 | 2.42 | 1.00 | 4.2 | p<0.001 * |
| 6 | classic_balanced | **50.7%** | 48.5%–52.9% | 49.8% | 0.98 | 20.7 | 2.56 | 0.88 | 4.6 | p<0.001 * |
| 7 | backline_artillery | **40.6%** | 38.5%–42.8% | 39.9% | 1.35 | 24.0 | 3.15 | 1.18 | 5.5 | p<0.001 * |
| 8 | blight_party | **20.7%** | 19.0%–22.5% | 19.7% | 1.96 | 26.7 | 3.77 | 1.55 | 6.5 | p<0.001 * |
| 9 | bleed_party | **19.4%** | 17.7%–21.1% | 17.9% | 2.16 | 25.7 | 3.73 | 1.58 | 6.5 | p<0.001 * |
| 10 | mark_backline_purge | **17.2%** | 15.7%–19.0% | 17.2% | 1.09 | 26.1 | 4.07 | 1.38 | 6.8 | p<0.001 * |
| 11 | mark_execute | **17.2%** | 15.6%–18.9% | 17.0% | 1.69 | 26.3 | 3.94 | 1.58 | 6.7 | p<0.001 * |
| 12 | double_healer_turtle | **5.4%** | 4.5%–6.5% | 5.4% | 0.86 | 28.2 | 4.64 | 1.31 | 7.4 | p<0.001 * |
| 13 | classic_stunlock | **1.6%** | 1.1%–2.2% | 1.6% | 1.95 | 28.4 | 4.54 | 1.59 | 7.4 | p<0.001 * |
| 14 | stun_wall | **0.0%** | 0.0%–0.2% | 0.0% | 0.36 | 27.2 | 4.97 | 0.67 | 6.7 | p<0.001 * |

`*` = significantly worse than the top strategy (two-proportion z-test, α=0.05).

## Strategy descriptions

- **shuffle_bruisers** — Crusader / Highwayman / Grave Robber / Vestal. Movement-skill bruisers over a Vestal anchor.
- **all_damage_no_healer** — Hellion / Highwayman / Bounty Hunter / Grave Robber. Deliberate baseline: zero sustain, pure damage.
- **glass_cannon_rush** — Hellion / Highwayman / Grave Robber / Plague Doctor. No dedicated healer; race the damage clock, snipe the backline.
- **classic_stress_first** — Crusader / Highwayman / Plague Doctor / Vestal. Classic comp; kill stress dealers before anything else.
- **classic_aoe** — Crusader / Highwayman / Plague Doctor / Vestal. Classic comp leaning on AOE clears and group healing.
- **classic_balanced** — Crusader / Highwayman / Plague Doctor / Vestal. The tutorial party: tank/dps/support/healer, balanced loadouts.
- **backline_artillery** — Crusader / Hellion / Plague Doctor / Occultist. Two frontliners hold while the back rains AOE on the enemy rear.
- **blight_party** — Hellion / Grave Robber / Plague Doctor / Occultist. Blight-heavy comp: strong into skeletons' low blight resist.
- **bleed_party** — Hellion / Highwayman / Grave Robber / Occultist. Bleed-heavy comp. Expected to struggle vs bleed-immune skeletons.
- **mark_backline_purge** — Crusader / Bounty Hunter / Occultist / Vestal. Drag the backline forward and beat it to death at the front.
- **mark_execute** — Crusader / Bounty Hunter / Occultist / Vestal. Mark synergy: Occultist hexes, Bounty Hunter collects.
- **double_healer_turtle** — Crusader / Bounty Hunter / Occultist / Vestal. Two healers, a marked tank, and patience.
- **classic_stunlock** — Crusader / Highwayman / Plague Doctor / Vestal. Classic comp, but every stun in the kit and a policy that loves them.
- **stun_wall** — Hellion / Bounty Hunter / Plague Doctor / Vestal. Maximum stun coverage across all four ranks.

## Findings (grounded-stats tournament)

With official wiki stat lines (see docs/ABILITY_AUDIT.md), the
hand-crafted ranking reshuffled again: shuffle_bruisers (80.0%) edges
all_damage_no_healer (78.0%, p=0.13 — statistically tied); stun-heavy
strategies collapsed outright (classic_stunlock 1.6%, stun_wall 0.0%)
because the official Blinding Gas is limited to 3 uses per battle and
YAWP self-debuffs; bleed strategies crashed (19.4%) on the Highwayman's
corrected 5–10 damage; and the classic party sits at a coin flip
(50.7%), consistent with the source game's reputation. The full
composition search (results/search/SEARCH_REPORT.md) finds substantially
better parties than any of these fourteen.
