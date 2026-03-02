# file: ui/menus/settings_menu.py

import pygame
from utils.enums import FogOfWarMode
from ui.menus.base_menu import BaseMenu

class SettingsMenu(BaseMenu):
    def __init__(self, get_fog_mode, set_fog_mode):
        super().__init__()
        self.get_fog_mode = get_fog_mode
        self.set_fog_mode = set_fog_mode

        self.settings = [
            {
                "label": "Fog of War",
                "get": self.get_fog_mode,
                "set": self.set_fog_mode,
                "options": list(FogOfWarMode)
            }
        ]

        self.options = []
        for setting in self.settings:
            for opt in setting["options"]:
                self.options.append({
                    "label": f"{setting['label']}: {opt.name.title()}",
                    "callback": lambda o=opt, s=setting: s["set"](o),
                    "active": setting["get"]() == opt
                })

        self.options.append({"label": "Back", "callback": self.go_back})
        self.button_width = 280
        self.button_height = 42
        self.button_spacing = 12
        self.border_radius = 10

    def go_back(self):
        return "back"

    def handle_action(self, action: str) -> bool:
        return super().handle_action(action)

    def draw(self):
        screen = pygame.display.get_surface()
        screen.fill((25, 25, 25))
        title = self.font.render("Settings", True, (255, 255, 255))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 50))

        x = screen.get_width() // 2 - self.button_width // 2
        y = 120

        option_rects = self.generate_button_rects(x, y)
        self.draw_buttons(screen, option_rects, draw_icons=False, dimmed=False)

        pygame.display.flip()
