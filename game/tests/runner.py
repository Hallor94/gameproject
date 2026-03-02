import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from ui.components.portrait_box import PortraitBoxWide
from utils import globals as G
from utils import image_cache
from utils.init_helper import init_fonts, init_global_managers
from utils.image_cache import preload_all_ui_icons
from entities.player_character import PlayerCharacter



class DummyEntity:
    def __init__(self, character):
        self.player_name = "TestPlayer"
        self.character = character
        self.health = character.max_health
        self.max_health = character.max_health
        self.move_points = character.move_points
        self.max_move_points = character.move_points
        self.base_attack = character.base_attack
        self.effects = DummyEffects()

    def get_stat(self, key):
        return getattr(self.character, key)


class DummyEffects:
    def get_stat_color(self, stat, mod, base):
        return (255, 255, 255)

    def get_all_effects(self):
        return []



def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    G.screen = screen
    init_fonts()
    init_global_managers()

    preload_all_ui_icons()

    character = Character.load_characters()[3]
    entity = DummyEntity(character)
    box = PortraitBoxWide(entity, {}, scale=1.0)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((10, 10, 10))
        box.draw(screen, 50, 50)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
