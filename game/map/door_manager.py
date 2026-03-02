# file: map/door_manager.py

import os
import glob
import random
import pygame
from map.tile import Tile
from utils import image_cache
from utils import globals as G
from utils.logger import log_warn
from .tile import TileVisibility


class Door:
    door_keys = []
    hatch_keys = []
    tile_width = 100
    tile_height = 100

    @classmethod
    def preload_images(cls, tile_width, tile_height):
        cls.tile_width = tile_width
        cls.tile_height = tile_height

        door_paths = glob.glob(os.path.join("assets/map", "door*.png"))
        hatch_paths = glob.glob(os.path.join("assets/map", "hatch*.png"))

        cls.door_keys = []
        cls.hatch_keys = []

        for path in door_paths + hatch_paths:
            key = os.path.splitext(os.path.basename(path))[0]
            try:
                img = pygame.image.load(path).convert_alpha()
                scaled = pygame.transform.smoothscale(img, (tile_width // 2, tile_height // 4))
                image_cache._cache[key] = scaled
                if "door" in key:
                    cls.door_keys.append(key)
                elif "hatch" in key:
                    cls.hatch_keys.append(key)
            except Exception as e:
                log_warn("DoorManager", f"Failed to preload image {path}: {e}", file=__file__)

    def __init__(self, tile_a, tile_b, direction, open=True):
        self.tile_a = tile_a
        self.tile_b = tile_b
        self.direction = direction
        self.open = open

        tile_width = self.tile_a.world_rect.width
        tile_height = self.tile_a.world_rect.height

        if direction == "horizontal":
            key = random.choice(self.__class__.door_keys) if self.__class__.door_keys else None
        else:
            key = random.choice(self.__class__.hatch_keys) if self.__class__.hatch_keys else None

        if key:
            self.base_image = image_cache.get_scaled_image(key, (tile_width // 2, tile_height // 4))
        else:
            log_warn("DoorManager", "No door/hatch images preloaded, using fallback", file=__file__)
            self.base_image = pygame.Surface((tile_width // 2, tile_height // 4), pygame.SRCALPHA)
            pygame.draw.rect(self.base_image, (255, 0, 0), self.base_image.get_rect(), 2)

        if direction == "horizontal":
            self.base_size = (int(tile_width * 0.05), int(tile_height * 0.69))
        else:
            self.base_size = (int(tile_width * 0.2), int(tile_height * 0.15))

        self._last_scale = None
        self._cached_img = None

    def draw(self, surface, offset_x=0, offset_y=0):
        scale = G.camera_scale

        if self._last_scale != scale:
            draw_w = int(self.base_size[0] * scale)
            draw_h = int(self.base_size[1] * scale)
            self._cached_img = pygame.transform.smoothscale(self.base_image, (draw_w, draw_h))
            self._last_scale = scale

        img = self._cached_img
        center_x, center_y = self._get_screen_center_between(offset_x, offset_y)

        if self.direction == "horizontal":
            rect_a = self.tile_a.get_screen_rect(scale, offset_x, offset_y)
            img_rect = img.get_rect(midbottom=(center_x, rect_a.bottom))
        else:
            img_rect = img.get_rect(center=(center_x, center_y))

        surface.blit(img, img_rect)

        outline_radius = int(12 * scale)
        indicator_radius = int(10 * scale)
        indicator_color = (0, 255, 0) if self.open else (255, 0, 0)
        indicator_y = img_rect.centery - (int(10 * scale) if self.direction == "horizontal" else 0)

        pygame.draw.circle(surface, (0, 0, 0), (img_rect.centerx, indicator_y), outline_radius)
        pygame.draw.circle(surface, indicator_color, (img_rect.centerx, indicator_y), indicator_radius)

    def _get_screen_center_between(self, offset_x, offset_y):
        scale = G.camera_scale
        rect_a = self.tile_a.get_screen_rect(scale, offset_x, offset_y)
        rect_b = self.tile_b.get_screen_rect(scale, offset_x, offset_y)

        screen_cx = (rect_a.centerx + rect_b.centerx) // 2
        screen_cy = (rect_a.centery + rect_b.centery) // 2
        return screen_cx, screen_cy


class DoorManager:
    def __init__(self, tile_width, tile_height):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.doors = []
        Door.preload_images(tile_width, tile_height)

    def add_door(self, door):
        self.doors.append(door)

    def get_door_between(self, tile1, tile2):
        key = frozenset((tile1, tile2))
        for door in self.doors:
            if frozenset((door.tile_a, door.tile_b)) == key:
                return door
        return None

    def can_move_between(self, tile1, tile2):
        door = self.get_door_between(tile1, tile2)
        if door:
            return door.open
        return False

    def draw_doors(self, surface, tiles):
        for door in self.doors:
            a_vis = door.tile_a.visibility_state
            b_vis = door.tile_b.visibility_state
            if a_vis in (TileVisibility.VISIBLE, TileVisibility.DISCOVERED) or \
               b_vis in (TileVisibility.VISIBLE, TileVisibility.DISCOVERED):
                offset_x = G.gamemap.camera.offset_x
                offset_y = G.gamemap.camera.offset_y
                door.draw(surface, offset_x=offset_x, offset_y=offset_y)
