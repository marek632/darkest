# Correctness Audit: Simulator vs. Official Board Game Rules

This audit compares the simulator (as of the v1 tournament) against the
official rules of **Darkest Dungeon: The Board Game** (Mythic Games), as
documented by the publisher's rulebook coverage and independent rules
guides. Findings are ordered by severity; each lists its resolution.

Sources consulted (the publisher's rulebook PDF itself is distributed via
Kickstarter/Gamefound backer links; rules details below are corroborated
across independent write-ups of the shipped rulebook):

- Dice n Board, "Darkest Dungeon Board Game Guide" — full rules walkthrough
  (initiative cards, two-action turns, d10 roll-under accuracy, death's door
  die, 4-round room limit, light tracker, 3-skill loadouts, camping).
- Wargamer review — d10 roll-under system, death's door die rolls,
  heart-attack deaths, hamlet phase.
- Mythic Games' "Combat" and "Heroes and Stances" previews — initiative
  cards, 4-round retreat + monster reinforcement, stance system.
- Meeple Shelter component breakdown — dice inventory (d10s, death's door
  dice), skill counts.

## Verdict summary

The v1 engine was, in effect, a faithful simulator of the **video game's**
apprentice-level combat math (percentage accuracy, 0–200 stress,
speed+1d8 initiative, unlimited-round battles, 4-skill loadouts). The board
game changes exactly these systems. Ten discrepancies were identified; the
seven that materially affect strategy conclusions are fixed in v2, three are
documented approximations.

## Findings

### F1 — Loadouts are 3 skills, not 4 · **CRITICAL — FIXED**

> "Pick three level one skills from the heroes skill card deck." (rules guide)

v1 gave every hero 4 skills, materially inflating kit flexibility (e.g. a
Vestal could carry both heals *and* both damage skills). **Fix:** heroes now
select exactly 3 skills; all strategies re-specified.

### F2 — Battles are capped at 4 rounds, then forced retreat · **CRITICAL — FIXED**

> "As soon as four rounds pass, the heroes, having lost precious time, will
> be forced to retreat... When heroes return to a room, monsters have called
> for reinforcements and they face a full cadre of monsters again."

v1 let battles run to 40 rounds, which legitimized stalling strategies
(turtle/stun comps) that the real game forbids. **Fix:** rooms last at most
4 rounds. An uncleared room forces a retreat: the party keeps its wounds,
every hero gains stress, the light tracker drops 1, and the room refills to
a full monster group for the next attempt.

### F3 — Initiative comes from an alternating card deck, not speed rolls · **CRITICAL — FIXED**

> "Reveal an initiative card (this will have either heroes or monsters on
> the face-up side). The left-most character who has not yet been activated
> takes their turn."

v1 sorted all combatants by speed + 1d8 each round — video-game logic that
overvalued high-speed heroes and allowed the whole party to act before any
enemy. **Fix:** each round shuffles a deck of one card per living combatant
(hero-faced or monster-faced); each reveal activates that side's front-most
not-yet-activated combatant. Speed no longer affects turn order.

### F4 — To-hit is a d10 roll-under, not a percentage roll · **MAJOR — FIXED**

> "Resolution uses a ten-sided die: if the result is less than the hero's
> accuracy minus the target's dodge value, the attack hits."

