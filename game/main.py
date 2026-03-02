import pygame
from config import constants
from ui.menus.setup_menu import SetupMenu
from ui.menus.pause_menu import PauseMenu
from utils.enums import FogOfWarMode
from entities.player import Player
from gamestate.manager import GameStateManager
from map.map_manager import MapManager
from map.map_loader import load_test_map

def main():
    pygame.init()
    info = pygame.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    # Setup menu
    setup_menu = SetupMenu()
    setup_menu.assign_default_characters()

    # Pause menu
    pause_menu = PauseMenu()
    settings_menu = None
    in_settings = False
    
    running = True
    in_setup = True
    gamemap = None
    gamestate = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and in_setup:
                running = False

            if in_setup:
                setup_menu.handle_input(event)
            else:
                pause_menu.handle_event(event)


        if in_setup:
            setup_menu.draw()
            if setup_menu.is_done():
                players = [Player(p["name"], p["character"]) for p in setup_menu.get_player_data()]
                gamemap = load_test_map(SCREEN_WIDTH, SCREEN_HEIGHT)
                gamestate = GameStateManager(players, enemies=[], map_ref=gamemap)
                pause_menu.set_settings_hooks(
                get_fog_mode=lambda: gamemap.fog_mode,
                set_fog_mode=lambda mode: setattr(gamemap, "fog_mode", mode)
                )

                print("Game started with players:")
                for player in players:
                    print(player)

                in_setup = False
        else:
            screen.fill((0, 0, 0))
            gamemap.draw(screen)
            if pause_menu.active:
                pause_menu.draw(screen)
            pygame.display.flip()

    clock.tick(constants.FPS)

pygame.quit()


if __name__ == '__main__':
    main()
