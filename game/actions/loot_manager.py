# file: actions/loot_manager.py

from utils import globals as G
from utils.image_cache import get_popup_image
import pygame
import random

class LootManager:
    def __init__(self):
        pass  # No need to store tile anymore

    def start_looting(self, tile):
        if tile.loot_count <= 0:
            return

        tile.loot_count -= 1
        if tile.loot_count <= 0:
            tile.has_loot = False

        image = get_popup_image("lootOpen")

        G.message_manager.show_center_dialogue(
            text="Look's like you found yourselves some nice fancy loot right there.",
            title="You found something!",
            width=500,
            duration=None,
            image=image  # Must be handled in message_manager.py
        )

    def spawn_loot_for_tile(self, tile):
        if random.random() < 0.6:  # 60% chance for no loot
            tile.loot_count = 0
            tile.has_loot = False
        else:
            tile.loot_count = random.randint(1, 3)
            tile.has_loot = True
