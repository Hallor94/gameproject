# file: utils/globals.py

import pygame
from config import constants as G_constants

# === Debug and System Flags ===
debug_mode = None
DEBUG_ATTR_WARNINGS = False
camera_scale = 1.0

# === Core Screen & Game Context ===
screen = None
gamestate = None
gamemap = None
enemy_pool = None
difficulty = None

# === Game Systems / Managers ===
message_manager = None
dialogue_manager = None
movement_animator = None
objectives_manager = None
loot_manager = None  # Handles loot spawn & interaction
effect_catalog = {}  # id -> Effect instance
tile_status_manager = None
is_recognizer_busy = False

# === UI Menus ===
setup_menu = None
pause_menu = None
action_menu = None
context_menu = None
contextual_action_menu = None
active_menu = None
inspector = None 
active_resolver = None
resolver_menu = None

# === Fonts ===
font = None
title_font = None
menu_font = None
stat_font = None
flavor_font = None
dialogue_font = None
speech_font = None
floating_font = None

# === Static UI Assets ===
static_background = None
stat_icons = None
stat_bg_colors = None

# === Font Initialization ===
def init_fonts():
    font_globals = globals()
    for name in dir(G_constants):
        if name.startswith("FONT_"):
            font_id = name.lower().replace("font_", "") + "_font"
            size = getattr(G_constants, name)
            font_globals[font_id] = pygame.font.SysFont(None, size)

# === Global Init ===
def init(pygame_screen):
    global screen
    screen = pygame_screen
    init_fonts()