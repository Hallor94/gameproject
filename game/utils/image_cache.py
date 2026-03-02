# file: utils/image_cache.py

import os
import glob
import random
import pygame
from config.constants import STANDEE_BASE_SIZE, PORTRAIT_SIZE
from utils import globals as G
from utils.logger import log_info, log_warn, log_error, log_debug

# === Internal caches ===
_cache = {}  # key -> surface
icon_cache = {}  # name -> 128x128 surface
popup_image_cache = {}  # name -> high-res surface
overlay_cache = {}  # name -> tile-sized overlay

# === Math ===

MATH_SYMBOL_MAP = {
    # Comparison operators
    ">": "math_greater",
    ">=": "math_greater_equal",
    "<": "math_less",
    "<=": "math_less_equal",
    "=": "math_equal",
    "!=": "math_not_equal",
    # Misc
    ":": "math_col",

    # Arithmetic operators
    "+": "math_plus",
    "-": "math_minus",
    "*": "math_multiply",
    "/": "math_divide"
}


# === Core image loading and scaling ===

def get_scaled_image(key, size=None):
    if os.path.sep in key or key.endswith('.png'):
        log_warn("ImageCache", f"get_scaled_image called with suspicious path '{key}'", file=__file__)
    if key not in _cache:
        log_error("ImageCache", f"Key '{key}' not found in cache. Using placeholder.", file=__file__)
        placeholder = pygame.Surface(size or (64, 64), pygame.SRCALPHA)
        pygame.draw.rect(placeholder, (255, 0, 0), placeholder.get_rect(), 4)
        return placeholder

    img = _cache[key]
    if not size or img.get_size() == size:
        return img

    return pygame.transform.smoothscale(img, size)

def preload_paths(paths, size):
    for path in paths:
        key = os.path.splitext(os.path.basename(path))[0]
        try:
            img = pygame.image.load(path).convert_alpha()
            scaled = pygame.transform.smoothscale(img, size)
            _cache[key] = scaled
        except Exception as e:
            log_error("ImageCache", f"Failed to preload image {path}: {e}", file=__file__)

# === Standees ===

def get_standee(key, width, height):
    cache_key = (key, height)
    if cache_key in _cache:
        return _cache[cache_key]

    if key not in _cache:
        log_error("ImageCache", f"Standee key '{key}' not found in cache.", file=__file__)
        placeholder = pygame.Surface((height, height), pygame.SRCALPHA)
        pygame.draw.rect(placeholder, (255, 0, 0), placeholder.get_rect(), 4)
        _cache[cache_key] = placeholder
        return placeholder

    original = _cache[key]
    aspect = original.get_width() / original.get_height()
    scaled_w = int(height * aspect)
    scaled = pygame.transform.smoothscale(original, (scaled_w, height))
    _cache[cache_key] = scaled
    return scaled

def preload_all_character_images():
    character_root = "assets/characters"

    for root, _, files in os.walk(character_root):
        for file in files:
            if not file.endswith(".png"):
                continue

            file_path = os.path.join(root, file)
            key = os.path.splitext(file)[0]

            try:
                surf = pygame.image.load(file_path).convert_alpha()

                if "portrait" in file:
                    scaled = pygame.transform.smoothscale(surf, PORTRAIT_SIZE)
                    _cache[key] = scaled

                elif "standee" in file:
                    _cache[key] = surf

            except Exception as e:
                log_error("ImageCache", f"Failed to preload {file}: {e}", file=__file__)

def preload_enemy_images():
    log_info("ImageCache", "Preloading enemy images...", file=__file__)
    enemy_root = "assets/enemies"
    fallback_path = os.path.join(enemy_root, "nemoEvil.png")

    for root, _, files in os.walk(enemy_root):
        for file in files:
            if not file.endswith(".png"):
                continue

            file_path = os.path.join(root, file)
            key = os.path.splitext(file)[0]

            try:
                surf = pygame.image.load(file_path).convert_alpha()
                _cache[key] = surf
            except Exception as e:
                log_error("ImageCache", f"Failed to preload enemy image {file}: {e}", file=__file__)

    if os.path.exists(fallback_path):
        key = os.path.splitext(os.path.basename(fallback_path))[0]
        if key not in _cache:
            try:
                surf = pygame.image.load(fallback_path).convert_alpha()
                _cache[key] = surf
                log_info("ImageCache", f"Preloaded fallback image '{key}'", file=__file__)
            except Exception as e:
                log_error("ImageCache", f"Failed to preload fallback image: {e}", file=__file__)

