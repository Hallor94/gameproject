# file: animations/light_flicker.py

import time
import random

class LightFlickerManager:
    def __init__(self):
        self.active_tiles = set()

    def trigger_flicker(self, tile, now=None, duration=2.5):
        if getattr(tile, "_flicker_active", False):
            return  # Already flickering

        now = now or time.time()
        end_time = now + duration
        sequence = []

        t = now
        while t < end_time:
            t += random.uniform(0.05, 0.15)  # off delay
            sequence.append((t, False))
            t += random.uniform(0.1, 0.25)   # on delay
            sequence.append((t, True))

        tile._flicker_sequence = sequence
        tile._flicker_index = 0
        tile._flicker_active = True
        self.active_tiles.add(tile)


    def update(self):
        now = time.time()
        finished = set()

        for tile in self.active_tiles:
            seq = getattr(tile, "_flicker_sequence", [])
            i = getattr(tile, "_flicker_index", 0)

            while i < len(seq) and now >= seq[i][0]:
                tile.light_on = seq[i][1]
                i += 1

            tile._flicker_index = i
            if i >= len(seq):
                tile._flicker_active = False
                tile.light_on = tile.light_baseline_on
                finished.add(tile)

        self.active_tiles -= finished