# file: render/tile_ui_overlay_renderer.py

import pygame
from config import constants
from utils.image_cache import get_icon
from utils import globals as G
from utils.logger import log_warn


def draw_tile_header(screen, tile, screen_x, screen_y, screen_width, scale=1.0, font=None, icon_size=None):
    font = font or G.menu_font
    icon_size = icon_size or int(60 * scale)
    spacing = int(4 * scale)

    name_padding_x = int(6 * scale)
    name_padding_y = int(4 * scale)
    text_x = screen_x + spacing + name_padding_x
    text_y = screen_y + spacing + name_padding_y

    name_surf = font.render(tile.name, True, (255, 255, 255))
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        outline = font.render(tile.name, True, (0, 0, 0))
        screen.blit(outline, (text_x + dx, text_y + dy))
    screen.blit(name_surf, (text_x, text_y))

    icons = []
    if tile.has_main_quest and tile.has_side_quest:
        icons.append("icon_tile_mqsq")
    elif tile.has_main_quest:
        icons.append("icon_tile_mq")
    elif tile.has_side_quest:
        icons.append("icon_tile_sq")

    if tile.has_loot and tile.loot_count > 0:
        icons.append("icon_tile_loot")
    if tile.has_vent:
        icons.append("icon_tile_vent")
    if tile.is_explored:
        icons.append("icon_tile_done")

    for i, icon_key in enumerate(icons):
        icon_img = get_icon(icon_key, size=(icon_size, icon_size))
        if not icon_img:
            continue

        icon_x = screen_x + screen_width - (icon_size + spacing) * (i + 1)
        icon_y = screen_y + spacing
        screen.blit(icon_img, (icon_x, icon_y))

        if icon_key == "icon_tile_loot" and tile.loot_count > 0:
            count_font = pygame.font.SysFont(None, int(G.cost_font.get_height() * scale))
            count_text = count_font.render(str(tile.loot_count), True, (255, 255, 255))
            outline = count_font.render(str(tile.loot_count), True, (0, 0, 0))

            cx = icon_x + icon_size // 2
            cy = icon_y + icon_size // 2
            screen.blit(outline, outline.get_rect(center=(cx + 1, cy + 1)))
            screen.blit(count_text, count_text.get_rect(center=(cx, cy)))


def draw_tile_overlay(screen, tile, scale, font, offset_x=0, offset_y=0):
    if tile.visibility_state.name == "HIDDEN":
        return

    screen_x = int(tile.world_rect.x * scale + offset_x)
    screen_y = int(tile.world_rect.y * scale + offset_y)
    screen_w = int(tile.world_rect.width * scale)
    screen_h = int(tile.world_rect.height * scale)

    draw_tile_header(screen, tile, screen_x, screen_y, screen_w, scale=scale, font=font)

    if tile.move_cost > 1:
        icon_size = int(60 * scale)
        spacing = int(4 * scale)
        move_icon = get_icon("move", size=(icon_size, icon_size))

        icon_x = screen_x + screen_w - icon_size - spacing
        icon_y = screen_y + screen_h - icon_size - spacing

        if move_icon:
            scaled = pygame.transform.smoothscale(move_icon, (icon_size, icon_size))
            screen.blit(scaled, (icon_x, icon_y))
        else:
            log_warn("TileUI", "Failed to print move icon on tile.", file=__file__)

        cost_font = pygame.font.SysFont(None, int(G.cost_font.get_height() * scale))
        text_surf = cost_font.render(str(tile.move_cost), True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(icon_x + icon_size // 2, icon_y + icon_size // 2))
        screen.blit(text_surf, text_rect)
