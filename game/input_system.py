# file: game/input_system.py

from actions import move
from actions import vent
from actions.resolver import resolver_input
from input.input_router import InputRouter
from utils import globals as G
from utils.enums import UIMode
from utils.ui_mode_manager import set_ui_mode

# Shared direction mapping (for menus, inspect, movement)
direction_map = {
    "move_up": (0, -1),
    "move_down": (0, 1),
    "move_left": (-1, 0),
    "move_right": (1, 0)
}

def handle_general_menu_navigation(action: str) -> bool:
    """
    Generic handler for any active menu using navigation, confirm, back actions.
    Menus must implement:
      - handle_navigation(action: str)
      - handle_confirm()
      - handle_back()
    """
    active_menu = getattr(G, "active_menu", None)
    if not active_menu:
        return False

    if action in direction_map:
        return active_menu.handle_navigation(action)
    elif action == "confirm":
        return active_menu.handle_confirm()
    elif action == "back":
        if not active_menu.handle_back():
            # Fallback: force escape closes menu and resumes
            set_ui_mode(UIMode.MAIN)
        return True

    return False

def handle_movement_action(action: str) -> bool:
    return move.handle_movement_action(action)

def handle_vent_action(action: str) -> bool:
    return vent.handle_vent_action(action)

def handle_inspection_input(action: str) -> bool:
    if G.gamestate.ui_mode != UIMode.INSPECTION:
        return False
    return G.inspector.handle_input(action)

def handle_resolver_input(action: str) -> bool:
    return resolver_input.handle_action_resolution_input(action)

def handle_tab_logic(action: str) -> bool:
    if action != "cycle_tab":
        return False

    mode = G.gamestate.ui_mode

    if mode == UIMode.INSPECTION:
        G.inspector.cycle_tab()
        return True

    if mode in (UIMode.SETUP, UIMode.PAUSED, UIMode.DIALOGUE):
        return True  # Block Tab in these modes

    # All others toggle camera
    G.gamemap.toggle_camera_mode()
    return True


def register_all_input_handlers(router: InputRouter):
    # Gameplay input gets priority
    router.register(handle_general_menu_navigation)
    router.register(handle_tab_logic)
    router.register(handle_movement_action)
    router.register(handle_vent_action)
    router.register(handle_inspection_input)
    router.register(handle_resolver_input)

    # Menus after
    router.register(G.context_menu.handle_action)
    router.register(G.action_menu.handle_action)
    router.register(G.pause_menu.handle_action)
    router.register(G.setup_menu.handle_action)

