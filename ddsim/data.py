"""Game content: hero classes, enemies, encounter tables.

All numeric stats are grounded in the official Darkest Dungeon wiki
(darkestdungeon.wiki.gg) — level-1 hero skills and apprentice-level
monsters (Ghoul: veteran, its lowest tier; Necromancer: apprentice boss).
The board game's monster stat cards are not publicly available, so the
source-material values the board game adapts are the best published
numbers; docs/ABILITY_AUDIT.md records the full sweep and every mapping.

Conversion to board-game dice scales (see docs/RULES_AUDIT.md):
* ACC%  -> d10 target number: round(ACC / 10), effective TN clamps to 1-9.
* Dodge -> integer points: round(dodge / 10).
* Stress -> 0-10 track: round(video value / 10), minimum 1.
* DOT / stun / debuff chances stay percentages (resisted rolls).
* Launch/target ranks use the classic layout (wiki position icons don't
  survive text extraction; ranks follow the game's standard kit design).

Skill kits are each hero's 7 level-1 skills (Vestal has 7 incl. Hand of
Light); strategies pick 3.
"""

from .models import Buff, Dot, EnemyType, HeroClass, Resists, Skill

# ---------------------------------------------------------------------------
# Hero classes
# ---------------------------------------------------------------------------

def _skills(*sk):
    return {s.name: s for s in sk}


CRUSADER = HeroClass(
    name="Crusader", hp=33, dodge=1, spd=1, dmg=(6, 12), crit=3,
    resists=Resists(stun=40, bleed=30, blight=30, debuff=30),
    skills=_skills(
        # ACC 85 -> 8, +0% dmg, +15% vs Unholy
        Skill("Smite", launch=(1, 2), targets=(1, 2), acc=8, dmg_mod=1.0,
              vs_family=("unholy", 0.15)),
        # ACC 85 -> 8, -40% dmg, -4% crit, hits two ranks
        Skill("Zealous Accusation", launch=(1, 2), targets=(1, 2), aoe=True, acc=8,
              dmg_mod=0.6, crit_mod=-4),
        # ACC 90 -> 9, -50% dmg, stun 100
        Skill("Stunning Blow", launch=(1, 2), targets=(1, 2), acc=9, dmg_mod=0.5,
              stun=100),
        # ACC 85 -> 8, +0% dmg, crit +6.5, +15% vs Unholy, advances 1
        Skill("Holy Lance", launch=(3, 4), targets=(2, 3), acc=8, dmg_mod=1.0,
              crit_mod=6.5, vs_family=("unholy", 0.15), self_move=-1),
        # heal 2-3
        Skill("Battle Heal", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4),
              target_type="ally", heal=(2, 3)),
        # heal 1, stress -5 (video) -> 1 point
        Skill("Inspiring Cry", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4),
              target_type="ally", stress_heal=(1, 1), heal=(1, 1)),
        # +20% PROT, marks self; once per battle
        Skill("Bulwark of Faith", launch=(1, 2), targets=(), target_type="self",
              self_buffs=(Buff("prot", 20, 3),), mark=3, limit=1),
    ),
)

HIGHWAYMAN = HeroClass(
    name="Highwayman", hp=23, dodge=1, spd=5, dmg=(5, 10), crit=5,
    resists=Resists(stun=40, bleed=30, blight=30, debuff=30),
    skills=_skills(
        # ACC 85 -> 8, +15% dmg
        Skill("Wicked Slice", launch=(1, 2), targets=(1, 2), acc=8, dmg_mod=1.15,
              crit_mod=5),
        # ACC 85 -> 8, -15% dmg, crit +7.5, +25% vs marked
        Skill("Pistol Shot", launch=(2, 3, 4), targets=(2, 3, 4), acc=8, dmg_mod=0.85,
              crit_mod=7.5, vs_marked=0.25),
        # ACC 95 -> 10, +50% dmg, knockback 1
        Skill("Point Blank Shot", launch=(1,), targets=(1,), acc=10, dmg_mod=1.5,
              crit_mod=5, target_move=1),
        # ACC 75 -> 8, -50% dmg, crit -9
        Skill("Grapeshot Blast", launch=(1, 2, 3), targets=(1, 2, 3), aoe=True, acc=8,
              dmg_mod=0.5, crit_mod=-9),
        # ACC 90 -> 9, -20% dmg, advances 1, riposte 3 rounds at -40% dmg
        Skill("Duelist's Advance", launch=(2, 3, 4), targets=(1, 2), acc=9, dmg_mod=0.8,
              crit_mod=5, self_move=-1, riposte=(3, 0.6)),
        # ACC 95 -> 10, -15% dmg, bleed 2/rd 3 rds
        Skill("Open Vein", launch=(1, 2), targets=(1, 2), acc=10, dmg_mod=0.85,
              dot=Dot("bleed", 100, 2, 3)),
        # ACC 95, -80% dmg; +6 ACC (+1 TN), +4% crit, +12% dmg; once per battle
        Skill("Tracking Shot", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), acc=10,
              dmg_mod=0.2, limit=1,
              self_buffs=(Buff("acc", 1, 4), Buff("crit", 4, 4),
                          Buff("dmg_mult", 0.12, 4))),
    ),
)

