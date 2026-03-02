import pygame
from utils.enums import FogOfWarMode

class SettingsMenu:
    def __init__(self, get_fog_mode, set_fog_mode):
        self.font = pygame.font.SysFont(None, 32)
        screen = pygame.display.get_surface()
        self.screen = screen
        self.options = list(FogOfWarMode)
        self.get_fog_mode = get_fog_mode
        self.set_fog_mode = set_fog_mode
        self.dropdown_open = False

        self.dropdown_rect = pygame.Rect(200, 150, 200, 40)
        self.back_button_rect = pygame.Rect(200, 300, 200, 40)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.dropdown_rect.collidepoint(event.pos):
                self.dropdown_open = not self.dropdown_open
            elif self.dropdown_open:
                for i, option in enumerate(self.options):
                    opt_rect = pygame.Rect(self.dropdown_rect.x, self.dropdown_rect.y + (i + 1) * 40, 200, 40)
                    if opt_rect.collidepoint(event.pos):
                        self.set_fog_mode(option)
                        self.dropdown_open = False
                        break
            elif self.back_button_rect.collidepoint(event.pos):
                return "back"

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"

        return None

    def draw(self):
        self.screen.fill((25, 25, 25))
        title = self.font.render("Settings", True, (255, 255, 255))
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 50))

        # Dropdown
        pygame.draw.rect(self.screen, (60, 60, 60), self.dropdown_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.dropdown_rect, 2)
        current_mode = self.get_fog_mode()
        label = self.font.render(f"Fog Mode: {current_mode.name}", True, (255, 255, 255))
        self.screen.blit(label, (self.dropdown_rect.x + 10, self.dropdown_rect.y + 5))

        if self.dropdown_open:
            for i, option in enumerate(self.options):
                rect = pygame.Rect(self.dropdown_rect.x, self.dropdown_rect.y + (i + 1) * 40, 200, 40)
                pygame.draw.rect(self.screen, (40, 40, 40), rect)
                pygame.draw.rect(self.screen, (80, 80, 80), rect, 1)
                opt_label = self.font.render(option.name.title(), True, (220, 220, 220))
                self.screen.blit(opt_label, (rect.x + 10, rect.y + 5))

        # Back Button
        pygame.draw.rect(self.screen, (80, 80, 80), self.back_button_rect)
        back_text = self.font.render("Back", True, (255, 255, 255))
        self.screen.blit(back_text, (self.back_button_rect.x + 10, self.back_button_rect.y + 5))

        pygame.display.flip()

    