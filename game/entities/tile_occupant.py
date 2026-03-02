# file: entities/tile_occupant.py

from utils import globals as G
from utils.coordinate_helper import CoordinateHelper

class TileOccupant:
    def __init__(self):
        self.tile = None          # Logical tile
        self.world_x = 0          # Visual position, in world space
        self.world_y = 0

    def get_world_position(self):
        return self.world_x, self.world_y

    def get_screen_position(self):
        return CoordinateHelper.world_to_screen(self.world_x, self.world_y)

    def get_tile_position(self):
        return self.tile.grid_pos if self.tile else None

    # --- Stat Access ---

    def get_base_stat(self, stat_name):
        """
        Return the base (immutable) stat set at spawn.
        E.g., strength_base, health_base
        """
        return getattr(self, f"{stat_name}_base", 0)

    def get_modified_stat(self, stat_name):
        """
        Return the modified (buffed/effected) value.
        E.g., strength_modified, health_modified
        """
        return getattr(self, f"{stat_name}_modified", 0)

    def get_current_stat(self, stat_name):
        """
        Return the current value (for mutable stats like health, move_points).
        E.g., health_current, move_points_current
        """
        return getattr(self, f"{stat_name}_current", 0)

    def has_stat(self, stat_name):
        return hasattr(self, f"{stat_name}_base")

    @property
    def effects(self):
        class DummyEffects:
            def get_stat_color(self, key, mod, base):
                return (255, 255, 255)
            def get_all_effects(self):
                return []
        return DummyEffects()
