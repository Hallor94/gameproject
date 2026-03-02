# file: ui/components/portrait_box.py

import pygame
from utils.image_cache import get_scaled_image, get_icon, preload_all_ui_icons
from utils import globals as G
from ui.components.bar import draw_bar
from ui.components.effect_icon_box import draw_effect_icon_box
from entities.enemy_marker import get_entity_mark_icon

# Mapping for stat labels to short forms used in UI
STAT_LABELS = {
    "strength": "STR", "intelligence": "INT", "dexterity": "DEX",
    "endurance": "END", "nerve": "NRV", "luck": "LCK",
    "health": "HP", "move_points": "MOV", "attack": "ATK"
}

# Buff icon rendering settings
BUFF_ICON_SIZE = 52  # px, fixed for consistency across compact and wide views
BUFF_ICON_GAP = 6

class PortraitBox:
    def __init__(self, entity, stat_icons, scale=1.0):
        """
        Render a visual summary of a game entity's portrait, stats, and effects.
        """
        self.entity = entity
        self.icons = stat_icons
        self.scale = scale
        self.font = pygame.font.SysFont(None, int(G.stat_font.get_height() * scale))
        self.WIDTH = int(400 * scale)
        self.HEIGHT = int(self.WIDTH * 4 / 9)
        preload_all_ui_icons()

        self.cols = 14
        self.col_w = self.WIDTH // self.cols
        wide_row_h = self.HEIGHT // 4
        self.row_h = wide_row_h // 2
        self.top_bar_h = self.row_h
        self.compact_height = self.top_bar_h + self.row_h * 4

    def draw_stat_cell(self, surface, icon, label, value, col, row, col_w, row_h, x, y, color, bg_color=None):
        """
        Draw a single stat cell with icon and value.
        """
        left_x = x + col * col_w
        top_y = y + row * row_h
        icon_rect = pygame.Rect(left_x, top_y, col_w, row_h)
        val_rect = pygame.Rect(left_x + col_w, top_y, col_w, row_h)

        if bg_color:
            pygame.draw.rect(surface, bg_color, icon_rect)
            pygame.draw.rect(surface, bg_color, val_rect)

        if icon:
            icon_surf = pygame.transform.smoothscale(icon, (min(col_w, row_h), min(col_w, row_h)))
            icon_pos = icon_surf.get_rect(center=icon_rect.center)
            surface.blit(icon_surf, icon_pos)
        else:
            small_font = pygame.font.SysFont(None, int(G.stat_font.get_height() * self.scale * 0.7))
            fallback_text = STAT_LABELS.get(label, label[:3].upper())
            fallback_label = small_font.render(fallback_text, True, (200, 200, 200))
            fallback_rect = fallback_label.get_rect(center=icon_rect.center)
            surface.blit(fallback_label, fallback_rect)

        value_surf = self.font.render(str(value), True, color)
        outline = self.font.render(str(value), True, (0, 0, 0))
        tx, ty = value_surf.get_size()
        label_x = val_rect.centerx - tx // 2
        label_y = val_rect.centery - ty // 2
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            surface.blit(outline, (label_x + dx, label_y + dy))
        surface.blit(value_surf, (label_x, label_y))

    def get_height(self, compact=False):
        """
        Get base height of this box depending on compact mode.
        """
        return self.compact_height if compact else self.HEIGHT

    def get_total_height(self, compact=False):
        """
        Get total height of this box including space for buffs if present.
        """
        base_height = self.get_height(compact)
        if self.entity:
            buff_count = len(self.entity.effects.get_all_effects())
            if buff_count > 0:
                return base_height + BUFF_ICON_SIZE + 4
        return base_height

    def draw_wide(self, surface, x, y):
        """
        Draw the detailed wide portrait box including:
        - Character name
        - Portrait and attack overlay
        - Stat grid (STR, INT, etc)
        - Health and Move bars
        - Buff overlays
        """
        col_w = self.WIDTH // 9
        row_h = self.HEIGHT // 4
        box_rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)

        # Background
        pygame.draw.rect(surface, (25, 25, 25), box_rect)

        # Character name
        name_surf = self.font.render(self.entity.character_display_name, True, (255, 255, 255))
        name_rect = name_surf.get_rect(center=(x + col_w * 1.5, y + row_h // 2))
        surface.blit(name_surf, name_rect)

        # Portrait
        portrait_rect = pygame.Rect(x, y + row_h, col_w * 3, row_h * 3)
        portrait = get_scaled_image(self.entity.get_portrait(), (portrait_rect.width, portrait_rect.height))
        if portrait:
            surface.blit(portrait, portrait_rect)

        # Enemy visual mark (centered at bottom of portrait)
        if getattr(self.entity, "type", None) == "enemy":
            mark_icon = get_entity_mark_icon(self.entity)
            if mark_icon:
                mark_size = int(row_h * 1.2)
                icon_surf = pygame.transform.smoothscale(mark_icon, (mark_size, mark_size))
                icon_rect = icon_surf.get_rect(center=(portrait_rect.centerx, portrait_rect.bottom + mark_size // 2 - 4))
                surface.blit(icon_surf, icon_rect)

        # Attack overlay icon
        atk_icon = self.icons.get("attack")
        atk_val = self.entity.attack_modified
        atk_base = self.entity.attack_base
        atk_color = self.entity.effects.get_stat_color("base_attack", atk_val, atk_base)
        atk_size = int(min(col_w, row_h) * 0.9)
        atk_x = portrait_rect.x + int(col_w * 0.15)
        atk_y = portrait_rect.y + portrait_rect.height - atk_size - int(row_h * 0.2)
        if atk_icon:
            atk_img = pygame.transform.smoothscale(atk_icon, (atk_size, atk_size))
            surface.blit(atk_img, (atk_x, atk_y))
        atk_surf = self.font.render(str(atk_val), True, atk_color)
        outline = self.font.render(str(atk_val), True, (0, 0, 0))
        tx, ty = atk_surf.get_size()
        surface.blit(outline, (atk_x + atk_size // 2 - tx // 2 - 1, atk_y + atk_size // 2 - ty // 2))
        surface.blit(atk_surf, (atk_x + atk_size // 2 - tx // 2, atk_y + atk_size // 2 - ty // 2))

        # Stat grid backgrounds
        stat_keys = ["strength", "intelligence", "dexterity", "endurance", "nerve", "luck"]
        strip_colors = [(85, 30, 30), (25, 45, 80), (180, 160, 90)]
        for col_index, color in enumerate(strip_colors):
            col = 3 + col_index * 2
            for row in [0, 1]:
                bg_rect = pygame.Rect(x + col * col_w, y + row * row_h, col_w * 2, row_h)
                pygame.draw.rect(surface, color, bg_rect)

        # Stat grid
        for i, key in enumerate(stat_keys):
            col = 3 + (i % 3) * 2
            row = 0 if i < 3 else 1
            base = self.entity.get_base_stat(key)
            mod = self.entity.get_modified_stat(key)
            color = self.entity.effects.get_stat_color(key, mod, base)
            self.draw_stat_cell(surface, self.icons.get(key), key, mod, col, row, col_w, row_h, x, y, color)

        # Health and Move bars
        for row_offset, key, bar_color in [(2, "health", (180, 40, 40)), (3, "move_points", (80, 130, 80))]:
            icon = self.icons.get(key)
            if icon:
                surface.blit(pygame.transform.smoothscale(icon, (col_w, row_h)), (x + col_w * 3, y + row_h * row_offset))
            cur = self.entity.get_current_stat(key)
            mod = self.entity.get_modified_stat(key)
            base = self.entity.get_base_stat(key)
            color = self.entity.effects.get_stat_color(f"max_{key}", mod, base)
            rect = pygame.Rect(x + col_w * 4, y + row_h * row_offset + 2, col_w * 5, row_h - 4)
            draw_bar(surface, rect, cur, mod, color=bar_color, font=G.label_font, label_color=color)

        # Turn/combat icons
        icon_size = int(col_w * 1.2)
        if G.gamestate and G.gamestate.turn_order and G.gamestate.turn_order[0] == self.entity:
            icon = get_icon("firstplayer")
            if icon:
                surface.blit(pygame.transform.smoothscale(icon, (icon_size, icon_size)), (x - icon_size // 2, y - icon_size // 2))
        if self.entity.is_state("combat"):
            icon = get_icon("combat")
            if icon:
                surface.blit(pygame.transform.smoothscale(icon, (icon_size, icon_size)), (x + self.WIDTH - icon_size // 2, y + self.HEIGHT - icon_size // 2))

        # Buff icons
        buffs = self.entity.effects.get_all_effects()
        if buffs:
            bx, by = x, y + self.HEIGHT + 8
            for effect in buffs:
                draw_effect_icon_box(surface, effect, bx, by, size=BUFF_ICON_SIZE)
                bx += BUFF_ICON_SIZE + BUFF_ICON_GAP

    def draw_compact(self, surface, x, y):
        """
        Draw a compact version of the portrait box: name, portrait, HP/MOV bars, combat markers and buffs.
        """
        col_w = self.col_w
        row_h = self.row_h
        self.font = pygame.font.SysFont(None, int(G.stat_font.get_height() * 0.7))

        pygame.draw.rect(surface, (25, 25, 25), pygame.Rect(x, y, self.WIDTH, self.compact_height))

        # Name
        name_surf = self.font.render(self.entity.character_display_name, True, (255, 255, 255))
        surface.blit(name_surf, name_surf.get_rect(center=(x + col_w * 7, y + row_h // 2)))

        # Portrait
        portrait_rect = pygame.Rect(x, y + row_h, col_w * 4, row_h * 4)
        portrait = get_scaled_image(self.entity.get_portrait(), (portrait_rect.width, portrait_rect.height))
        surface.blit(portrait, portrait_rect)

        # Enemy visual mark (centered at bottom of portrait)
        if getattr(self.entity, "type", None) == "enemy":
            mark_icon = get_entity_mark_icon(self.entity)
            if mark_icon:
                mark_size = int(row_h * 1.2)
                icon_surf = pygame.transform.smoothscale(mark_icon, (mark_size, mark_size))
                icon_rect = icon_surf.get_rect(center=(portrait_rect.centerx, portrait_rect.bottom + mark_size // 2 - 4))
                surface.blit(icon_surf, icon_rect)

        # Health/Move bars with icons
        for row_index, stat, icon_key, color in [(1, "health", "health", (180, 40, 40)), (3, "move_points", "move", (80, 130, 80))]:
            icon = self.icons.get(icon_key)
            if icon:
                surface.blit(pygame.transform.smoothscale(icon, (col_w * 2, row_h * 2)), (x + col_w * 4, y + row_h * row_index))
            cur = self.entity.get_current_stat(stat)
            mod = self.entity.get_modified_stat(stat)
            base = self.entity.get_base_stat(stat)
            label_color = self.entity.effects.get_stat_color(f"max_{stat}", mod, base)
            bar_rect = pygame.Rect(x + col_w * 6, y + row_h * row_index, col_w * 8 - 4, row_h * 2 - 4)
            draw_bar(surface, bar_rect, cur, mod, color=color, font=G.label_font, label_color=label_color)

        # Turn/combat overlays
        icon_size = int(col_w * 1.2)
        if G.gamestate and G.gamestate.turn_order and G.gamestate.turn_order[0] == self.entity:
            icon = get_icon("firstplayer")
            if icon:
                surface.blit(pygame.transform.smoothscale(icon, (icon_size, icon_size)), (x + self.WIDTH - icon_size // 2, y - icon_size // 2))
        if self.entity.is_state("combat"):
            icon = get_icon("combat")
            if icon:
                surface.blit(pygame.transform.smoothscale(icon, (icon_size, icon_size)), (x + self.WIDTH - icon_size // 2, y + self.compact_height - icon_size // 2))

        # Buffs
        buffs = self.entity.effects.get_all_effects()
        if buffs:
            bx, by = x, y + self.compact_height + 8
            for effect in buffs:
                draw_effect_icon_box(surface, effect, bx, by, size=BUFF_ICON_SIZE)
                bx += BUFF_ICON_SIZE + BUFF_ICON_GAP


