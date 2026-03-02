import pygame
import sys
from .settings_menu import SettingsMenu
from utils.enums import FogOfWarMode

class PauseMenu:
    def __init__(self):
        screen = pygame.display.get_surface()
        self.active = False
        self.font = pygame.font.SysFont(None, 32)
        self.menu_width = 300
        self.menu_height = 300
        self.menu_rect = pygame.Rect(
            (screen.get_width() - self.menu_width) // 2,
            (screen.get_height() - self.menu_height) // 2,
            self.menu_width,
            self.menu_height
        )
        self.close_button = pygame.Rect(self.menu_rect.right - 30, self.menu_rect.y + 10, 20, 20)
        self.buttons = []
        self.setup_buttons()

        self.in_settings = False
        self.settings_menu = None 

    def setup_buttons(self):
        button_texts = ["Save Game", "Load Game", "Settings", "Exit Game", "", "Continue"]
        self.buttons.clear()
        y = self.menu_rect.y + 20

        for text in button_texts:
            if text == "":
                y += 20  # spacer
                continue
            rect = pygame.Rect(self.menu_rect.x + 20, y, self.menu_width - 40, 40)
            self.buttons.append((text, rect))
            y += 50

    def toggle(self):
        self.active = not self.active

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.in_settings:
                self.in_settings = False
            elif self.active:
                self.active = False
            else:
                self.active = True
            return



    def handle_click(self, label):
        if label == "Exit Game":
            pygame.quit()
            sys.exit()
        elif label == "Continue":
            self.active = False
        else:
            print(f"[Menu] '{label}' clicked (placeholder)")

    def draw(self, screen):
        if not self.active:
            return
        if self.in_settings:
            self.settings_menu.draw()
            return
        pygame.draw.rect(screen, (150, 50, 50), self.close_button)
        x_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (self.close_button.x + 4, self.close_button.y))

        pygame.draw.rect(screen, (30, 30, 30), self.menu_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.menu_rect, 3)

        for label, rect in self.buttons:
            pygame.draw.rect(screen, (60, 60, 60), rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, 2)
            text = self.font.render(label, True, (255, 255, 255))
            screen.blit(text, (rect.x + 10, rect.y + 8))
            
    def set_settings_hooks(self, get_fog_mode, set_fog_mode):
        self.settings_menu = SettingsMenu(get_fog_mode, set_fog_mode)