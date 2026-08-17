"""Hero panels and level-I skill cards transcribed from photos.

Single source of truth: docs/CARDS_PL.md. Uncertain readings are marked
there; here they are encoded as the best-guess values.

Effect DSL (strings "kind:params"):
  krwotok:A:T   bleed A wounds for T turns      zaraza:A:T   blight
  stun:T  wzmoc:T  oslab:T  nazn:T  riposta:T  ochrona:T  garda:T
  push:N / pull:N            move target away from / toward the actor
  push_self:N / pull_self:N  move self away from / toward nearest enemy
  stress:N (may be negative) light:N  heal:N  rany_self:N
  usun:krwotok,zaraza        usun:stun,nazn
  transform:bestia / transform:czlowiek
"""

from __future__ import annotations

from dataclasses import dataclass, field

STANCES = ("A", "D", "Z", "W")  # kolejność aktywacji: Agresywna -> Wspierająca


@dataclass(frozen=True)
class SkillCard:
    name: str
    stances: str = "WZDA"        # letters of allowed stances
    rng: tuple = (0, 0)          # (min, max) distance in areas
    tgt: str = "enemy"           # enemy | ally | any | self | allies_all
    n: int = 1                   # max number of targets
    acc: int | None = None       # Dok threshold (None = no roll)
    crit: int = 0                # Krytyk threshold
    dmg: int = 0                 # wounds on hit (or heal on hit if heal)
    cdmg: int = 0                # wounds on crit
    heal: bool = False
    fx: tuple = ()               # effects on target (on hit)
    self_fx: tuple = ()          # personal effects (always apply)
    ally_fx: tuple = ()          # for tgt="any": effects when target is ally
    bonus: tuple = ()            # (("plugawy",1), ("nazn",2), ...)
    ignore_ochrona: bool = False
    form: str | None = None      # Wynaturzenie: required form


@dataclass(frozen=True)
class HeroClass:
    name: str
    hp: int
    speed: int
    unik: int
    odp: tuple = ()              # resistances
    skills: dict = field(default_factory=dict)
    forms: bool = False          # Wynaturzenie


def S(name, **kw):
    return SkillCard(name=name, **kw)


def _index(cards):
    return {c.name: c for c in cards}


HERO_CLASSES = {}


def _hero(name, hp, speed, unik, odp, cards, forms=False):
    HERO_CLASSES[name] = HeroClass(
        name=name, hp=hp, speed=speed, unik=unik, odp=tuple(odp),
        skills=_index(cards), forms=forms)


_hero("Krzyżowiec", 17, 1, 0, ("stun",), [
    S("Kara boska", stances="DA", rng=(0, 0), acc=9, crit=0, dmg=7, cdmg=13,
      bonus=(("plugawy", 1),)),
    S("Ogłuszający cios", stances="DA", rng=(0, 0), acc=9, crit=0, dmg=4,
      cdmg=8, fx=("stun:1",)),
    S("Święta lanca", stances="WZ", rng=(1, 1), acc=9, crit=1, dmg=7, cdmg=13,
      self_fx=("pull_self:1",), bonus=(("plugawy", 1),)),
    S("Bastion wiary", stances="DA", tgt="self",
      self_fx=("ochrona:2", "garda:3", "light:2")),
    S("Inspirujący okrzyk", stances="WZDA", rng=(0, 0), tgt="ally",
      heal=True, dmg=1, cdmg=1, fx=("stress:-1", "light:1")),
    S("Pierwsza pomoc", stances="WZDA", rng=(0, 1), tgt="ally", heal=True,
      acc=12, crit=2, dmg=2, cdmg=4),
    S("Żarliwe oskarżenie", stances="DA", rng=(1, 1), n=2, acc=9, crit=0,
      dmg=5, cdmg=9),
])

_hero("Kapłanka", 12, 1, 0, ("krwotok",), [
    S("Gwiazda poranna", stances="DA", rng=(1, 1), acc=9, crit=0, dmg=5,
      cdmg=9, bonus=(("plugawy", 1),)),
    S("Oślepiająca światłość", stances="WZD", rng=(1, 1), acc=9, crit=1,
      dmg=2, cdmg=4, fx=("stun:1", "light:1")),
    S("Boskie pocieszenie", stances="WZD", rng=(1, 1), tgt="ally", n=3,
      heal=True, acc=12, crit=3, dmg=2, cdmg=3, self_fx=("heal:2",)),
    S("Osąd", stances="WZ", rng=(1, 2), acc=9, crit=1, dmg=4, cdmg=8,
      self_fx=("heal:2",)),
    S("Boża łaska", stances="WZ", rng=(0, 1), tgt="ally", heal=True,
      acc=12, crit=3, dmg=3, cdmg=5),
    S("Oświecenie", stances="WZ", rng=(1, 2), acc=9, crit=0, dmg=2, cdmg=4,
      fx=("oslab:1", "light:1")),
    S("Ręka światłości", stances="DA", rng=(1, 1), acc=9, crit=1, dmg=3,
      cdmg=6, self_fx=("wzmoc:3",), bonus=(("plugawy", 1),)),
])

