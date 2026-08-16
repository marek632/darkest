# Darkest Dungeon Simulator — Strategy Report

*14 strategies x 2000 runs each (28,000 simulated dungeons, 50s).*

A run is a 4-room dungeon (random draws from the encounter table) under board-game rules: rooms last at most 4 rounds, an uncleared room forces a retreat (stress, -1 light, full monster reinforcements), and the quest fails when the light tracker (start 5) hits 0. **Win** = clear all 4 rooms with at least one hero alive. Seeds are deterministic, so every strategy faces the same distribution of dungeons.

## Ranking

| # | Strategy | Win rate | 95% CI | Deathless | Avg deaths | Avg rounds | Retreats | Avg afflictions | Survivor stress | vs best (p) |
|---|----------|----------|--------|-----------|------------|------------|----------|-----------------|-----------------|-------------|
| 1 | all_damage_no_healer | **93.9%** | 92.8%–94.9% | 81.3% | 0.38 | 12.2 | 0.32 | 0.03 | 1.2 | — |
| 2 | glass_cannon_rush | **90.5%** | 89.1%–91.7% | 87.9% | 0.37 | 14.8 | 0.84 | 0.16 | 2.1 | p<0.001 * |
| 3 | shuffle_bruisers | **84.5%** | 82.8%–86.0% | 82.6% | 0.40 | 15.8 | 1.23 | 0.28 | 2.6 | p<0.001 * |
| 4 | classic_aoe | **77.6%** | 75.7%–79.4% | 76.4% | 0.47 | 18.4 | 1.65 | 0.37 | 3.2 | p<0.001 * |
| 5 | classic_stress_first | **65.7%** | 63.6%–67.7% | 65.0% | 0.34 | 20.7 | 2.35 | 0.17 | 3.4 | p<0.001 * |
| 6 | bleed_party | **60.7%** | 58.5%–62.8% | 59.7% | 0.79 | 22.3 | 2.59 | 0.51 | 4.2 | p<0.001 * |
| 7 | classic_balanced | **47.4%** | 45.2%–49.6% | 47.3% | 0.35 | 22.8 | 3.02 | 0.20 | 4.1 | p<0.001 * |
| 8 | classic_stunlock | **34.1%** | 32.1%–36.2% | 34.0% | 0.52 | 25.0 | 3.60 | 0.32 | 4.9 | p<0.001 * |
| 9 | backline_artillery | **30.0%** | 28.1%–32.1% | 30.0% | 0.80 | 26.1 | 3.78 | 0.90 | 6.0 | p<0.001 * |
| 10 | mark_backline_purge | **27.3%** | 25.3%–29.2% | 27.3% | 0.39 | 25.6 | 3.89 | 0.34 | 5.7 | p<0.001 * |
| 11 | double_healer_turtle | **18.1%** | 16.5%–19.9% | 18.1% | 0.19 | 26.6 | 4.30 | 0.22 | 5.8 | p<0.001 * |
| 12 | mark_execute | **16.2%** | 14.6%–17.8% | 16.1% | 0.79 | 26.1 | 4.32 | 1.00 | 6.7 | p<0.001 * |
| 13 | blight_party | **1.9%** | 1.4%–2.6% | 1.8% | 0.79 | 28.4 | 4.84 | 0.69 | 6.7 | p<0.001 * |
| 14 | stun_wall | **0.1%** | 0.0%–0.3% | 0.1% | 1.13 | 25.4 | 4.87 | 1.18 | 7.3 | p<0.001 * |

`*` = significantly worse than the top strategy (two-proportion z-test, α=0.05).

## Strategy descriptions

