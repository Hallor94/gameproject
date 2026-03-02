# file: ui/menus/pause_menu.py

import pygame
import sys
from .settings_menu import SettingsMenu
from utils.enums import UIMode
from utils import globals as G
from utils.ui_mode_manager import set_ui_mode
from .base_menu import BaseMenu

class PauseMenu(BaseMenu):
    def __init__(self):
        super().__init__()
        self.active = False
        self.in_settings = False
        self.settings_menu = None

        self.options = [
            {"label": "Save Game", "callback": lambda: print("TODO: Save Game")},
            {"label": "Load Game", "callback": lambda: print("TODO: Load Game")},
            {"label": "Settings", "callback": self.open_settings},
            {"label": "Exit Game", "callback": self.exit_game},
            {"label": "Continue", "callback": self.continue_game}
        ]
        self.button_width = 280
        self.button_height = 42
        self.button_spacing = 12
        self.border_radius = 10

    def open_settings(self):
        self.in_settings = True

    def continue_game(self):
        self.active = False

    def exit_game(self):
        pygame.quit()
        sys.exit()

    def toggle(self):
        self.active = not self.active

    def set_settings_hooks(self):
        self.settings_menu = SettingsMenu(
            get_fog_mode=lambda: G.gamemap.fog_mode,
            set_fog_mode=lambda mode: (
                setattr(G.gamemap, "fog_mode", mode),
                G.gamemap.update_visibility(G.gamestate.get_visible_tiles())
            )
        )

    def handle_action(self, action: str) -> bool:
        if self.in_settings and self.settings_menu:
            result = self.settings_menu.handle_action(action)
            if result == "back":
                self.handle_back()
            return True

        if G.gamestate.ui_mode not in (UIMode.MAIN, UIMode.MAIN):
            return False
        if not self.active:
                return False

        return super().handle_action(action)

    def handle_back(self) -> bool:
        if self.in_settings:
            self.in_settings = False
        elif self.active:
            set_ui_mode(UIMode.MAIN)
            self.active = False
        return True

    def draw(self, surface):
        if G.gamestate.ui_mode not in (UIMode.MAIN, UIMode.MAIN):
            return False
        if not self.active:
            return

        if self.in_settings and self.settings_menu:
            self.settings_menu.draw()
            return

        x = surface.get_width() // 2 - self.button_width // 2
        y = surface.get_height() // 2 - (len(self.options) * (self.button_height + self.button_spacing)) // 2

        option_rects = self.generate_button_rects(x, y)
        self.draw_buttons(surface, option_rects, draw_icons=True, dimmed=False)
