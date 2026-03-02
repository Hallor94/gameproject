# file: game/game_loop.py

import pygame

from config import constants
from entities.spawn_manager import spawn_players
from render_system import render_frame
from update_system import update_all
from map.map_loader import load_test_map
from utils import globals as G
from utils.enums import UIMode
from utils.image_cache import load_random_background
from utils.init_helper import (
    center_camera_on_player,
    init_game_state,
    init_global_managers,
    update_visibility_for_players
)
from utils.ui_mode_manager import set_ui_mode
from utils.logger import log_info, log_debug, log_warn, log_banner


class GameLoop:
    def __init__(self):
        log_banner("GameLoop Start", tag="GameLoop", file=__file__)
        pygame.init()
        G.init_fonts()

        # Setup display
        info = pygame.display.Info()
        G.SCREEN_WIDTH, G.SCREEN_HEIGHT = info.current_w, info.current_h
        G.screen = pygame.display.set_mode((G.SCREEN_WIDTH, G.SCREEN_HEIGHT), pygame.FULLSCREEN)
        log_info("GameLoop", f"Display initialized at {G.SCREEN_WIDTH}x{G.SCREEN_HEIGHT}", file=__file__)

        # Initialize global systems
        init_global_managers()
        G.static_background = load_random_background(screen_size=(G.SCREEN_WIDTH, G.SCREEN_HEIGHT))
        log_info("GameLoop", "Static background selected", file=__file__)

        self.clock = pygame.time.Clock()
        self.running = True
        self.in_setup = True
        self.welcome_shown = False
        self.input_router = G.input_router
        log_info("GameLoop", "Initialization complete", file=__file__)

    def run(self):
        log_banner("GameLoop Running", tag="GameLoop", file=__file__)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.process_event(event)

            if self.in_setup:
                if not self.handle_setup_phase():
                    log_info("GameLoop", "Setup phase complete, entering main loop", file=__file__)
                    self.in_setup = False
                continue

            if not self.welcome_shown:
                log_info("GameLoop", "Displaying welcome message", file=__file__)
                G.message_manager.show_center_dialogue(
                    "Welcome to the game! Press Enter or Escape to continue.",
                    title="Introduction",
                    duration=None
                )
                G.gamestate.ambience.trigger_map_flicker(duration=4.0)
                self.welcome_shown = True

            render_frame()
            update_all(self.clock.get_time() / 1000.0)
            self.clock.tick(constants.FPS)

        log_info("GameLoop", "Exiting game loop and shutting down", file=__file__)
        pygame.quit()

    # --- Input Routing ---

    def process_event(self, event):
        if event.type == pygame.QUIT:
            log_info("Input", "QUIT event received", file=__file__)
            self.running = False
            return

        if G.message_manager.wants_input_block():
            log_debug("Input", "Input blocked by modal message", file=__file__)
            G.message_manager.handle_event(event)
            return

        G.message_manager.handle_event(event)

        if event.type == pygame.KEYDOWN:
            log_debug("Input", f"KeyDown event: {event.key}", file=__file__)
            self.input_router.handle_event(event)

    # --- Setup Phase ---

    def handle_setup_phase(self):
        G.setup_menu.draw(G.screen)
        if G.setup_menu.is_done():
            log_info("Setup", "Setup menu complete, loading game map", file=__file__)

            # Clean exit from setup mode
            if hasattr(G, "setup_menu"):
                G.setup_menu.force_exit()
                
            G.gamemap = load_test_map(G.SCREEN_WIDTH, G.SCREEN_HEIGHT)

            player_data = G.setup_menu.get_player_data()
            log_info("Setup", f"Spawning {len(player_data)} players", file=__file__)
            players = spawn_players(player_data, self.random_spawn_tile)

            init_game_state(players, G.gamemap)
            log_info("Setup", "Game state initialized", file=__file__)

            center_camera_on_player(players[0])
            update_visibility_for_players(players)
            log_info("Setup", "Camera centered and visibility updated", file=__file__)

            set_ui_mode(UIMode.MAIN)
            log_info("Setup", "UI mode set to MAIN", file=__file__)
            return False
        return True

    # temp for random spawns
    def random_spawn_tile(self):
        import random
        x = random.choice([0, 1])
        y = random.choice([0, 1])
        tile = G.gamemap.tiles[y][x]
        log_debug("Setup", f"Selected random spawn tile: ({x}, {y})", file=__file__)
        return tile


if __name__ == '__main__':
    GameLoop().run()
