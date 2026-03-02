# file: ui/inspector/tile_inspector.py

import pygame
from render.tile_ui_overlay_renderer import draw_tile_header
from utils import globals as G


def get_filtered_tile_options(tile):
    """
    Return filtered context actions: only display interesting tile options
    like quests, vents, loot — not generic movement or inspect actions.
    """
    G.contextual_action_manager.populate_tile_actions(tile)
    actions = G.contextual_action_manager.get_actions(tile.grid_pos)

    # Filter out default actions we don't care about in inspection
    skip_ids = {"inspect", "move", "attack"}
    return [a for a in actions if a.id not in skip_ids]


def draw_tile_panel(surface, tile, interactive=True, selected_index=None):
    if not tile:
        return

    from render.tile_ui_overlay_renderer import draw_tile_header

    button_width = 280
    button_height = 42
    button_spacing = 8
    border_radius = 6
    font = G.context_font

    # --- Prepare actions ---
    G.contextual_action_manager.populate_tile_actions(tile)
    actions = G.contextual_action_manager.get_actions(tile.grid_pos)

    if not interactive:
        skip_ids = {"inspect", "move", "attack"}
        actions = [a for a in actions if a.id not in skip_ids]
    else:
        actions = [a for a in actions if a.id != "inspect"]

    # --- Sizes ---
    banner_height = 140  # fixed visual height for banner area
    label_height = 32
    menu_top_overlap = 40

    button_area_height = len(actions) * (button_height + button_spacing)
    total_height = banner_height + label_height + button_area_height

    # Create render surface
    menu_surface = pygame.Surface((button_width, total_height), pygame.SRCALPHA)

    # === 1. Draw banner + gradient ===
    banner_image = tile.background_image
    if banner_image:
        banner = pygame.transform.smoothscale(banner_image, (button_width, banner_height))
        menu_surface.blit(banner, (0, 0))

    gradient = pygame.Surface((button_width, banner_height), pygame.SRCALPHA)
    for i in range(banner_height):
        alpha = int(255 * max(0, min(1, (i / banner_height) ** 1.6)))
        pygame.draw.line(gradient, (30, 30, 30, alpha), (0, i), (button_width, i))
    menu_surface.blit(gradient, (0, 0))

    # === 2. Draw tile header (on top of banner) ===
    draw_tile_header(menu_surface, tile, 0, 0, button_width, scale=1.0, font=font, icon_size=40)

    # === 3. Label ===
    label_text = font.render("Tile Actions", True, (255, 255, 255))
    label_rect = label_text.get_rect(center=(button_width // 2, banner_height + 8))
    menu_surface.blit(label_text, label_rect)

    # === 4. Buttons ===
    button_start_y = banner_height + label_height
    for i, action in enumerate(actions):
        bx = 5
        by = button_start_y + i * (button_height + button_spacing)

        if interactive and selected_index == i:
            pygame.draw.rect(menu_surface, (200, 200, 50), (bx - 2, by - 2, button_width - 6, button_height + 4), border_radius=6)

        pygame.draw.rect(menu_surface, (50, 50, 50), (bx, by, button_width - 10, button_height), border_radius=6)
        label = font.render(action.label, True, (220, 220, 220))
        menu_surface.blit(label, (bx + 10, by + 8))

    # === 5. Final blit — anchored to bottom-right ===
    x = surface.get_width() - button_width - 20
    y = surface.get_height() - total_height - 30
    surface.blit(menu_surface, (x, y))
