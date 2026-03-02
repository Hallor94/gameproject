import os
import json

TILE_DIRS = ["data/tiles/base", "data/tiles/custom"]

def load_tile_types():
    tiles = []
    for folder in TILE_DIRS:
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                with open(os.path.join(folder, filename), "r") as f:
                    tiles.append(json.load(f))
    return tiles
