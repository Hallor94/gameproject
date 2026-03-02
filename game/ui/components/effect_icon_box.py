# file: ui/components/effect_icon_box.py

import pygame
from utils import globals as G
from utils.image_cache import get_icon, icon_cache
from utils.logger import log_warn, log_debug
from ui.common import render_text_wrapped

STAT_LABELS = {
    "strength": "STR", "endurance": "END", "dexterity": "DEX",
    "intelligence": "INT", "nerve": "NRV", "luck": "LCK",
    "health": "HP", "move_points": "MOV", "attack": "ATK", "base_attack": "ATK"
}

MOD_COLOR = (255, 255, 255)
DESC_COLOR = (220, 220, 220)
SRC_COLOR = (180, 180, 180)
BOX_BG = (10, 10, 10)
BOX_BORDER = (80, 80, 80)

BUFF_COLORS = {
    "buff": (80, 180, 80),
    "debuff": (200, 60, 60),
    "mixed": (200, 180, 60),
    "aura": (130, 80, 200),
}


def get_buff_frame_color(effect):
    pos, neg = 0, 0
    for mod in effect.modifiers.values():
        val = mod.get("add") if isinstance(mod, dict) else mod
        if isinstance(val, (int, float)):
            if val > 0: pos += 1
            elif val < 0: neg += 1
    if "aura" in effect.tags:
        return BUFF_COLORS["aura"]
    if pos and neg:
        return BUFF_COLORS["mixed"]
    if pos:
        return BUFF_COLORS["buff"]
    if neg:
        return BUFF_COLORS["debuff"]
    return (140, 140, 140)


def get_modifier_summary(mod_dict):
    parts = []
    for stat, mod in mod_dict.items():
        label = STAT_LABELS.get(stat, stat[:3].upper())
        if isinstance(mod, dict):
            if "add" in mod:
                parts.append(f"{label} +{mod['add']}")
            if "mul" in mod:
                parts.append(f"{label} ×{mod['mul']}")
            if "set" in mod:
                parts.append(f"{label} = {mod['set']}")
        elif isinstance(mod, (int, float)):
            sign = "+" if mod >= 0 else ""
            parts.append(f"{label} {sign}{mod}")
    return parts


def draw_effect_icon_box(surface, effect, x, y, size=64, detailed=False, width=240):
    if not effect or not effect.icon:
        return
    if not detailed:
        if G.debug_mode:
            log_debug("BuffDraw", f"effect.icon = '{effect.icon}'", file=__file__)
            log_debug("BuffDraw", f"available keys = {list(icon_cache.keys())}", file=__file__)
        icon = get_icon(effect.icon, size=(size, size))
        if not icon:
            log_warn("BuffDraw", f"Skipping effect '{effect.name}' due to missing icon '{effect.icon}'", file=__file__)
            return

        surface.blit(icon, (x, y))
        color = get_buff_frame_color(effect)
        pygame.draw.rect(surface, color, pygame.Rect(x, y, size, size), 2)

        if effect.remaining_duration is not None:
            font = G.stat_font
            duration = str(effect.remaining_duration)
            text = font.render(duration, True, (255, 255, 255))
            outline = font.render(duration, True, (0, 0, 0))
            tx, ty = text.get_size()
            px = x + (size - tx) // 2
            py = y + (size - ty) // 2
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                surface.blit(outline, (px + dx, py + dy))
            surface.blit(text, (px, py))
        return

    # --- Detailed panel ---
    font = G.stat_font
    small_font = G.hud_font

    line_height = font.get_height() 
    mod_lines = get_modifier_summary(effect.modifiers)
    desc_lines = render_text_wrapped(effect.description or "", font, width - size - 16)
    height = max(size, len(mod_lines) * line_height) + len(desc_lines) * line_height + line_height * 2

    panel_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, BOX_BG, panel_rect)
    pygame.draw.rect(surface, BOX_BORDER, panel_rect, 2)

    icon = get_icon(effect.icon)
    if icon:
        icon_img = pygame.transform.smoothscale(icon, (size, size))
        surface.blit(icon_img, (x, y))

    if effect.remaining_duration is not None:
        dur_text = str(effect.remaining_duration)
        dur_surf = font.render(dur_text, True, (255, 255, 255))
        dur_rect = dur_surf.get_rect(center=(x + size // 2 , y + size // 2 ))
        surface.blit(dur_surf, dur_rect)

    for i, line in enumerate(mod_lines):
        line_surf = small_font.render(line, True, MOD_COLOR)
        surface.blit(line_surf, (x + size + 12, y  + i * line_height))

    name_surf = font.render(effect.name, True, (255, 255, 255))
    surface.blit(name_surf, (x + size + 12, y))

    desc_y = y + max(size, len(mod_lines) * line_height) 
    for i, line in enumerate(desc_lines):
        surf = small_font.render(line, True, DESC_COLOR)
        surface.blit(surf, (x + 6, desc_y + i * line_height))

    if effect.source:
        src_surf = small_font.render(f"Source: {effect.source}", True, SRC_COLOR)
        surface.blit(src_surf, (x + 6, desc_y + len(desc_lines) * line_height ))

    return height
