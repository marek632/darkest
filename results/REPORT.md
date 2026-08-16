# Darkest Dungeon Simulator — Strategy Report

*14 strategies x 2000 runs each (28,000 simulated dungeons, 61s).*

A run is a 4-room dungeon (random draws from the encounter table) under board-game rules: rooms last at most 4 rounds; an uncleared room forces a retreat (stress, -1 light, full monster reinforcements). Low light never ends the quest — it strengthens monsters (damage/crit/stress per the source game's light-meter table), so failure comes from attrition. **Win** = clear all 4 rooms with at least one hero alive. Seeds are deterministic, so every strategy faces the same distribution of dungeons.

## Ranking

| # | Strategy | Win rate | 95% CI | Deathless | Avg deaths | Avg rounds | Retreats | Avg afflictions | Survivor stress | vs best (p) |
|---|----------|----------|--------|-----------|------------|------------|----------|-----------------|-----------------|-------------|
| 1 | shuffle_bruisers | **78.7%** | 76.9%–80.4% | 76.3% | 0.88 | 15.6 | 1.36 | 0.54 | 2.4 | — |
| 2 | all_damage_no_healer | **77.8%** | 76.0%–79.6% | 65.1% | 1.02 | 15.2 | 1.08 | 0.35 | 2.7 | p=0.515 |
| 3 | glass_cannon_rush | **70.9%** | 68.8%–72.8% | 65.6% | 1.22 | 16.5 | 1.37 | 0.64 | 2.7 | p<0.001 * |
| 4 | classic_stress_first | **53.1%** | 51.0%–55.3% | 52.3% | 1.88 | 20.8 | 2.37 | 1.12 | 2.2 | p<0.001 * |
| 5 | classic_aoe | **50.7%** | 48.5%–52.9% | 49.1% | 1.99 | 20.8 | 2.39 | 1.16 | 2.7 | p<0.001 * |
| 6 | classic_balanced | **49.4%** | 47.2%–51.6% | 48.2% | 2.04 | 21.6 | 2.61 | 1.25 | 2.4 | p<0.001 * |
| 7 | backline_artillery | **38.5%** | 36.3%–40.6% | 37.3% | 2.47 | 24.8 | 3.16 | 1.47 | 3.3 | p<0.001 * |
| 8 | blight_party | **18.9%** | 17.2%–20.6% | 17.8% | 3.26 | 27.6 | 3.77 | 1.87 | 3.6 | p<0.001 * |
| 9 | bleed_party | **18.4%** | 16.7%–20.1% | 17.3% | 3.28 | 26.4 | 3.69 | 1.84 | 3.4 | p<0.001 * |
| 10 | mark_backline_purge | **16.4%** | 14.8%–18.1% | 16.3% | 3.35 | 28.8 | 4.36 | 2.09 | 2.3 | p<0.001 * |
| 11 | mark_execute | **15.8%** | 14.3%–17.5% | 15.8% | 3.37 | 27.7 | 3.99 | 1.97 | 2.7 | p<0.001 * |
| 12 | double_healer_turtle | **5.1%** | 4.2%–6.2% | 5.1% | 3.80 | 32.3 | 5.19 | 2.45 | 1.8 | p<0.001 * |
| 13 | classic_stunlock | **1.6%** | 1.1%–2.2% | 1.6% | 3.94 | 30.1 | 4.62 | 2.38 | 1.7 | p<0.001 * |
| 14 | stun_wall | **0.0%** | 0.0%–0.2% | 0.0% | 4.00 | 34.9 | 6.30 | 2.17 | 0.0 | p<0.001 * |

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
