# file: map/map_generator.py

import glob
import os
import random
from .tile import Tile, TileVisibility
from utils import image_cache
from utils.json_loader import load_all_json_entries
from utils import globals as G

TILE_LIMITS = {
    "sleeping": 2,
    "kitchen": 1,
    "canteen": 1,
    "storage": 3,
    "armory": 2,
    "power": 1,
    "lock": 1,
    "corridor": -1,
    "office": 2
}

DEFAULT_TILE = {
    "type": "empty",
    "name": "Empty",
    "actions": [],
    "walkable": True
}

def generate_static_map(rows, cols, tile_width, tile_height):
    tile_types = load_all_json_entries("data/tiles")
    tiles_flat = rows * cols
    tile_pool = []

    for tile_type in tile_types:
        type_id = tile_type["type"]
        limit = TILE_LIMITS.get(type_id, -1)
        if limit == -1:
            tile_pool.extend([tile_type] * tiles_flat)
        else:
            tile_pool.extend([tile_type] * limit)

    if not tile_pool:
        tile_pool = [DEFAULT_TILE] * tiles_flat

    random.shuffle(tile_pool)
    tile_pool = tile_pool[:tiles_flat]

    unique_tile_types = {tile["type"] for tile in tile_pool}
    preload_images = set()
    for tile_type in unique_tile_types:
        pattern = os.path.join("assets/tiles/base", f"{tile_type}*.png")
        images = glob.glob(pattern)
        preload_images.update(images)

    image_cache.preload_tile_backgrounds(tile_types=unique_tile_types, size=(tile_width, tile_height))

    tiles = []
    index = 0
    for row in range(rows):
        tile_row = []
        for col in range(cols):
            tile_type = tile_pool[index] if index < len(tile_pool) else DEFAULT_TILE
            tile = Tile(col, row, tile_width, tile_height, tile_type)
            tile.visibility_state = TileVisibility.HIDDEN
            G.loot_manager.spawn_loot_for_tile(tile)
            tile_row.append(tile)
            index += 1
        tiles.append(tile_row)

    return tiles