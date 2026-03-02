# file: animations/flicker.py

import math
import random

class FlickerEffect:
    def __init__(self, base_alpha=180, range_alpha=80, speed=0.02, seed=None):
        self.base = base_alpha
        self.range = range_alpha
        self.speed = speed
        self.time = random.uniform(0, 10) if seed is None else seed

    def update(self, dt=1):
        self.time += dt * self.speed

    def get_alpha(self):
        flicker = math.sin(self.time * 2.5) * 0.5 + 0.5  # 0–1
        return int(self.base + flicker * self.range)
