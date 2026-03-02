# file: actions/vent.py

import pygame
from actions.resolver.resolver_manager import ActionResolver
from actions.cards.card_loader import get_card_by_id
from map.tile import assign_entity_to_tile
from events.broadcaster import broadcast
from ui.menus.resolver_menu import ResolverMenu
from utils.enums import TileVisibility, UIMode
from utils.ui_mode_manager import set_ui_mode
from utils import globals as G
from utils.image_cache import get_icon
from utils.logger import log_info, log_warn, log_debug

VENT_MOVE_COST = 2

vent_mode = {
    "active": False,
    "legal_tiles": [],
    "highlight_index": 0,
    "player": None,
    "prev_camera_target": None
}


def enter_vent_mode():
    player = G.gamestate.get_active_player()
    if not player or not player.tile or not player.tile.has_vent:
        log_warn("Vent", "Cannot vent: no valid player or vent tile", file=__file__)
        return


    card = get_card_by_id("vent")
    if not card:
        log_warn("Vent", "No resolver card found with ID 'vent'", file=__file__)
        return

    resolver = ActionResolver(actor=player, template_dict=None, test_mode=True)
    resolver.apply_card(card["id"])

    G.active_resolver = resolver
    G.active_menu = G.resolver_menu or ResolverMenu(resolver)
    G.active_menu.update_options()

    set_ui_mode(UIMode.RESOLVER)
    log_info("Vent", f"Started resolver for vent: {player.player_name}", file=__file__)


def trigger_vent_resolution_success():
    """
    Called by resolver when venting check succeeds.
    Proceeds to original enter_vent_mode logic (camera, tile selector, etc.).
    """
    player = G.gamestate.get_active_player()
    if not player:
        return
    player_tile = player.tile
    legal_tiles = [
        tile for row in G.gamemap.tiles for tile in row
        if tile.has_vent
        and tile.visibility_state != TileVisibility.SECRET
        and tile != player_tile
    ]

    if not legal_tiles:
        log_warn("Vent", "No legal vent targets found", file=__file__)
        return

    vent_mode.update({
        "prev_camera_mode_index": vent_mode.get("prev_camera_mode_index"),
        "active": True,
        "legal_tiles": legal_tiles,
        "highlight_index": 0,
        "player": player,
        "prev_camera_target": (G.gamemap.camera.target_offset_x, G.gamemap.camera.target_offset_y)
    })

    set_ui_mode(UIMode.VENT)
    G.gamemap.camera.camera_mode_override = "all"
    G.gamemap.camera.center_camera_on_map()
    log_info("Vent", f"Entered vent mode with {len(legal_tiles)} legal tiles", file=__file__)


def handle_vent_action(action: str) -> bool:
    if not vent_mode["active"]:
        return False

    current_tile = vent_mode["legal_tiles"][vent_mode["highlight_index"]]
    cx, cy = current_tile.grid_pos

    offsets = {
        "move_right": (1, 0),
        "move_left": (-1, 0),
        "move_down": (0, 1),
        "move_up": (0, -1)
    }

    if action in offsets:
        dx, dy = offsets[action]
        best_index = None
        best_dist = float('inf')

        for i, tile in enumerate(vent_mode["legal_tiles"]):
            tx, ty = tile.grid_pos
            dx_actual = tx - cx
            dy_actual = ty - cy

            if (dx, dy) == (0, 1) and dy_actual <= 0:
                continue
            if (dx, dy) == (0, -1) and dy_actual >= 0:
                continue
            if (dx, dy) == (1, 0) and dx_actual <= 0:
                continue
            if (dx, dy) == (-1, 0) and dx_actual >= 0:
                continue

            dist = abs(tx - (cx + dx)) + abs(ty - (cy + dy))
            if dist < best_dist:
                best_dist = dist
                best_index = i

        if best_index is not None:
            vent_mode["highlight_index"] = best_index
            log_debug("Vent", f"Moved highlight to tile {vent_mode['legal_tiles'][best_index].grid_pos}", file=__file__)
            return True

    elif action == "confirm":
        log_debug("Vent", "Confirm action triggered", file=__file__)
        confirm_vent()
        return True

    elif action == "back":
        log_info("Vent", "Exiting vent mode via back", file=__file__)
        exit_vent_mode()
        return True

    return False


