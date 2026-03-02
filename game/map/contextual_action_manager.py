# file: map/contextual_action_manager.py

from actions.contextual_action import ContextualAction
from actions.vent import enter_vent_mode
from collections import defaultdict
from utils import globals as G
from utils.logger import log_info


class ContextualActionManager:
    def __init__(self):
        self._tile_actions = defaultdict(list)

    def add_action(self, tile_pos, action):
        self._tile_actions[tile_pos].append(action)

    def remove_action(self, tile_pos, action_id):
        actions = self._tile_actions[tile_pos]
        self._tile_actions[tile_pos] = [a for a in actions if a.id != action_id]
        if not self._tile_actions[tile_pos]:
            del self._tile_actions[tile_pos]

    def get_actions(self, tile_pos, context=None):
        actions = self._tile_actions.get(tile_pos, [])
        return [a for a in actions if a.is_visible(context)]

    def clear_actions(self, tile_pos):
        if tile_pos in self._tile_actions:
            del self._tile_actions[tile_pos]

    def all_positions(self):
        return list(self._tile_actions.keys())

    def populate_tile_actions(self, tile):
        self.clear_actions(tile.grid_pos)

        def placeholder(label):
            return lambda: log_info("ContextAction", f"{label} started", file=__file__)

        if tile.has_loot and tile.loot_count > 0:
            self.add_action(tile.grid_pos, ContextualAction(
                "loot",
                "Loot",
                callback=lambda tile=tile: G.loot_manager.start_looting(tile),
                icon="resolve"
            ))
        if tile.has_vent:
            self.add_action(tile.grid_pos, ContextualAction(
                "vent",
                "Enter Vent",
                callback=enter_vent_mode,
                icon="resolve"
            ))
        if tile.has_main_quest:
            self.add_action(tile.grid_pos, ContextualAction("main_quest", "Main Objective", placeholder("Main Quest")))
        if tile.has_side_quest:
            self.add_action(tile.grid_pos, ContextualAction("side_quest", "Side Objective", placeholder("Side Quest")))
