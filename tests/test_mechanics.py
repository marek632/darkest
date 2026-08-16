"""Mechanics tests for the Darkest Dungeon simulator."""

import random

import pytest

from ddsim.combat import Battle, clamp
from ddsim.data import ENEMY_TYPES, HERO_CLASSES
from ddsim.dungeon import run_dungeon
from ddsim.models import Enemy, Hero
from ddsim.policy import PolicyParams, make_policy
from ddsim.stats import two_proportion_z, wilson_ci
from ddsim.strategies import STRATEGIES


def hero(cls="Crusader", skills=("Smite", "Stunning Blow", "Battle Heal", "Inspiring Cry")):
    return Hero(HERO_CLASSES[cls], list(skills))


def enemy(name="Cultist Brawler"):
    return Enemy(ENEMY_TYPES[name])


def battle(heroes, enemies, seed=1):
    params = PolicyParams()
    return Battle(heroes, enemies, random.Random(seed), make_policy(params))


# --------------------------------------------------------------------- setup
def test_party_requires_four_skills():
    with pytest.raises(ValueError):
        Hero(HERO_CLASSES["Crusader"], ["Smite"])
    with pytest.raises(ValueError):
        Hero(HERO_CLASSES["Crusader"], ["Smite", "Nope", "Battle Heal", "Inspiring Cry"])


def test_all_strategy_definitions_are_valid():
    for s in STRATEGIES:
        for cls, skills in s.party:
            Hero(HERO_CLASSES[cls], list(skills))  # raises if invalid


# ------------------------------------------------------------------- clamps
def test_hit_chance_clamped():
    assert clamp(150, 5, 95) == 95
    assert clamp(-20, 5, 95) == 5


# -------------------------------------------------------------- death's door
def test_hero_drops_to_deaths_door_not_dead():
    h = hero()
    b = battle([h], [enemy()])
    b.damage_hero(h, 999)
    assert h.alive and h.at_deaths_door and h.hp == 0


def test_deaths_door_death_blow():
    rng_hits = 0
    deaths = 0
    for seed in range(300):
        h = hero()
        b = battle([h], [enemy()], seed=seed)
        b.damage_hero(h, 999)  # to death's door
        b.damage_hero(h, 1)  # death blow check
        rng_hits += 1
        deaths += 0 if h.alive else 1
    # deathblow resist is 67%: death rate should be ~33%
    assert 0.23 < deaths / rng_hits < 0.43


def test_heal_recovers_from_deaths_door():
    h = hero()
    v = hero("Vestal", ("Divine Grace", "Divine Comfort", "Judgement", "Dazzling Light"))
    b = battle([h, v], [enemy()])
    b.damage_hero(h, 999)
    assert h.at_deaths_door
    b.resolve_support(v, v.skills[0], h)  # Divine Grace
    assert h.hp > 0 and not h.at_deaths_door


# ------------------------------------------------------------------- stress
def test_resolve_check_at_100_stress():
    afflicted = virtuous = 0
    for seed in range(400):
        h = hero()
        b = battle([h], [enemy()], seed=seed)
        b.add_stress(h, 100)
        assert h.resolve_tested
        afflicted += int(h.afflicted)
        virtuous += int(h.virtuous)
    assert afflicted + virtuous == 400
    # virtue chance is 25%
    assert 0.17 < virtuous / 400 < 0.33


def test_heart_attack_at_200():
    h = hero()
    b = battle([h], [enemy()])
    b.add_stress(h, 100)  # resolve check fires here (virtue may reset stress)
    b.add_stress(h, 300)  # guaranteed to hit the 200 cap either way
    assert h.at_deaths_door or not h.alive  # heart attack


# --------------------------------------------------------------------- dots
def test_skeletons_immune_to_bleed():
    hm = hero("Highwayman", ("Wicked Slice", "Open Vein", "Pistol Shot", "Take Aim"))
    for seed in range(100):
        e = enemy("Bone Soldier")
        b = battle([hm], [e], seed=seed)
        sk = next(s for s in hm.skills if s.name == "Open Vein")
        b.resolve_attack(hm, sk, e)
        assert not e.dots, "skeletons must never bleed"


def test_bleed_ticks_and_expires():
    h = hero()
    b = battle([h], [enemy()])
    h.dots.append(["bleed", 2, 2])
    hp0 = h.hp
    b.tick_dots(h)
    assert h.hp == hp0 - 2 and len(h.dots) == 1
    b.tick_dots(h)
    assert h.hp == hp0 - 4 and not h.dots


# --------------------------------------------------------------------- stun
def test_stun_skips_turn_and_clears():
    e = enemy()
    h = hero()
    b = battle([h], [e])
    e.stunned = True
    b.take_turn(e)
    assert not e.stunned  # cleared
    assert e.stat("stun_resist") > e.resists.stun  # bonus resist applied
    assert h.hp == h.max_hp  # no attack happened


# ------------------------------------------------------------------- policy
def test_healer_prioritizes_deaths_door_ally():
    v = hero("Vestal", ("Divine Grace", "Divine Comfort", "Judgement", "Dazzling Light"))
    front = hero()
    mid = hero("Highwayman", ("Wicked Slice", "Pistol Shot", "Open Vein", "Take Aim"))
    b = battle([front, mid, v], [enemy()])  # Vestal at rank 3: heals are legal
    b.damage_hero(front, 999)
    action = make_policy(PolicyParams())(b, v)
    assert action.kind == "skill" and action.skill.heal is not None
    assert front in action.targets


def test_out_of_position_hero_moves():
    # Vestal forced into rank 1 with front-line-illegal skills moves back
    v = hero("Vestal", ("Divine Grace", "Divine Comfort", "Judgement", "Dazzling Light"))
    c = hero()
    b = battle([v, c], [enemy("Bone Defender")])
    action = make_policy(PolicyParams())(b, v)
    # Judgement launches from 2-4, Dazzling from anywhere; either acts or moves back
    assert action.kind in ("skill", "move")
    if action.kind == "move":
        assert action.move > 0


# ------------------------------------------------------------ determinism
def test_runs_are_deterministic():
    s = STRATEGIES[0]
    a = run_dungeon(s.party, s.params, seed=123)
    b = run_dungeon(s.party, s.params, seed=123)
    assert (a.win, a.encounters_cleared, a.deaths, a.rounds, a.end_stress) == (
        b.win, b.encounters_cleared, b.deaths, b.rounds, b.end_stress)


def test_different_seeds_differ_somewhere():
    s = STRATEGIES[0]
    outcomes = {run_dungeon(s.party, s.params, seed=i).rounds for i in range(10)}
    assert len(outcomes) > 1


# ------------------------------------------------------------------- smoke
def test_every_strategy_smoke_runs():
    for s in STRATEGIES:
        for seed in range(3):
            r = run_dungeon(s.party, s.params, seed=seed)
            assert 0 <= r.encounters_cleared <= 4
            assert 0 <= r.deaths <= 4
            if r.win:
                assert r.encounters_cleared == 4 and r.survivors >= 1


# -------------------------------------------------------------------- stats
def test_wilson_ci_sane():
    lo, hi = wilson_ci(50, 100)
    assert lo < 0.5 < hi and (hi - lo) < 0.25


def test_two_proportion_z():
    z, p = two_proportion_z(80, 100, 50, 100)
    assert z > 0 and p < 0.001
    z2, p2 = two_proportion_z(50, 100, 50, 100)
    assert abs(z2) < 1e-9 and p2 > 0.99
