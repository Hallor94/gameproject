# file: ai/ai_manager.py

import random
from map.tile import assign_entity_to_tile
from utils.logger import log_info, log_warn
from utils import globals as G


def handle_entity_turn(entity, map_ref, players):
    """
    Core AI decision point. Called once per entity during its turn.
    Currently only supports ENEMY faction.
    Future logic will branch by tag: 'aggressive', 'guard', 'hunt', etc.
    """
    if entity.character_faction != "ENEMY":
        return

    behaviors = getattr(entity, "character_behaviors", [])

    if "guard" in behaviors:
        return _guard_behavior(entity, map_ref)

    if "aggressive" in behaviors or not behaviors:
        return _basic_enemy_move(entity, map_ref)

    return _idle(entity)


def _basic_enemy_move(entity, map_ref):
    current_tile = entity.tile
    if not current_tile:
        log_warn("AI", f"{entity.character_display_name} has no tile.", file=__file__)
        return

    adjacent_tiles = map_ref.get_adjacent_tiles(current_tile)
    legal_moves = [
        tile for tile in adjacent_tiles
        if tile.walkable and tile.occupants.count(None) > 0 and map_ref.can_move_between(current_tile, tile)
    ]

    if legal_moves:
        target = random.choice(legal_moves)
        current_tile.remove_occupant(entity)
        if assign_entity_to_tile(entity, target):
            entity.world_x, entity.world_y = target.get_world_position_for(entity)
            log_info("AI", f"{entity.character_display_name} moved to {target.grid_pos}", file=__file__)
        else:
            log_warn("AI", f"{entity.character_display_name} failed to move to {target.grid_pos}", file=__file__)
    else:
        log_info("AI", f"{entity.character_display_name} had no valid move options.", file=__file__)


def _guard_behavior(entity, map_ref):
    log_info("AI", f"{entity.character_display_name} is guarding and does not move this turn.", file=__file__)


def _idle(entity):
    log_info("AI", f"{entity.character_display_name} has no behavior and idles.", file=__file__)
