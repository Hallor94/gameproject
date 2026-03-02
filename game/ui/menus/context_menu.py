# file: ui/menus/context_menu.py

from ui.menus.base_menu import BaseMenu
from utils.enums import UIMode
from utils.ui_mode_manager import set_ui_mode
from ui.inspector.tile_inspector import draw_tile_panel
from utils import globals as G

class ContextMenu(BaseMenu):
    def __init__(self):
        super().__init__()
        self.visible = True
        self.tile_pos = None
        self.last_tile_pos = None
        self.inspection_tile_pos = None
        self.font = G.context_font
        self.button_height = 42
        self.button_spacing = 8
        self.button_width = 280
        self.border_radius = 6
        self.selected_index = None

    def enter_inspect_mode(self, tile_pos):
        self.inspection_tile_pos = tile_pos
        G.gamestate.ui_mode = UIMode.INSPECTION
        self._update_for_tile(tile_pos, disable_interaction=True)

    def _update_for_tile(self, tile_pos, disable_interaction=False):
        self.tile_pos = tile_pos
        self.last_tile_pos = tile_pos
        ref_tile = self.inspection_tile_pos if G.gamestate.ui_mode == UIMode.INSPECTION else self.tile_pos
        tile = G.gamemap.tiles[ref_tile[1]][ref_tile[0]]

        G.contextual_action_manager.populate_tile_actions(tile)
        self.actions = G.contextual_action_manager.get_actions(ref_tile)
        self.actions.sort(key=lambda a: 0 if a.id == "inspect" else 1)
        self.options = [{"label": a.label, "callback": a.callback, "id": a.id, "icon": a.icon} for a in self.actions]

        if disable_interaction:
            for o in self.options:
                o["callback"] = lambda: None

        self.selected_index = None if disable_interaction else 0

    def update_for_player_tile(self, tile_pos):
        if tile_pos != self.last_tile_pos:
            self._update_for_tile(tile_pos, disable_interaction=False)

    def update_inspection_tile(self, tile_pos):
        self.tile_pos = tile_pos
        self.inspection_tile_pos = tile_pos
        self.last_tile_pos = tile_pos

        tile = G.gamemap.tiles[tile_pos[1]][tile_pos[0]]
        G.contextual_action_manager.populate_tile_actions(tile)
        self.actions = G.contextual_action_manager.get_actions(tile_pos)
        self.actions.sort(key=lambda a: 0 if a.id == "inspect" else 1)

        self.options = [{"label": a.label, "callback": lambda: None, "id": a.id, "icon": a.icon} for a in self.actions]
        self.selected_index = next((i for i, o in enumerate(self.options) if o["id"] == "inspect"), None)

    def handle_action(self, action: str) -> bool:
        if not self.visible or not self.options:
            return False

        if G.gamestate.ui_mode == UIMode.INSPECTION:
            return False  # let inspect input handle itself

        if G.gamestate.ui_mode != UIMode.CONTEXT:
            return False

        if action == "back":
            return self.handle_back()
        return super().handle_action(action)

    def handle_back(self) -> bool:
        player = G.gamestate.get_active_player()
        self.update_for_player_tile(player.tile.grid_pos)
        set_ui_mode(UIMode.MAIN)
        return True

    def draw(self, surface, tile):
        if not self.visible or not self.tile_pos:
            return
        
        draw_tile_panel(surface, tile, interactive=True, selected_index=self.selected_index)
