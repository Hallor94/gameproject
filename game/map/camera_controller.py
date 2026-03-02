# file: map/camera_controller.py

import pygame
from utils import globals as G
from config.constants import HOLY_PADDING, GROUP_CAMERA_MARGIN_TILES


class CameraController:
    CAMERA_MODES = ["center", "player", "all"]

    def __init__(self, tile_width, tile_height, cols, rows):
        self.camera_mode_index = self.CAMERA_MODES.index("center")
        self.base_camera_speed = 0.15

        self.offset_x = 0               # current screen-space offset
        self.offset_y = 0
        self.target_offset_x = 0        # interpolated target offset
        self.target_offset_y = 0

        self.focus_tile = None
        self.camera_mode_override = None
        self.focus_timeout_ms = 0

        self.free_pan_x = 0
        self.free_pan_y = 0

        self.tile_width = tile_width
        self.tile_height = tile_height
        self.cols = cols
        self.rows = rows

    def toggle_camera_mode(self):
        self.camera_mode_index = (self.camera_mode_index + 1) % len(self.CAMERA_MODES)

    def update_camera(self, map_manager):
        if G.movement_animator.is_active():
            return

        if not G.gamestate or not G.gamestate.get_active_player():
            return

        self._update_camera_override_timeout()

        mode = self.camera_mode_override or self.CAMERA_MODES[self.camera_mode_index]

        if mode == "player":
            self._update_camera_player_mode()
        elif mode == "center":
            self._update_camera_center_mode()
        elif mode == "all":
            self.center_camera_on_map()
        elif mode == "focus":
            self._update_camera_focus_mode()

    def apply_lerp(self):
        t = self.base_camera_speed
        self.offset_x = int(self.lerp(self.offset_x, self.target_offset_x, t))
        self.offset_y = int(self.lerp(self.offset_y, self.target_offset_y, t))

    def _update_camera_override_timeout(self):
        if self.camera_mode_override == "focus":
            if pygame.time.get_ticks() > self.focus_timeout_ms:
                self.camera_mode_override = None
                self.focus_tile = None

    def _update_camera_player_mode(self):
        player = G.gamestate.get_active_player()
        grid_x, grid_y = player.tile.grid_pos
        zoom = 1.2
        G.camera_scale = zoom

        world_cx = grid_x * self.tile_width + self.tile_width // 2
        world_cy = grid_y * self.tile_height + self.tile_height // 2

        screen_w, screen_h = G.SCREEN_WIDTH, G.SCREEN_HEIGHT
        self.target_offset_x, self.target_offset_y = self.compute_zoom_and_offset(
            world_cx, world_cy, zoom, screen_w, screen_h
        )

    def _update_camera_center_mode(self):
        tiles = [p.tile for p in G.gamestate.players if p.tile]
        if not tiles:
            return

        min_x = min(t.grid_pos[0] for t in tiles)
        max_x = max(t.grid_pos[0] for t in tiles)
        min_y = min(t.grid_pos[1] for t in tiles)
        max_y = max(t.grid_pos[1] for t in tiles)

        margin = GROUP_CAMERA_MARGIN_TILES
        width_tiles = (max_x - min_x + 1 + margin * 2)
        height_tiles = (max_y - min_y + 1 + margin * 2)

        # Center on the full region (players + margin)
        center_grid_x = (min_x - margin + max_x + margin + 1) // 2
        center_grid_y = (min_y - margin + max_y + margin + 1) // 2

        screen_w, screen_h = G.SCREEN_WIDTH, G.SCREEN_HEIGHT
        tile_w, tile_h = self.tile_width, self.tile_height

        zoom_x = screen_w / (width_tiles * tile_w)
        zoom_y = screen_h / (height_tiles * tile_h)
        zoom = min(zoom_x, zoom_y)

        G.camera_scale = zoom

        world_cx = center_grid_x * tile_w
        world_cy = center_grid_y * tile_h

        self.target_offset_x, self.target_offset_y = self.compute_zoom_and_offset(
            world_cx, world_cy, zoom, screen_w, screen_h
        )

    def _update_camera_focus_mode(self):
        zoom = 1.5
        G.camera_scale = zoom

        screen_w, screen_h = G.SCREEN_WIDTH, G.SCREEN_HEIGHT
        map_pixel_w = self.cols * self.tile_width
        map_pixel_h = self.rows * self.tile_height

        min_offset_x = screen_w - map_pixel_w * zoom
        min_offset_y = screen_h - map_pixel_h * zoom

        self.target_offset_x = self.clamp(self.free_pan_x, min_offset_x, 0)
        self.target_offset_y = self.clamp(self.free_pan_y, min_offset_y, 0)

    def compute_zoom_and_offset(self, world_cx, world_cy, zoom, screen_w, screen_h):
        target_offset_x = -world_cx * zoom + screen_w // 2
        target_offset_y = -world_cy * zoom + screen_h // 2

        return self.clamp_camera_to_map(
            target_offset_x, target_offset_y, zoom, screen_w, screen_h, margin_tiles=1.0
        )

    def clamp_camera_to_map(self, offset_x, offset_y, zoom, screen_w, screen_h, margin_tiles=1.0):
        tile_wz = self.tile_width * zoom
        tile_hz = self.tile_height * zoom

        margin_x = tile_wz * margin_tiles
        margin_y = tile_hz * margin_tiles

        map_w = self.cols * tile_wz
        map_h = self.rows * tile_hz

        min_x = screen_w - map_w - margin_x
        max_x = margin_x
        min_y = screen_h - map_h - margin_y
        max_y = margin_y

        clamped_x = max(min(offset_x, max_x), min_x)
        clamped_y = max(min(offset_y, max_y), min_y)

        return clamped_x, clamped_y

    def center_camera_on_map(self):
        screen_w, screen_h = G.SCREEN_WIDTH, G.SCREEN_HEIGHT
        map_pixel_w = self.cols * self.tile_width
        map_pixel_h = self.rows * self.tile_height

        scale_w = (screen_w - 2 * HOLY_PADDING) / map_pixel_w
        scale_h = (screen_h - 2 * HOLY_PADDING) / map_pixel_h
        zoom = max(min(scale_w, scale_h), 0.1)

        G.camera_scale = zoom

        screen_center_x = screen_w // 2
        screen_center_y = screen_h // 2

        map_center_x = (map_pixel_w * zoom) // 2
        map_center_y = (map_pixel_h * zoom) // 2

        self.offset_x = screen_center_x - map_center_x
        self.offset_y = screen_center_y - map_center_y
        self.target_offset_x = self.offset_x
        self.target_offset_y = self.offset_y

    def world_to_screen(self, world_x, world_y):
        scale = G.camera_scale
        return int(world_x * scale + self.offset_x), int(world_y * scale + self.offset_y)

    def get_scaled_rect(self, rect):
        scale = G.camera_scale
        return pygame.Rect(
            int(rect.x * scale + self.offset_x),
            int(rect.y * scale + self.offset_y),
            int(rect.width * scale),
            int(rect.height * scale)
        )

    def pan_camera(self, dx, dy):
        if self.CAMERA_MODES[self.camera_mode_index] == "free":
            self.free_pan_x += dx
            self.free_pan_y += dy

    def focus_on_tile(self, tile, duration_sec=5):
        self.focus_tile = tile
        self.camera_mode_override = "focus"
        self.focus_timeout_ms = pygame.time.get_ticks() + duration_sec * 1000

    def lerp(self, a, b, t):
        return a + (b - a) * t