_hero("Oprych", 12, 2, 1, ("stun",), [
    S("Doskok", stances="WZDA", rng=(1, 1), acc=9, crit=1, dmg=4, cdmg=8,
      self_fx=("riposta:2", "pull_self:1")),
    S("Strzał z bliska", stances="WZD", rng=(0, 0), acc=10, crit=1, dmg=9,
      cdmg=15, self_fx=("push_self:1",), fx=("push:1",)),
    S("Strzał naprowadzający", stances="WZ", rng=(1, 2), acc=10, crit=0,
      dmg=2, cdmg=3, self_fx=("wzmoc:3",)),
    S("Puszczenie krwi", stances="ZDA", rng=(0, 0), acc=10, crit=0, dmg=5,
      cdmg=9, fx=("krwotok:2:2",)),
    S("Siekańce", stances="ZD", rng=(0, 1), n=3, acc=8, crit=0, dmg=3,
      cdmg=5, fx=("oslab:1",)),
    S("Wystrzał", stances="WZ", rng=(1, 2), acc=9, crit=1, dmg=5, cdmg=9,
      bonus=(("nazn", 2),)),
    S("Ohydne cięcie", stances="DA", rng=(0, 0), acc=9, crit=1, dmg=7,
      cdmg=11),
])

_hero("Awanturniczka", 14, 2, 1, ("krwotok",), [
    S("Szerokie cięcie", stances="ZDA", rng=(1, 1), n=3, acc=8, crit=0,
      dmg=4, cdmg=6, self_fx=("pull_self:1",)),
    S("Okrutne cięcie", stances="DA", rng=(0, 0), acc=9, crit=1, dmg=7,
      cdmg=12),
    S("Żelazny łabędź", stances="DA", rng=(2, 2), acc=9, crit=1, dmg=7,
      cdmg=12),
    S("Rozlew krwi", stances="DA", rng=(0, 0), acc=9, crit=1, dmg=9,
      cdmg=14, self_fx=("rany_self:3",), fx=("krwotok:3:2",)),
    S("Każdy krwawi", stances="ZDA", rng=(1, 1), acc=9, crit=0, dmg=5,
      cdmg=8, fx=("krwotok:2:2",)),
    S("Przypływ adrenaliny", stances="WZDA", tgt="self",
      self_fx=("usun:krwotok,zaraza", "wzmoc:3")),
    S("Barbarzyński ryk", stances="DA", rng=(0, 0), n=2, acc=10,
      fx=("stun:1",)),
])

_hero("Okultysta", 10, 2, 1, ("oslab",), [
    S("Mroczna rekonstrukcja", stances="WZ", rng=(0, 1), tgt="ally",
      heal=True, acc=9, crit=3, dmg=4, cdmg=8, fx=("krwotok:1:2",)),
    S("Uścisk demona", stances="WZD", rng=(2, 2), acc=9, crit=1, dmg=3,
      cdmg=4, fx=("pull:2",)),
    S("Artyleria otchłani", stances="WZ", rng=(2, 2), n=2, acc=9, crit=0,
      dmg=4, cdmg=6, bonus=(("przedwieczny", 1),)),
    S("Klątwa osłabienia", stances="WZD", rng=(1, 2), acc=10, crit=1,
      dmg=2, cdmg=3, fx=("oslab:2",)),
    S("Cięcie ofiarne", stances="ZDA", rng=(0, 0), acc=8, crit=1, dmg=5,
      cdmg=7, bonus=(("przedwieczny", 1),)),
    S("Przekleństwo", stances="WZ", rng=(1, 2), acc=10, crit=1, dmg=1,
      cdmg=2, fx=("nazn:2",)),
    S("Macki otchłani", stances="DA", rng=(1, 1), acc=9, crit=1, dmg=3,
      cdmg=4, fx=("stun:2", "light:-1")),
])