v1 used percentage accuracy (85%) minus percentage dodge, clamped [5, 95].
**Fix:** skills carry integer accuracy on the d10 scale, dodge is an integer
0–2, and a hit requires `d10 roll < ACC − dodge` (effective target clamped
to 1–9, preserving the game's always-possible miss/hit). Granularity now
matches the physical die: accuracy modifiers move in 10% steps.

### F5 — Heroes get two actions: move and still use a skill · **MAJOR — FIXED**

> "Each hero may perform two actions per turn, selecting from: moving up to
> their speed value, changing stance, interacting with objects, or using
> skills."

v1 forced a hero to spend the entire turn either moving *or* acting, so a
mispositioned hero wasted whole turns — harsher than the real action
economy. **Fix:** a hero turn may combine a one-step position change with a
skill use (move-then-strike); the policy evaluates skills from both the
current and adjacent positions. One skill per turn is retained (the sources
do not show double-skill turns).

### F6 — Stress is a short track, not 0–200 · **MAJOR — FIXED**

> Stress in the board game is tracked on a short per-hero track (single-digit
> scale, cf. the community discussion "Is stress 0-10 or 0-20"), with
> afflictions and heart-attack deaths as escalating consequences; walking a
> corridor or scouting inflicts 1 stress.

v1 used the video game's 0–200 meter with +8/+12 hits. **Fix:** stress is a
0–10 track; enemy stress attacks inflict 1–2, crits taken and death's-door
events inflict 1. Filling the track tests resolve once
(affliction/virtue); filling it again causes a heart attack. Rescaled
support skills accordingly.

### F7 — Between-fight recovery is rationed rest points, not free skill casts · **MAJOR — FIXED**

> "Some quests provide campfire supplies allowing rest after clearing rooms.
> Rest points distribute among players to recover stress and/or life."

v1 granted 3 free *skill casts* after each victory, which favored parties
whose healers had strong heal skills twice over (in combat and in recovery).
**Fix:** clearing a room grants a fixed pool of rest points; each point
restores a flat amount of HP or stress to any hero, independent of anyone's
skill kit — matching the official camping economy's shape.

### F8 — The light tracker: darkness punishes, it does not end the quest · **MODERATE — FIXED (corrected)**

> "The light tracker begins at five. Dark rooms reduce light by one."
> Source-game light meter: darkness applies escalating penalties — up to
> +25% monster damage, higher monster accuracy/crit, +40% stress at
> "Black as Pitch" (0) — and better loot; it never fails the mission.

Runs start at light 5; each forced retreat burns 1 light (an adaptation:
time wasted in the dark — the official trigger is exploring dark rooms).
Low light applies the published darkness penalties, scaled to the
simulator's dice: at light 3 and below enemies gain +10–25% damage,
+2–5 crit, and stress inflicted rises by +20–40%. **Light 0 does not end
the quest** — a party can keep fighting in pitch darkness, and failure
comes from attrition (wipes, stress spirals) or a generous simulation
safety cap (20 battles/run) that real runs practically never reach. An
earlier revision of the simulator wrongly treated light 0 as automatic
quest failure; that was an invented bound, not an official rule, and it
has been removed. Loot bonuses for darkness are out of scope (no loot
economy in the simulator).

### F9 — Death's door die is rolled per wound · **MODERATE — PARTIALLY FIXED (documented)**

> "Roll the 'at death's door' die for each wound they suffer. If they roll a
> skull icon, the hero dies. Gaining one life point removes death's door."

v1 already matched the heal-removes-death's-door rule and rolls a death
check per damage *event*. The official game rolls per *wound*; since the
simulator keeps video-game-scale damage numbers (a hit is ~5–10 "HP" rather
than 1–3 wounds), a per-HP roll would distort death rates. The per-event
roll with a 1/3 death chance approximates the official expectation at
board-game wound counts. The exact skull-face count of the physical die is
not public in our sources; 1/3 is retained and documented as an assumption.

### F10 — Stances vs. ranks · **MODERATE — DOCUMENTED APPROXIMATION**

The board game positions heroes in four stances (Aggressive / Defensive /
Range / Support) on a 2D room board, with monsters on a stance tracker.
The simulator's ranks 1–4 map onto this structure (1≈Aggressive,
2≈Defensive, 3≈Range, 4≈Support): skills' launch/target ranks encode the
same "be further back to use ranged or healing abilities" constraint. Full
2D room geometry (movement spaces, environmental features like healing
fountains and spike pits) is out of scope; this compresses movement but
preserves the stance-gating of skills that drives loadout strategy.

### F11 — Campaign layer · **OUT OF SCOPE — DOCUMENTED**

