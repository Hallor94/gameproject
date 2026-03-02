# file: utils/init_helper.py

import json
import pygame
import random

from utils import globals as G
from utils.logger import log_banner, log_info, log_debug

# Managers
from actions.loot_manager import LootManager
from animations.movement_animator import MovementAnimator
from entities.effects import effect_loader
from entities.enemy_character_loader import load_enemies
from entities import spawn_manager
from events.dialogue.dialogue_manager import DialogueManager
from events.dialogue.dialogue_loader import load_all_triggers
from gamestate.ambience_manager import AmbienceManager
from gamestate.gamestate_manager import GameStateManager
from input_system import register_all_input_handlers
from input.input_router import InputRouter
from input.mqtt_bridge import init_mqtt_bridge
from map.contextual_action_manager import ContextualActionManager
from map.tile_status_manager import TileStatusManager
from objectives.objective_manager import ObjectivesManager
from objectives.objective_loader import load_objectives
from setup.setup_menu import SetupMenu
from ui.components.loading_icon import LoadingIcon
from ui.menus.action_menu import ActionMenu
from ui.menus.context_menu import ContextMenu
from ui.hud import HUD
from ui.inspector.inspector_ui import InspectorUI
from ui.message_manager import MessageManager
from ui.menus.pause_menu import PauseMenu
from ui.menus.resolver_menu import ResolverMenu
from utils.enums import Difficulty
from utils.image_cache import (
    preload_all_character_images, preload_all_ui_icons,
    preload_all_mark_icons, preload_all_card_images,
    preload_popup_images, get_icon, preload_all_overlays,
    preload_fallback_images, preload_enemy_images, 
    print_cache_summary, verify_icon_set
)
from utils.logger import (
    log_banner, log_info, log_warn, log_error, log_debug
)

def init_global_managers():
    """Initialize global UI and manager instances used across menus and gameplay."""
    log_info("INIT", "Initializing global managers...", file=__file__)

    # Fonts
    G.font = pygame.font.SysFont(None, 20)

    # Setup menu (used early)
    G.setup_menu = SetupMenu()
    log_debug("INIT", "Setup menu initialized", file=__file__)

    # Preload images and fonts
    preload_all_character_images()
    init_enemies()
    preload_fallback_images()
    preload_all_ui_icons()
    preload_popup_images()
    preload_all_mark_icons()
    preload_all_card_images()
    log_info("INIT", "All core images preloaded", file=__file__)

    G.stat_icons = {
        key: get_icon(key) for key in [
            "strength", "endurance", "dexterity",
            "intelligence", "nerve", "luck",
            "health", "move", "attack"
        ]
    }
    log_debug("INIT", "Stat icons assigned to G.stat_icons", file=__file__)

    verify_icon_set([
        "strength", "endurance", "dexterity", "intelligence", "nerve", "luck",
        "health", "move", "attack", "firstplayer", "combat", "camera", "hourglass"
    ])

    G.stat_bg_colors = {
        "strength": (40, 30, 30),
        "endurance": (40, 30, 30),
        "dexterity": (30, 40, 30),
        "intelligence": (30, 30, 40),
        "nerve": (30, 30, 30),
        "luck": (30, 30, 40),
        "health": (20, 20, 20),
        "move": (20, 20, 20),
        "attack": (20, 20, 20),
    }
    log_debug("INIT", "Stat background colors assigned", file=__file__)

    G.difficulty = Difficulty.NORMAL
    log_debug("INIT", f"Difficulty set to {G.difficulty.name.title()}.", file=__file__)

    # UI + Menu instances
    G.message_manager = MessageManager()
    G.action_menu = ActionMenu()
    G.pause_menu = PauseMenu()
    G.context_menu = ContextMenu()
    G.resolver_menu = ResolverMenu()
    log_info("INIT", "UI menus instantiated", file=__file__)

    # Managers
    G.loot_manager = LootManager()
    G.objectives_manager = ObjectivesManager()
    G.movement_animator = MovementAnimator()
    G.tile_status_manager = TileStatusManager()
    log_info("INIT", "Core game managers instantiated", file=__file__)

    # Event-driven systems
    init_dialogue_manager()
    load_objectives("objectives/test_map.json", {})
    log_info("INIT", "Objectives and dialogues loaded", file=__file__)

    G.effect_catalog = effect_loader.load_effects()
    log_debug("INIT", "Effects catalog loaded", file=__file__)

    # Context action system
    G.contextual_action_manager = ContextualActionManager()
    log_info("INIT", "Contextual action system ready", file=__file__)

    # InputRouter (placed last to guarantee all menus exist)
    G.input_router = InputRouter()
    register_all_input_handlers(G.input_router)
    log_info("INIT", "Input system registered", file=__file__)

    log_banner("Global Managers Initiated", tag="INIT", file=__file__, color="\033[96m")

    # Listener
    init_mqtt_bridge()
    G.loading_icon = LoadingIcon(frame_count=24, frame_duration=50)

