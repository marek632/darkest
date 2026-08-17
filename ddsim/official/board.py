"""Room tiles (areas + capacities + adjacency) and formation helpers.

Tile geometry is an approximation of the photographed tiles 2/5/6
(zone graphs redrawn from photos; exact shapes flagged as approximate in
docs/CARDS_PL.md). Start areas: gold = heroes, red = monsters.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class RoomTile:
    name: str
    caps: tuple                  # capacity per area (in occupancy points)
    adj: tuple                   # tuple of (a, b) undirected edges
    hero_start: tuple            # two gold start areas
    monster_start: tuple         # two red start areas

    @property
    def n(self):
        return len(self.caps)

    def neighbors(self, a):
        out = []
        for x, y in self.adj:
            if x == a:
                out.append(y)
            elif y == a:
                out.append(x)
        return out

    def dist(self, a, b):
        return DIST[self.name][a][b]


TILES = {
    # kafel 5: 2x2 zones
    "kafel_5": RoomTile("kafel_5", caps=(4, 4, 4, 4),
                        adj=((0, 1), (0, 2), (1, 3), (2, 3)),
                        hero_start=(0, 2), monster_start=(1, 3)),
    # kafel 2: 2x3 grid  0 1 2 / 3 4 5
    "kafel_2": RoomTile("kafel_2", caps=(3, 4, 3, 3, 4, 3),
                        adj=((0, 1), (1, 2), (3, 4), (4, 5), (0, 3),
                             (1, 4), (2, 5)),
                        hero_start=(0, 3), monster_start=(2, 5)),
    # kafel 6: L-shaped chain with a branch
    "kafel_6": RoomTile("kafel_6", caps=(2, 4, 4, 3, 2),
                        adj=((0, 1), (1, 2), (2, 3), (3, 4)),
                        hero_start=(0, 1), monster_start=(3, 4)),
}

MAX_AREAS = max(t.n for t in TILES.values())


def _all_dist(tile):
    out = []
    for s in range(tile.n):
        d = [99] * tile.n
        d[s] = 0
        q = deque([s])
        while q:
            a = q.popleft()
            for b in tile.neighbors(a):
                if d[b] > d[a] + 1:
                    d[b] = d[a] + 1
                    q.append(b)
        out.append(tuple(d))
    return tuple(out)


DIST = {name: _all_dist(t) for name, t in TILES.items()}
