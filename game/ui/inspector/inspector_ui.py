# file: ui/inspector/inspector_ui.py

import pygame
from utils.enums import Enum, UIMode
from utils import globals as G
from ui.inspector.entity_inspector import draw_entity_inspector, handle_input as entity_handle_input
from ui.inspector.tile_inspector import draw_tile_panel
from utils.ui_mode_manager import set_ui_mode


class InspectionTab(Enum):
    ENTITIES = 0
    OBJECTIVES = 1
    MAP = 2


class InspectorUI:
    def __init__(self):
        self.visible = False
        self.active_tab = InspectionTab.ENTITIES
        self.selected_entity_index = 0
        self.map_inspection_tile = None

    def open(self):
        self.visible = True
        self.active_tab = InspectionTab.ENTITIES
        set_ui_mode(UIMode.INSPECTION)

    def close(self):
        self.visible = False
        set_ui_mode(UIMode.MAIN)

    def cycle_tab(self):
        tab_values = list(InspectionTab)
        current_index = tab_values.index(self.active_tab)
        self.active_tab = tab_values[(current_index + 1) % len(tab_values)]

    def handle_input(self, action):
        if action == "back":
            self.close()
            return True
        if action == "cycle_tab":
            self.cycle_tab()
            return True
        if self.active_tab == InspectionTab.MAP and action in ("move_left", "move_right", "move_up", "move_down"):
            self._cycle_map_tile(action)
            return True
        if self.active_tab == InspectionTab.ENTITIES:
            entity_handle_input(action)
            return True
        return False

    def update(self, dt):
        pass

    def draw(self, surface):
        if not self.visible:
            return

        if self.active_tab == InspectionTab.MAP:
            self._draw_map_overlay(surface)
            return

        width = int(surface.get_width() * 0.8)
        height = int(surface.get_height() * 0.8)
        x = (surface.get_width() - width) // 2
        y = (surface.get_height() - height) // 2

        panel = pygame.Surface((width, height))
        panel.fill((10, 10, 10))

        self._draw_tabs(panel)

        if self.active_tab == InspectionTab.ENTITIES:
            self._draw_entities_tab(panel)
        elif self.active_tab == InspectionTab.OBJECTIVES:
            self._draw_objectives_tab(panel)

        surface.blit(panel, (x, y))

    def _draw_tabs(self, surface):
        font = G.font
        tab_titles = ["Entities", "Objectives", "Map"]
        tab_width = 140
        for i, title in enumerate(tab_titles):
            x = 10 + i * (tab_width + 20)
            color = (255, 255, 255) if self.active_tab.value == i else (100, 100, 100)
            pygame.draw.rect(surface, color, (x, 10, tab_width, 40), border_radius=6)
            label = font.render(title, True, (0, 0, 0))
            surface.blit(label, (x + 10, 20))

    def _draw_entities_tab(self, surface):
        draw_entity_inspector(surface)

    def _draw_objectives_tab(self, surface):
        pygame.draw.rect(surface, (60, 40, 40), (40, 70, surface.get_width() - 80, surface.get_height() - 110))

    def _draw_map_overlay(self, surface):
        # Default inspection target if none yet
        if self.map_inspection_tile is None:
            for row in G.gamemap.tiles:
                for tile in row:
                    if tile.visibility_state.name != "HIDDEN":
                        self.map_inspection_tile = tile
                        break
                if self.map_inspection_tile:
                    break

        # Draw tile inspection popup
        if self.map_inspection_tile:
            draw_tile_panel(surface, self.map_inspection_tile, interactive=False)

            # Draw pulsing tile highlight
            rect = G.gamemap.camera.get_scaled_rect(self.map_inspection_tile.world_rect)
            border_color = (255, 255, 0)
            thickness = 3
            pygame.draw.rect(surface, border_color, rect, thickness)

        # Overlay instructions
        text = "Tile Inspection Mode - Use arrows to browse, Tab or Escape to exit"
        font = G.font
        text_surf = font.render(text, True, (255, 255, 255))
        rect = text_surf.get_rect(center=(surface.get_width() // 2, 80))

        bg = pygame.Surface((rect.width + 40, rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(bg, (20, 20, 20, 220), bg.get_rect(), border_radius=8)
        surface.blit(bg, (rect.x - 20, rect.y - 10))
        surface.blit(text_surf, rect)

    def _cycle_map_tile(self, direction):
        if not self.map_inspection_tile:
            return

        x, y = self.map_inspection_tile.grid_pos
        dx, dy = {
            "move_left": (-1, 0),
            "move_right": (1, 0),
            "move_up": (0, -1),
            "move_down": (0, 1),
        }.get(direction, (0, 0))

        cols = len(G.gamemap.tiles[0])
        rows = len(G.gamemap.tiles)

        while True:
            x += dx
            y += dy
            if not (0 <= y < rows and 0 <= x < cols):
                break
            new_tile = G.gamemap.tiles[y][x]
            if new_tile.visibility_state.name != "HIDDEN":
                self.map_inspection_tile = new_tile
                break
