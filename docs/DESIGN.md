# Design: Darkest Dungeon Board-Game Simulator

## Scope

The simulator models the tabletop adaptation of *Darkest Dungeon*: a
cooperative rank-based dungeon crawl where a party of four heroes fights
through a series of encounters while managing hit points **and** stress.
It implements the systems that actually drive strategic choice — party
composition, skill loadouts (3 chosen from each hero's kit, per the official rules), rank
positioning, stress/resolve, death's door, damage-over-time, stuns, and
marks — and deliberately omits campaign-layer systems (see *Out of scope*).

## A run

A **run** is one dungeon: 4 rooms drawn randomly from a slotted
encounter table of escalating difficulty (slot 4 contains the Ghoul and
Necromancer climax fights). Heroes carry HP, stress, and
virtue/affliction state between rooms; DOTs, buffs, marks and stuns
clear.

Per the official rules, a room's battle lasts **at most 4 rounds**. If
the room isn't cleared, the party retreats: heroes keep their wounds,
each gains 1 stress, the **light tracker** (start 5) drops 1, and the
room refills to a full monster group for the next attempt. Darkness
never ends the quest — as the light dies, monsters grow stronger
(+10–25% damage, +2–5 crit, +20–40% stress, per the source game's
light-meter table), so failure comes from attrition, not a timer.
After clearing a room (except the last), the party camps: a pool of 4
**rest points**, each restoring 3 HP or clearing 2 stress on any hero —
a fixed economy independent of anyone's skill kit.

**Win** = all 4 rooms cleared with at least one hero alive.

## Combat model

* **Ranks/stances.** Four hero positions (1 = front) approximating the
  board game's Aggressive/Defensive/Range/Support stances, and up to four
  enemy positions. Skills have *launch* ranks and *target* ranks. Dead
  combatants are removed and the line compacts forward.
* **Initiative.** An alternating card deck: one card per living
  combatant, hero-faced or monster-faced, shuffled each round; a reveal
  activates that side's front-most not-yet-activated combatant. Speed
  does not determine turn order.
* **Turns.** A hero turn may combine a one-step position change with a
  skill use (the official two-action turn). Monsters likewise step into
  range when their current position offers no legal skill.
* **To-hit.** d10 roll-under: hit iff `d10 < skill ACC + mods − dodge`,
  with the effective target number clamped to 1–9 (a hit and a miss are
  always possible).
* **Damage.** Heroes roll uniformly in `weapon range × skill modifier`,
  scaled by damage buffs, mark/stun bonuses, then reduced by the target's
  PROT (%). Minimum 1 on a damaging hit.
* **Crits.** `chance = base crit + skill crit mod` (percent). A crit
  deals `1.5 × max damage`; a hero suffering one gains 1 stress.
* **DOTs.** Bleed/blight apply on `chance − resist`, tick at the start of
  the victim's turn. Skeletons have 200 bleed resist (immune) — bleed
  comps should measurably underperform in bone-heavy encounters.
* **Stun.** `chance − stun resist`; a stunned combatant loses its next
  turn and gains +50 stun resist for 2 rounds.
* **Marks.** Last 3 rounds; some skills gain large bonuses vs marked
  targets (Collect Bounty +90%), and enemies prefer marked heroes.

## Stress & resolve

Stress is a **0–10 track** (board-game scale). Heroes gain it from enemy
stress skills (1–2), crits taken (+1), reaching death's door (+1), ally
deaths (+1), and forced retreats (+1). Filling the track triggers a
one-time **resolve check**: 25% virtue (stress drops to 4, permanent
+1 ACC, +15% damage), else **affliction** (stress drops to 7, permanent
−1 ACC/dodge, and each turn a 20% chance to act out, stressing the
party). Filling the track *again* causes a **heart attack** — straight
to death's door, or death if already there.

## Death

At 0 HP a hero stands at **death's door**: any further damage forces a
death's-door die roll (1/3 death). Any heal removes death's door. Death
is permanent for the run.

## Deviations from the official board game

The full rules-correctness audit, with severity ratings and sources, is
in `docs/RULES_AUDIT.md`. Remaining documented simplifications:

| Simplified | Rationale |
|---|---|
| 2D room boards → four positions | Preserves stance-gating of skills; drops room geometry (fountains, pits) |
| Death's-door die rolled per damage event, not per wound | Damage keeps source-material HP scale; 1/3 death chance per event approximates official expectation |
| Campaign layer (hamlet, leveling, quirks, provisions) | Strategy choice binds within a single run; campaign effects are roughly uniform across strategies |
| Percentage-based crits, stun/DOT/debuff resists | Physical game's per-card mechanisms aren't public; probabilities preserved |

Enemy stat cards are not public, so enemy numbers approximate the source
material's apprentice-level proportions, globally scaled by
`ddsim/tuning.py` so that strategy win rates spread over roughly 0–95% —
wide spread maximizes the statistical power of strategy comparisons at a
given number of runs.

## Strategy evaluation

Each `Strategy` = party composition + 3-skill loadout per hero + policy
knobs (targeting focus, heal thresholds, stun affinity). The hero AI
scores every legal (skill, target) pair with expected-value heuristics
(hit chance × expected damage, kill bonuses, death's-door heal priority,
stun value scaled by target threat) and plays the best; the knobs bias
those scores so strategies genuinely play differently.

Runs are seeded deterministically (`BASE_SEED + strategy_index·10⁶ + i`),
so results are exactly reproducible and every strategy faces the same
dungeon distribution. Comparisons use Wilson 95% intervals and
two-proportion z-tests against the top performer.
