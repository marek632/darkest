"""Mechanics tests for the official-rules engine."""

import random
import unittest

from ddsim.official.battle import Action, Battle, Fighter
from ddsim.official.cards import DEFAULT_LOADOUT, HERO_CLASSES
from ddsim.official.monsters import BOSSES, MONSTERS
from ddsim.official.quest import make_party, run_quest


def hero(name, loadout=None):
    return Fighter(cls=HERO_CLASSES[name],
                   loadout=loadout or DEFAULT_LOADOUT[name])


def mon(name):
    return Fighter(mcard=MONSTERS[name])


def battle(heroes=None, monsters=None, tile="kafel_5", light=5, seed=1,
           policy=None):
    return Battle(heroes or make_party(), monsters or [mon("Kościany Obrońca")],
                  tile, light, random.Random(seed), policy=policy)


def skills_in(acts):
    return {a.card.name for a in acts if a.kind == "skill"}


class TestStanceLegality(unittest.TestCase):
    def test_stance_gates_skills(self):
        # Krzyżowiec na slocie 0 (Agresywna): Kara boska tak, Święta lanca nie
        b = battle(heroes=make_party(
            [("Krzyżowiec", ("Kara boska", "Święta lanca", "Pierwsza pomoc")),
             "Kapłanka", "Oprych", "Awanturniczka"]))
        k = b.heroes[0]
        k.area = b.monsters[0].area  # range 0
        names = skills_in(b.legal_actions(k))
        self.assertIn("Kara boska", names)
        self.assertNotIn("Święta lanca", names)

    def test_swap_changes_legality(self):
        b = battle()
        k = b.heroes[0]
        b.apply_action(k, Action("swap", move=1))
        self.assertEqual(k.slot, 1)
        self.assertEqual(b.hero_slots[1], k)
        # sąsiad zamieniony na slot 0
        self.assertEqual(b.hero_slots[0].name, "Kapłanka")

    def test_lanca_legal_only_from_back_stances(self):
        b = battle(heroes=make_party(
            [("Krzyżowiec", ("Kara boska", "Święta lanca", "Pierwsza pomoc")),
             "Kapłanka", "Oprych", "Awanturniczka"]))
        k = b.heroes[0]
        # przenieś na slot Zasięgowy (2) przez dwa swapy
        b.apply_action(k, Action("swap", move=1))
        b.apply_action(k, Action("swap", move=1))
        # ustaw zasięg 1 do potwora
        m = b.monsters[0]
        k.area = 0
        m.area = 1
        names = skills_in(b.legal_actions(k))
        self.assertIn("Święta lanca", names)
        self.assertNotIn("Kara boska", names)


class TestRangeAndTargets(unittest.TestCase):
    def test_exact_range_two(self):
        # Żelazny łabędź: dokładnie 2 obszary
        b = battle(tile="kafel_6")
        aw = b.heroes[3]
        aw.slot = 0  # dowolna przednia postawa
        b.hero_slots = [aw, b.heroes[1], b.heroes[2], b.heroes[0]]
        for i, h in enumerate(b.hero_slots):
            h.slot = i
        m = b.monsters[0]
        aw.area, m.area = 0, 2
        names = skills_in(b.legal_actions(aw))
        self.assertIn("Żelazny łabędź", names)
        m.area = 1
        names = skills_in(b.legal_actions(aw))
        self.assertNotIn("Żelazny łabędź", names)

    def test_aoe_limited_to_area_and_count(self):
        b = battle(heroes=make_party(
            [("Oprych", ("Siekańce", "Wystrzał", "Doskok")),
             "Kapłanka", "Krzyżowiec", "Awanturniczka"]),
            monsters=[mon("Kościany Obrońca"), mon("Gladiator Kultystów"),
                      mon("Kościany Kusznik"), mon("Kościany Dworzanin")])
        o = b.heroes[0]
        o.slot = 2
        b.hero_slots[2] = o
        for m in b.monsters:
            m.area = o.area  # wszyscy w tym samym obszarze
        acts = [a for a in b.legal_actions(o)
                if a.kind == "skill" and a.card.name == "Siekańce"]
        self.assertEqual(len(acts), 1)
        self.assertEqual(len(acts[0].targets), 3)  # max 3 cele

    def test_moves_respect_speed_and_capacity(self):
        b = battle(tile="kafel_2")
        k = b.heroes[0]  # Krzyżowiec, szybkość 1
        dests = {a.area for a in b.legal_actions(k) if a.kind == "move"}
        for d in dests:
            self.assertLessEqual(b.tile.dist(k.area, d), 1)