PLAGUE_DOCTOR = HeroClass(
    name="Plague Doctor", hp=22, dodge=0, spd=7, dmg=(4, 7), crit=2,
    resists=Resists(stun=40, bleed=30, blight=60, debuff=50),
    skills=_skills(
        # ACC 95 -> 10, -80% dmg, blight 5/rd 3 rds
        Skill("Noxious Blast", launch=(3, 4), targets=(1, 2), acc=10, dmg_mod=0.2,
              crit_mod=5, dot=Dot("blight", 100, 5, 3)),
        # ACC 95 -> 10, -90% dmg, blight 4/rd 3 rds, back ranks
        Skill("Plague Grenade", launch=(3, 4), targets=(3, 4), aoe=True, acc=10,
              dmg_mod=0.1, dot=Dot("blight", 100, 4, 3)),
        # stun 100, no damage; 3 uses per battle
        Skill("Blinding Gas", launch=(3, 4), targets=(3, 4), aoe=True, acc=10,
              stun=100, limit=3),
        # stun + shuffle, no damage
        Skill("Disorienting Blast", launch=(3, 4), targets=(1, 2, 3, 4), acc=10,
              stun=100, target_move=1),
        # ACC 85 -> 8, +0% dmg, bleed 2/rd 3 rds
        Skill("Incision", launch=(1, 2), targets=(1, 2), acc=8, dmg_mod=1.0,
              crit_mod=5, dot=Dot("bleed", 100, 2, 3)),
        # heal 1, cures dots
        Skill("Battlefield Medicine", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4),
              target_type="ally", heal=(1, 1), cure_dots=True),
        # +20% dmg (spd omitted: initiative is card-driven); 2 uses per battle
        Skill("Emboldening Vapours", launch=(3, 4), targets=(1, 2, 3, 4),
              target_type="ally", limit=2,
              target_buffs=(Buff("dmg_mult", 0.20, 3),)),
    ),
)

VESTAL = HeroClass(
    name="Vestal", hp=24, dodge=0, spd=4, dmg=(4, 8), crit=1,
    resists=Resists(stun=40, bleed=30, blight=30, debuff=30),
    skills=_skills(
        # heal 4-5, single ally
        Skill("Divine Grace", launch=(3, 4), targets=(1, 2, 3, 4), target_type="ally",
              heal=(4, 5)),
        # heal 1-3, whole party
        Skill("Divine Comfort", launch=(3, 4), targets=(1, 2, 3, 4), target_type="party",
              heal=(1, 3)),
        # ACC 85 -> 8, -15% dmg, self-heal 1-2
        Skill("Judgement", launch=(2, 3, 4), targets=(1, 2, 3, 4), acc=8, dmg_mod=0.85,
              crit_mod=5, self_heal=(1, 2)),
        # ACC 90 -> 9, -50% dmg, stun 100
        Skill("Dazzling Light", launch=(1, 2, 3, 4), targets=(1, 2, 3), acc=9,
              dmg_mod=0.5, crit_mod=5, stun=100),
        # ACC 85 -> 8, +0% dmg, +15% vs Unholy
        Skill("Mace Bash", launch=(1, 2), targets=(1, 2), acc=8, dmg_mod=1.0,
              vs_family=("unholy", 0.15)),
        # ACC 90 -> 9, -50% dmg, -20 dodge (-2) for 4 rounds
        Skill("Illumination", launch=(2, 3, 4), targets=(1, 2, 3, 4), acc=9,
              dmg_mod=0.5, target_debuffs=(Buff("dodge", -2, 4),), debuff_chance=100),
        # ACC 85 -> 8, +25% dmg, +15% vs Unholy, +6 ACC self (+1 TN)
        Skill("Hand of Light", launch=(1, 2), targets=(1, 2), acc=8, dmg_mod=1.25,
              crit_mod=1, vs_family=("unholy", 0.15),
              self_buffs=(Buff("acc", 1, 4),)),
    ),
)

