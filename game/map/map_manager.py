# file: map/map_manager.py

import pygame
import random
from config.constants import HOLY_PADDING
from map.camera_controller import CameraController
from map.map_generator import generate_static_map
from map.visibility_manager import update_tile_visibility, get_adjacent_tiles, can_see_through
from map.door_manager import DoorManager
from render.standee_renderer import draw_standee
from render.tile_ui_overlay_renderer import draw_tile_overlay
from render.tile_status_overlay_renderer import draw_tile_status
from map.tile import TileVisibility
from utils.enums import FogOfWarMode, UIMode
from utils import globals as G
from utils.image_cache import get_scaled_image
from utils.logger import log_warn


class MapManager:
    CAMERA_MODES = ["player", "all", "center"]

    def __init__(self, rows, cols, tile_width, tile_height, fog_mode=FogOfWarMode.NORMAL):
        self.rows = rows
        self.cols = cols
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.fog_mode = fog_mode
        self.camera = CameraController(tile_width, tile_height, cols, rows)
        self.tiles = generate_static_map(rows, cols, tile_width, tile_height)
        self.door_manager = DoorManager(tile_width, tile_height)

        self.hidden_tile_image = get_scaled_image(
            "hidden", (self.tile_width, self.tile_height)
        )

    # === Camera ===
    def toggle_camera_mode(self):
        self.camera.toggle_camera_mode()

    def update_camera(self):
        self.camera.update_camera(self)

    def pan_camera(self, dx, dy):
        self.camera.pan_camera(dx, dy)

    def focus_on_tile(self, tile, duration_sec=5):
        self.camera.focus_on_tile(tile, duration_sec)

    def world_to_screen(self, x, y):
        return self.camera.world_to_screen(x, y)

    def clamp_camera_to_map(self, *args, **kwargs):
        return self.camera.clamp_camera_to_map(*args, **kwargs)

    # === Tile Logic ===

    def get_adjacent_tiles(self, tile):
        return get_adjacent_tiles(tile, self.tiles, self.rows, self.cols)

    def can_move_between(self, tile1, tile2):
        return self.door_manager.can_move_between(tile1, tile2)

    def can_see_through(self, tile_a, tile_b):
        return can_see_through(tile_a, tile_b, self.door_manager)

    def update_visibility(self, player_tiles):
        update_tile_visibility(
            self.tiles,
            player_tiles,
            lambda tile: get_adjacent_tiles(tile, self.tiles, self.rows, self.cols),
            lambda a, b: can_see_through(a, b, self.door_manager),
        )

    # === Rendering ===

    def draw(self, surface):
        self.camera.apply_lerp()
        scale = G.camera_scale
        offset_x = self.camera.offset_x
        offset_y = self.camera.offset_y

        for row in self.tiles:
            for tile in row:
                scaled_rect = self.camera.get_scaled_rect(tile.world_rect)

                if tile.visibility_state in (TileVisibility.HIDDEN, TileVisibility.SECRET):
                    self._draw_hidden_tile(surface, scaled_rect)
                    continue

                if tile.background_image:
                    bg_scaled = pygame.transform.smoothscale(
                        tile.background_image, (scaled_rect.width, scaled_rect.height)
                    )
                    surface.blit(bg_scaled, scaled_rect)

                draw_tile_status(surface, tile, self.camera, phase="behind")

                if tile.visibility_state == TileVisibility.DISCOVERED:
                    fog_overlay = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
                    fog_overlay.fill((30, 30, 30, 160))
                    surface.blit(fog_overlay, scaled_rect.topleft)

                pygame.draw.rect(surface, (80, 80, 80), scaled_rect, 2)

        self._draw_standees(surface, debug=G.debug_mode)

        for row in self.tiles:
            for tile in row:
                if tile.visibility_state.name == "VISIBLE":
                    draw_tile_status(surface, tile, self.camera, phase="above")

        for row in self.tiles:
            for tile in row:
                if tile.visibility_state.name == "VISIBLE":
                    draw_tile_overlay(surface, tile, scale, G.menu_font, offset_x, offset_y)

        self.door_manager.draw_doors(surface, self.tiles)

    def _draw_hidden_tile(self, surface, rect):
        if self.hidden_tile_image:
            image = pygame.transform.smoothscale(self.hidden_tile_image, (rect.width, rect.height))
            surface.blit(image, rect.topleft)
        else:
            fog_overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            fog_overlay.fill((10, 10, 10, 255))
            surface.blit(fog_overlay, rect.topleft)

        pygame.draw.rect(surface, (60, 60, 60), rect, 1)

    def _draw_standees(self, surface, debug=False):
        for row in self.tiles:
            for tile in row:
                if tile.visibility_state.name != "VISIBLE":
                    continue
                for entity in tile.occupants:
                    if entity:
                        draw_standee(entity, surface, debug)

    def __setattr__(self, name, value):
        if G.DEBUG_ATTR_WARNINGS and not hasattr(self, name):
            log_warn("MapManager", f"{self.__class__.__name__} has no attribute '{name}'", file=__file__)
        super().__setattr__(name, value)


def randomize_tile_lights(map_manager, on_chance=0.6):
    for row in map_manager.tiles:
        for tile in row:
            tile.light_on = random.random() < on_chance