- **all_damage_no_healer** — Hellion / Highwayman / Bounty Hunter / Grave Robber. Deliberate baseline: zero sustain, pure damage.
- **glass_cannon_rush** — Hellion / Highwayman / Grave Robber / Plague Doctor. No dedicated healer; race the damage clock, snipe the backline.
- **shuffle_bruisers** — Crusader / Highwayman / Grave Robber / Vestal. Movement-skill bruisers over a Vestal anchor.
- **classic_aoe** — Crusader / Highwayman / Plague Doctor / Vestal. Classic comp leaning on AOE clears and group healing.
- **classic_stress_first** — Crusader / Highwayman / Plague Doctor / Vestal. Classic comp; kill stress dealers before anything else.
- **bleed_party** — Hellion / Highwayman / Grave Robber / Occultist. Bleed-heavy comp. Expected to struggle vs bleed-immune skeletons.
- **classic_balanced** — Crusader / Highwayman / Plague Doctor / Vestal. The tutorial party: tank/dps/support/healer, balanced loadouts.
- **classic_stunlock** — Crusader / Highwayman / Plague Doctor / Vestal. Classic comp, but every stun in the kit and a policy that loves them.
- **backline_artillery** — Crusader / Hellion / Plague Doctor / Occultist. Two frontliners hold while the back rains AOE on the enemy rear.
- **mark_backline_purge** — Crusader / Bounty Hunter / Occultist / Vestal. Drag the backline forward and beat it to death at the front.
- **double_healer_turtle** — Crusader / Bounty Hunter / Occultist / Vestal. Two healers, a marked tank, and patience.
- **mark_execute** — Crusader / Bounty Hunter / Occultist / Vestal. Mark synergy: Occultist hexes, Bounty Hunter collects.
- **blight_party** — Hellion / Grave Robber / Plague Doctor / Occultist. Blight-heavy comp: strong into skeletons' low blight resist.
- **stun_wall** — Hellion / Bounty Hunter / Plague Doctor / Vestal. Maximum stun coverage across all four ranks.

## Findings (v2 — corrected board-game rules)

The rules audit (docs/RULES_AUDIT.md) led to seven fixes: 3-skill loadouts,
the 4-round room limit with forced retreat and monster reinforcement,
initiative cards, d10 roll-under accuracy, move-then-strike turns, the 0-10
stress track, the light tracker, and rationed camp rest. They **inverted the
meta**:

1. **Tempo is everything under the official rules.** v1's champion,
   classic_balanced, fell from 81.8% (tied 1st) to 47.4% (7th). v1's worst
   strategy — all_damage_no_healer, the zero-sustain baseline — is now the
   best (93.9%). The 4-round room limit turns every fight into a race, and
   every non-damage activation costs a fraction of a room.
2. **The light tracker, not the monsters, is what kills parties.** Strategies
   above 84% average under 1.3 retreats per run; every strategy below 31%
   averages ~4-5 and dies to darkness. Hero deaths are uniformly low
   (0.19-1.13 per run) — the dominant failure mode is the quest clock, not
   the party wipe.
3. **In-fight healing no longer pays.** A heal spends a scarce activation on
   HP the clock doesn't refund, and the official camp system (rationed rest
   points between rooms) covers recovery anyway. double_healer_turtle keeps
   its heroes safest (0.19 deaths/run) and still loses 82% of its quests.
4. **Stalling is dead, exactly as the rules intend.** stun_wall — 57.4% in
   v1's unlimited-round battles — wins 0.1% now. Instrumented runs show it
   spending activations on zero-damage stuns and group heals, clearing rooms
   1-2, then burning all five light on room 3. v1's 40-round battles were
   quietly legitimizing an illegal strategy.
5. **DOT ramp doesn't fit a 4-round clock.** blight_party collapsed to 1.9%:
   a blight lands at most ~3 ticks before the room ends or refills — and a
   retreat resets enemy HP, wasting every stacked DOT.
6. **The adaptive-policy result still holds.** bleed_party still uses 0%
   bleed skills against bleed-immune skeletons (~35% vs brigands), but its
   flexibility only carries it to 6th (60.7%): its Occultist's healing
   actions now cost tempo the comp can't spare.

**Recommendation:** under official rules, **all_damage_no_healer** — Hellion /
Highwayman / Bounty Hunter / Grave Robber, pure damage loadouts — is the best
quest-completion strategy (93.9%, CI 92.8-94.9%, significantly ahead of every
alternative at p<0.001). If minimizing hero deaths matters more than the
extra win margin, **glass_cannon_rush** trades 3.4 points of win rate for the
best deathless rate (87.9% vs 81.3%). The general law the tournament
supports: bring damage, clear rooms on schedule, and let the official camp
system do the healing.

*Caveats:* official monster stat cards are not public (enemy numbers are
calibrated approximations), and the hero AI is heuristic — results rank
strategy+policy pairs, not perfect play. The magnitude of the reordering
(rank correlation with v1 is strongly negative at the extremes) is the
robust conclusion: the official action-economy rules punish sustain and
control far harder than video-game-style simulations suggest.
