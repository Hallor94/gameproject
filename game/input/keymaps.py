# file: game/input/keymaps.py

import pygame

DEFAULT_KEYMAP = {
    # Numpad directional keys (for menu navigation)
    pygame.K_KP8: "move_up",
    pygame.K_KP2: "move_down",
    pygame.K_KP4: "move_left",
    pygame.K_KP6: "move_right",

    # Other keys
    pygame.K_KP_ENTER: "confirm",
    pygame.K_RETURN: "confirm",
    pygame.K_ESCAPE: "back",
    pygame.K_TAB: "cycle_tab",
    pygame.K_UP: "move_up",
    pygame.K_DOWN: "move_down",
    pygame.K_LEFT: "move_left",
    pygame.K_RIGHT: "move_right",
    pygame.K_KP0: "inspect_mode",
    pygame.K_SPACE: "toggle_mode",

}
