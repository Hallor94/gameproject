# file: utils/logger.py

import os

# Color maps
TAG_COLORS = {
    "BuffDraw": "\033[38;5;201m",     # Pinkish
    "ContextAction": "\033[38;5;111m",# Light blue
    "Dialogue": "\033[94m",           # Blue
    "EnemyLoader": "\033[95m",        # Magenta
    "GameLoop": "\033[38;5;214m",     # Amber
    "GameState": "\033[38;5;150m",    # Light green
    "ImageCache": "\033[93m",         # Yellow
    "INIT": "\033[38;5;213m",         # Pinkish banner tone
    "Input": "\033[91m",              # Red
    "Inspector": "\033[38;5;208m",    # Orange
    "JsonLoader": "\033[38;5;245m",   # Gray
    "MQTT": "\033[38;5;33m",          # Bright blue
    "OverlayCache": "\033[90m",       # Dim
    "Setup": "\033[38;5;208m",        # Orange
    "Standees": "\033[38;5;160m",     # Red/pink
    "TileOverlay": "\033[38;5;241m",  # Dim gray
    "TileUI": "\033[38;5;118m",       # Green
    "UI": "\033[96m",                 # Cyan
    "UT": "\033[96m",                 # Alias for UI
    "Default": "\033[37m",            # White
}



LEVEL_COLORS = {
    "INFO": "\033[37m",
    "WARN": "\033[33m",
    "ERROR": "\033[31m",
    "DEBUG": "\033[90m",
}

RESET = "\033[0m"

def log(tag, message, level="INFO", file=None, debug_only=False):
    # Lazy import for globals
    from utils import globals as G
    is_debug = getattr(G, "debug_mode", False)

    if debug_only and not is_debug:
        return
    if level.upper() == "DEBUG" and not is_debug:
        return

    tag_color = TAG_COLORS.get(tag, TAG_COLORS["Default"])
    level_color = LEVEL_COLORS.get(level.upper(), "\033[37m")

    tag_str = f"{tag_color}[{tag}]{RESET}"
    level_str = f"{level_color}{level.upper()}{RESET}"
    file_str = f"[{os.path.relpath(file, os.getcwd())}]" if file else ""

    print(f"{tag_str}{file_str} {level_str}: {message}")

# Helper aliases
def log_info(tag, msg, file=None, debug_only=False):
    log(tag, msg, "INFO", file, debug_only)

def log_warn(tag, msg, file=None, debug_only=False):
    log(tag, msg, "WARN", file, debug_only)

def log_error(tag, msg, file=None, debug_only=False):
    log(tag, msg, "ERROR", file, debug_only)

def log_debug(tag, msg, file=None):
    log(tag, msg, "DEBUG", file)

def log_banner(message, tag="INIT", file=None, color="\033[95m"):
    bar = "=" * (len(message) + 10)
    padded = f"==  {message.upper()}  =="
    colored = f"{color}{bar}\n{padded}\n{bar}{RESET}"
    print(colored)
