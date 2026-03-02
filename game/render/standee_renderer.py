# file: render/standee_renderer.py

import pygame
from config import constants
from utils import globals as G
from utils.image_cache import get_standee
from utils.coordinate_helper import CoordinateHelper
from utils.logger import log_warn
from entities.enemy_marker import get_entity_mark_icon


def get_scaled_standee_and_rect(entity):
    if not entity.tile:
        return None, None

    world_x, world_y = entity.world_x, entity.world_y
    screen_x, screen_y = CoordinateHelper.world_to_screen(world_x, world_y)

    base_h = int(entity.tile.world_rect.height * constants.STANDEE_HEIGHT_RATIO)
    char_scale = getattr(entity, "character_scale", 1.0)
    zoom = G.camera_scale

    draw_h = int(base_h * char_scale * zoom)
    standee_key = entity.get_standee()

    image = get_standee(standee_key, draw_h, draw_h)
    if not image:
        log_warn("Standees", f"Could not load standee image for: {standee_key}", file=__file__)
        return None, None

    aspect_ratio = image.get_width() / image.get_height()
    draw_w = int(draw_h * aspect_ratio)

    scaled_image = pygame.transform.smoothscale(image, (draw_w, draw_h))
    draw_rect = pygame.Rect(0, 0, draw_w, draw_h)
    draw_rect.midbottom = (screen_x, screen_y)

    return scaled_image, draw_rect


def draw_standee(entity, surface, debug_mode=False):
    if not entity.tile:
        return

    image, draw_rect = get_scaled_standee_and_rect(entity)
    if not image:
        return

    surface.blit(image, draw_rect)

    # Draw enemy mark if applicable
    if getattr(entity, "type", None) == "enemy":
        mark_icon = get_entity_mark_icon(entity)
        if mark_icon:
            mark_size = int(draw_rect.height * 0.18)
            icon_surf = pygame.transform.smoothscale(mark_icon, (mark_size, mark_size))
            icon_rect = icon_surf.get_rect(center=(draw_rect.centerx, draw_rect.bottom - mark_size // 2))
            surface.blit(icon_surf, icon_rect)

    if debug_mode:
        pygame.draw.rect(surface, (255, 0, 0), draw_rect, 1)


def draw_standee_outline(surface, entity, color=(255, 255, 0), thickness=4, scale_boost=1.02):
    image, draw_rect = get_scaled_standee_and_rect(entity)
    if not image:
        return

    # Step 1: Slightly enlarge image for outline generation
    orig_size = image.get_size()
    boosted_size = (int(orig_size[0] * scale_boost), int(orig_size[1] * scale_boost))
    boosted_image = pygame.transform.smoothscale(image, boosted_size)

    # Step 2: Create mask and outline
    mask = pygame.mask.from_surface(boosted_image)
    outline_points = mask.outline()

    if not outline_points:
        return

    # Step 3: Draw outline on boosted surface
    outline_surface = pygame.Surface(boosted_size, pygame.SRCALPHA)
    pygame.draw.lines(outline_surface, color, True, outline_points, thickness)

    # Step 4: Align boosted outline to original draw position
    offset_x = draw_rect.centerx - boosted_size[0] // 2
    offset_y = draw_rect.centery - boosted_size[1] // 2
    surface.blit(outline_surface, (offset_x, offset_y))

    # Step 5: Draw original standee on top
    surface.blit(image, draw_rect.topleft)
