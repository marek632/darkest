"""The strategy space under test.

A Strategy = party composition (classes in rank order, front first)
           + a 4-skill loadout per hero
           + policy knobs (targeting focus, heal thresholds, stun affinity).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .policy import PolicyParams


@dataclass(frozen=True)
class Strategy:
    name: str
    party: tuple  # ((class_name, (s1, s2, s3, s4)), ...) rank 1 first
    params: PolicyParams = field(default_factory=PolicyParams)
    desc: str = ""


STRATEGIES = [
    # ------------------------------------------------------------------ classic
    Strategy(
        "classic_balanced",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Zealous Accusation", "Inspiring Cry")),
            ("Highwayman", ("Wicked Slice", "Pistol Shot", "Grapeshot Blast", "Open Vein")),
            ("Plague Doctor", ("Noxious Blast", "Blinding Gas", "Plague Grenade",
                               "Battlefield Medicine")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement", "Dazzling Light")),
        ),
        PolicyParams(focus="threat"),
        "The tutorial party: tank/dps/support/healer, balanced loadouts.",
    ),
    Strategy(
        "classic_stunlock",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Holy Lance", "Inspiring Cry")),
            ("Highwayman", ("Wicked Slice", "Pistol Shot", "Duelist's Advance", "Open Vein")),
            ("Plague Doctor", ("Blinding Gas", "Disorienting Blast", "Noxious Blast",
                               "Battlefield Medicine")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Dazzling Light", "Judgement")),
        ),
        PolicyParams(focus="threat", stun_weight=1.8),
        "Classic comp, but every stun in the kit and a policy that loves them.",
    ),
    Strategy(
        "classic_stress_first",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Zealous Accusation", "Inspiring Cry")),
            ("Highwayman", ("Wicked Slice", "Pistol Shot", "Grapeshot Blast", "Open Vein")),
            ("Plague Doctor", ("Noxious Blast", "Blinding Gas", "Plague Grenade",
                               "Battlefield Medicine")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement", "Dazzling Light")),
        ),
        PolicyParams(focus="stress_first"),
        "Classic comp; kill stress dealers before anything else.",
    ),
    Strategy(
        "classic_aoe",
        (
            ("Crusader", ("Zealous Accusation", "Smite", "Stunning Blow", "Battle Heal")),
            ("Highwayman", ("Grapeshot Blast", "Wicked Slice", "Pistol Shot", "Take Aim")),
            ("Plague Doctor", ("Plague Grenade", "Blinding Gas", "Noxious Blast",
                               "Emboldening Vapours")),
            ("Vestal", ("Divine Comfort", "Divine Grace", "Dazzling Light", "Judgement")),
        ),
        PolicyParams(focus="lowest_hp"),
        "Classic comp leaning on AOE clears and group healing.",
    ),
    # ------------------------------------------------------------------- marks
    Strategy(
        "mark_execute",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Battle Heal", "Inspiring Cry")),
            ("Bounty Hunter", ("Collect Bounty", "Mark for Death", "Flashbang",
                               "Finish Him")),
            ("Occultist", ("Vulnerability Hex", "Abyssal Artillery", "Wyrd Reconstruction",
                           "Weakening Curse")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement", "Dazzling Light")),
        ),
        PolicyParams(focus="threat"),
        "Mark synergy: Occultist hexes, Bounty Hunter collects.",
    ),
    Strategy(
        "mark_backline_purge",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Battle Heal", "Inspiring Cry")),
            ("Bounty Hunter", ("Collect Bounty", "Come Hither", "Flashbang", "Uppercut")),
            ("Occultist", ("Vulnerability Hex", "Daemon's Pull", "Wyrd Reconstruction",
                           "Abyssal Artillery")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement", "Dazzling Light")),
        ),
        PolicyParams(focus="backline", stun_weight=1.3),
        "Drag the backline forward and beat it to death at the front.",
    ),
    # ------------------------------------------------------------------- DoTs
    Strategy(
        "bleed_party",
        (
            ("Hellion", ("Wicked Hack", "If It Bleeds", "Barbaric YAWP", "Adrenaline Rush")),
            ("Highwayman", ("Open Vein", "Wicked Slice", "Pistol Shot", "Duelist's Advance")),
            ("Grave Robber", ("Flashing Daggers", "Thrown Dagger", "Poison Dart",
                              "Toxin Trickery")),
            ("Occultist", ("Wyrd Reconstruction", "Weakening Curse", "Abyssal Artillery",
                           "Hands from the Abyss")),
        ),
        PolicyParams(focus="threat"),
        "Bleed-heavy comp. Expected to struggle vs bleed-immune skeletons.",
    ),
    Strategy(
        "blight_party",
        (
            ("Hellion", ("Wicked Hack", "Iron Swan", "Barbaric YAWP", "Adrenaline Rush")),
            ("Grave Robber", ("Poison Dart", "Flashing Daggers", "Thrown Dagger",
                              "Toxin Trickery")),
            ("Plague Doctor", ("Noxious Blast", "Plague Grenade", "Blinding Gas",
                               "Battlefield Medicine")),
            ("Occultist", ("Wyrd Reconstruction", "Weakening Curse", "Vulnerability Hex",
                           "Abyssal Artillery")),
        ),
        PolicyParams(focus="threat"),
        "Blight-heavy comp: strong into skeletons' low blight resist.",
    ),
    # ---------------------------------------------------------------- offense
    Strategy(
        "glass_cannon_rush",
        (
            ("Hellion", ("Wicked Hack", "Iron Swan", "If It Bleeds", "Adrenaline Rush")),
            ("Highwayman", ("Wicked Slice", "Pistol Shot", "Grapeshot Blast", "Take Aim")),
            ("Grave Robber", ("Thrown Dagger", "Poison Dart", "Flashing Daggers", "Lunge")),
            ("Plague Doctor", ("Noxious Blast", "Plague Grenade", "Blinding Gas",
                               "Battlefield Medicine")),
        ),
        PolicyParams(focus="backline", heal_threshold=0.45),
        "No dedicated healer; race the damage clock, snipe the backline.",
    ),
    Strategy(
        "all_damage_no_healer",
        (
            ("Hellion", ("Wicked Hack", "Iron Swan", "If It Bleeds", "Bleed Out")),
            ("Highwayman", ("Wicked Slice", "Pistol Shot", "Grapeshot Blast", "Open Vein")),
            ("Bounty Hunter", ("Collect Bounty", "Mark for Death", "Hook and Slice",
                               "Flashbang")),
            ("Grave Robber", ("Thrown Dagger", "Poison Dart", "Flashing Daggers", "Lunge")),
        ),
        PolicyParams(focus="lowest_hp", heal_threshold=0.3),
        "Deliberate baseline: zero sustain, pure damage.",
    ),
    # ---------------------------------------------------------------- defense
    Strategy(
        "double_healer_turtle",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Bulwark of Faith", "Inspiring Cry")),
            ("Bounty Hunter", ("Collect Bounty", "Mark for Death", "Uppercut", "Flashbang")),
            ("Occultist", ("Wyrd Reconstruction", "Weakening Curse", "Hands from the Abyss",
                           "Vulnerability Hex")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement", "Dazzling Light")),
        ),
        PolicyParams(focus="threat", heal_threshold=0.75, stun_weight=1.3),
        "Two healers, a marked tank, and patience.",
    ),
    Strategy(
        "stun_wall",
        (
            ("Hellion", ("Barbaric YAWP", "Wicked Hack", "If It Bleeds", "Adrenaline Rush")),
            ("Bounty Hunter", ("Uppercut", "Flashbang", "Collect Bounty", "Finish Him")),
            ("Plague Doctor", ("Blinding Gas", "Disorienting Blast", "Noxious Blast",
                               "Battlefield Medicine")),
            ("Vestal", ("Divine Grace", "Dazzling Light", "Divine Comfort", "Judgement")),
        ),
        PolicyParams(focus="threat", stun_weight=2.0),
        "Maximum stun coverage across all four ranks.",
    ),
    # ------------------------------------------------------------- unorthodox
    Strategy(
        "shuffle_bruisers",
        (
            ("Crusader", ("Smite", "Holy Lance", "Stunning Blow", "Battle Heal")),
            ("Highwayman", ("Duelist's Advance", "Point Blank Shot", "Wicked Slice",
                            "Pistol Shot")),
            ("Grave Robber", ("Lunge", "Thrown Dagger", "Shadow Fade", "Poison Dart")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement", "Dazzling Light")),
        ),
        PolicyParams(focus="threat"),
        "Movement-skill bruisers over a Vestal anchor.",
    ),
    Strategy(
        "backline_artillery",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Zealous Accusation", "Battle Heal")),
            ("Hellion", ("Wicked Hack", "If It Bleeds", "Barbaric YAWP", "Adrenaline Rush")),
            ("Plague Doctor", ("Plague Grenade", "Blinding Gas", "Noxious Blast",
                               "Battlefield Medicine")),
            ("Occultist", ("Abyssal Artillery", "Daemon's Pull", "Wyrd Reconstruction",
                           "Weakening Curse")),
        ),
        PolicyParams(focus="backline"),
        "Two frontliners hold while the back rains AOE on the enemy rear.",
    ),
]

STRATEGY_INDEX = {s.name: s for s in STRATEGIES}