HELLION = HeroClass(
    name="Hellion", hp=26, dodge=1, spd=4, dmg=(6, 12), crit=5,
    resists=Resists(stun=40, bleed=40, blight=30, debuff=30),
    skills=_skills(
        # ACC 85 -> 8, +0% dmg, crit +4
        Skill("Wicked Hack", launch=(1, 2), targets=(1, 2), acc=8, dmg_mod=1.0,
              crit_mod=4),
        # ACC 85 -> 8, +0% dmg, hits rank 4 only
        Skill("Iron Swan", launch=(1,), targets=(4,), acc=8, dmg_mod=1.0, crit_mod=5),
        # stun 110, no damage, self -20% dmg 3 rds; 3 uses per battle
        Skill("Barbaric YAWP", launch=(1, 2), targets=(1, 2), aoe=True, acc=10,
              stun=110, limit=3, self_buffs=(Buff("dmg_mult", -0.20, 3),)),
        # ACC 85 -> 8, -35% dmg, bleed 2/rd 3 rds
        Skill("If It Bleeds", launch=(1, 2), targets=(1, 2), acc=8, dmg_mod=0.65,
              dot=Dot("bleed", 100, 2, 3)),
        # ACC 85 -> 8, -50% dmg, crit -1, charges to the front, self -10% dmg
        Skill("Breakthrough", launch=(3, 4), targets=(1, 2, 3), aoe=True, acc=8,
              dmg_mod=0.5, crit_mod=-1, self_move=-2,
              self_buffs=(Buff("dmg_mult", -0.10, 3),)),
        # heal 1, cure dots, +5 ACC (+1) and +20% dmg 4 rds
        Skill("Adrenaline Rush", launch=(1, 2, 3, 4), targets=(), target_type="self",
              heal=(1, 1), cure_dots=True,
              self_buffs=(Buff("acc", 1, 4), Buff("dmg_mult", 0.20, 4))),
        # heavy bleed finisher (not in the fetched table; kept at kit-consistent
        # values: -50% dmg, bleed 4/rd 3 rds)
        Skill("Bleed Out", launch=(1,), targets=(1,), acc=8, dmg_mod=0.5,
              dot=Dot("bleed", 100, 4, 3)),
    ),
)

OCCULTIST = HeroClass(
    name="Occultist", hp=19, dodge=1, spd=6, dmg=(4, 7), crit=6,
    resists=Resists(stun=40, bleed=30, blight=30, debuff=60),
    skills=_skills(
        # ACC 80 -> 8, +0% dmg, +15% vs Eldritch
        Skill("Sacrificial Stab", launch=(1, 2), targets=(1, 2), acc=8, dmg_mod=1.0,
              vs_family=("eldritch", 0.15)),
        # ACC 85 -> 8, -33% dmg, +15% vs Eldritch, back ranks
        Skill("Abyssal Artillery", launch=(3, 4), targets=(3, 4), aoe=True, acc=8,
              dmg_mod=0.67, vs_family=("eldritch", 0.15)),
        # ACC 95 -> 10, -75% dmg, -10% dmg and -10 PROT debuffs
        Skill("Weakening Curse", launch=(2, 3, 4), targets=(1, 2, 3, 4), acc=10,
              dmg_mod=0.25, crit_mod=5,
              target_debuffs=(Buff("dmg_mult", -0.10, 3), Buff("prot", -10, 3)),
              debuff_chance=100),
        # heal 0-13, 60% bleed 1/rd 3 rds on the target
        Skill("Wyrd Reconstruction", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4),
              target_type="ally", heal=(0, 13), dot=Dot("bleed", 60, 1, 3)),
        # ACC 95 -> 10, -90% dmg, mark 3 rds, -15 dodge (-2)
        Skill("Vulnerability Hex", launch=(2, 3, 4), targets=(1, 2, 3, 4), acc=10,
              dmg_mod=0.1, crit_mod=5, mark=3,
              target_debuffs=(Buff("dodge", -2, 3),), debuff_chance=100),
        # ACC 90 -> 9, -50% dmg, pull 2
        Skill("Daemon's Pull", launch=(3, 4), targets=(3, 4), acc=9, dmg_mod=0.5,
              crit_mod=5, target_move=-2),
        # ACC 90 -> 9, -50% dmg, crit +9, stun 110
        Skill("Hands from the Abyss", launch=(1, 2), targets=(1, 2), acc=9,
              dmg_mod=0.5, crit_mod=9, stun=110),
    ),
)

