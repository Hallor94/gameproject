# file: map/visibility_manager.py

from utils import globals as G
from utils.enums import Difficulty, FogOfWarMode
from .tile import TileVisibility

# file: map/visibility_manager.py

def update_tile_visibility(tiles, player_tiles, get_adjacent_fn, can_see_fn):
    fog_mode = lambda: G.gamemap.fog_mode
    difficulty = G.difficulty
    if fog_mode == FogOfWarMode.NORMAL:
        for row in tiles:
            for tile in row:
                if tile.visibility_state == TileVisibility.VISIBLE:
                    tile.visibility_state = TileVisibility.DISCOVERED

    elif fog_mode == FogOfWarMode.KNOWN_LAYOUT:
        for row in tiles:
            for tile in row:
                tile.visibility_state = TileVisibility.DISCOVERED

    elif fog_mode == FogOfWarMode.BOARDGAME:
        for row in tiles:
            for tile in row:
                tile.visibility_state = TileVisibility.VISIBLE
        return

    for tile in player_tiles:
        if tile is None:
            continue
        tile.visibility_state = TileVisibility.VISIBLE
        for neighbor in get_adjacent_fn(tile):
            if can_see_fn(tile, neighbor):
                # Hardcore mode blocks visibility if light is off
                if difficulty == Difficulty.HARDCORE and not neighbor.light_on:
                    continue
                neighbor.visibility_state = TileVisibility.VISIBLE


def get_adjacent_tiles(tile, grid, rows, cols):
    x, y = tile.grid_pos
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    neighbors = []
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= ny < rows and 0 <= nx < cols:
            neighbors.append(grid[ny][nx])
    return neighbors

def can_see_through(tile_a, tile_b, door_manager):
    door = door_manager.get_door_between(tile_a, tile_b)
    return door is not None and door.open
