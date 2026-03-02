# file: ui/inspector/entity_inspector.py

import pygame
from ui.components.icon_legend import draw_icon_legend
from utils import globals as G
from utils.image_cache import get_scaled_image
from utils.logger import log_debug 



GRID_COLS = 36
GRID_ROWS = 18

COLOR_GRID = (50, 50, 50)
COLOR_BORDER = (180, 180, 180)
COLOR_LABEL = (255, 255, 255)

COLOR_HEADER = (30, 30, 60)
COLOR_STANDEE = (60, 30, 30)
COLOR_STATS = (30, 60, 30)
COLOR_EFFECTS = (30, 30, 30)
COLOR_LEGEND = (50, 30, 50)

selected_index = 0
stat_icons = G.stat_icons

def get_visible_inspectables():
    players = G.gamestate.players
    enemies = [
        e for e in G.gamestate.enemies
        if e.tile and e.tile.visibility_state.name != "HIDDEN"
    ]
    return players + enemies


def draw_entity_inspector(surface):
    inspector = G.inspector
    entities = get_visible_inspectables()
    if not entities:
        return
    selected_index = inspector.selected_entity_index

    width, height = surface.get_width(), surface.get_height()
    cell_w = width // GRID_COLS
    cell_h = height // GRID_ROWS
    font = G.font
    hud_font = G.hud_font
    stat_font = G.stat_font

    def draw_box(x, y, w, h, label, bg_color):
        rect = pygame.Rect(x * cell_w, y * cell_h, w * cell_w, h * cell_h)
        pygame.draw.rect(surface, bg_color, rect)
        pygame.draw.rect(surface, COLOR_BORDER, rect, 2)
        return rect

    def draw_full_grid():
        for col in range(1, GRID_COLS):
            pygame.draw.line(surface, COLOR_GRID, (col * cell_w, 0), (col * cell_w, height))
        for row in range(1, GRID_ROWS):
            pygame.draw.line(surface, COLOR_GRID, (0, row * cell_h), (width, row * cell_h))

    def draw_player_selector():
        box_rect = draw_box(0, 0, 36, 3, "", COLOR_HEADER)
        box_y = box_rect.y
        padding = 10
        portrait_w = int(cell_w * 3)
        portrait_h = int(cell_h * 2)
        spacing = 16
        total_width = len(entities) * (portrait_w + spacing) - spacing
        start_x = (width - total_width) // 2

        for i, player in enumerate(entities):
            name_label = player.character_display_name
            portrait_path = player.get_portrait()
            x = start_x + i * (portrait_w + spacing)
            y = box_y + 10

            rect = pygame.Rect(x - 4, y - 4, portrait_w + 8, portrait_h + 36)
            outline_color = (255, 50, 50) if i == selected_index else (80, 80, 80)
            pygame.draw.rect(surface, outline_color, rect, 2)

            portrait = get_scaled_image(portrait_path, (portrait_w, portrait_h))
            surface.blit(portrait, (x, y))

            name_surf = font.render(name_label, True, COLOR_LABEL)
            name_rect = name_surf.get_rect(center=(x + portrait_w // 2, y + portrait_h + 20))
            surface.blit(name_surf, name_rect)

        arrow_size = 24
        arrow_color = (255, 60, 60)
        pygame.draw.polygon(surface, arrow_color, [
            (20, box_y + cell_h), (40, box_y + cell_h - 20), (40, box_y + cell_h + 20)
        ])
        pygame.draw.polygon(surface, arrow_color, [
            (width - 20, box_y + cell_h), (width - 40, box_y + cell_h - 20), (width - 40, box_y + cell_h + 20)
        ])

    def draw_selected_standee():
        player = entities[selected_index]
        name_label = player.character_display_name
        standee_path = player.get_standee()

        box_x, box_y, box_w, box_h = 0, 3, 9, 9
        rect = draw_box(box_x, box_y, box_w, box_h, "", COLOR_STANDEE)

        name_surf = G.title_font.render(name_label, True, COLOR_LABEL)
        name_rect = name_surf.get_rect(center=(rect.centerx, rect.y + 20))
        surface.blit(name_surf, name_rect)

        standee_h = int(rect.height * 0.85)
        # Load standee at full resolution
        from utils.image_cache import get_scaled_image
        standee = get_scaled_image(standee_path)
        if standee:
            # Scale to fixed height, preserve aspect ratio
            scale_factor = standee_h / standee.get_height()
            new_width = int(standee.get_width() * scale_factor)
            standee = pygame.transform.smoothscale(standee, (new_width, standee_h))

            standee_rect = standee.get_rect(midbottom=(rect.centerx, rect.bottom - 10))
            surface.blit(standee, standee_rect)

    def draw_stat_grid(surface, rect, entity):
        effects = entity.effects if hasattr(entity, "effects") else None
        icons = G.stat_icons

        label_font = G.hud_font
        value_font = G.inspect_font
        title_font = G.title_font

        tile_w = rect.width // 9
        tile_h = rect.height // 9
        STAT_BG_COLOR = getattr(G, "stat_bg_color", (24, 24, 24))

        def get_tile_rect(col, row):
            x = rect.x + (col - 9) * tile_w
            y = rect.y + (row - 3) * tile_h
            return pygame.Rect(x, y, tile_w, tile_h)

        def center_blit(surf, dest_rect):
            r = surf.get_rect(center=dest_rect.center)
            surface.blit(surf, r)

        def get_stat_value(stat):
            return entity.get_modified_stat(stat) if hasattr(entity, "get_modified_stat") else 0

        def get_base_stat(stat):
            if hasattr(entity, "template"):
                return entity.get_base_stat(stat)
            return 0

        def draw_stat(col, row, stat_key, mod, base):
            stat_bg = G.stat_bg_colors.get(stat_key, STAT_BG_COLOR)
            for offset in range(3):
                bg_rect = get_tile_rect(col + offset, row)
                pygame.draw.rect(surface, stat_bg, bg_rect)

            icon = icons.get(stat_key)
            if icon:
                icon_img = pygame.transform.smoothscale(icon, (tile_w, tile_h))
                icon_rect = get_tile_rect(col, row)
                center_blit(icon_img, icon_rect)

            color = effects.get_stat_color(stat_key, mod, base) if effects else (255, 255, 255)
            mod_surf = value_font.render(str(mod), True, color)
            mod_rect = get_tile_rect(col + 1, row)
            center_blit(mod_surf, mod_rect)

            base_surf = value_font.render(f"({base})", True, (160, 160, 160))
            base_rect = get_tile_rect(col + 2, row)
            center_blit(base_surf, base_rect)

        def draw_label(text, col_start, row, stat_key):
            bg_colors = getattr(G, "stat_bg_colors", {})
            bg_color = bg_colors.get(stat_key, STAT_BG_COLOR)
            for offset in range(3):
                rect = get_tile_rect(col_start + offset, row)
                pygame.draw.rect(surface, bg_color, rect)

            label_surf = label_font.render(text, True, (255, 255, 255))
            label_rect = get_tile_rect(col_start, row).union(get_tile_rect(col_start + 2, row))
            center_blit(label_surf, label_rect)

        def draw_bg_rows(start_row):
            for row in (start_row, start_row + 1):
                for col in range(9, 18):
                    r = get_tile_rect(col, row)
                    pygame.draw.rect(surface, STAT_BG_COLOR, r)

        # --- Title ---
        title_surf = title_font.render("Stats", True, (255, 255, 255))
        title_rect = pygame.Rect(rect.x, get_tile_rect(9, 3).y, rect.width, tile_h)
        center_blit(title_surf, title_rect)

        # --- Top stats ---
        draw_label("Health", 9, 5, "health")
        draw_stat(9, 6, "health",
                entity.get_current_stat("health"),
                entity.get_base_stat("health"))

        draw_label("Move", 12, 5, "move_points")
        draw_stat(12, 6, "move_points",
                entity.get_current_stat("move_points"),
                entity.get_base_stat("move_points"))

        draw_label("Attack", 15, 5, "attack")
        draw_stat(15, 6, "attack",
                entity.get_modified_stat("attack"),
                entity.get_base_stat("attack"))

        # --- Core stats ---
        draw_bg_rows(7)
        draw_label("Strength", 9, 7, "strength")
        draw_label("Intelligence", 12, 7, "intelligence")
        draw_label("Dexterity", 15, 7, "dexterity")

        draw_stat(9, 8, "strength",
                entity.get_modified_stat("strength"),
                entity.get_base_stat("strength"))
        draw_stat(12, 8, "intelligence",
                entity.get_modified_stat("intelligence"),
                entity.get_base_stat("intelligence"))
        draw_stat(15, 8, "dexterity",
                entity.get_modified_stat("dexterity"),
                entity.get_base_stat("dexterity"))

        draw_bg_rows(9)
        draw_label("Endurance", 9, 9, "endurance")
        draw_label("Nerve", 12, 9, "nerve")
        draw_label("Luck", 15, 9, "luck")

        draw_stat(9, 10, "endurance",
                entity.get_modified_stat("endurance"),
                entity.get_base_stat("endurance"))
        draw_stat(12, 10, "nerve",
                entity.get_modified_stat("nerve"),
                entity.get_base_stat("nerve"))
        draw_stat(15, 10, "luck",
                entity.get_modified_stat("luck"),
                entity.get_base_stat("luck"))

        # --- Legend ---
        legend_text = "Value in ( ) is unmodified base value"
        legend_surf = label_font.render(legend_text, True, (200, 200, 200))
        legend_rect = pygame.Rect(rect.x, get_tile_rect(9, 11).y, rect.width, tile_h)
        center_blit(legend_surf, legend_rect)

    # --- Draw All Sections ---
    entity = entities[selected_index]
    stats_rect = draw_box(9, 3, 9, 9, "Stats", COLOR_STATS)
    draw_stat_grid(surface, stats_rect, entity)
    effects_rect = draw_box(18, 3, 18, 9, "Effects", COLOR_EFFECTS)

    # --- Legend for icons ---
    draw_box(0, 12, 36, 6, "Legend", COLOR_LEGEND)
    legend_rect = draw_box(0, 12, 36, 6, "Legend", COLOR_LEGEND)

    legend_entries = [
    {"icon": "attack", "label": "Attack", "desc": "How much damage this unit deals on a successful hit."},
    {"icon": "health", "label": "Health", "desc": "The unit’s max HP before being knocked out."},
    {"icon": "move", "label": "Movement", "desc": "How many tiles the unit can move per turn."},
    {"icon": "intelligence", "label": "Intelligence", "desc": "Used for solving puzzles and certain effects."},
    {"icon": "dexterity", "label": "Dexterity", "desc": "Used for evasion and fast actions."},
    {"icon": "strength", "label": "Strength", "desc": "Determines physical power and lifting capacity."},
    {"icon": "endurance", "label": "Endurance", "desc": "Determines how much fatigue or damage a unit can take."},
    {"icon": "nerve", "label": "Nerve", "desc": "Influences bravery and resisting fear effects."},
    {"icon": "luck", "label": "Luck", "desc": "Affects dice rolls and chance-based events."},
    ]

    draw_icon_legend(
        surface,
        legend_rect.x + 10,
        legend_rect.y + 10,
        legend_rect.width - 20,
        legend_rect.height - 20,
        legend_entries
    )

    # --- Effects Detail Panel ---
    import ui.components.effect_icon_box as effect_box

    # Apply updated font sizes for clarity once
    effect_box.MOD_COLOR = (255, 255, 255)
    effect_box.DESC_COLOR = (220, 220, 220)
    effect_box.SRC_COLOR = (180, 180, 180)
    effect_box.MOD_FONT = G.stat_font
    effect_box.DESC_FONT = G.hud_font
    effect_box.TITLE_FONT = G.hud_font
    effect_x = effects_rect.x + 8
    effect_y = effects_rect.y + 8
    effect_list = entity.effects.get_all_effects()
    if G.debug_mode:
        log_debug("Inspector", f"Entity '{entity}' has {len(effect_list)} effects: {[e.name for e in effect_list]}", file=__file__)  # <-- Replaced print
        
    for effect in effect_list:
        panel_height = effect_box.draw_effect_icon_box(surface, effect, effect_x, effect_y, detailed=True, width=effects_rect.width - 32) or 0
        
        if panel_height:
            pygame.draw.line(surface, (80, 80, 80), (effect_x, effect_y + panel_height + 4), (effect_x + effects_rect.width - 32, effect_y + panel_height + 4), 1)
            effect_y += panel_height + 12

    draw_player_selector()
    draw_selected_standee()
    draw_full_grid()

def handle_input(action):
    inspector = G.inspector
    entities = get_visible_inspectables()
    if not entities:
        return
    if action == "move_left":
        inspector.selected_entity_index = (inspector.selected_entity_index - 1) % len(entities)
    elif action == "move_right":
        inspector.selected_entity_index = (inspector.selected_entity_index + 1) % len(entities)