BOUNTY_HUNTER = HeroClass(
    name="Bounty Hunter", hp=25, dodge=1, spd=5, dmg=(5, 10), crit=4,
    resists=Resists(stun=50, bleed=30, blight=30, debuff=30),
    skills=_skills(
        # ACC 85 -> 8, +0% dmg, crit +7, +90% vs marked, +15% vs humans
        Skill("Collect Bounty", launch=(1, 2), targets=(1, 2), acc=8, dmg_mod=1.0,
              crit_mod=7, vs_marked=0.9, vs_family=("human", 0.15)),
        # ACC 100 -> 10, no damage, mark 3 rds, -10 PROT
        Skill("Mark for Death", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), acc=10,
              mark=3, target_debuffs=(Buff("prot", -10, 3),), debuff_chance=100),
        # ACC 90 -> 9, -80% dmg, mark 2 rds, pull 2
        Skill("Come Hither", launch=(1, 2, 3), targets=(3, 4), acc=9, dmg_mod=0.2,
              mark=2, target_move=-2),
        # ACC 90 -> 9, -67% dmg, stun, knockback 2
        Skill("Uppercut", launch=(1, 2), targets=(1, 2), acc=9, dmg_mod=0.33,
              stun=100, target_move=2),
        # ACC 95 -> 10, no damage, stun, shuffle
        Skill("Flashbang", launch=(2, 3, 4), targets=(2, 3, 4), acc=10, stun=100,
              target_move=1),
        # ACC 85 -> 8, +0% dmg, +25% vs stunned
        Skill("Finish Him", launch=(1, 2), targets=(1, 2), acc=8, dmg_mod=1.0,
              crit_mod=5, vs_stunned=0.25),
        # ACC 90 -> 9, -95% dmg, bleed 2/rd 3 rds
        Skill("Caltrops", launch=(1, 2), targets=(2, 3), acc=9, dmg_mod=0.05,
              crit_mod=5, dot=Dot("bleed", 100, 2, 3)),
    ),
)