class TestCombatMath(unittest.TestCase):
    def test_fixed_damage_and_thresholds(self):
        b = battle(light=3)  # light<=4: kryt +1
        k = hero("Krzyżowiec", ("Kara boska", "Święta lanca", "Pierwsza pomoc"))
        m = mon("Kościany Obrońca")
        card = HERO_CLASSES["Krzyżowiec"].skills["Kara boska"]
        # acc_eff = 9 - 1 (unik) = 8; crit_eff = 0 + 1 (mrok)
        hits = 0
        random.seed(5)
        for roll in range(1, 11):
            b.rng = FakeRng(roll)
            m.hp = m.max_hp
            m.dead = False
            b.resolve_attack(k, card, m)
            dealt = m.max_hp - m.hp
            if roll <= 1:
                self.assertEqual(dealt, 13 + 1)  # kryt + bonus plugawy
            elif roll <= 8:
                self.assertEqual(dealt, 7 + 1)
            else:
                self.assertEqual(dealt, 0)
            hits += dealt > 0
        self.assertEqual(hits, 8)

    def test_ochrona_halves_and_riposta_reflects(self):
        b = battle()
        k = b.heroes[0]
        m = b.monsters[0]
        m.stacks.append(["ochrona", None, 2])
        m.stacks.append(["riposta", None, 2])
        card = HERO_CLASSES["Krzyżowiec"].skills["Kara boska"]
        b.rng = FakeRng(5)  # trafienie bez kryta
        hp0, khp0 = m.hp, k.hp
        b.resolve_attack(k, card, m)
        dealt = hp0 - m.hp
        self.assertEqual(dealt, 4)  # ceil((7+1)/2)
        self.assertEqual(khp0 - k.hp, 2)  # riposta: ceil(4/2)

    def test_stun_removes_one_action(self):
        counter = {"n": 0}

        def counting_policy(bb, h):
            counter["n"] += 1
            return Action("pass")

        b = battle(policy=counting_policy)
        k = b.heroes[0]
        k.stacks.append(["stun", None, 1])
        b.hero_turn(k)
        # pass kończy turę przy pierwszym wywołaniu — ale stun zjada 1 akcję,
        # więc polityka została zapytana najwyżej raz
        self.assertLessEqual(counter["n"], 1)
        self.assertFalse(k.has("stun"))


class TestShoveAndBoard(unittest.TestCase):
    def test_push_blocked_by_full_area(self):
        b = battle(tile="kafel_6")
        m = b.monsters[0]
        k = b.heroes[0]
        m.area = 3
        k.area = 2
        # zapełnij obszar 4 (pojemność 2)
        extra = [mon("Pluwacz"), mon("Pluwacz")]
        for e in extra:
            b.monsters.append(e)
            e.area = 4
        b.shove(m, k.area, 1, away=True)
        self.assertEqual(m.area, 3)  # nie może wejść na pełny obszar

    def test_pull_moves_toward(self):
        b = battle(tile="kafel_6")
        m = b.monsters[0]
        k = b.heroes[0]
        k.area, m.area = 0, 3
        b.shove(m, k.area, 2, away=False)
        self.assertEqual(b.tile.dist(m.area, k.area), 1)

    def test_przesuwanie_resist_shortens(self):
        b = battle(tile="kafel_6")
        ku = hero("Kuszniczka")  # odporność: przesuwanie
        ku.area = 2
        b.heroes.append(ku)
        b.shove(ku, 0, 2, away=True)   # 2-1=1 krok
        self.assertEqual(ku.area, 3)


