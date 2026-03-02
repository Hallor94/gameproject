# file: ui/setup_menu.py

import random

from entities.effects.effects_manager import EffectManager
from entities.player_character import PlayerCharacter
from entities.player_character_loader import load_player_characters
from entities.tile_occupant import TileOccupant
from ui.common import render_text_centered
from ui.components.portrait_box import PortraitBox
from utils import globals as G
from utils.logger import log_info, log_debug

DEFAULT_NAMES = ["Alexander", "Viktor", "Tim", "Karin"]

class SetupMenu:
    """
    Handles player setup flow including:
    - player count
    - name entry
    - character selection
    - confirming game start
    """

    def __init__(self, test_mode=True):
        self.skip_setup = getattr(G, "skip_setup", False) or test_mode
        self.phase = "confirm" if self.skip_setup else "player_count"

        self.players = []
        self.temp_name_buffer = ""
        self.player_count = 3
        self.selected_index = 0
        self.awaiting_final_confirm = False

        # Character list: placeholder first, then real characters
        self.available_characters = [PlayerCharacter.create_random_placeholder()] + load_player_characters()
        self.selected_character_index = []
        self.character_locked = []

        if self.skip_setup:
            self.players = [{"name": DEFAULT_NAMES[i], "character": None} for i in range(3)]
            self.selected_character_index = [0] * 3
            self.character_locked = [True] * 3
            self._assign_random_characters()
            self.phase = "confirm"
            log_info("SetupMenu", "Test mode enabled. Auto-selected characters for default players.", file=__file__)

    def _assign_random_characters(self):
        available = self.available_characters[1:]  # Skip placeholder
        random.shuffle(available)
        used = set()

        for i, player in enumerate(self.players):
            idx = self.selected_character_index[i]
            if idx == 0:
                for char in available:
                    if char not in used:
                        self.players[i]["character"] = char
                        used.add(char)
                        log_debug("SetupMenu", f"Assigned random character '{char.display_name}' to {player['name']}", file=__file__)
                        break
            else:
                self.players[i]["character"] = self.available_characters[idx]
                log_debug("SetupMenu", f"Manually selected character '{self.available_characters[idx].display_name}' for {player['name']}", file=__file__)

    def _draw_character_selection(self, surface):
        render_text_centered(surface, "Character Selection", (255, 255, 255), 100)

        num_players = len(self.players)
        box_width = 360
        box_height = 520
        padding = 40
        total_width = num_players * box_width + (num_players - 1) * padding
        start_x = (surface.get_width() - total_width) // 2
        y = (surface.get_height() - box_height) // 2 - 40

        for i, player in enumerate(self.players):
            x = start_x + i * (box_width + padding)
            selected = i == self.selected_index
            locked = self.character_locked[i]

            if locked and self.selected_character_index[i] == 0:
                char = self.players[i].get("character") or PlayerCharacter.create_random_placeholder()
            else:
                char = self.available_characters[self.selected_character_index[i]]

            name = player["name"]
            stub = EntityStub(char, name)
            box = PortraitBox(stub, G.stat_icons, scale=1.0)
            box.draw_wide(surface, x, y)

        if self.phase == "confirm":
            render_text_centered(surface, "PRESS ENTER TO START", (255, 255, 255), surface.get_height() - 60)

    def get_player_data(self):
        return self.players

    def handle_action(self, action: str) -> bool:
        if self.phase != "confirm":
            return False

        if action == "left":
            self._cycle_character(-1)
            return True
        elif action == "right":
            self._cycle_character(1)
            return True
        elif action == "confirm":
            self.character_locked[self.selected_index] = True
            log_debug("SetupMenu", f"Locked character for player {self.players[self.selected_index]['name']}", file=__file__)
            if self.selected_index < len(self.players) - 1:
                self.selected_index += 1
            else:
                self.phase = "confirm"
                log_info("SetupMenu", "All players confirmed. Moving to final confirm screen.", file=__file__)
            return True
        elif action == "back":
            if self.character_locked[self.selected_index]:
                self.character_locked[self.selected_index] = False
                log_debug("SetupMenu", f"Unlocked character for player {self.players[self.selected_index]['name']}", file=__file__)
            elif self.selected_index > 0:
                self.selected_index -= 1
            else:
                self.phase = "player_count"
                log_info("SetupMenu", "Backed out to player count selection.", file=__file__)
            return True

        return False

    def _cycle_character(self, direction: int):
        if not self.character_locked[self.selected_index]:
            current = self.selected_character_index[self.selected_index]
            next_idx = (current + direction) % len(self.available_characters)
            self.selected_character_index[self.selected_index] = next_idx
            log_debug("SetupMenu", f"Player {self.players[self.selected_index]['name']} cycled to character index {next_idx}", file=__file__)

    def draw(self, surface):
        surface.fill((0, 0, 0))
        self._draw_character_selection(surface)

    def is_done(self):
        return self.phase == "complete" or (
            self.phase == "confirm" and all(self.character_locked)
        )
    
    def force_exit(self):
        self.phase = "complete"


class EntityStub(TileOccupant):
    """
    Temporary stand-in for Player or Enemy during setup,
    designed to work with PortraitBox and effect systems.
    """
    def __init__(self, character_template, name="Player"):
        super().__init__()
        self.player_name = name

        # Character info (flattened)
        self.char_id = character_template.char_id
        self.character_display_name = character_template.display_name
        self.character_description = character_template.description
        self.character_base_type = character_template.base_type
        self.character_scale = character_template.scale

        # Core stats
        for key in ["strength", "endurance", "dexterity", "intelligence", "nerve", "luck"]:
            value = getattr(character_template, key, 0)
            setattr(self, f"{key}_base", value)
            setattr(self, f"{key}_modified", value)

        # Derived stats
        self.attack_base = character_template.attack_base
        self.attack_modified = self.attack_base
        self.health_base = character_template.health_base
        self.health_current = self.health_base
        self.move_points_base = character_template.move_points_base
        self.move_points_current = self.move_points_base

        self._effects = EffectManager(self)

    @property
    def effects(self):
        return self._effects

    def get_base_stat(self, key):
        return getattr(self, f"{key}_base", 0)

    def get_modified_stat(self, key):
        base = self.get_base_stat(key)
        return self.effects.get_modified_value(key, base)

    def get_current_stat(self, key):
        if key == "health":
            return self.health_current
        if key == "move_points":
            return self.move_points_current
        return self.get_base_stat(key)

    def is_state(self, label):
        return False

    @property
    def display_name(self):
        return self.character_display_name

    @property
    def name(self):
        return self.player_name

    def get_portrait(self):
        return f"{self.char_id}_portrait_default"

    def get_standee(self):
        return f"{self.char_id}_standee_default"