GRAVE_ROBBER = HeroClass(
    name="Grave Robber", hp=20, dodge=1, spd=8, dmg=(4, 8), crit=6,
    resists=Resists(stun=40, bleed=30, blight=50, debuff=30),
    skills=_skills(
        # ACC 90 -> 9, -15% dmg, armor piercing
        Skill("Pick to the Face", launch=(1, 2), targets=(1, 2), acc=9, dmg_mod=0.85,
              crit_mod=1, ignore_prot=True),
        # ACC 90 -> 9, -10% dmg, crit +8, +25% vs marked, +20% vs blighted
        Skill("Thrown Dagger", launch=(3, 4), targets=(2, 3, 4), acc=9, dmg_mod=0.9,
              crit_mod=8, vs_marked=0.25, vs_blighted=0.2),
        # ACC 90 -> 9, -33% dmg, crit -5, two ranks
        Skill("Flashing Daggers", launch=(2, 3), targets=(2, 3), aoe=True, acc=9,
              dmg_mod=0.67, crit_mod=-5),
        # ACC 95 -> 10, -60% dmg, crit +7.5, blight 2/rd 4 rds
        Skill("Poison Dart", launch=(2, 3, 4), targets=(2, 3, 4), acc=10, dmg_mod=0.4,
              crit_mod=7.5, dot=Dot("blight", 100, 2, 4)),
        # cure dots, +10 dodge (+1) (video also grants stealth — approximated)
        Skill("Toxin Trickery", launch=(1, 2, 3, 4), targets=(), target_type="self",
              cure_dots=True, self_buffs=(Buff("dodge", 1, 3),)),
        # ACC 95 -> 10, +40% dmg, crit +8, +20% vs blighted, charges forward 2
        Skill("Lunge", launch=(3, 4), targets=(1, 2), acc=10, dmg_mod=1.4, crit_mod=8,
              vs_blighted=0.2, self_move=-2),
        # move back 2; +80% dmg and +4% crit 2 rds, +10 dodge (+1) 4 rds
        Skill("Shadow Fade", launch=(1, 2, 3), targets=(), target_type="self",
              self_move=2, self_buffs=(Buff("dmg_mult", 0.80, 2), Buff("crit", 4, 2),
                                       Buff("dodge", 1, 4))),
    ),
)

HERO_CLASSES = {
    c.name: c
    for c in (
        CRUSADER, HIGHWAYMAN, PLAGUE_DOCTOR, VESTAL,
        HELLION, OCCULTIST, BOUNTY_HUNTER, GRAVE_ROBBER,
    )
}

# ---------------------------------------------------------------------------
# Enemies — apprentice-level stats from the official wiki
# ---------------------------------------------------------------------------

BONE_RABBLE = EnemyType(
    name="Bone Rabble", hp=8, dodge=0, prot=0, spd=1, crit=2,
    resists=Resists(stun=10, bleed=200, blight=10, debuff=15, move=10),
    skills=(
        Skill("Bump in the Night", launch=(1, 2), targets=(1, 2), acc=6,
              dmg_range=(2, 5), crit_mod=2),
        Skill("Tic-Toc", launch=(2, 3), targets=(1, 2), acc=4, dmg_range=(2, 5),
              self_move=-1),
    ),
    weights=(0.75, 0.25),
    family="unholy",
)

BONE_SOLDIER = EnemyType(
    name="Bone Soldier", hp=10, dodge=0, prot=15, spd=2, crit=6,
    resists=Resists(stun=25, bleed=200, blight=10, debuff=15, move=20),
    skills=(
        Skill("Graveyard Slash", launch=(1, 2), targets=(1, 2), acc=8,
              dmg_range=(3, 8), crit_mod=6),
        Skill("Graveyard Stumble", launch=(2, 3), targets=(1, 2), acc=4,
              dmg_range=(2, 5), self_move=-1),
    ),
    weights=(0.8, 0.2),
    family="unholy",
)

BONE_ARBALIST = EnemyType(
    name="Bone Arbalist", hp=15, dodge=0, prot=0, spd=5, crit=12,
    resists=Resists(stun=10, bleed=200, blight=10, debuff=15, move=25),
    skills=(
        Skill("Quarrel", launch=(2, 3, 4), targets=(2, 3, 4), acc=8,
              dmg_range=(3, 7), crit_mod=12, vs_marked=0.25),
        Skill("Bayonet Jab", launch=(1, 2), targets=(1, 2), acc=7,
              dmg_range=(2, 4), crit_mod=2, self_move=1),
    ),
    weights=(0.85, 0.15),
    prefer="back", tags=("ranged",), family="unholy",
)

BONE_DEFENDER = EnemyType(
    name="Bone Defender", hp=15, dodge=0, prot=25, spd=0, crit=6,
    resists=Resists(stun=25, bleed=200, blight=10, debuff=15, move=50),
    skills=(
        Skill("Axeblade", launch=(1, 2), targets=(1, 2), acc=7, dmg_range=(3, 5),
              crit_mod=6),
        Skill("Dead Weight", launch=(1, 2), targets=(1, 2), acc=8, dmg_range=(2, 4),
              crit_mod=6, stun=100, target_move=1),
        Skill("Clumsy Axeblade", launch=(2, 3), targets=(1, 2), acc=4,
              dmg_range=(2, 4), self_move=-1),
    ),
    weights=(0.5, 0.3, 0.2),
    tags=("tank",), family="unholy",
)

