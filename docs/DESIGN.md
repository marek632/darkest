# Design: Darkest Dungeon Board-Game Simulator

## Scope

The simulator models the tabletop adaptation of *Darkest Dungeon*: a
cooperative rank-based dungeon crawl where a party of four heroes fights
through a series of encounters while managing hit points **and** stress.
It implements the systems that actually drive strategic choice — party
composition, skill loadouts (4 chosen from each hero's kit), rank
positioning, stress/resolve, death's door, damage-over-time, stuns, and
marks — and deliberately omits campaign-layer systems (see *Out of scope*).

## A run

A **run** is one dungeon: 4 encounters drawn randomly from a slotted
encounter table of escalating difficulty (slot 4 contains the Ghoul and
Necromancer climax fights). Heroes carry HP, stress, and
virtue/affliction state between encounters; DOTs, buffs, marks and stuns
clear. After each victorious encounter the party gets a short breather:
up to 3 worthwhile support casts (heals/stress heals), emulating the
tabletop practice of patching up before opening the next door.

**Win** = all 4 encounters cleared with at least one hero alive.

## Combat model

* **Ranks.** Four hero ranks (1 = front) and up to four enemy ranks.
  Skills have *launch* ranks and *target* ranks. Dead combatants are
  removed and the line compacts forward.
* **Initiative.** Each round every combatant rolls speed + 1d8 (uniform);
  order is descending.
* **To-hit.** `chance = skill ACC + attacker ACC mods − target dodge`,
  clamped to [5%, 95%].
* **Damage.** Heroes roll uniformly in `weapon range × skill modifier`,
  scaled by damage buffs, mark/stun bonuses, then reduced by the target's
  PROT (%). Minimum 1 on a damaging hit.
* **Crits.** `chance = base crit + skill crit mod`. A crit deals
  `1.5 × max damage`. A hero landing a crit sheds 3 stress; a hero
  *suffering* one gains 8 stress.
* **DOTs.** Bleed/blight apply on `chance − resist`, tick at the start of
  the victim's turn. Skeletons have 200 bleed resist (immune) — bleed
  comps should measurably underperform in bone-heavy encounters.
* **Stun.** `chance − stun resist`; a stunned combatant loses its next
  turn and gains +50 stun resist for 2 rounds.
* **Marks.** Last 3 rounds; some skills gain large bonuses vs marked
  targets (Collect Bounty +90%), and enemies prefer marked heroes.

## Stress & resolve

Heroes accumulate stress (0–200) from enemy stress skills, crits taken,
allies hitting death's door (+4), deaths (+10). At 100, a one-time
**resolve check**: 25% virtue (stress resets to 45, permanent +10 ACC,
+15% damage), else **affliction** (permanent −5 ACC/dodge, and each turn
a 20% chance to act out, stressing the party). At 200: **heart attack**
— straight to death's door, or death if already there.

## Death

At 0 HP a hero stands at **death's door**: any further damage forces a
death-blow check (67% survive). Any heal revives them. Death is
permanent for the run.

## Deviations from the source material

Documented simplifications, chosen to keep the strategy space honest
without modeling the full campaign:

| Omitted | Rationale |
|---|---|
| Torch/light meter | Fixed "radiant" assumption; affects all strategies equally |
| Corpses occupying ranks | Enemies compact forward instead |
| Trinkets, quirks, diseases, provisions | Campaign-layer; orthogonal to comp/loadout choice |
| Guard/riposte/summons | Replaced by stat-equivalent effects (tanky defenders, high-HP bosses) |
| Surprise rounds | Symmetric initiative instead |
| Retreat | A run is fought to the end; failure = party wipe or stalemate (40-round cap) |

Skill and enemy numbers approximate apprentice-level values from the
source material, then are globally scaled by `ddsim/tuning.py` so that
strategy win rates spread over roughly 30–85% — near the point of
maximum variance for a binomial outcome, which maximizes the statistical
power of strategy comparisons at a given number of runs.

## Strategy evaluation

Each `Strategy` = party composition + 4-skill loadout per hero + policy
knobs (targeting focus, heal thresholds, stun affinity). The hero AI
scores every legal (skill, target) pair with expected-value heuristics
(hit chance × expected damage, kill bonuses, death's-door heal priority,
stun value scaled by target threat) and plays the best; the knobs bias
those scores so strategies genuinely play differently.

Runs are seeded deterministically (`BASE_SEED + strategy_index·10⁶ + i`),
so results are exactly reproducible and every strategy faces the same
dungeon distribution. Comparisons use Wilson 95% intervals and
two-proportion z-tests against the top performer.
