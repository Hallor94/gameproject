# file: map/map_loader.py

import random

from config import constants
from map.map_manager import MapManager
from map.door_manager import Door
from utils.enums import TileOverlayState
from utils import globals as G

def load_test_map(screen_width, screen_height):
    TILE_HEIGHT = int(constants.TILE_BASE_HEIGHT)
    TILE_WIDTH = int(TILE_HEIGHT * constants.TILE_WIDTH_RATIO)

    MAP_ROWS = 3
    MAP_COLS = 5
    MAP_WIDTH = MAP_COLS * TILE_WIDTH
    MAP_HEIGHT = MAP_ROWS * TILE_HEIGHT

    # Visual offset only (not used by camera logic)
    map_draw_offset_x = (screen_width - MAP_WIDTH) // 2
    map_draw_offset_y = (screen_height - MAP_HEIGHT) // 2

    gamemap = MapManager(rows=MAP_ROWS, cols=MAP_COLS, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT)
    gamemap.offset_x = map_draw_offset_x
    gamemap.offset_y = map_draw_offset_y

    _generate_doors(gamemap)

    all_tiles = [tile for row in gamemap.tiles for tile in row if tile.walkable]
    fire_tiles = random.sample(all_tiles, 2)
    for tile in fire_tiles:
        G.tile_status_manager.set_tile_status(tile, TileOverlayState.FIRE)

    return gamemap


def _generate_doors(gamemap):
    """
    Connects tiles using a minimal spanning tree plus some random extra doors.
    """

    def get_neighbors(x, y, rows, cols):
        directions = [(1, 0), (0, 1)]
        return [(x + dx, y + dy) for dx, dy in directions if 0 <= x + dx < cols and 0 <= y + dy < rows]

    tile_lookup = {(tile.grid_pos[0], tile.grid_pos[1]): tile for row in gamemap.tiles for tile in row}
    rows = gamemap.rows
    cols = gamemap.cols

    edges = []
    for y in range(rows):
        for x in range(cols):
            for nx, ny in get_neighbors(x, y, rows, cols):
                a = tile_lookup[(x, y)]
                b = tile_lookup[(nx, ny)]
                direction = "horizontal" if x != nx else "vertical"
                edges.append((a, b, direction))

    random.shuffle(edges)
    parent = {}

    def find(t):
        while parent.get(t, t) != t:
            t = parent[t]
        return t

    def union(a, b):
        parent[find(a)] = find(b)

    seen_pairs = set()

    # First pass: connect all tiles with a minimum spanning tree
    for a, b, direction in edges:
        key = frozenset((a, b))
        if find(a) != find(b):
            gamemap.door_manager.add_door(Door(a, b, direction, open=True))
            union(a, b)
            seen_pairs.add(key)

    # Second pass: randomly add extra doors
    for a, b, direction in edges:
        key = frozenset((a, b))
        if key not in seen_pairs and random.random() < 0.8:
            is_open = random.random() < 0.9
            gamemap.door_manager.add_door(Door(a, b, direction, open=is_open))
            seen_pairs.add(key)
