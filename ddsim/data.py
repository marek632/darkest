"""Game content: hero classes, enemies, encounter tables.

Numbers approximate the source material (apprentice-level Darkest Dungeon,
which the board game adapts); deviations are documented in docs/DESIGN.md.
"""

from .models import Buff, Dot, EnemyType, HeroClass, Resists, Skill

# ---------------------------------------------------------------------------
# Hero classes
# ---------------------------------------------------------------------------

def _skills(*sk):
    return {s.name: s for s in sk}


CRUSADER = HeroClass(
    name="Crusader", hp=33, dodge=5, spd=1, dmg=(6, 12), crit=3,
    resists=Resists(stun=40, bleed=30, blight=30, debuff=30),
    skills=_skills(
        Skill("Smite", launch=(1, 2), targets=(1, 2), acc=85, dmg_mod=1.0, crit_mod=3),
        Skill("Zealous Accusation", launch=(1, 2), targets=(1, 2), aoe=True, acc=85, dmg_mod=0.5),
        Skill("Stunning Blow", launch=(1, 2), targets=(1, 2), acc=90, dmg_mod=0.5, stun=100),
        Skill("Holy Lance", launch=(3, 4), targets=(2, 3), acc=85, dmg_mod=1.15, crit_mod=6,
              self_move=-1),
        Skill("Battle Heal", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), target_type="ally",
              heal=(3, 4)),
        Skill("Inspiring Cry", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), target_type="ally",
              stress_heal=(5, 8), heal=(1, 1)),
        Skill("Bulwark of Faith", launch=(1, 2), targets=(), target_type="self",
              self_buffs=(Buff("prot", 25, 3), Buff("dodge", -5, 3)), mark=3),
    ),
)

HIGHWAYMAN = HeroClass(
    name="Highwayman", hp=23, dodge=10, spd=5, dmg=(8, 16), crit=6,
    resists=Resists(stun=40, bleed=30, blight=30, debuff=30),
    skills=_skills(
        Skill("Wicked Slice", launch=(1, 2), targets=(1, 2), acc=85, dmg_mod=1.0, crit_mod=5),
        Skill("Pistol Shot", launch=(2, 3, 4), targets=(2, 3, 4), acc=85, dmg_mod=0.85,
              crit_mod=7),
        Skill("Point Blank Shot", launch=(1,), targets=(1,), acc=85, dmg_mod=1.3,
              target_move=1, self_move=1),
        Skill("Grapeshot Blast", launch=(1, 2, 3), targets=(1, 2, 3), aoe=True, acc=80,
              dmg_mod=0.45),
        Skill("Duelist's Advance", launch=(2, 3, 4), targets=(1, 2), acc=85, dmg_mod=0.7,
              self_move=-1, self_buffs=(Buff("dodge", 10, 2),)),
        Skill("Open Vein", launch=(1, 2), targets=(1, 2), acc=85, dmg_mod=0.7,
              dot=Dot("bleed", 90, 2, 3)),
        Skill("Take Aim", launch=(1, 2, 3, 4), targets=(), target_type="self",
              self_buffs=(Buff("acc", 10, 3), Buff("crit", 5, 3))),
    ),
)

PLAGUE_DOCTOR = HeroClass(
    name="Plague Doctor", hp=22, dodge=0, spd=7, dmg=(4, 7), crit=2,
    resists=Resists(stun=40, bleed=30, blight=60, debuff=50),
    skills=_skills(
        Skill("Noxious Blast", launch=(3, 4), targets=(1, 2), acc=85, dmg_mod=0.25,
              dot=Dot("blight", 90, 3, 3)),
        Skill("Plague Grenade", launch=(3, 4), targets=(3, 4), aoe=True, acc=85, dmg_mod=0.2,
              dot=Dot("blight", 80, 3, 3)),
        Skill("Blinding Gas", launch=(3, 4), targets=(3, 4), aoe=True, acc=90, stun=90),
        Skill("Disorienting Blast", launch=(3, 4), targets=(1, 2, 3, 4), acc=90, stun=80,
              target_move=1),
        Skill("Incision", launch=(1, 2), targets=(1, 2), acc=85, dmg_mod=0.75,
              dot=Dot("bleed", 80, 2, 3)),
        Skill("Battlefield Medicine", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4),
              target_type="ally", heal=(2, 3), cure_dots=True),
        Skill("Emboldening Vapours", launch=(3, 4), targets=(1, 2, 3, 4), target_type="ally",
              target_buffs=(Buff("dmg_mult", 0.20, 3), Buff("spd", 2, 3))),
    ),
)

