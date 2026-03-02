# file: game/render_system.py

import pygame
from actions import move
from actions import vent
from ui.resolver_overlay import draw_resolver_overlay
from utils import globals as G
from utils.enums import UIMode
from utils.logger import log_warn


def render_frame():
    """Handles drawing all game layers in the correct order."""
    _draw_background()
    _draw_world()
    _draw_ui()
    _draw_messages()
    pygame.display.flip()


def _draw_background():
    if G.static_background:
        G.screen.blit(G.static_background, (0, 0))
    else:
        G.screen.fill((0, 0, 0))


def _draw_world():
    G.gamemap.update_camera()
    G.gamemap.draw(G.screen)


def _draw_ui():
    G.hud.draw(G.screen)

    ui_mode = G.gamestate.ui_mode
    move_mode = move.movement_mode["active"]

    highlight_index = None
    dimmed = False

    if ui_mode == UIMode.CONTEXT:
        highlight_index = 3  # "Action"
        dimmed = True
    elif move_mode:
        highlight_index = 0  # "Move"
        dimmed = True

    G.action_menu.draw(G.screen, dimmed=dimmed, highlighted_index=highlight_index)

    if move_mode:
        move.draw_movement_overlay(G.screen)

    if G.gamestate.ui_mode == UIMode.PAUSED and G.pause_menu.active:
        G.pause_menu.draw(G.screen)

    if G.objectives_manager:
        G.objectives_manager.draw(G.screen)

    if G.gamestate.ui_mode == UIMode.INSPECTION:
        G.inspector.draw(G.screen)

    if G.gamestate.ui_mode == UIMode.VENT:
        vent.draw_vent_overlay(G.screen)

    if G.gamestate.ui_mode == UIMode.RESOLVER:
        draw_resolver_overlay(G.screen)


def _draw_messages():
    G.message_manager.draw(G.screen)

    if hasattr(G, "_player_attr_access_log"):
        log_warn("Render", "\n[SUMMARY] Player attribute fallbacks detected:", file=__file__)
        for attr in sorted(G._player_attr_access_log):
            log_warn("Render", f"  - player.{attr} → should likely be player.character.{attr}", file=__file__)