class TestStressDeath(unittest.TestCase):
    def test_will_test_and_heart_attack(self):
        b = battle(seed=3)
        k = b.heroes[0]
        b.rng = FakeRng(9)  # test Woli: 9 -> udręka
        b.add_stress(k, 10)
        self.assertEqual(k.affl, "udreka")
        self.assertEqual(k.stress, 0)
        b.add_stress(k, 10)
        self.assertTrue(k.dead)  # atak serca

    def test_deaths_door_and_death_die(self):
        b = battle()
        k = b.heroes[0]
        b.wound_hero(k, k.max_hp)
        self.assertTrue(k.dd)
        self.assertFalse(k.dead)
        b.rng = FakeRandomBelow(0.1)   # < 0.3 -> czaszka
        b.wound_hero(k, 1)
        self.assertTrue(k.dead)

    def test_heal_removes_deaths_door(self):
        b = battle()
        k = b.heroes[0]
        b.wound_hero(k, k.max_hp)
        b.heal_fighter(k, 3)
        self.assertFalse(k.dd)


class TestMonstersAndBosses(unittest.TestCase):
    def test_monster_targets_closest(self):
        b = battle(tile="kafel_2")
        m = b.monsters[0]
        sk = m.skills[0]  # Zamach, najbliższy
        for h in b.heroes:
            h.area = 0
        b.heroes[2].area = 1
        m.area = 2
        t = b._mtargets(m, sk)
        self.assertEqual(t[0], b.heroes[2])

    def test_garda_taunts(self):
        b = battle()
        b.heroes[1].stacks.append(["garda", None, 2])
        m = b.monsters[0]
        t = b._mtargets(m, m.skills[0])
        self.assertEqual(t[0], b.heroes[1])

    def test_boss_battle_has_no_round_limit(self):
        boss = Fighter(mcard=BOSSES["Fanatyk"])
        b = battle(monsters=[boss])
        self.assertTrue(b.boss)
        b.round_no = 10
        self.assertNotEqual(b.run_round(), "timeout")

    def test_quest_runs(self):
        r = run_quest(seed=11)
        self.assertGreaterEqual(r.rooms_cleared, 0)
        self.assertIsInstance(r.win, bool)

    def test_transformation_switches_form(self):
        b = battle(heroes=make_party(
            ["Wynaturzenie", "Kapłanka", "Oprych", "Awanturniczka"]))
        w = b.heroes[0]
        names = skills_in(b.legal_actions(w))
        self.assertIn("Transformacja w Bestię", names)
        self.assertNotIn("Szał", names)
        act = [a for a in b.legal_actions(w)
               if a.kind == "skill" and a.card.name == "Transformacja w Bestię"]
        b.apply_action(w, act[0])
        self.assertEqual(w.form, "bestia")
        w.slot = 0
        b.hero_slots[0] = w
        m = b.monsters[0]
        m.area = w.area
        names = skills_in(b.legal_actions(w))
        self.assertIn("Szał", names)
        self.assertNotIn("Kajdany", names)


class FakeRng:
    """randint zwraca stałą; shuffle/choice neutralne."""

    def __init__(self, roll):
        self.roll = roll

    def randint(self, a, b):
        return self.roll

    def random(self):
        return 0.99

    def shuffle(self, x):
        pass

    def choice(self, x):
        return x[0]


class FakeRandomBelow(FakeRng):
    def __init__(self, val):
        super().__init__(5)
        self.val = val

    def random(self):
        return self.val


if __name__ == "__main__":
    unittest.main()