VESTAL = HeroClass(
    name="Vestal", hp=24, dodge=0, spd=4, dmg=(4, 8), crit=1,
    resists=Resists(stun=40, bleed=30, blight=30, debuff=30),
    skills=_skills(
        Skill("Divine Grace", launch=(3, 4), targets=(1, 2, 3, 4), target_type="ally",
              heal=(4, 6)),
        Skill("Divine Comfort", launch=(3, 4), targets=(1, 2, 3, 4), target_type="party",
              heal=(2, 3)),
        Skill("Judgement", launch=(2, 3, 4), targets=(1, 2, 3, 4), acc=85, dmg_mod=0.85),
        Skill("Dazzling Light", launch=(1, 2, 3, 4), targets=(1, 2, 3), acc=90, dmg_mod=0.4,
              stun=90),
        Skill("Mace Bash", launch=(1, 2), targets=(1, 2), acc=85, dmg_mod=1.0),
        Skill("Illumination", launch=(2, 3, 4), targets=(1, 2, 3, 4), acc=90, dmg_mod=0.5,
              target_debuffs=(Buff("dodge", -10, 3),), debuff_chance=90),
    ),
)

HELLION = HeroClass(
    name="Hellion", hp=26, dodge=10, spd=4, dmg=(6, 12), crit=5,
    resists=Resists(stun=40, bleed=40, blight=30, debuff=30),
    skills=_skills(
        Skill("Wicked Hack", launch=(1, 2), targets=(1, 2), acc=85, dmg_mod=1.0, crit_mod=5),
        Skill("Iron Swan", launch=(1,), targets=(4,), acc=85, dmg_mod=1.0, crit_mod=5),
        Skill("Barbaric YAWP", launch=(1, 2), targets=(1, 2), aoe=True, stun=90),
        Skill("If It Bleeds", launch=(1, 2), targets=(1, 2), acc=85, dmg_mod=0.8,
              dot=Dot("bleed", 90, 2, 3)),
        Skill("Breakthrough", launch=(3, 4), targets=(1, 2, 3), aoe=True, acc=80, dmg_mod=0.4,
              self_move=-2),
        Skill("Adrenaline Rush", launch=(1, 2, 3, 4), targets=(), target_type="self",
              heal=(2, 3), cure_dots=True, self_buffs=(Buff("dmg_mult", 0.10, 3),)),
        Skill("Bleed Out", launch=(1,), targets=(1,), acc=85, dmg_mod=1.2,
              dot=Dot("bleed", 100, 3, 3)),
    ),
)

OCCULTIST = HeroClass(
    name="Occultist", hp=19, dodge=10, spd=6, dmg=(4, 7), crit=6,
    resists=Resists(stun=40, bleed=30, blight=30, debuff=60),
    skills=_skills(
        Skill("Sacrificial Stab", launch=(1, 2), targets=(1, 2), acc=85, dmg_mod=0.9,
              crit_mod=5),
        Skill("Abyssal Artillery", launch=(3, 4), targets=(3, 4), aoe=True, acc=85,
              dmg_mod=0.5),
        Skill("Weakening Curse", launch=(2, 3, 4), targets=(1, 2, 3, 4), acc=95, dmg_mod=0.2,
              target_debuffs=(Buff("dmg_mult", -0.25, 3),), debuff_chance=100),
        Skill("Wyrd Reconstruction", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4),
              target_type="ally", heal=(0, 12), dot=Dot("bleed", 25, 1, 3)),
        Skill("Vulnerability Hex", launch=(2, 3, 4), targets=(1, 2, 3, 4), acc=95, dmg_mod=0.2,
              mark=3, target_debuffs=(Buff("dodge", -10, 3),), debuff_chance=90),
        Skill("Daemon's Pull", launch=(3, 4), targets=(3, 4), acc=90, dmg_mod=0.5,
              target_move=-2),
        Skill("Hands from the Abyss", launch=(1, 2), targets=(1, 2), acc=90, dmg_mod=0.3,
              stun=90),
    ),
)

BOUNTY_HUNTER = HeroClass(
    name="Bounty Hunter", hp=25, dodge=5, spd=5, dmg=(5, 10), crit=4,
    resists=Resists(stun=50, bleed=30, blight=30, debuff=30),
    skills=_skills(
        Skill("Collect Bounty", launch=(1, 2), targets=(1, 2), acc=85, dmg_mod=1.0,
              vs_marked=0.9),
        Skill("Mark for Death", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), acc=100, mark=3,
              target_debuffs=(Buff("prot", -10, 3),), debuff_chance=100),
        Skill("Come Hither", launch=(1, 2, 3), targets=(3, 4), acc=90, dmg_mod=0.3,
              target_move=-2),
        Skill("Uppercut", launch=(1, 2), targets=(1, 2), acc=85, dmg_mod=0.75, stun=80,
              target_move=1),
        Skill("Flashbang", launch=(2, 3, 4), targets=(2, 3, 4), acc=90, stun=90,
              target_move=1),
        Skill("Finish Him", launch=(1, 2), targets=(1, 2), acc=90, dmg_mod=1.0,
              vs_stunned=0.4),
        Skill("Hook and Slice", launch=(1, 2), targets=(2, 3), acc=85, dmg_mod=0.9,
              dot=Dot("bleed", 66, 2, 3)),
    ),
)