_hero("Arlekin", 10, 3, 2, ("oslab",), [
    S("Pchnięcie sztyletem", stances="WZDA", rng=(1, 1), acc=9, crit=1,
      dmg=5, cdmg=7, self_fx=("pull_self:1",), ignore_ochrona=True),
    S("Ukłon", stances="DA", rng=(0, 0), acc=14, crit=1, dmg=7, cdmg=10,
      self_fx=("push_self:3",)),
    S("Solówka", stances="WZ", rng=(2, 2), acc=12,
      self_fx=("wzmoc:2", "pull_self:2"), fx=("stun:1",)),
    S("Inspirująca nuta", stances="WZ", rng=(0, 0), tgt="ally", n=2,
      self_fx=("stress:-1",), fx=("stress:-1",)),
    S("Heroiczna ballada", stances="WZ", rng=(1, 1), tgt="ally", n=2,
      self_fx=("wzmoc:2",), fx=("wzmoc:2",)),
    S("Żniwa", stances="DA", rng=(1, 1), n=2, acc=9, crit=0, dmg=3, cdmg=4,
      fx=("krwotok:2:2",)),
    S("Urwany wątek", stances="ZD", rng=(1, 1), acc=10, crit=1, dmg=4,
      cdmg=6, fx=("krwotok:3:1",)),
])

_hero("Badaczka Zarazy", 11, 3, 0, ("zaraza",), [
    S("Panaceum", stances="WZ", rng=(0, 0), tgt="ally", heal=True, acc=20,
      crit=1, dmg=1, cdmg=2, fx=("usun:krwotok,zaraza",)),
    S("Trujący podmuch", stances="WZD", rng=(1, 1), acc=9, crit=1, dmg=2,
      cdmg=4, fx=("zaraza:4:2", "oslab:1")),
    S("Granat zarazy", stances="WZ", rng=(2, 2), n=2, acc=9, crit=0,
      dmg=1, cdmg=2, fx=("zaraza:3:2",)),
    S("Nacięcie", stances="ZDA", rng=(0, 0), acc=9, crit=1, dmg=5, cdmg=8,
      fx=("krwotok:2:2",)),
    S("Gaz oślepiający", stances="WZ", rng=(1, 2), n=2, acc=9,
      fx=("stun:1",)),
    S("Sole trzeźwiące", stances="WZ", rng=(0, 0), tgt="ally",
      fx=("wzmoc:3",)),
    S("Podmuch zamętu", stances="WZD", rng=(1, 1), acc=9,
      fx=("push:2", "stun:1")),
])

_hero("Kuszniczka", 14, 1, 0, ("przesuwanie",), [
    S("Bandażowanie", stances="WZ", rng=(0, 1), tgt="ally", heal=True,
      acc=8, crit=0, dmg=4, cdmg=6, self_fx=("wzmoc:2",)),
    S("Priorytetowy cel", stances="WZ", rng=(1, 2), acc=10,
      fx=("nazn:2",)),
    S("Bolas", stances="WZ", rng=(1, 1), acc=10, crit=1, dmg=3, cdmg=6,
      self_fx=("push_self:1",), fx=("push:2",)),
    S("Na oślep", stances="WZDA", rng=(0, 2), acc=8, crit=0, dmg=5,
      cdmg=8, self_fx=("push_self:1",)),
    S("Ogień zaporowy", stances="WZ", rng=(1, 2), n=2, acc=9, crit=0,
      dmg=2, cdmg=4, fx=("oslab:1",)),
    S("Snajperska precyzja", stances="WZ", rng=(2, 2), acc=9, crit=1,
      dmg=6, cdmg=9, bonus=(("nazn", 3),)),
    S("Flara", stances="WZ", rng=(1, 2), tgt="any", n=2, acc=10,
      fx=("oslab:2",), ally_fx=("usun:stun,nazn",),
      self_fx=("usun:stun,nazn",)),
])

_hero("Hiena Cmentarna", 11, 3, 1, ("zaraza",), [
    S("Rzut sztyletem", stances="WZD", rng=(1, 2), acc=9, crit=2, dmg=4,
      cdmg=7, bonus=(("zaraza", 1), ("nazn", 2))),
    S("Rozłupanie czaszki", stances="ZDA", rng=(0, 0), acc=9, crit=1,
      dmg=4, cdmg=7, ignore_ochrona=True),
    S("Zatrute strzałki", stances="WZ", rng=(1, 2), acc=10, crit=1,
      dmg=2, cdmg=4, fx=("zaraza:2:3",)),
    S("Wypad", stances="WZ", rng=(2, 2), acc=10, crit=1, dmg=7, cdmg=11,
      self_fx=("pull_self:2",), bonus=(("zaraza", 2),)),
    S("Nawałnica sztyletów", stances="ZD", rng=(1, 1), n=2, acc=9, crit=0,
      dmg=3, cdmg=6),
    S("Odsunięcie w cień", stances="DA", tgt="self",
      self_fx=("wzmoc:2", "push_self:2")),
    S("Środki dopingujące", stances="WZDA", tgt="self",
      self_fx=("wzmoc:2", "usun:krwotok,zaraza")),
])