def confirm_vent():
    index = vent_mode["highlight_index"]
    target_tile = vent_mode["legal_tiles"][index]
    player = vent_mode["player"]

    if player.move_points_current < VENT_MOVE_COST:
        G.message_manager.show_floating("Not enough move points", duration=2.0)
        log_warn("Vent", f"{player.player_name} attempted venting with {player.move_points_current} MP (required: {VENT_MOVE_COST})", file=__file__)
        return

    if player.tile:
        player.tile.remove_occupant(player)

    if assign_entity_to_tile(player, target_tile):
        player.move_points_current -= VENT_MOVE_COST
        player.world_x, player.world_y = target_tile.get_world_position_for(player)
        G.gamemap.update_visibility([p.tile for p in G.gamestate.players if p.tile])

        broadcast("character_moved", {
            "entity": player,
            "tile": target_tile,
            "event": "vent_travel"
        })

        log_info("Vent", f"{player.player_name} vented to {target_tile.grid_pos}, MP left: {player.move_points_current}", file=__file__)
        exit_vent_mode()
    else:
        G.message_manager.show_floating("Target tile is full", duration=2.0)
        log_warn("Vent", f"{player.player_name} attempted vent to full tile {target_tile.grid_pos}", file=__file__)
        exit_vent_mode()


def exit_vent_mode():
    if vent_mode["prev_camera_target"]:
        G.gamemap.camera.target_offset_x, G.gamemap.camera.target_offset_y = vent_mode["prev_camera_target"]

    if vent_mode.get("prev_camera_mode_index") is not None:
        G.gamemap.camera.camera_mode_index = vent_mode["prev_camera_mode_index"]

    G.gamemap.camera.camera_mode_override = None
    set_ui_mode(UIMode.MAIN)

    vent_mode.update({
        "active": False,
        "legal_tiles": [],
        "highlight_index": 0,
        "player": None,
        "prev_camera_target": None
    })

    log_info("Vent", "Exited vent mode", file=__file__)


def draw_vent_overlay(surface):
    if not vent_mode["active"]:
        return

    scale = G.camera_scale
    offset_x = G.gamemap.camera.offset_x
    offset_y = G.gamemap.camera.offset_y
    player_mp = vent_mode["player"].move_points_current

    for i, tile in enumerate(vent_mode["legal_tiles"]):
        screen_rect = tile.get_screen_rect(scale, offset_x, offset_y)

        if i == vent_mode["highlight_index"]:
            pygame.draw.rect(surface, (255, 255, 0), screen_rect, 3)

        panel = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
        panel.fill((50, 50, 50, 180))
        surface.blit(panel, screen_rect.topleft)

        vent_icon = get_icon("icon_tile_vent", size=(int(32 * scale), int(32 * scale)))
        if vent_icon:
            icon_pos = screen_rect.topleft[0] + 8, screen_rect.topleft[1] + 8
            surface.blit(vent_icon, icon_pos)

        cost_text = "???" if tile.visibility_state == TileVisibility.HIDDEN else tile.name
        font = pygame.font.SysFont(None, int(G.hud_font.get_height() * scale))
        label = font.render(cost_text, True, (255, 255, 255))
        surface.blit(label, label.get_rect(center=screen_rect.center))

        icon_size = int(60 * scale)
        move_icon = get_icon("move", size=(icon_size, icon_size))
        if move_icon:
            scaled = pygame.transform.smoothscale(move_icon, (icon_size, icon_size))
            icon_rect = scaled.get_rect(center=screen_rect.center)
            surface.blit(scaled, icon_rect)

            font = pygame.font.SysFont(None, int(G.cost_font.get_height() * scale))
            text_color = (0, 255, 0) if player_mp >= VENT_MOVE_COST else (255, 0, 0)
            text_surf = font.render(str(VENT_MOVE_COST), True, text_color)
            surface.blit(text_surf, text_surf.get_rect(center=icon_rect.center))
        else:
            log_warn("Vent", "Failed to render move icon on vent tile", file=__file__)

    