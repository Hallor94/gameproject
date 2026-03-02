# file: map/tile.py

import glob
import os
import pygame
import random

from config import constants
from utils.enums import TileVisibility, TileOverlayState
from utils.image_cache import get_icon, get_scaled_image
from utils import globals as G
from utils.logger import log_warn


class Tile:
    """
    Represents a logical and visual tile on the map grid.
    Holds occupants, standee positions, tile state flags, and background image.
    """

    def __init__(self, x, y, width, height, tile_type_data):
        # --- Positional metadata ---
        self.width = width
        self.height = height
        self.grid_pos = (x, y)
        self.grid_x = x
        self.grid_y = y
        self.world_rect = pygame.Rect(x * width, y * height, width, height)

        # --- Tile metadata and behavior ---
        self.type = tile_type_data.get("type", "default")
        self.name = tile_type_data.get("name", "Unknown")
        self.actions = tile_type_data.get("actions", [])
        self.walkable = tile_type_data.get("walkable", True)
        self.move_cost = tile_type_data.get("move_cost", 1)

        # --- Occupancy tracking ---
        self.max_occupants = tile_type_data.get("max_occupants", 6)
        self.occupants = [None] * self.max_occupants

        # --- Visibility and interactivity ---
        self.visibility_state = TileVisibility.HIDDEN
        self.event_trigger = None
        self.standee_positions = self._generate_standee_slots()
        self.icon_surface = get_icon("move", size=(24, 24))  # optional overlay use

        # --- Tile content flags ---
        self.has_loot = random.random() < 0.60
        self.loot_count = random.randint(1, 3) if self.has_loot else 0
        self.has_main_quest = random.random() < 0.15
        self.has_side_quest = random.random() < 0.25
        self.has_vent = random.random() < 0.7

        self.is_explored = not (
            self.has_main_quest or
            self.has_side_quest or
            self.has_loot or
            self.has_vent
        )

        # --- Visuals & lights ---
        self.background_image = self.load_background_image()
        self.tile_overlay_status = TileOverlayState.NONE
        self.light_on = random.random() < 0.8
        self.light_baseline_on = self.light_on
        self._flicker_sequence = []
        self._flicker_index = 0
        self._flicker_active = False

    def _generate_standee_slots(self):
        """
        Creates visual slots where standees will appear on this tile.
        Each slot is evenly spaced along the bottom of the tile.
        """
        slots = []
        w, h = self.world_rect.width, self.world_rect.height
        spacing = w // (self.max_occupants + 1)
        bottom_y = self.world_rect.bottom

        standee_height = int(h * constants.STANDEE_HEIGHT_RATIO)
        slot_width = int(h * constants.STANDEE_SLOT_WIDTH_RATIO)

        for i in range(self.max_occupants):
            x = self.world_rect.left + spacing * (i + 1)
            y = bottom_y
            slot_rect = pygame.Rect(x - slot_width // 2, y - standee_height, slot_width, standee_height)
            slots.append(slot_rect)

        return slots

    def get_world_position_for(self, entity):
        """
        Returns the world-space (x, y) where the standee for this entity should appear.
        """
        try:
            index = self.occupants.index(entity)
            return self.standee_positions[index].centerx, self.standee_positions[index].bottom
        except (ValueError, IndexError):
            return self.world_rect.centerx, self.world_rect.bottom

    def get_slot_index(self, entity):
        try:
            return self.occupants.index(entity)
        except ValueError:
            return None

    def get_screen_rect(self, scale, offset_x, offset_y):
        """
        Returns the scaled screen-space rect for drawing this tile.
        """
        return pygame.Rect(
            int(self.world_rect.x * scale + offset_x),
            int(self.world_rect.y * scale + offset_y),
            int(self.world_rect.width * scale),
            int(self.world_rect.height * scale),
        )

    def remove_occupant(self, entity):
        for i, occupant in enumerate(self.occupants):
            if occupant == entity:
                self.occupants[i] = None
                return True
        return False

    def clear_occupants(self):
        """
        Removes all entities from the tile (useful for reset or tests).
        """
        self.occupants = [None] * self.max_occupants

    def load_background_image(self):
        image_folder = "assets/tiles/base"
        pattern = os.path.join(image_folder, f"{self.type}*.png")
        available_images = glob.glob(pattern)

        if not available_images:
            log_warn("Tile", f"No background for tile type '{self.type}'. Using default.", file=__file__)
            return None

        chosen_path = random.choice(available_images)
        key = os.path.splitext(os.path.basename(chosen_path))[0]
        return get_scaled_image(key, (self.width, self.height))


# === Placement Logic ===

def assign_entity_to_tile(entity, tile):
    """
    Attempts to assign the given entity to an available standee slot on the tile.
    If successful, sets tile reference and returns True. Otherwise, returns False.
    """
    if entity in tile.occupants:
        return True  # already assigned

    if tile.occupants.count(None) == 0:
        return False  # tile full

    search_range = (
        range(tile.max_occupants) if entity.type in ("npc", "player")
        else reversed(range(tile.max_occupants))
    )

    for i in search_range:
        if tile.occupants[i] is None:
            tile.occupants[i] = entity
            entity.tile = tile
            _update_combat_states_for_all_tiles()
            return True

    return False

def _update_combat_states(tile):
    has_enemy = any(o for o in tile.occupants if o and getattr(o, "type", None) == "enemy")

    for o in tile.occupants:
        if not o or getattr(o, "type", None) != "player":
            continue

        if has_enemy:
            o.add_state("combat")
        else:
            o.remove_state("combat")

def _update_combat_states_for_all_tiles():
    for row in G.gamemap.tiles:
        for tile in row:
            _update_combat_states(tile)
