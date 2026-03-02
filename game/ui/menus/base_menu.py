# file: ui/menus/base_menu.py

import pygame
from input_system import direction_map, handle_general_menu_navigation
from utils.image_cache import get_icon
from utils.enums import UIMode

class BaseMenu:
    def __init__(self):
        self.selected_index = None  # None = nothing selected
        self.options = []  # list of option strings or dicts with callbacks
        self.rects = []    # list of pygame.Rect objects for each button
        self.font = pygame.font.SysFont(None, 32)
        self.button_width = 200
        self.button_height = 42
        self.button_spacing = 12
        self.border_radius = 10
        self.base_color = (35, 35, 35)
        self.selected_color = (60, 90, 140)
        self.selected_border = (255, 255, 150)
        self.default_border = (80, 80, 80)

    def handle_action(self, action: str) -> bool:
        return handle_general_menu_navigation(action)

    def handle_navigation(self, action: str) -> bool:
        dx, dy = direction_map.get(action, (0, 0))
        if not self.options:
            return False

        if dx or dy:
            if self.selected_index is None:
                self.selected_index = 0
            else:
                step = 1 if dx > 0 or dy > 0 else -1
                self.selected_index = (self.selected_index + step) % len(self.options)
            return True
        return False

    def handle_confirm(self) -> bool:
        if self.selected_index is None or not self.options:
            return False
        selected = self.options[self.selected_index]
        if isinstance(selected, dict) and callable(selected.get("callback")):
            selected["callback"]()
        return True

    def handle_back(self) -> bool:
        from utils.ui_mode_manager import set_ui_mode
        set_ui_mode(UIMode.MAIN)
        return True

    def draw_buttons(self, screen, option_rects, draw_icons=False, dimmed=False, highlighted_index=None):
        self.rects = [r for _, r in option_rects]

        icon_size = 32
        icon_pad = 8

        for i, (label, rect) in enumerate(option_rects):
            item = self.options[i] if isinstance(self.options[i], dict) else {}
            is_selected = (self.selected_index == i)
            is_highlighted = (highlighted_index == i)
            is_active = item.get("active", False)
            is_disabled = item.get("disabled", False)

            fill_color = self.base_color
            border_color = self.default_border
            text_color = (255, 255, 255)

            if is_highlighted:
                fill_color = (0, 180, 180)
            elif is_selected:
                fill_color = self.selected_color
                border_color = self.selected_border
            if is_active:
                fill_color = (90, 130, 180)
            if is_disabled:
                fill_color = (40, 40, 40)
                text_color = (120, 120, 120)
            if dimmed:
                text_color = (160, 160, 160)

            pygame.draw.rect(screen, fill_color, rect, border_radius=self.border_radius)
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=self.border_radius)

            icon_offset = 0
            if draw_icons and item.get("icon"):
                icon_img = get_icon(item["icon"], size=(icon_size, icon_size))
                if icon_img:
                    icon_x = rect.x + icon_pad
                    icon_y = rect.y + (rect.height - icon_size) // 2
                    screen.blit(icon_img, (icon_x, icon_y))
                    icon_offset = icon_size + icon_pad * 2

            text = self.font.render(label, True, text_color)
            text_x = rect.x + icon_offset + (rect.width - icon_offset - text.get_width()) // 2
            text_y = rect.y + (rect.height - text.get_height()) // 2
            screen.blit(text, (text_x, text_y))

    def generate_button_rects(self, x, y):
        """
        Generate (label, rect) tuples for each option, using configured size and spacing.
        Returns a list of (str, pygame.Rect)
        """
        rects = []
        for i, item in enumerate(self.options):
            label = item if isinstance(item, str) else item.get("label", f"Option {i+1}")
            rect = pygame.Rect(x, y + i * (self.button_height + self.button_spacing), self.button_width, self.button_height)
            rects.append((label, rect))
        return rects

    # Add this to class BaseMenu

    def draw(self, surface, *, x=0, y=0, draw_icons=False, dimmed=False):
        option_rects = self.generate_button_rects(x, y)
        self.draw_buttons(surface, option_rects, draw_icons=draw_icons, dimmed=dimmed)
