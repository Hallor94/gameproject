# file: ui/common.py

from utils import globals as G
import pygame

def render_text_centered(surface, text, color, y, font=None):
    """Renders text centered horizontally at a given vertical position using G.font by default."""
    font = font or G.font
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(surf, rect)


def render_text_wrapped_centered(surface, text, font, topleft, width, color=(255, 255, 255)):
    """Renders wrapped multi-line text centered within a box of given width starting at (x, y)."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if font.size(test)[0] <= width:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    x, y = topleft
    for line in lines:
        surf = font.render(line, True, color)
        rect = surf.get_rect(center=(x + width // 2, y))
        surface.blit(surf, rect)
        y += surf.get_height() + 4

def render_text_wrapped(text, font, width):
    """Returns a list of wrapped lines that fit within the given width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if font.size(test)[0] <= width:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
