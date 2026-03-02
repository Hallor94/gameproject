# file: map/tile_status_manager.py

from utils.enums import TileOverlayState
from utils import globals as G
from entities.effects.effect import Effect

TILE_STATUS_EFFECTS = {
    TileOverlayState.FIRE: {"health_current": -1},
    TileOverlayState.FLOODED: {"move_points": {"mul": 0.5}},
    TileOverlayState.GAS: {"intelligence": {"mul": 0.5}},
    TileOverlayState.RADIATION: {"health_current": -2},
    TileOverlayState.ALARM: {},
}


class TileStatusManager:
    def __init__(self):
        self.status_by_tile = {}  # tile -> (status, duration)

    def set_tile_status(self, tile, status, duration=None):
        tile.tile_overlay_status = status
        self.status_by_tile[tile] = {"status": status, "duration": duration}
        self._apply_effects_to_tile(tile, status)
        if status == TileOverlayState.FIRE:
            tile.light_baseline_on = True

    def clear_tile_status(self, tile):
        if tile in self.status_by_tile:
            self._remove_effects_from_tile(tile)
            tile.tile_overlay_status = TileOverlayState.NONE
            del self.status_by_tile[tile]

    def tick_round(self):
        expired_tiles = []
        for tile, data in list(self.status_by_tile.items()):
            if data["duration"] is not None:
                data["duration"] -= 1
                if data["duration"] <= 0:
                    expired_tiles.append(tile)

            self._apply_effects_to_tile(tile, data["status"])

        for tile in expired_tiles:
            self.clear_tile_status(tile)

    def _apply_effects_to_tile(self, tile, status):
        modifiers = TILE_STATUS_EFFECTS.get(status)
        if not modifiers:
            return

        for entity in tile.occupants:
            if not entity:
                continue

            # Direct application only (do not store the effect)
            effect = Effect(
                id=f"tile_{status.name.lower()}",
                name=f"tile_{status.name.lower()}",
                source="tile",
                duration=None,
                modifiers=modifiers,
                per_turn=False
            )

            entity.effects._handle_applied_effect(effect)
            entity.effects._enforce_stat_clamps()
