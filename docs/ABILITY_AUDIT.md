# Ability-Effects Audit and Stat Grounding

Second correctness sweep, this time at the level of individual skills and
monster stat lines. The board game's own cards remain unpublished (the
rulebook circulates only through backer links), so every ability and
monster was checked against the **official Darkest Dungeon wiki**
(darkestdungeon.wiki.gg) — the exact source material the board game
adapts — using level-1 hero skills and apprentice-tier monsters
(Ghoul: veteran, its lowest tier; Necromancer: apprentice boss).

## Conversion rules (unchanged board-game framework)

| Quantity | Mapping |
|---|---|
| Accuracy % | d10 target number = `round(ACC/10)`, effective 1–9 |
| Dodge % | integer points = `round(dodge/10)` |
| Stress (video 0–200 scale) | 0–10 track points = `round(value/10)`, min 1 |
| DOT / stun / debuff chances | stay percentages (resisted rolls) |
| Launch/target ranks | classic kit layout (wiki position icons don't survive text extraction) |

## Mistakes found in the previous data (now fixed)

### Hero base stats

* **Highwayman damage was 8–16; official is 5–10.** The single largest
  error — and it inflated the exact class the composition search
  identified as most load-bearing. Also crit 6 → 5.
* Bounty Hunter damage 5–10 ✓ but several skill mods were wrong (below).
* Dodge values normalized to the official numbers via the /10 mapping.

### Hero skills — wrong numbers

| Skill | Was | Official (level 1) |
|---|---|---|
| Zealous Accusation | −50% dmg | −40% dmg, crit −4 |
| Battle Heal | 3–4 | 2–3 |
| Inspiring Cry | stress −1–2 | stress −5 (video) → −1 |
| Wicked Slice | +0% | **+15%** |
| Point Blank Shot | +30% | **+50%**, ACC 95 |
| Grapeshot Blast | −55% | −50%, crit −9 |
| Duelist's Advance | −30%, dodge buff | −20%, **riposte** (was missing) |
| Open Vein | −30% | −15%, ACC 95 |
| Noxious Blast | −75%, blight 3 | −80%, **blight 5**/rd |
| Plague Grenade | −80%, blight 3 | −90%, blight 4/rd |
| Incision | −25% | **±0%** |
| Battlefield Medicine | heal 2–3 | heal 1 + cure |
| Judgement | plain attack | −15% **+ self-heal 1–2** (was missing) |
| Divine Grace | 4–6 | 4–5 |
| Divine Comfort | 2–3 | 1–3 |
| Illumination | dodge −1 | dodge **−2**, 4 rds |
| If It Bleeds | −20% | −35% |
| Barbaric YAWP | plain stun | stun **110**, self −20% dmg, **3/battle** |
| Breakthrough | −60% | −50%, self-debuff |
| Adrenaline Rush | heal 2–3 | heal 1, **+20% dmg +1 ACC** buff |
| Abyssal Artillery | −50% | −33% |
| Weakening Curse | −25% dmg debuff | **−10% dmg and −10 PROT** debuffs |
| Vulnerability Hex | dodge −1 | dodge −2, ACC 95 |
| Collect Bounty | +90% vs mark | + crit 7 and **+15% vs humans** (missing) |
| Uppercut | −25%, knockback 1 | **−67%, knockback 2** |
| Come Hither | −70% | −80%, **marks the target** (missing) |
| Finish Him | +40% vs stunned | **+25%** vs stunned |
| Pick to the Face | +0%, vs-mark bonus | −15%, **armor piercing** (missing) |
| Thrown Dagger | −15% | −10%, **+25% vs marked, +20% vs blighted** (missing) |
| Flashing Daggers | −55% + bleed | −33%, no direct bleed |
| Poison Dart | −40%, blight 2×3 | −60%, **blight 2×4 rds** |
| Lunge | +10% | **+40%**, +20% vs blighted |
| Shadow Fade | dodge +2 | **+80% dmg 2 rds**, dodge +1, crit +4 |

### Missing content and mechanics (added)

* **Vestal's Hand of Light** — the class was missing its 7th skill.
* **Riposte** (Duelist's Advance): defender counters each hit taken while
  active, at −40% damage.
* **Armor piercing** (Pick to the Face): ignores PROT.
* **Vs-type bonuses**: +15% vs Unholy (Smite, Holy Lance, Mace Bash, Hand
  of Light), +15% vs Eldritch (Sacrificial Stab, Abyssal Artillery),
  +15% vs Human (Collect Bounty), +20% vs Blighted (Lunge, Thrown
  Dagger). Every enemy now carries its official family.
* **Per-battle limits**: Blinding Gas 3, Barbaric YAWP 3, Emboldening
  Vapours 2, Bulwark of Faith 1, Tracking Shot 1.
* "Take Aim" and "Hook and Slice" were renamed to their official
  counterparts (**Tracking Shot**, **Caltrops**) with official numbers.

### Enemies — replaced with official apprentice stat lines

| Enemy | Was (invented) | Official |
|---|---|---|
| Bone Rabble | 7 hp, ACC 75 | **8 hp, ACC 62.5/42.5**, spd 1 |
| Bone Soldier | 15 hp, prot 10 | **10 hp, prot 15**, dmg 3–8 |
| Bone Arbalist | 12 hp, crit 6 | **15 hp, crit 12%**, +25% vs marked |
| Bone Defender | 22 hp, prot 40 | **15 hp, prot 25**, stun+knockback skill |
| Cultist Brawler | 12 hp | **15 hp, crit 12%**, bleed + vs-mark rider |
| Cultist Acolyte | 10 hp, stress 1–2 | **13 hp, stress 15 (→2)**, Eldritch Pull |
| Brigand Cutthroat | 14 hp, dodge 1 | **12 hp, prot 15**, 3 real skills incl. Shank 4–8 |
| Brigand Fusilier | 11 hp, single shot | **12 hp, Blanket Fire hits the whole party** |
| Brigand Bloodletter | *does not exist* | replaced by **Rabid Gnasher** (official Weald bleeder) |
| Madman | 9 hp, dodge 2 | **14 hp, dodge 20 (→2), spd 9**, Doomsay/Accusation stress |
| Ghoul | 42 hp, prot 10 | **41 hp, prot 40, stun 70%**, Skull Toss stress+stun |
| Necromancer | 55 hp, bolt attacks | **105 hp, summons skeletons** every action (summons now implemented) |

## Consequences

Real stats at 1.0 scaling proved far harder than the invented ones (the
source game assumes stalling, provisions and trinkets, which the board
game's 4-round rooms deny). Global calibration is now `0.8 × HP` and
`0.8 × damage` (`ddsim/tuning.py`) — a single documented knob pair over
otherwise-official numbers, preserving every relative relationship
between enemies. The 14-strategy tournament and the full composition
search were re-run from scratch on the corrected data.

## Remaining approximations

* Horror (stress-over-time) is folded into one-time stress values.
* Stealth (Shadow Fade, Toxin Trickery) approximated as dodge.
* Necromancer's summon cap is 4 visible ranks (board-track limit).
* Wiki position icons are unreadable in text form, so launch/target ranks
  follow the game's standard kit layout rather than per-row extraction.