GRAVE_ROBBER = HeroClass(
    name="Grave Robber", hp=20, dodge=10, spd=8, dmg=(4, 8), crit=6,
    resists=Resists(stun=40, bleed=30, blight=50, debuff=30),
    skills=_skills(
        Skill("Pick to the Face", launch=(1, 2), targets=(1, 2), acc=85, dmg_mod=1.0,
              vs_marked=0.4),
        Skill("Thrown Dagger", launch=(3, 4), targets=(2, 3, 4), acc=85, dmg_mod=0.85,
              crit_mod=6),
        Skill("Flashing Daggers", launch=(2, 3), targets=(2, 3), aoe=True, acc=80,
              dmg_mod=0.45, dot=Dot("bleed", 60, 1, 3)),
        Skill("Poison Dart", launch=(2, 3, 4), targets=(2, 3, 4), acc=85, dmg_mod=0.6,
              dot=Dot("blight", 90, 2, 3)),
        Skill("Toxin Trickery", launch=(1, 2, 3, 4), targets=(), target_type="self",
              cure_dots=True, self_buffs=(Buff("dodge", 10, 3), Buff("spd", 2, 3))),
        Skill("Lunge", launch=(3, 4), targets=(1, 2), acc=85, dmg_mod=1.1, crit_mod=6,
              self_move=-2),
        Skill("Shadow Fade", launch=(1, 2, 3), targets=(), target_type="self", self_move=2,
              self_buffs=(Buff("dodge", 20, 2), Buff("crit", 4, 2))),
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
# Enemies
# ---------------------------------------------------------------------------

# Skeletons: immune to bleed, weak to blight-ish (normal blight resist).
_SKELETON_RES = Resists(stun=25, bleed=200, blight=20, debuff=15, move=25)
_HUMAN_RES = Resists(stun=25, bleed=20, blight=20, debuff=15, move=25)

BONE_RABBLE = EnemyType(
    name="Bone Rabble", hp=7, dodge=5, prot=0, spd=4, crit=2, resists=_SKELETON_RES,
    skills=(
        Skill("Gravelly Slash", launch=(1, 2), targets=(1, 2), acc=75, dmg_range=(2, 4)),
    ),
    weights=(1.0,),
)

BONE_SOLDIER = EnemyType(
    name="Bone Soldier", hp=15, dodge=8, prot=10, spd=3, crit=4, resists=_SKELETON_RES,
    skills=(
        Skill("Wicked Cut", launch=(1, 2), targets=(1, 2), acc=80, dmg_range=(4, 7)),
        Skill("Bone Rush", launch=(2, 3), targets=(1, 2), acc=75, dmg_range=(3, 6),
              self_move=-1),
    ),
    weights=(0.7, 0.3),
)

BONE_ARBALIST = EnemyType(
    name="Bone Arbalist", hp=12, dodge=5, prot=0, spd=5, crit=6, resists=_SKELETON_RES,
    skills=(
        Skill("Sniper Shot", launch=(2, 3, 4), targets=(2, 3, 4), acc=85, dmg_range=(5, 9)),
        Skill("Point Blank", launch=(1,), targets=(1,), acc=75, dmg_range=(3, 6),
              self_move=1),
    ),
    weights=(0.85, 0.15),
    prefer="back", tags=("ranged",),
)

BONE_DEFENDER = EnemyType(
    name="Bone Defender", hp=22, dodge=10, prot=40, spd=2, crit=2, resists=_SKELETON_RES,
    skills=(
        Skill("Shield Bash", launch=(1, 2), targets=(1, 2), acc=80, dmg_range=(3, 5),
              stun=60),
    ),
    weights=(1.0,),
    tags=("tank",),
)

CULTIST_BRAWLER = EnemyType(
    name="Cultist Brawler", hp=12, dodge=8, prot=0, spd=4, crit=4, resists=_HUMAN_RES,
    skills=(
        Skill("Fervent Slash", launch=(1, 2), targets=(1, 2), acc=80, dmg_range=(3, 6)),
        Skill("Rushed Slice", launch=(2, 3), targets=(1, 2), acc=75, dmg_range=(2, 5),
              self_move=-1),
    ),
    weights=(0.8, 0.2),
)

CULTIST_ACOLYTE = EnemyType(
    name="Cultist Acolyte", hp=10, dodge=12, prot=0, spd=6, crit=4, resists=_HUMAN_RES,
    skills=(
        Skill("Stressful Incantation", launch=(2, 3, 4), targets=(1, 2, 3, 4), acc=90,
              stress_dmg=(8, 12)),
        Skill("Sacrificial Dagger", launch=(1,), targets=(1, 2), acc=75, dmg_range=(2, 4)),
    ),
    weights=(0.9, 0.1),
    prefer="stress", tags=("stress",),
)

BRIGAND_CUTTHROAT = EnemyType(
    name="Brigand Cutthroat", hp=14, dodge=12, prot=0, spd=6, crit=6, resists=_HUMAN_RES,
    skills=(
        Skill("Slice and Dice", launch=(1, 2), targets=(1, 2), acc=82, dmg_range=(4, 7),
              dot=Dot("bleed", 50, 2, 2)),
        Skill("Uncanny Slash", launch=(2, 3), targets=(1, 2), acc=78, dmg_range=(3, 6),
              self_move=-1),
    ),
    weights=(0.8, 0.2),
)

BRIGAND_FUSILIER = EnemyType(
    name="Brigand Fusilier", hp=11, dodge=8, prot=0, spd=4, crit=5, resists=_HUMAN_RES,
    skills=(
        Skill("Aimed Shot", launch=(2, 3, 4), targets=(2, 3, 4), acc=85, dmg_range=(4, 8)),
        Skill("Rebuke", launch=(1,), targets=(1,), acc=75, dmg_range=(2, 5), self_move=1),
    ),
    weights=(0.85, 0.15),
    prefer="back", tags=("ranged",),
)

BRIGAND_BLOODLETTER = EnemyType(
    name="Brigand Bloodletter", hp=14, dodge=8, prot=0, spd=5, crit=5, resists=_HUMAN_RES,
    skills=(
        Skill("Let Blood", launch=(1, 2), targets=(1, 2), acc=82, dmg_range=(3, 5),
              dot=Dot("bleed", 80, 3, 3)),
    ),
    weights=(1.0,),
)

MADMAN = EnemyType(
    name="Madman", hp=9, dodge=15, prot=0, spd=7, crit=3, resists=_HUMAN_RES,
    skills=(
        Skill("Accusation", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), acc=90,
              stress_dmg=(6, 10)),
        Skill("Doomsay", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), aoe=True, acc=90,
              stress_dmg=(3, 5)),
    ),
    weights=(0.6, 0.4),
    prefer="stress", tags=("stress",),
)

