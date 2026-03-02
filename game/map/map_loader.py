from map.map_manager import MapManager
from map.door import Door
from config import constants
import random

def load_test_map(screen_width, screen_height):
    TILE_HEIGHT = int(constants.TILE_BASE_HEIGHT * 1.4)  # 40% larger
    TILE_WIDTH = int(TILE_HEIGHT * 1.6)

    MAP_ROWS = 3
    MAP_COLS = 5
    MAP_WIDTH = MAP_COLS * TILE_WIDTH
    MAP_HEIGHT = MAP_ROWS * TILE_HEIGHT

    OFFSET_X = (screen_width - MAP_WIDTH) // 2
    OFFSET_Y = (screen_height - MAP_HEIGHT) // 2

    gamemap = MapManager(rows=MAP_ROWS, cols=MAP_COLS, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT)
    gamemap.offset_x = OFFSET_X
    gamemap.offset_y = OFFSET_Y

    _generate_doors(gamemap)

    return gamemap


def _generate_doors(gamemap):
    def get_neighbors(x, y, rows, cols):
        directions = [(1, 0), (0, 1)]  # Only right/down neighbors
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

    # Minimum set of doors for connectivity
    for a, b, direction in edges:
        key = frozenset((a, b))
        if find(a) != find(b):
            gamemap.doors.append(Door(a, b, direction, open=True))
            union(a, b)
            seen_pairs.add(key)

    # Additional random doors
    for a, b, direction in edges:
        key = frozenset((a, b))
        if key not in seen_pairs:
            if random.random() < 0.8:
                is_open = random.random() < 0.9
                gamemap.doors.append(Door(a, b, direction, open=is_open))
                seen_pairs.add(key)