_hero("Wynaturzenie", 13, 2, 1, ("zaraza",), [
    S("Potworna żółć", stances="ZD", rng=(1, 2), n=2, acc=10, crit=0,
      dmg=2, cdmg=3, fx=("zaraza:2:2",), form="czlowiek"),
    S("Kajdany", stances="ZD", rng=(1, 1), acc=10, crit=0, dmg=4, cdmg=6,
      fx=("stun:1",), form="czlowiek"),
    S("Rozgrzeszenie", stances="WZ", tgt="self", heal=True, acc=12,
      crit=1, dmg=2, cdmg=4, self_fx=("stress:-1",), form="czlowiek"),
    S("Transformacja w Bestię", stances="WZDA", tgt="allies_all",
      self_fx=("transform:bestia", "wzmoc:3", "heal:6"),
      ally_fx=("stress:2",), form="czlowiek"),
    S("Roztrzaskanie", stances="DA", rng=(1, 1), acc=8, crit=0, dmg=7,
      cdmg=10, self_fx=("pull_self:1", "stress:1"),
      fx=("push:2", "oslab:1"), form="bestia"),
    S("Szał", stances="DA", rng=(0, 0), acc=9, crit=1, dmg=9, cdmg=12,
      self_fx=("stress:1",), form="bestia"),
    S("Pokiereszowanie", stances="DA", rng=(0, 0), n=2, acc=9, crit=0,
      dmg=5, cdmg=9, self_fx=("wzmoc:2", "stress:1"), form="bestia"),
    S("Transformacja w człowieka", stances="WZDA", tgt="allies_all",
      self_fx=("transform:czlowiek", "oslab:3", "stress:-1"),
      ally_fx=("stress:-1",), form="bestia"),
], forms=True)

_hero("Łowca Nagród", 14, 2, 1, ("stun",), [
    S("Do mnie", stances="WZDA", rng=(2, 2), acc=9, crit=0, dmg=2, cdmg=4,
      fx=("nazn:2", "pull:2")),
    S("Wykonanie wyroku", stances="ZDA", rng=(0, 0), acc=9, crit=1, dmg=6,
      cdmg=10, bonus=(("czlowiek", 1), ("nazn", 2))),
    S("Wyrok śmierci", stances="WZD", rng=(0, 2), acc=10,
      self_fx=("wzmoc:2",), fx=("nazn:3", "oslab:2")),
    S("Egzekucja", stances="ZDA", rng=(0, 1), acc=9, crit=1, dmg=6,
      cdmg=10, bonus=(("stun", 2),)),
    S("Podbródkowy", stances="DA", rng=(0, 0), acc=9, crit=0, dmg=3,
      cdmg=5, fx=("stun:1", "push:2")),
    S("Granat błyskowy", stances="WZ", rng=(1, 2), acc=10,
      fx=("stun:1", "push:1")),
    S("Kolczatki", stances="WZD", rng=(2, 2), acc=9, crit=1, dmg=1,
      cdmg=2, fx=("krwotok:2:3", "oslab:1")),
])

# Curated default loadouts (3 of 7; transformacje Wynaturzenia zawsze w grze)
DEFAULT_LOADOUT = {
    "Krzyżowiec": ("Kara boska", "Święta lanca", "Pierwsza pomoc"),
    "Kapłanka": ("Boskie pocieszenie", "Osąd", "Boża łaska"),
    "Oprych": ("Wystrzał", "Puszczenie krwi", "Doskok"),
    "Awanturniczka": ("Żelazny łabędź", "Szerokie cięcie", "Okrutne cięcie"),
    "Okultysta": ("Mroczna rekonstrukcja", "Uścisk demona",
                  "Artyleria otchłani"),
    "Arlekin": ("Pchnięcie sztyletem", "Ukłon", "Żniwa"),
    "Badaczka Zarazy": ("Trujący podmuch", "Granat zarazy",
                        "Gaz oślepiający"),
    "Kuszniczka": ("Snajperska precyzja", "Priorytetowy cel",
                   "Bandażowanie"),
    "Hiena Cmentarna": ("Wypad", "Rzut sztyletem", "Zatrute strzałki"),
    "Wynaturzenie": ("Kajdany", "Szał", "Pokiereszowanie"),
    "Łowca Nagród": ("Wyrok śmierci", "Wykonanie wyroku", "Podbródkowy"),
}

BOX_PARTY = ("Krzyżowiec", "Kapłanka", "Oprych", "Awanturniczka")
