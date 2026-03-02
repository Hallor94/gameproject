# file: ui/components/icon_legends.py

import pygame
from utils.image_cache import get_icon
from utils import globals as G

COLS = 5
ROWS = 2
PADDING = 12
ICON_SIZE = 40
LABEL_SPACING = 4
DESC_SPACING = 6


def draw_icon_legend(surface, x, y, width, height, entries, font=None, wrap_font=None):
    """
    Draws a 5x2 grid of icon legend entries.
    Each entry: {"icon": "attack", "label": "Attack", "desc": "Description"}
    """
    font = font or G.hud_font
    wrap_font = wrap_font or G.font

    cell_w = width // COLS
    cell_h = height // ROWS

    for i, entry in enumerate(entries[:COLS * ROWS]):
        col = i % COLS
        row = i // COLS
        cx = x + col * cell_w
        cy = y + row * cell_h

        draw_legend_cell(surface, cx, cy, cell_w, cell_h, entry, font, wrap_font)


def draw_legend_cell(surface, x, y, w, h, entry, font, wrap_font):
    """Draw a single cell with icon, label, and description."""
    icon = get_icon(entry["icon"])
    label = entry["label"]
    desc = entry["desc"]

    # Icon
    if icon:
        icon_scaled = pygame.transform.smoothscale(icon, (ICON_SIZE, ICON_SIZE))
        icon_rect = icon_scaled.get_rect(center=(x + w // 2, y + PADDING + ICON_SIZE // 2))
        surface.blit(icon_scaled, icon_rect)

    # Label
    label_surf = font.render(label, True, (255, 255, 255))
    label_rect = label_surf.get_rect(center=(x + w // 2, icon_rect.bottom + LABEL_SPACING))
    surface.blit(label_surf, label_rect)

    # Description (wrapped)
    desc_top = label_rect.bottom + DESC_SPACING
    max_desc_height = h - (desc_top - y) - PADDING
    draw_wrapped_text(surface, desc, wrap_font, x + PADDING, desc_top, w - 2 * PADDING, max_desc_height)


def draw_wrapped_text(surface, text, font, x, y, max_width, max_height=None):
    """Render wrapped text within max width and optional height."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())

    for line in lines:
        line_surf = font.render(line, True, (220, 220, 220))
        if max_height is not None and y + line_surf.get_height() > y + max_height:
            break
        surface.blit(line_surf, (x, y))
        y += line_surf.get_height() + 2
