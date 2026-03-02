# file: ui/menus/action_menu.py

import pygame
from actions import move
from actions.resolver.resolver_manager import start_resolver
from actions.pass_turn import execute_pass_turn
from ui.menus.base_menu import BaseMenu
from ui.menus.resolver_menu import ResolverMenu
from utils import globals as G
from utils.enums import UIMode
from utils.ui_mode_manager import set_ui_mode

class ActionMenu(BaseMenu):
    def __init__(self):
        super().__init__()
        self.options = [
            {"label": "Move", "callback": move.enter_movement_mode, "icon": "move"},
            {"label": "Tile Actions", "callback": self._open_context, "icon": "action"},
            {"label": "Inspect", "callback": self._open_inspector, "icon": "magnifying"},
            {"label": "Pass Turn", "callback": execute_pass_turn, "icon": "hourglass"}
        ]
        self.button_width = 200
        self.button_height = 42
        self.button_spacing = 10
        self.border_radius = 12
        self.selected_index = 0

    def _open_context(self):
        player = G.gamestate.get_active_player()
        G.context_menu.update_for_player_tile(player.tile.grid_pos)
        set_ui_mode(UIMode.CONTEXT)
            
    def _open_inspector(self):
        G.inspector.open()
        set_ui_mode(UIMode.INSPECTION)

    def handle_action(self, action: str) -> bool:
        if action == "back":
            return self.handle_back()
        return super().handle_action(action)

        
    def handle_back(self) -> bool:
        set_ui_mode(UIMode.PAUSED)
        return True


    def draw(self, surface, dimmed=False, highlighted_index=None):
        x = 20

        total_height = len(self.options) * (self.button_height + self.button_spacing) - self.button_spacing
        y = surface.get_height() - total_height - 30  # Always anchored to bottom with 30px margin

        option_rects = self.generate_button_rects(x, y)

        background_rect = pygame.Rect(
            x - 12,
            y - 12,
            self.button_width + 24,
            total_height + 24
        )

        bg_surface = pygame.Surface((background_rect.width, background_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 150), bg_surface.get_rect(), border_radius=self.border_radius)
        surface.blit(bg_surface, background_rect.topleft)

        self.draw_buttons(
            surface,
            option_rects,
            draw_icons=True,
            dimmed=dimmed,
            highlighted_index=highlighted_index
        )