The official game is an 11-episode campaign with a hamlet phase, hero
leveling (skills to level 3), quirks, diseases, and provisioning. The
simulator evaluates strategies within a single dungeon run, which is where
party composition and skill loadout decisions bind. Campaign-level effects
(gold, leveling, replacement heroes arriving pre-leveled) apply roughly
uniformly across party choices and are excluded, as before.

## Remaining known assumptions

* Monster stat cards are not publicly available; enemy stats remain
  faithful-in-shape approximations, globally calibrated (`ddsim/tuning.py`).
* The initiative deck's exact composition (cards per side) is not public;
  one card per living combatant is assumed, which reproduces the alternating,
  unpredictable activation the rulebook describes.
* The resolve test's virtue chance in the board game is not public; the
  25% figure carries over from the source material.
* Crit chances remain percentage-based (the physical game's crit mechanism
  differs per skill card; cards are not public).

## Assumption ledger (full provenance sweep)

Prompted by the light-tracker correction, every mechanic in the simulator
was re-classified by provenance. Three classes:

* **OFFICIAL** — directly stated in publisher material or corroborated
  rules coverage of the board game, or exact published source-game values.
* **ADAPTATION** — official mechanic whose exact magnitude/trigger isn't
  public; implemented in the official mechanic's *shape* with documented
  numbers.
* **ASSUMPTION** — invented for the simulation (usually to make it
  terminate or tractable); flagged so no conclusion is silently built on it.

| Mechanic | Class | Notes |
|---|---|---|
| 3 skills per hero | OFFICIAL | |
| 4-round room limit, forced retreat | OFFICIAL | |
| Full monster reinforcements on re-entry | OFFICIAL | publisher's combat preview |
| d10 roll-under to-hit | OFFICIAL | mechanic; per-skill numbers converted from source values |
| Two actions per turn (step + skill) | ADAPTATION | official action list; "at most one skill per turn" is our reading — double-skill turns are not shown in sources |
| Initiative card deck | ADAPTATION | official mechanic; one card per living combatant is assumed (deck composition not public) |
| Light tracker: darkness penalties, never failure | OFFICIAL (shape + source table) | retreat costing 1 light is an ADAPTATION (official trigger is dark rooms during exploration) |
| Death's door + heal removes it | OFFICIAL | |
| Death's-door die = 1/3 death, rolled per damage event | ADAPTATION | die faces not public; per-event (not per-wound) keeps source HP scale |
| Stress short track, afflictions, heart attacks | ADAPTATION | 0–10 track; resolve at first fill (25% virtue — source value), heart attack at second fill mirrors the source's 200 cap; virtue→4 matches source's reset-to-45 ratio; affliction→7 is invented to avoid an instant-heart-attack loop |
| Camp rest points after a cleared room | ADAPTATION | official shape; 4 points × (3 HP or 2 stress) magnitudes invented |
| Bleed/blight/stun/mark/resists | OFFICIAL values | percentages from published stat lines |
| Stun grants +50 stun resist for 2 rounds | OFFICIAL (source game) | |
| Crit = 1.5 × max damage | OFFICIAL (source game) | |
| Riposte, armor piercing, vs-family bonuses, skill limits, summons | OFFICIAL (source game) | |
| Effective to-hit clamped 1–9 (hit and miss always possible) | ASSUMPTION | guardrail; the physical game may allow auto-hits/misses |
| Enemy AI: weighted skills + targeting preferences | ADAPTATION | official monsters follow per-card behavior; weights approximate them |
| Encounter tables, 4-room dungeon shape | ASSUMPTION | official quests vary; fixed shape isolates strategy comparison |
| 20-battle simulation safety cap | ASSUMPTION | anti-infinite-loop guard only; practically unreachable |
| Voluntary early retreat from a room | NOT MODELED | heroes always fight the full 4 rounds |
| Torch provisions restoring light | NOT MODELED | no provisioning economy |
| Difficulty calibration 0.8× enemy HP/damage | ASSUMPTION | single documented knob over official values |

No conclusion in the final report rests on an ASSUMPTION-class mechanic
except the fixed dungeon shape (which applies identically to every
strategy) and the calibration knob (which preserves all relative
relationships between enemies).