def preload_fallback_images():
    log_info("ImageCache", "Preloading fallback images...", file=__file__)
    fallback_dir = "assets/fallbacks"

    for name in ["nemo", "nemoEvil"]:
        path = os.path.join(fallback_dir, f"{name}.png")
        if os.path.exists(path):
            try:
                surf = pygame.image.load(path).convert_alpha()
                _cache[name] = surf
                log_info("ImageCache", f"Loaded fallback '{name}'", file=__file__)
            except Exception as e:
                log_error("ImageCache", f"Failed to load fallback '{name}': {e}", file=__file__)
        else:
            log_warn("ImageCache", f"Missing fallback image: {name}.png", file=__file__)

# === UI Icons ===

def preload_all_ui_icons(root="assets/ui/icons", size=(128, 128)):
    if getattr(preload_all_ui_icons, "_has_run", False):
        return
    preload_all_ui_icons._has_run = True

    global icon_cache
    icon_cache.clear()
    preload_all_ui_icons._loaded_counts = {}

    for dirpath, _, files in os.walk(root):
        for file in files:
            if not file.endswith(".png"):
                continue
            name = os.path.splitext(file)[0].lower()
            full_path = os.path.join(dirpath, file)
            try:
                img = pygame.image.load(full_path).convert_alpha()
                scaled = pygame.transform.smoothscale(img, size)
                icon_cache[name] = scaled
                category = os.path.relpath(dirpath, root).replace('\\', '/').lower()
                preload_all_ui_icons._loaded_counts[category] = preload_all_ui_icons._loaded_counts.get(category, 0) + 1
            except Exception as e:
                log_error("ImageCache", f"Failed to load icon: {name} ({full_path}): {e}", file=__file__)