CULTIST_BRAWLER = EnemyType(
    name="Cultist Brawler", hp=15, dodge=0, prot=0, spd=5, crit=12,
    resists=Resists(stun=25, bleed=20, blight=20, debuff=15, move=25),
    skills=(
        Skill("Rend for the Old Gods", launch=(1, 2), targets=(1, 2), acc=7,
              dmg_range=(2, 4), crit_mod=12, vs_marked=0.5,
              dot=Dot("bleed", 100, 1, 3), self_move=-1),
        Skill("Stumbling Scratch", launch=(2, 3), targets=(1, 2), acc=4,
              dmg_range=(2, 4), self_move=-1),
    ),
    weights=(0.8, 0.2),
    family="eldritch",
)

CULTIST_ACOLYTE = EnemyType(
    name="Cultist Acolyte", hp=13, dodge=1, prot=0, spd=7, crit=4,
    resists=Resists(stun=25, bleed=20, blight=20, debuff=40, move=10),
    skills=(
        # video stress +15 -> 2 points on the 0-10 track
        Skill("Stressful Incantation", launch=(2, 3, 4), targets=(1, 2, 3, 4), acc=8,
              dmg_range=(1, 1), stress_dmg=(2, 2)),
        Skill("Eldritch Pull", launch=(1, 2, 3), targets=(1, 2, 3, 4), acc=8,
              dmg_range=(1, 1), crit_mod=6, target_move=-2),
    ),
    weights=(0.85, 0.15),
    prefer="stress", tags=("stress",), family="eldritch",
)

BRIGAND_CUTTHROAT = EnemyType(
    name="Brigand Cutthroat", hp=12, dodge=0, prot=15, spd=3, crit=12,
    resists=Resists(stun=25, bleed=20, blight=20, debuff=15, move=25),
    skills=(
        Skill("Slice and Dice", launch=(1, 2), targets=(1, 2), acc=7,
              dmg_range=(3, 5), crit_mod=12),
        Skill("Shank", launch=(1, 2), targets=(1, 2), acc=7, dmg_range=(4, 8),
              crit_mod=6, dot=Dot("bleed", 100, 1, 3)),
        Skill("Uppercut Slice", launch=(1, 2), targets=(1, 2), acc=7,
              dmg_range=(2, 4), crit_mod=6, target_move=1),
    ),
    weights=(0.4, 0.4, 0.2),
    family="human",
)

BRIGAND_FUSILIER = EnemyType(
    name="Brigand Fusilier", hp=12, dodge=1, prot=0, spd=6, crit=5,
    resists=Resists(stun=25, bleed=20, blight=20, debuff=15, move=25),
    skills=(
        Skill("Blanket Fire", launch=(2, 3, 4), targets=(1, 2, 3, 4), aoe=True,
              acc=7, dmg_range=(1, 3)),
        Skill("Rushed Shot", launch=(1,), targets=(1, 2), acc=6, dmg_range=(2, 4),
              crit_mod=6, self_move=1),
    ),
    weights=(0.85, 0.15),
    prefer="back", tags=("ranged",), family="human",
)

RABID_GNASHER = EnemyType(
    name="Rabid Gnasher", hp=10, dodge=2, prot=0, spd=8, crit=16,
    resists=Resists(stun=10, bleed=20, blight=60, debuff=10, move=10),
    skills=(
        Skill("Rabid Rush", launch=(1, 2, 3, 4), targets=(1, 2, 3), acc=8,
              dmg_range=(1, 3), crit_mod=16, dot=Dot("bleed", 100, 1, 3),
              self_move=-3),
    ),
    weights=(1.0,),
    family="beast",
)

MADMAN = EnemyType(
    name="Madman", hp=14, dodge=2, prot=0, spd=9, crit=3,
    resists=Resists(stun=10, bleed=10, blight=10, debuff=15, move=10),
    skills=(
        # video stress +7 AOE -> 1 point
        Skill("Doomsay", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), aoe=True, acc=10,
              stress_dmg=(1, 1)),
        # dmg 1 + horror (12 stress over 4 rds) -> 1-2 points
        Skill("Accusation", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), acc=10,
              dmg_range=(1, 1), stress_dmg=(1, 2)),
    ),
    weights=(0.5, 0.5),
    prefer="stress", tags=("stress",), family="human",
)