def init_game_state(players, gamemap):
    """Initialize gameplay state: players, enemies, objectives, HUD."""
    log_info("INIT", "Initializing game state...", file=__file__)

    G.gamestate = GameStateManager(players, enemies=[], map_ref=gamemap)
    G.gamestate.message_manager = G.message_manager
    G.gamestate.ambience = AmbienceManager(gamemap)
    log_debug("INIT", "GameStateManager and AmbienceManager ready", file=__file__)

    G.hud = HUD()
    G.pause_menu.set_settings_hooks()
    preload_all_overlays(size=(G.gamemap.tile_width, G.gamemap.tile_height))
    log_debug("INIT", "HUD, overlays, and pause settings initialized", file=__file__)

    print_cache_summary()

    G.inspector = InspectorUI()
    G.DEBUG_ATTR_WARNINGS = True
    log_info("INIT", "Inspector ready and debug warnings enabled", file=__file__)

    spawn_manager.init_spawn_manager()
    spawn_manager.spawn_initial_enemies()

    log_banner("Game State Initiated", tag="INIT", file=__file__, color="\033[92m")


def init_dialogue_manager():
    log_banner("Dialogue Loader", tag="Dialogue", file=__file__, color="\033[95m")
    G.dialogue_manager = DialogueManager()
    G.dialogue_manager.subscribe_to_events()
    log_debug("Dialogue", "Subscribed to event system", file=__file__)

    triggers = load_all_triggers("events/dialogue/triggers/")
    for t in triggers:
        G.dialogue_manager.register_trigger(t)
    log_info("Dialogue", f"Registered {len(triggers)} dialogue triggers", file=__file__)

    log_banner("Dialogue Finished Loading", tag="Dialogue", file=__file__, color="\033[95m")


def init_enemies():
    """Initialize all enemy data and preload required images."""
    log_banner("Enemy Loader", tag="Enemies", file=__file__, color="\033[91m")

    preload_enemy_images()
    G.enemy_pool = load_enemies()
    log_info("Enemies", f"Loaded {len(G.enemy_pool)} enemies into pool", file=__file__)

    random.shuffle(G.enemy_pool)
    log_debug("Enemies", "Enemy pool shuffled", file=__file__)

    log_banner("Finished Loading Enemies", tag="Enemies", file=__file__, color="\033[91m")

def center_camera_on_player(player):
    """Center the camera on a player's tile immediately."""
    tile = player.tile
    if not tile:
        log_warn("Camera", "No tile found for player; cannot center camera", file=__file__)
        return

    grid_x, grid_y = tile.grid_pos
    world_cx = grid_x * G.gamemap.tile_width + G.gamemap.tile_width // 2
    world_cy = grid_y * G.gamemap.tile_height + G.gamemap.tile_height // 2

    zoom = 1.5
    G.camera_scale = zoom

    screen_w, screen_h = G.SCREEN_WIDTH, G.SCREEN_HEIGHT
    offset_x = -world_cx * zoom + screen_w // 2
    offset_y = -world_cy * zoom + screen_h // 2

    G.gamemap.camera.offset_x = offset_x
    G.gamemap.camera.offset_y = offset_y
    G.gamemap.camera.target_offset_x = offset_x
    G.gamemap.camera.target_offset_y = offset_y
    log_debug("Camera", f"Camera centered on player at tile ({grid_x}, {grid_y})", file=__file__)


def update_visibility_for_players(players):
    """Update fog-of-war visibility for all player tiles."""
    tiles = [p.tile for p in players if p.tile is not None]
    G.gamemap.update_visibility(tiles)
    log_debug("Map", f"Visibility updated for {len(tiles)} player tiles", file=__file__)


def init_fonts():
    G.init_fonts()
    log_info("INIT", "Fonts initialized", file=__file__)
