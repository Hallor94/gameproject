# file: utils/ui_mode_manager.py

from utils.enums import UIMode
from utils import globals as G
from utils.logger import log

def set_ui_mode(mode):
    """Sets the current UI mode and updates the active menu."""
    old_mode = getattr(G.gamestate, "ui_mode", None)
    G.gamestate.ui_mode = mode

    if mode == UIMode.PAUSED:
        G.active_menu = G.pause_menu
        G.pause_menu.active = True
    elif mode == UIMode.MAIN or mode is None:
        G.active_menu = G.action_menu
    elif mode == UIMode.CONTEXT:
        G.active_menu = G.context_menu
    elif mode == UIMode.MOVEMENT:
        G.active_menu = None
    elif mode == UIMode.INSPECTION:
        G.active_menu = None
    elif mode == UIMode.DIALOGUE:
        G.active_menu = None
    elif mode == UIMode.VENT:
        G.active_menu = None
    elif mode == UIMode.RESOLVER:
        G.active_menu = G.resolver_menu
    else:
        G.active_menu = G.action_menu  # fallback

    if old_mode != mode:
        log("UI", f"Switched UI mode: {old_mode} → {mode}, active_menu = {type(G.active_menu).__name__ if G.active_menu else 'None'}", file=__file__)