GHOUL = EnemyType(
    name="Ghoul", hp=41, dodge=1, prot=40, spd=6, crit=16,
    resists=Resists(stun=70, bleed=40, blight=40, debuff=40, move=82),
    skills=(
        Skill("Rend", launch=(1, 2), targets=(1, 2), acc=9, dmg_range=(5, 11),
              crit_mod=16, dot=Dot("bleed", 100, 3, 3)),
        # video stress +15 -> 2, with a stun rider
        Skill("Skull Toss", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), acc=9,
              dmg_range=(5, 11), crit_mod=12, stress_dmg=(2, 2), stun=100),
        # Howl: horror -> 1-2 stress, all ranks
        Skill("Terrifying Howl", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), aoe=True,
              acc=9, stress_dmg=(1, 2)),
    ),
    weights=(0.45, 0.3, 0.25),
    tags=("boss", "stress"), family="unholy", is_boss=True,
)

NECROMANCER = EnemyType(
    name="Necromancer", hp=105, dodge=0, prot=0, spd=8, crit=6,
    resists=Resists(stun=75, bleed=200, blight=20, debuff=40, move=25),
    skills=(
        Skill("The Flesh is Willing", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4),
              acc=10, dmg_range=(4, 8), crit_mod=6, summon="Bone Soldier",
              self_move=1),
        Skill("The Clawing Dead", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4),
              acc=10, dmg_range=(3, 5), crit_mod=6, summon="Bone Rabble",
              self_move=1),
        # video stress +15 -> 2
        Skill("Six Feet Under", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), acc=10,
              stress_dmg=(2, 2), summon="Bone Rabble", self_move=1),
    ),
    weights=(0.4, 0.35, 0.25),
    prefer="back", tags=("boss",), family="unholy", is_boss=True,
)

ENEMY_TYPES = {
    e.name: e
    for e in (
        BONE_RABBLE, BONE_SOLDIER, BONE_ARBALIST, BONE_DEFENDER,
        CULTIST_BRAWLER, CULTIST_ACOLYTE, BRIGAND_CUTTHROAT, BRIGAND_FUSILIER,
        RABID_GNASHER, MADMAN, GHOUL, NECROMANCER,
    )
}

# ---------------------------------------------------------------------------
# Encounter tables: a dungeon run = one draw from each slot, front rank first.
# ---------------------------------------------------------------------------

ENCOUNTER_TABLE = [
    # Slot 1 — warm-up
    [
        ["Bone Rabble", "Bone Rabble", "Bone Rabble", "Cultist Acolyte"],
        ["Cultist Brawler", "Cultist Brawler", "Cultist Acolyte"],
        ["Bone Rabble", "Bone Soldier", "Bone Rabble"],
        ["Brigand Cutthroat", "Rabid Gnasher", "Madman"],
    ],
    # Slot 2 — medium
    [
        ["Bone Soldier", "Cultist Brawler", "Cultist Acolyte", "Cultist Acolyte"],
        ["Brigand Cutthroat", "Brigand Fusilier", "Madman"],
        ["Bone Soldier", "Bone Arbalist", "Cultist Acolyte"],
        ["Cultist Brawler", "Bone Soldier", "Brigand Fusilier"],
    ],
    # Slot 3 — hard
    [
        ["Bone Soldier", "Bone Soldier", "Bone Arbalist", "Cultist Acolyte"],
        ["Brigand Cutthroat", "Rabid Gnasher", "Brigand Fusilier", "Madman"],
        ["Bone Defender", "Bone Soldier", "Bone Arbalist"],
        ["Rabid Gnasher", "Cultist Brawler", "Bone Arbalist", "Madman"],
    ],
    # Slot 4 — climax
    [
        ["Ghoul", "Cultist Acolyte", "Bone Arbalist"],
        ["Necromancer", "Bone Soldier"],
        ["Ghoul", "Rabid Gnasher", "Brigand Fusilier"],
    ],
]
