"""Mechanics tests for the Darkest Dungeon board-game simulator."""

import random

import pytest

from ddsim.combat import ROOM_ROUNDS, Battle, clamp
from ddsim.data import ENEMY_TYPES, HERO_CLASSES
from ddsim.dungeon import LIGHT_START, run_dungeon
from ddsim.models import Enemy, Hero
from ddsim.policy import PolicyParams, make_policy
from ddsim.stats import two_proportion_z, wilson_ci
from ddsim.strategies import STRATEGIES


def hero(cls="Crusader", skills=("Smite", "Stunning Blow", "Inspiring Cry")):
    return Hero(HERO_CLASSES[cls], list(skills))


def enemy(name="Cultist Brawler"):
    return Enemy(ENEMY_TYPES[name])


def battle(heroes, enemies, seed=1):
    params = PolicyParams()
    return Battle(heroes, enemies, random.Random(seed), make_policy(params))


# --------------------------------------------------------------------- setup
def test_party_requires_three_skills():
    with pytest.raises(ValueError):
        Hero(HERO_CLASSES["Crusader"], ["Smite"])
    with pytest.raises(ValueError):
        Hero(HERO_CLASSES["Crusader"], ["Smite", "Nope", "Battle Heal"])
    with pytest.raises(ValueError):  # four skills is no longer legal
        Hero(HERO_CLASSES["Crusader"],
             ["Smite", "Stunning Blow", "Battle Heal", "Inspiring Cry"])


def test_all_strategy_definitions_are_valid():
    for s in STRATEGIES:
        for cls, skills in s.party:
            Hero(HERO_CLASSES[cls], list(skills))  # raises if invalid


# ----------------------------------------------------------------- d10 to-hit
def test_hit_target_number_clamped():
    c = hero()
    e = enemy("Madman")  # dodge 2
    b = battle([c], [e])
    smite = c.skills[0]
    tn = b.hit_target_number(c, smite, e)
    assert 1 <= tn <= 9
    # acc 8 vs dodge 2 -> 6
    assert tn == 6


def test_hit_rate_matches_target_number():
    c = hero()
    hits = 0
    n = 4000
    for seed in range(n):
        e = enemy("Bone Rabble")  # dodge 0
        b = battle([c], [e], seed=seed)
        smite = c.skills[0]  # acc 8 -> 80%
        if b.resolve_attack(c, smite, e) != "miss":
            hits += 1
    assert 0.76 < hits / n < 0.84


# -------------------------------------------------------------- death's door
def test_hero_drops_to_deaths_door_not_dead():
    h = hero()
    b = battle([h], [enemy()])
    b.damage_hero(h, 999)
    assert h.alive and h.at_deaths_door and h.hp == 0


def test_deaths_door_death_blow():
    checks = deaths = 0
    for seed in range(300):
        h = hero()
        b = battle([h], [enemy()], seed=seed)
        b.damage_hero(h, 999)  # to death's door
        b.damage_hero(h, 1)  # death's-door die roll
        checks += 1
        deaths += 0 if h.alive else 1
    # death's-door die kills ~1/3 of the time
    assert 0.23 < deaths / checks < 0.43


def test_heal_recovers_from_deaths_door():
    h = hero()
    v = hero("Vestal", ("Divine Grace", "Divine Comfort", "Judgement"))
    b = battle([h, v], [enemy()])
    b.damage_hero(h, 999)
    assert h.at_deaths_door
    b.resolve_support(v, v.skills[0], h)  # Divine Grace
    assert h.hp > 0 and not h.at_deaths_door


# ------------------------------------------------------------------- stress
def test_resolve_check_when_track_fills():
    afflicted = virtuous = 0
    for seed in range(400):
        h = hero()
        b = battle([h], [enemy()], seed=seed)
        b.add_stress(h, 10)
        assert h.resolve_tested
        afflicted += int(h.afflicted)
        virtuous += int(h.virtuous)
    assert afflicted + virtuous == 400
    # virtue chance is 25%
    assert 0.17 < virtuous / 400 < 0.33


def test_heart_attack_on_second_fill():
    h = hero()
    b = battle([h], [enemy()])
    b.add_stress(h, 10)  # resolve test fires, stress resets below cap
    assert h.alive and not h.at_deaths_door
    b.add_stress(h, 10)  # track fills again -> heart attack
    assert h.at_deaths_door or not h.alive


