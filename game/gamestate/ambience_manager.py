# gamestate/ambience_manager.py

import random
import time
from animations.light_flicker import LightFlickerManager

class AmbienceManager:
    def __init__(self, gamemap):
        self.timer = 0
        self.interval = 20.0
        self.gamemap = gamemap
        self.light_flicker = LightFlickerManager()  # moved here

    def update(self, dt):
        self.light_flicker.update()

        self.timer += dt
        if self.timer < self.interval:
            return
        self.timer = 0

        candidates = [
            tile for row in self.gamemap.tiles for tile in row
            if not tile._flicker_active
        ]

        for tile in random.sample(candidates, k=min(2, len(candidates))):
            self.trigger_tile_flicker(tile)


    def trigger_tile_flicker(self, tile):
        """
        Controls flicker rules: frequency, style, maybe even sound or color.
        """
        self.light_flicker.trigger_flicker(tile)

    def trigger_map_flicker(self, duration=3.0):
        """
        Trigger a flicker across the whole map for visual effect.
        Each tile will get a randomized flicker that lasts ~duration seconds.
        """
        for row in self.gamemap.tiles:
            for tile in row:
                self.light_flicker.trigger_flicker(tile, duration=duration)
