"""The strategy space under test.

A Strategy = party composition (classes in rank order, front first)
           + a 3-skill loadout per hero (official rule: pick three)
           + policy knobs (targeting focus, heal thresholds, stun affinity).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .policy import PolicyParams


@dataclass(frozen=True)
class Strategy:
    name: str
    party: tuple  # ((class_name, (s1, s2, s3)), ...) rank 1 first
    params: PolicyParams = field(default_factory=PolicyParams)
    desc: str = ""


STRATEGIES = [
    # ------------------------------------------------------------------ classic
    Strategy(
        "classic_balanced",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Inspiring Cry")),
            ("Highwayman", ("Wicked Slice", "Pistol Shot", "Open Vein")),
            ("Plague Doctor", ("Noxious Blast", "Blinding Gas", "Battlefield Medicine")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement")),
        ),
        PolicyParams(focus="threat"),
        "The tutorial party: tank/dps/support/healer, balanced loadouts.",
    ),
    Strategy(
        "classic_stunlock",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Inspiring Cry")),
            ("Highwayman", ("Wicked Slice", "Pistol Shot", "Duelist's Advance")),
            ("Plague Doctor", ("Blinding Gas", "Disorienting Blast", "Battlefield Medicine")),
            ("Vestal", ("Divine Grace", "Dazzling Light", "Judgement")),
        ),
        PolicyParams(focus="threat", stun_weight=1.8),
        "Classic comp, but every stun in the kit and a policy that loves them.",
    ),
    Strategy(
        "classic_stress_first",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Inspiring Cry")),
            ("Highwayman", ("Wicked Slice", "Pistol Shot", "Open Vein")),
            ("Plague Doctor", ("Noxious Blast", "Blinding Gas", "Battlefield Medicine")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement")),
        ),
        PolicyParams(focus="stress_first"),
        "Classic comp; kill stress dealers before anything else.",
    ),
    Strategy(
        "classic_aoe",
        (
            ("Crusader", ("Zealous Accusation", "Smite", "Battle Heal")),
            ("Highwayman", ("Grapeshot Blast", "Wicked Slice", "Pistol Shot")),
            ("Plague Doctor", ("Plague Grenade", "Blinding Gas", "Noxious Blast")),
            ("Vestal", ("Divine Comfort", "Divine Grace", "Dazzling Light")),
        ),
        PolicyParams(focus="lowest_hp"),
        "Classic comp leaning on AOE clears and group healing.",
    ),
    # ------------------------------------------------------------------- marks
    Strategy(
        "mark_execute",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Battle Heal")),
            ("Bounty Hunter", ("Collect Bounty", "Mark for Death", "Flashbang")),
            ("Occultist", ("Vulnerability Hex", "Abyssal Artillery", "Wyrd Reconstruction")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement")),
        ),
        PolicyParams(focus="threat"),
        "Mark synergy: Occultist hexes, Bounty Hunter collects.",
    ),
    Strategy(
        "mark_backline_purge",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Inspiring Cry")),
            ("Bounty Hunter", ("Collect Bounty", "Come Hither", "Uppercut")),
            ("Occultist", ("Vulnerability Hex", "Daemon's Pull", "Wyrd Reconstruction")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement")),
        ),
        PolicyParams(focus="backline", stun_weight=1.3),
        "Drag the backline forward and beat it to death at the front.",
    ),
    # ------------------------------------------------------------------- DoTs
    Strategy(
        "bleed_party",
        (
            ("Hellion", ("Wicked Hack", "If It Bleeds", "Adrenaline Rush")),
            ("Highwayman", ("Open Vein", "Wicked Slice", "Pistol Shot")),
            ("Grave Robber", ("Flashing Daggers", "Thrown Dagger", "Poison Dart")),
            ("Occultist", ("Wyrd Reconstruction", "Weakening Curse", "Abyssal Artillery")),
        ),
        PolicyParams(focus="threat"),
        "Bleed-heavy comp. Expected to struggle vs bleed-immune skeletons.",
    ),
    Strategy(
        "blight_party",
        (
            ("Hellion", ("Wicked Hack", "Iron Swan", "Adrenaline Rush")),
            ("Grave Robber", ("Poison Dart", "Thrown Dagger", "Toxin Trickery")),
            ("Plague Doctor", ("Noxious Blast", "Plague Grenade", "Battlefield Medicine")),
            ("Occultist", ("Wyrd Reconstruction", "Weakening Curse", "Vulnerability Hex")),
        ),
        PolicyParams(focus="threat"),
        "Blight-heavy comp: strong into skeletons' low blight resist.",
    ),
    # ---------------------------------------------------------------- offense
    Strategy(
        "glass_cannon_rush",
        (
            ("Hellion", ("Wicked Hack", "Iron Swan", "If It Bleeds")),
            ("Highwayman", ("Wicked Slice", "Pistol Shot", "Grapeshot Blast")),
            ("Grave Robber", ("Thrown Dagger", "Poison Dart", "Lunge")),
            ("Plague Doctor", ("Noxious Blast", "Plague Grenade", "Battlefield Medicine")),
        ),
        PolicyParams(focus="backline", heal_threshold=0.45),
        "No dedicated healer; race the damage clock, snipe the backline.",
    ),
    Strategy(
        "all_damage_no_healer",
        (
            ("Hellion", ("Wicked Hack", "Iron Swan", "Bleed Out")),
            ("Highwayman", ("Wicked Slice", "Pistol Shot", "Open Vein")),
            ("Bounty Hunter", ("Collect Bounty", "Mark for Death", "Caltrops")),
            ("Grave Robber", ("Thrown Dagger", "Poison Dart", "Lunge")),
        ),
        PolicyParams(focus="lowest_hp", heal_threshold=0.3),
        "Deliberate baseline: zero sustain, pure damage.",
    ),
    # ---------------------------------------------------------------- defense
    Strategy(
        "double_healer_turtle",
        (
            ("Crusader", ("Smite", "Bulwark of Faith", "Inspiring Cry")),
            ("Bounty Hunter", ("Collect Bounty", "Mark for Death", "Uppercut")),
            ("Occultist", ("Wyrd Reconstruction", "Weakening Curse", "Hands from the Abyss")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement")),
        ),
        PolicyParams(focus="threat", heal_threshold=0.75, stun_weight=1.3),
        "Two healers, a marked tank, and patience.",
    ),
    Strategy(
        "stun_wall",
        (
            ("Hellion", ("Barbaric YAWP", "Wicked Hack", "Adrenaline Rush")),
            ("Bounty Hunter", ("Uppercut", "Flashbang", "Collect Bounty")),
            ("Plague Doctor", ("Blinding Gas", "Disorienting Blast", "Battlefield Medicine")),
            ("Vestal", ("Divine Grace", "Dazzling Light", "Divine Comfort")),
        ),
        PolicyParams(focus="threat", stun_weight=2.0),
        "Maximum stun coverage across all four ranks.",
    ),
    # ------------------------------------------------------------- unorthodox
    Strategy(
        "shuffle_bruisers",
        (
            ("Crusader", ("Smite", "Holy Lance", "Battle Heal")),
            ("Highwayman", ("Duelist's Advance", "Point Blank Shot", "Wicked Slice")),
            ("Grave Robber", ("Lunge", "Thrown Dagger", "Shadow Fade")),
            ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement")),
        ),
        PolicyParams(focus="threat"),
        "Movement-skill bruisers over a Vestal anchor.",
    ),
    Strategy(
        "backline_artillery",
        (
            ("Crusader", ("Smite", "Stunning Blow", "Battle Heal")),
            ("Hellion", ("Wicked Hack", "If It Bleeds", "Adrenaline Rush")),
            ("Plague Doctor", ("Plague Grenade", "Blinding Gas", "Noxious Blast")),
            ("Occultist", ("Abyssal Artillery", "Daemon's Pull", "Wyrd Reconstruction")),
        ),
        PolicyParams(focus="backline"),
        "Two frontliners hold while the back rains AOE on the enemy rear.",
    ),
]

STRATEGY_INDEX = {s.name: s for s in STRATEGIES}
