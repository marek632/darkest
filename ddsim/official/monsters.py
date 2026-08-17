"""Monster and boss cards (photos + rulebook extract).

Column previously mislabelled "Szybkość" in docs was actually Unik
(gold jagged icon). Monster speed is unknown -> assumed 2 (flagged).

stance_map: 4 entries (A, D, Z, W) -> skill index or K10 table
[(lo, hi, idx), ...]. Boss k10 tables read partially from card bottoms.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MSkill:
    name: str
    rule: str            # najblizszy|najdalszy|zestresowany|zatloczony|
                         # nazn_najdalszy|nazn_najblizszy|specjalna|summon
    rng: tuple = (0, 1)
    n: int = 1
    acc: int = 8
    crit: int = 0
    dmg: int = 0
    cdmg: int = 0
    fx: tuple = ()
    self_fx: tuple = ()
    bonus: tuple = ()


@dataclass(frozen=True)
class MonsterCard:
    name: str
    family: str          # plugawy|czlowiek|bestia|przedwieczny|demiurgiczny
    row: str             # front|tyl
    size: int = 1
    level: int = 1
    hp: int = 5
    speed: int = 2       # ASSUMPTION (unknown)
    unik: int = 0
    odp: tuple = ()
    niewr: tuple = ()
    skills: tuple = ()
    stance_map: tuple = (0, 0, 1, 1)
    actions: int = 1
    boss: bool = False
    retaliate: tuple = ()   # Brzemienne Serce: fx on attacker + self heal


MONSTERS = {}


def _mon(card):
    MONSTERS[card.name] = card


_mon(MonsterCard(
    "Strzelec bandytów", "czlowiek", "tyl", hp=8, unik=1, odp=("krwotok",),
    skills=(
        MSkill("Chmura śrutu", "zatloczony", rng=(1, 2), n=4, acc=7, crit=0,
               dmg=2, cdmg=4, fx=("oslab:2",)),
        MSkill("Pośpieszny strzał", "najblizszy", rng=(0, 1), acc=6, crit=1,
               dmg=3, cdmg=5, self_fx=("push_self:1",)),
    ),
    stance_map=(1, 1, 0, 0)))

_mon(MonsterCard(
    "Pluwacz", "bestia", "tyl", hp=5, unik=1, odp=("zaraza",),
    skills=(
        MSkill("Splunięcie", "nazn_najdalszy", rng=(1, 2), acc=9, crit=1,
               dmg=4, cdmg=6, fx=("oslab:2", "zaraza:1:3"),
               bonus=(("nazn", 2),)),
        MSkill("Ugryzienie", "nazn_najblizszy", rng=(0, 0), acc=8, crit=0,
               dmg=2, cdmg=4, fx=("zaraza:1:3",), bonus=(("nazn", 2),)),
    ),
    stance_map=(1, 1, 0, 0)))

_mon(MonsterCard(
    "Kościany Kapitan", "plugawy", "front", size=2, level=2, hp=33, unik=1,
    odp=("przesuwanie",), niewr=("krwotok", "zaraza"),
    skills=(
        MSkill("Dewastujące uderzenie", "najblizszy", rng=(0, 1), acc=9,
               crit=2, dmg=11, cdmg=17, fx=("push:1",)),
        MSkill("Wbicie w ziemię", "zatloczony", rng=(0, 0), n=4, acc=9,
               crit=1, dmg=5, cdmg=7, fx=("stun:2",)),
    ),
    stance_map=(((1, 6, 0), (7, 10, 1)), 0, 1, 1)))

_mon(MonsterCard(
    "Akolita Kultystów", "czlowiek", "tyl", hp=9, unik=1, odp=("oslab",),
    skills=(
        MSkill("Koszmarna inkantacja", "zestresowany", rng=(0, 3), acc=9,
               crit=0, dmg=1, cdmg=2, fx=("stress:1", "light:-1")),
        MSkill("Wezwanie przedwiecznych", "najdalszy", rng=(0, 3), n=2,
               acc=9, crit=1, dmg=1, cdmg=2, fx=("push:2",)),
        MSkill("Odprawa przedwiecznych", "najblizszy", rng=(0, 1), acc=9,
               crit=1, dmg=1, cdmg=2, fx=("push:2",)),
    ),
    stance_map=(2, 2, 1, 0)))

_mon(MonsterCard(
    "Kościany Dworzanin", "plugawy", "tyl", hp=7, unik=1,
    niewr=("krwotok",),
    skills=(
        MSkill("Kielich pokuszenia", "zestresowany", rng=(0, 2), n=2,
               acc=10, crit=0, dmg=3, cdmg=5, fx=("stress:1",)),
        MSkill("Ostrze w mroku", "najblizszy", rng=(0, 1), acc=7, crit=1,
               dmg=3, cdmg=5),
    ),
    stance_map=(1, 1, 0, 0)))

_mon(MonsterCard(
    "Kościany Kusznik", "plugawy", "tyl", hp=11, unik=1,
    niewr=("krwotok",),
    skills=(
        MSkill("Bełt", "nazn_najdalszy", rng=(1, 2), acc=9, crit=1, dmg=5,
               cdmg=8, bonus=(("nazn", 1),)),
        MSkill("Pchnięcie bagnetem", "najblizszy", rng=(0, 0), acc=8,
               crit=0, dmg=3, cdmg=5, self_fx=("push_self:1",)),
    ),
    stance_map=(1, 1, 0, 0)))

_mon(MonsterCard(
    "Gladiator Kultystów", "czlowiek", "front", hp=11, unik=0,
    odp=("stun",),
    skills=(
        MSkill("Szrama dawnych bogów", "najblizszy", rng=(0, 1), acc=8,
               crit=0, dmg=3, cdmg=5,
               fx=("krwotok:1:3", "oslab:2", "stress:1"),
               self_fx=("pull_self:1",)),
        MSkill("Cięcie z wyskoku", "najblizszy", rng=(0, 1), acc=5, crit=1,
               dmg=3, cdmg=5, bonus=(("nazn", 1),),
               self_fx=("pull_self:1",)),
    ),
    stance_map=(0, 0, 1, 1)))

_mon(MonsterCard(
    "Kościany Obrońca", "plugawy", "front", hp=10, unik=1,
    niewr=("krwotok",),
    skills=(
        # dmg um. 1/2 nieznane z przykładu instrukcji -> założone 4/5
        MSkill("Zamach", "najblizszy", rng=(0, 1), acc=8, crit=1, dmg=4,
               cdmg=6),
        MSkill("Martwy ciąg", "najblizszy", rng=(0, 1), acc=9, crit=1,
               dmg=5, cdmg=8),
        MSkill("Niechlujny zamach", "najdalszy", rng=(0, 3), acc=5, crit=0,
               dmg=3, cdmg=5, fx=("pull:1",)),
    ),
    stance_map=(0, 1, 2, 2)))

# ------------------------------- bossowie -------------------------------

BOSSES = {}


def _boss(card):
    BOSSES[card.name] = card


_boss(MonsterCard(
    "Prorok", "plugawy", "front", size=2, level=3, hp=151, unik=3,
    odp=("stun",), niewr=("przesuwanie",), boss=True, actions=2,
    skills=(
        MSkill("Mam cię na oku", "zatloczony", rng=(0, 1), n=2, acc=11,
               crit=1, dmg=3, cdmg=5, fx=("zaraza:1:2", "stress:1")),
        MSkill("Odrzucenie", "zatloczony", rng=(0, 1), n=4, acc=10, crit=1,
               dmg=3, cdmg=5, fx=("zaraza:3:3",)),
        MSkill("W gruz się obrócisz", "specjalna", rng=(0, 9), n=4, acc=10,
               crit=0, dmg=16, cdmg=24),
    ),
    stance_map=(((1, 5, 0), (6, 9, 1), (10, 10, 2)),) * 4))

_boss(MonsterCard(
    "Fanatyk", "czlowiek", "front", size=2, level=3, hp=72, unik=2,
    odp=("zaraza",), niewr=("przesuwanie",), boss=True, actions=2,
    skills=(
        MSkill("Słuszne potępienie", "zatloczony", rng=(0, 2), n=4, acc=12,
               crit=0, dmg=2, cdmg=4, fx=("stress:2",),
               self_fx=("wzmoc:3",)),
        MSkill("Pogromienie heretyków", "zestresowany", rng=(0, 1), acc=11,
               crit=1, dmg=6, cdmg=11, fx=("stun:1", "push:2", "stress:1")),
        MSkill("Sprawiedliwa furia", "zatloczony", rng=(0, 1), n=4, acc=11,
               crit=0, dmg=10, cdmg=14, fx=("stress:1",)),
    ),
    stance_map=(((1, 2, 0), (3, 6, 1), (7, 10, 2)),) * 4))

_boss(MonsterCard(
    "Serce Ciemności", "demiurgiczny", "front", size=2, level=3, hp=250,
    unik=3, odp=("oslab",), niewr=("stun", "przesuwanie"), boss=True,
    actions=2,
    skills=(
        MSkill("Ujrzyj prawdę", "zatloczony", rng=(0, 9), n=3, acc=12,
               crit=1, dmg=2, cdmg=3, fx=("stress:3", "light:-1")),
        MSkill("Nakłucie", "najblizszy", rng=(0, 9), acc=12, crit=2,
               dmg=14, cdmg=18, fx=("krwotok:3:3", "stress:1")),
        MSkill("Zniweczenie", "najdalszy", rng=(0, 9), acc=12, crit=2,
               dmg=14, cdmg=18, fx=("stun:1", "zaraza:3:3", "stress:1")),
    ),
    stance_map=(((1, 4, 0), (5, 7, 1), (8, 10, 2)),) * 4))

_boss(MonsterCard(
    "Brzemienne Serce", "przedwieczny", "front", size=2, level=3, hp=100,
    unik=3, odp=("zaraza",), niewr=("stun", "przesuwanie"), boss=True,
    actions=2, retaliate=("zaraza:2:3", "heal:2"),
    skills=(MSkill("Przywołanie", "summon"),),
    stance_map=(0, 0, 0, 0)))

_boss(MonsterCard(
    "Druga Forma Antenata", "przedwieczny", "front", size=2, level=3,
    hp=166, unik=2, niewr=("przesuwanie",), boss=True, actions=2,
    skills=(
        MSkill("Przetworzenie", "zatloczony", rng=(0, 1), n=2, acc=12,
               crit=2, dmg=9, cdmg=16,
               fx=("krwotok:3:3", "stress:1", "light:-1")),
        MSkill("Masowa anihilacja", "najdalszy", rng=(0, 2), acc=12,
               crit=1, dmg=4, cdmg=8, fx=("zaraza:2:4", "stress:1")),
        MSkill("Objęcia beznadziei", "najblizszy", rng=(0, 0), acc=12,
               crit=0, dmg=2, cdmg=4,
               fx=("oslab:2", "stress:2", "push:2")),
    ),
    stance_map=(((1, 2, 0), (3, 6, 1), (7, 10, 2)),) * 4))

_boss(MonsterCard(
    "Powłócząca Przeraza", "przedwieczny", "front", size=2, level=3,
    hp=109, unik=3, odp=("zaraza",), niewr=("stun", "przesuwanie"),
    boss=True, actions=2,
    skills=(
        MSkill("Rozprucie", "najblizszy", rng=(0, 1), acc=11, crit=1,
               dmg=7, cdmg=11, fx=("krwotok:3:2",)),
        MSkill("Negatywne wibracje", "zatloczony", rng=(0, 1), n=4, acc=11,
               crit=0, dmg=1, cdmg=2, fx=("shuffle_stances",)),
        MSkill("Rezonujący rozkład", "zatloczony", rng=(0, 1), n=4, acc=12,
               crit=1, dmg=2, cdmg=4, fx=("stress:2", "light:-1")),
    ),
    stance_map=(((1, 5, 0), (6, 8, 1), (9, 10, 2)),) * 4))

# Talia doboru potworów do zwykłej bitwy (poziom I; Kapitan II jako
# rzadki ciężki przeciwnik).
ENCOUNTER_DECK = [
    ("Strzelec bandytów", 3), ("Pluwacz", 3), ("Akolita Kultystów", 3),
    ("Kościany Dworzanin", 3), ("Kościany Kusznik", 3),
    ("Gladiator Kultystów", 3), ("Kościany Obrońca", 3),
    ("Kościany Kapitan", 1),
]
