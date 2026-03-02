# ui/componenets/loading_icon.py

import pygame
from utils.image_cache import icon_cache

class LoadingIcon:
    def __init__(self, frame_count=24, frame_duration=50):
        self.frames = [icon_cache.get(f"loading_{i}") for i in range(1, frame_count + 1)]
        self.frame_duration = frame_duration
        self.last_update = pygame.time.get_ticks()
        self.index = 0

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.frame_duration:
            self.index = (self.index + 1) % len(self.frames)
            self.last_update = now

    def draw(self, surface, pos):
        frame = self.frames[self.index]
        if frame:
            surface.blit(frame, pos)