GHOUL = EnemyType(
    name="Ghoul", hp=42, dodge=8, prot=10, spd=4, crit=6,
    resists=Resists(stun=60, bleed=40, blight=40, debuff=40, move=80),
    skills=(
        Skill("Rend", launch=(1, 2), targets=(1, 2), acc=85, dmg_range=(6, 11),
              dot=Dot("bleed", 60, 2, 3)),
        Skill("Terrifying Howl", launch=(1, 2), targets=(1, 2, 3, 4), aoe=True, acc=95,
              stress_dmg=(5, 8)),
    ),
    weights=(0.65, 0.35),
    tags=("boss", "stress"), is_boss=True,
)

NECROMANCER = EnemyType(
    name="Necromancer", hp=55, dodge=10, prot=15, spd=6, crit=5,
    resists=Resists(stun=65, bleed=200, blight=30, debuff=40, move=80),
    skills=(
        Skill("Spectral Bolt", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), acc=88,
              dmg_range=(5, 9)),
        Skill("Curse of Decay", launch=(1, 2, 3, 4), targets=(1, 2, 3, 4), aoe=True, acc=90,
              stress_dmg=(3, 4), dot=Dot("blight", 70, 2, 3)),
    ),
    weights=(0.6, 0.4),
    prefer="back", tags=("boss",), is_boss=True,
)

ENEMY_TYPES = {
    e.name: e
    for e in (
        BONE_RABBLE, BONE_SOLDIER, BONE_ARBALIST, BONE_DEFENDER,
        CULTIST_BRAWLER, CULTIST_ACOLYTE, BRIGAND_CUTTHROAT, BRIGAND_FUSILIER,
        BRIGAND_BLOODLETTER, MADMAN, GHOUL, NECROMANCER,
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
        ["Brigand Cutthroat", "Bone Rabble", "Madman"],
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
        ["Brigand Cutthroat", "Brigand Bloodletter", "Brigand Fusilier", "Madman"],
        ["Bone Defender", "Bone Soldier", "Bone Arbalist"],
        ["Brigand Bloodletter", "Cultist Brawler", "Bone Arbalist", "Madman"],
    ],
    # Slot 4 — climax
    [
        ["Ghoul", "Cultist Acolyte", "Bone Arbalist"],
        ["Necromancer", "Bone Soldier", "Bone Arbalist"],
        ["Ghoul", "Brigand Bloodletter", "Brigand Fusilier"],
    ],
]