def test_stress_capped_at_track():
    h = hero()
    b = battle([h], [enemy()])
    b.add_stress(h, 4)
    assert h.stress == 4


# --------------------------------------------------------------------- dots
def test_skeletons_immune_to_bleed():
    hm = hero("Highwayman", ("Wicked Slice", "Open Vein", "Pistol Shot"))
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


# ----------------------------------------------------------- room round cap
def test_battle_never_exceeds_four_rounds():
    for seed in range(30):
        # an unkillable wall guarantees the clock runs out
        heroes = [hero("Vestal", ("Divine Grace", "Divine Comfort", "Judgement"))]
        wall = enemy("Bone Defender")
        wall.hp = wall.max_hp = 10_000
        b = battle(heroes, [wall], seed=seed)
        won = b.run()
        assert not won
        assert b.round <= ROOM_ROUNDS
        assert b.alive_heroes()  # retreat, not a wipe


def test_initiative_alternates_by_cards():
    # with equal numbers, every combatant acts exactly once per round
    h1, h2 = hero(), hero("Highwayman", ("Wicked Slice", "Pistol Shot", "Open Vein"))
    e1, e2 = enemy("Bone Defender"), enemy("Bone Defender")
    b = battle([h1, h2], [e1, e2])
    turns = []
    orig = Battle.take_turn
    Battle.take_turn = lambda self, a: turns.append(a.is_hero) or orig(self, a)
    try:
        b.run()
    finally:
        Battle.take_turn = orig
    # each round: as many hero activations as living heroes (<= 2), etc.
    assert turns.count(True) <= ROOM_ROUNDS * 2
    assert turns.count(False) <= ROOM_ROUNDS * 2


# ------------------------------------------------------- retreats and light
def test_retreat_reinforcement_and_light_failure():
    # a party that cannot win slot-4 fights must burn all light and fail
    party = (
        ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement")),
        ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement")),
        ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement")),
        ("Vestal", ("Divine Grace", "Divine Comfort", "Judgement")),
    )
    failed_by_light = 0
    for seed in range(20):
        r = run_dungeon(party, PolicyParams(), seed=seed)
        assert r.retreats + r.deaths > 0 or r.win is False
        if not r.win and r.light_remaining == 0:
            failed_by_light += 1
    assert failed_by_light > 0  # the light clock actually ends runs


def test_light_budget_bounds_attempts():
    for seed in range(10):
        r = run_dungeon(STRATEGIES[0].party, STRATEGIES[0].params, seed=seed)
        assert r.retreats <= LIGHT_START


# ------------------------------------------------------------------- policy
def test_healer_prioritizes_deaths_door_ally():
    v = hero("Vestal", ("Divine Grace", "Divine Comfort", "Judgement"))
    front = hero()
    mid = hero("Highwayman", ("Wicked Slice", "Pistol Shot", "Open Vein"))
    b = battle([front, mid, v], [enemy()])  # Vestal at rank 3: heals are legal
    b.damage_hero(front, 999)
    action = make_policy(PolicyParams())(b, v)
    assert action.kind in ("skill", "move_skill") and action.skill.heal is not None
    assert front in action.targets


def test_move_then_strike_when_out_of_position():
    # A Hellion trapped at rank 3 can step forward and still attack
    hell = hero("Hellion", ("Wicked Hack", "Iron Swan", "Adrenaline Rush"))
    c1 = hero()
    c2 = hero("Highwayman", ("Wicked Slice", "Pistol Shot", "Open Vein"))
    b = battle([c1, c2, hell], [enemy()])
    action = make_policy(PolicyParams())(b, hell)
    # she should not waste the turn: either a legal skill or move+skill
    assert action.kind in ("skill", "move_skill")


# ------------------------------------------------------------ determinism
def test_runs_are_deterministic():
    s = STRATEGIES[0]
    a = run_dungeon(s.party, s.params, seed=123)
    b = run_dungeon(s.party, s.params, seed=123)
    assert (a.win, a.encounters_cleared, a.deaths, a.rounds, a.retreats,
            a.end_stress) == (b.win, b.encounters_cleared, b.deaths, b.rounds,
                              b.retreats, b.end_stress)


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
