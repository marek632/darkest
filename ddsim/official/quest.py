"""Quest wrapper: a sequence of battles with persistent heroes, light
track and rest points between rooms.

Adaptation layer (official quest cards not photographed): 3 monster
rooms, light -1 after each room, 4 rest points between rooms
(1 point = heal 1 wound OR remove 1 stress, requires cleared room),
timeout in any room = quest failed (heroes retreat, +1 stress).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .battle import Battle, Fighter
from .board import TILES
from .cards import DEFAULT_LOADOUT, HERO_CLASSES
from .monsters import BOSSES, ENCOUNTER_DECK, MONSTERS

N_ROOMS = 3
REST_POINTS = 4
LIGHT_START = 5


@dataclass
class QuestResult:
    win: bool
    deaths: int
    rooms_cleared: int
    timeout: bool
    final_light: int


def make_party(spec=None):
    """spec: list of names or (name, loadout) tuples."""
    from .cards import BOX_PARTY
    spec = spec or BOX_PARTY
    party = []
    for item in spec:
        if isinstance(item, str):
            name, loadout = item, DEFAULT_LOADOUT[item]
        else:
            name, loadout = item
        party.append(Fighter(cls=HERO_CLASSES[name], loadout=loadout))
    return party


def gen_encounter(rng):
    monsters = []
    free = 4
    tries = 0
    while free > 0 and tries < 50:
        tries += 1
        names = [n for n, w in ENCOUNTER_DECK for _ in range(w)]
        card = MONSTERS[rng.choice(names)]
        if card.size <= free:
            monsters.append(Fighter(mcard=card))
            free -= card.size
    return monsters


def _rest(heroes, points):
    for _ in range(points):
        alive = [h for h in heroes if not h.dead]
        if not alive:
            return
        worst = max(alive, key=lambda h: max(
            (h.max_hp - h.hp) / h.max_hp + (2.0 if h.dd else 0.0),
            h.stress / 10.0))
        if (worst.max_hp - worst.hp) / worst.max_hp + \
                (2.0 if worst.dd else 0.0) >= worst.stress / 10.0:
            worst.hp = min(worst.max_hp, worst.hp + 1)
            if worst.dd and worst.hp > 0:
                worst.dd = False
        else:
            worst.stress = max(0, worst.stress - 1)


def run_quest(party_spec=None, seed=0, policy=None, on_event=None,
              n_rooms=N_ROOMS, boss=None):
    rng = random.Random(seed)
    heroes = make_party(party_spec)
    light = LIGHT_START
    tiles = list(TILES)
    rooms_cleared = 0
    timeout = False
    total_rooms = n_rooms + (1 if boss else 0)
    for room in range(total_rooms):
        for h in heroes:
            h.battle_reset()
        alive = [h for h in heroes if not h.dead]
        if not alive:
            break
        is_boss_room = boss and room == total_rooms - 1
        if is_boss_room:
            monsters = [Fighter(mcard=BOSSES[boss])]
            monsters += gen_encounter(rng)[:1]
        else:
            monsters = gen_encounter(rng)
        b = Battle(alive, monsters, rng.choice(tiles), light, rng,
                   policy=policy, on_event=on_event)
        result = b.run()
        light = b.light
        if result == "win":
            rooms_cleared += 1
            if on_event:
                on_event("room_cleared", room)
        elif result == "timeout":
            timeout = True
            break
        else:
            break
        if room < total_rooms - 1:
            _rest(heroes, REST_POINTS)
            light = max(0, light - 1)
    win = rooms_cleared == total_rooms
    deaths = sum(1 for h in heroes if h.dead)
    res = QuestResult(win=win, deaths=deaths, rooms_cleared=rooms_cleared,
                      timeout=timeout, final_light=light)
    if on_event:
        on_event("run_end", res)
    return res
