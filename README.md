# Darkest Dungeon Board-Game Simulator

A complete, dependency-free (stdlib-only) simulator for a rank-based
*Darkest Dungeon* dungeon crawl, plus a Monte Carlo harness that pits
party/skill strategies against each other and ranks them statistically.

* **8 hero classes** (Crusader, Highwayman, Plague Doctor, Vestal,
  Hellion, Occultist, Bounty Hunter, Grave Robber), each with a 6–7 skill
  kit from which every strategy picks 3 per hero (the official loadout rule).
* **12 enemy types** (skeletons, cultists, brigands, Madman, Ghoul and
  Necromancer climax fights) with per-type AI preferences and resists —
  including bleed-immune skeletons.
* **Full combat model**: ranks & movement, ACC/dodge/PROT/crit, bleed,
  blight, stun, marks, buffs/debuffs, stress with virtue/affliction
  resolve checks, heart attacks, death's door and death blows.
* **14 named strategies** spanning classic balanced parties, stun-lock,
  mark-synergy, bleed/blight, glass cannon, and turtle archetypes.
* **Statistics**: Wilson 95% confidence intervals, two-proportion z-tests
  vs the best strategy, deterministic seeding for exact reproducibility.

## Quick start

```bash
# run the full tournament (14 strategies x 2000 dungeons)
python -m ddsim.simulate --runs 2000 --out results

# one strategy only
python -m ddsim.simulate --strategy classic_balanced --runs 500

# watch a single narrated dungeon run
python -m ddsim.simulate --demo

# tests
python -m pytest tests/
```

Outputs land in `results/`: `REPORT.md` (ranked table with CIs and
significance tests) and `summary.csv` (raw metrics).

## Layout

| Path | What it is |
|---|---|
| `ddsim/models.py` | Data model: skills, buffs, DOTs, heroes, enemies |
| `ddsim/data.py` | Content: hero classes, skill kits, enemies, encounter tables |
| `ddsim/combat.py` | Battle engine: initiative, attacks, stress, death |
| `ddsim/policy.py` | Heuristic hero AI, parameterized by strategy knobs |
| `ddsim/dungeon.py` | 4-encounter run loop with recovery phases |
| `ddsim/strategies.py` | The 14 strategies under test |
| `ddsim/tuning.py` | Global difficulty calibration |
| `ddsim/stats.py` | Wilson CIs, z-tests (stdlib only) |
| `ddsim/simulate.py` | Monte Carlo runner / CLI / report writer |
| `docs/DESIGN.md` | Rules model, assumptions, deviations from source |
| `results/` | Committed report from the reference 28k-run tournament |

## Defining your own strategy

Add a `Strategy` to `ddsim/strategies.py`: a party (rank 1 first), four
skills per hero, and optional `PolicyParams` (targeting focus
`threat|stress_first|backline|lowest_hp`, heal thresholds, stun weight).
The test suite validates every registered strategy automatically.
