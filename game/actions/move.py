# file: actions/move.py

import pygame
from animations.movement_animator import MovementAnimator
from events.broadcaster import broadcast
from map.tile import TileVisibility
from map.tile import assign_entity_to_tile
from utils import globals as G
from utils.enums import UIMode
from utils.image_cache import get_icon
from utils.ui_mode_manager import set_ui_mode
from utils.logger import log_info, log_warn, log_debug


movement_mode = {
    "active": False,
    "legal_tiles": [],
    "highlight_index": 0,
    "player": None,
    "map": None
}


def enter_movement_mode():
    player = G.gamestate.get_active_player()
    map_ref = G.gamestate.map_ref
    current_tile = player.tile

    if not current_tile:
        log_warn("Move", "Player has no tile; cannot enter movement mode", file=__file__)
        return

    adjacent_tiles = map_ref.get_adjacent_tiles(current_tile)
    legal_tiles = [
        tile for tile in adjacent_tiles
        if tile.walkable
        and tile.visibility_state != TileVisibility.SECRET
        and map_ref.can_move_between(current_tile, tile)
    ]

    if not legal_tiles:
        log_warn("Move", "No valid movement options", file=__file__)
        return

    set_ui_mode(UIMode.MOVEMENT)
    movement_mode.update({
        "active": True,
        "legal_tiles": legal_tiles,
        "highlight_index": 0,
        "player": player,
        "map": map_ref
    })
    log_info("Move", f"Entered movement mode for player at {current_tile.grid_pos}, {len(legal_tiles)} options", file=__file__)


def handle_movement_action(action: str) -> bool:
    if not movement_mode["active"] or G.movement_animator.is_active():
        return False

    current_tile = movement_mode["player"].tile
    cx, cy = current_tile.grid_pos

    offsets = {
        "move_right": (1, 0),
        "move_left": (-1, 0),
        "move_down": (0, 1),
        "move_up": (0, -1)
    }

    if action in offsets:
        dx, dy = offsets[action]
        tx, ty = cx + dx, cy + dy
        for i, tile in enumerate(movement_mode["legal_tiles"]):
            if tile.grid_pos == (tx, ty):
                movement_mode["highlight_index"] = i
                log_debug("Move", f"Moved highlight to tile at ({tx}, {ty})", file=__file__)
                return True

    elif action == "confirm":
        log_debug("Move", "Confirm action triggered", file=__file__)
        confirm_move()
        return True

    elif action == "back":
        log_info("Move", "Exiting movement mode via back", file=__file__)
        exit_movement_mode()
        return True

    return False


def confirm_move():
    index = movement_mode["highlight_index"]
    target_tile = movement_mode["legal_tiles"][index]

    if target_tile.visibility_state == TileVisibility.SECRET:
        log_warn("Move", "Attempted to move to secret tile", file=__file__)
        return

    player = movement_mode["player"]
    current_tile = player.tile
    move_cost = target_tile.move_cost

    if player.move_points_current < move_cost:
        log_warn("Move", f"Not enough movement points: {player.move_points_current} < {move_cost}", file=__file__)
        return

    start_x, start_y = current_tile.get_world_position_for(player)
    current_tile.remove_occupant(player)

    if assign_entity_to_tile(player, target_tile):
        end_x, end_y = target_tile.get_world_position_for(player)
        movement_time = 1.2
        G.movement_animator.start(player, start_x, start_y, end_x, end_y, duration=movement_time)
        player.move_points_current -= move_cost

        visible_tiles = G.gamestate.get_visible_tiles()
        movement_mode["map"].update_visibility(visible_tiles)

        broadcast("character_moved", {
            "entity": player,
            "tile": player.tile,
            "event": "character_moved"
        })

        log_info("Move", f"Player moved to {target_tile.grid_pos}, MP left: {player.move_points_current}", file=__file__)
        exit_movement_mode()
    else:
        log_warn("Move", "Target tile is full; movement aborted", file=__file__)


def exit_movement_mode():
    set_ui_mode(UIMode.MAIN)
    movement_mode.update({
        "active": False,
        "legal_tiles": [],
        "highlight_index": 0,
        "player": None,
        "map": None
    })
    log_info("Move", "Exited movement mode", file=__file__)


def draw_movement_overlay(surface):
    if not movement_mode["active"]:
        return

    scale = G.camera_scale
    camera = movement_mode["map"].camera
    offset_x = camera.offset_x
    offset_y = camera.offset_y
    player_mp = movement_mode["player"].move_points_current

    for i, tile in enumerate(movement_mode["legal_tiles"]):
        if tile.visibility_state == TileVisibility.SECRET:
            continue

        cost = tile.move_cost
        text_color = (0, 255, 0) if player_mp >= cost else (255, 0, 0)
        scaled_rect = tile.get_screen_rect(scale, offset_x, offset_y)

        if i == movement_mode["highlight_index"]:
            pygame.draw.rect(surface, (255, 255, 0), scaled_rect, 3)

        icon_size = int(56 * scale)
        panel_size = int(64 * scale)
        cost_bg = pygame.Rect(0, 0, panel_size, panel_size)
        cost_bg.center = scaled_rect.center

        panel_surface = pygame.Surface((panel_size, panel_size), pygame.SRCALPHA)
        panel_surface.fill((80, 80, 80, 200))
        pygame.draw.rect(panel_surface, (0, 0, 0, 220), panel_surface.get_rect(), width=2, border_radius=int(10 * scale))
        surface.blit(panel_surface, cost_bg.topleft)

        move_icon = get_icon("move", size=(icon_size, icon_size))
        if move_icon:
            icon_scaled = pygame.transform.smoothscale(move_icon, (icon_size, icon_size))
            icon_rect = icon_scaled.get_rect(center=cost_bg.center)
            surface.blit(icon_scaled, icon_rect)

        font = pygame.font.SysFont(None, int(G.cost_font.get_height() * scale))
        text_surf = font.render(str(cost), True, text_color)
        text_rect = text_surf.get_rect(center=cost_bg.center)
        surface.blit(text_surf, text_rect)