def get_icon(name, size=None):
    name = name.lower()

    if name.startswith("math:"):
        symbol = name[5:]
        mapped = MATH_SYMBOL_MAP.get(symbol)
        if not mapped:
            log_error("ImageCache", f"Math icon for '{symbol}' not mapped.")
            return None
        name = mapped

    base = icon_cache.get(name)
    if not base:
        log_error("ImageCache", f"icon '{name}' not found. Using red placeholder.", file=__file__)
        surf_size = size if size else (32, 32)
        placeholder = pygame.Surface(surf_size, pygame.SRCALPHA)
        pygame.draw.circle(placeholder, (255, 0, 0), (surf_size[0] // 2, surf_size[1] // 2), min(surf_size) // 3)
        return placeholder

    if not size or base.get_size() == size:
        return base

    return pygame.transform.smoothscale(base, size)


def preload_all_mark_icons():
    from utils.logger import log_info
    for mark in range(1, 10):
        key = f"mark_{mark}"
        path = os.path.join("assets", "ui", "icons", "marks", f"{key}.png")
        icon_cache[key] = pygame.image.load(path).convert_alpha()
    log_info("ImageCache", "Preloaded all mark icons.")


# === Preload cards ===
def preload_all_card_images(root="assets/cards"):
    log_info("ImageCache", "Preloading card images...", file=__file__)
    for dirpath, _, files in os.walk(root):
        for file in files:
            if not file.lower().endswith(".png"):
                continue
            key = os.path.splitext(file)[0]
            full_path = os.path.join(dirpath, file)
            try:
                img = pygame.image.load(full_path).convert_alpha()
                _cache[key] = img
            except Exception as e:
                log_error("ImageCache", f"Failed to load card image '{file}': {e}", file=__file__)


# === Popup Images ===

def preload_popup_images(root="assets/images", size=(640, 400)):
    global popup_image_cache
    popup_image_cache.clear()

    for file in os.listdir(root):
        if file.endswith(".png"):
            name = os.path.splitext(file)[0].lower()
            full_path = os.path.join(root, file)
            try:
                img = pygame.image.load(full_path).convert_alpha()
                scaled = pygame.transform.smoothscale(img, size)
                popup_image_cache[name] = scaled
            except Exception as e:
                log_error("ImageCache", f"Failed to preload popup {name}: {e}", file=__file__)

def get_popup_image(name):
    return popup_image_cache.get(name.lower())

# === Tiles ===

def preload_tile_backgrounds(tile_types, folder="assets/tiles/base", size=None):
    if not size:
        raise ValueError("Must pass a preload size when calling preload_tile_backgrounds()")

    hidden_path = os.path.join(folder, "hidden.png")
    preload_paths([hidden_path], size)

    paths = []
    for t in tile_types:
        pattern = os.path.join(folder, f"{t}*.png")
        paths += glob.glob(pattern)
    preload_paths(paths, size)

def preload_all_overlays(root="assets/overlays", size=(512, 512)):
    global overlay_cache
    overlay_cache.clear()
    log_info("OverlayCache", f"Loading overlays from '{root}' at size {size}", file=__file__)

    for file in os.listdir(root):
        if not file.endswith(".png"):
            continue
        name = os.path.splitext(file)[0].lower()
        full_path = os.path.join(root, file)
        try:
            img = pygame.image.load(full_path).convert_alpha()
            scaled = pygame.transform.smoothscale(img, size)
            overlay_cache[name] = scaled
        except Exception as e:
            log_error("OverlayCache", f"Failed to load overlay {name}: {e}", file=__file__)

def get_overlay(name, size=None):
    name = name.lower()
    base = overlay_cache.get(name)
    if not base:
        log_error("ImageCache", f"overlay '{name}' not found. Available keys: {list(overlay_cache.keys())}", file=__file__)
        surf_size = size if size else (100, 100)
        placeholder = pygame.Surface(surf_size, pygame.SRCALPHA)
        pygame.draw.rect(placeholder, (255, 0, 0), placeholder.get_rect(), 3)
        return placeholder
    if not size or base.get_size() == size:
        return base
    return pygame.transform.smoothscale(base, size)

# === Background ===

def load_random_background(screen_size=None):
    bg_paths = glob.glob("assets/map/backgrounds/*.png")
    if not bg_paths:
        return None

    chosen = random.choice(bg_paths)
    key = os.path.splitext(os.path.basename(chosen))[0]

    try:
        surf = pygame.image.load(chosen).convert_alpha()
        scaled = pygame.transform.smoothscale(surf, screen_size) if screen_size else surf
        _cache[key] = scaled
        return scaled
    except Exception as e:
        log_error("ImageCache", f"Failed to load background: {chosen}: {e}", file=__file__)
        return None

# === Summary ===

def print_cache_summary():
    counts = getattr(preload_all_ui_icons, "_loaded_counts", {})
    total_icons = sum(counts.values())
    log_info("ImageCache", f"Preloaded {total_icons} UI icons:", file=__file__)
    for category, count in sorted(counts.items()):
        log_info("ImageCache", f" - {category}: {count}", file=__file__)
    log_info("ImageCache", f"Total popup images: {len(popup_image_cache)}", file=__file__)
    log_info("ImageCache", f"Total overlays: {len(overlay_cache)}", file=__file__)
    log_info("ImageCache", f"Total scaled images (get_scaled_image): {len(_cache)}", file=__file__)
    log_info("ImageCache", f"Total standees (via get_standee): {len([k for k in _cache if isinstance(k, tuple)])}", file=__file__)

def verify_icon_set(required_icons):
    missing = [name for name in required_icons if name.lower() not in icon_cache]
    if missing:
        log_warn("ImageCache", f"MISSING ICONS: {missing}", file=__file__)
    else:
        log_info("ImageCache", f"All {len(required_icons)} required icons loaded.", file=__file__)

def has_image(key: str) -> bool:
    if key in _cache:
        return True
    log_warn("ImageCache", f"Missing image key '{key}', falling back.", file=__file__)
    return False
