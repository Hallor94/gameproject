# file: entities/player.py

from entities.tile_occupant import TileOccupant
from entities.effects.effects_manager import EffectManager
from utils import globals as G
from utils.image_cache import has_image
from utils.logger import log_warn


class Player(TileOccupant):
    def __init__(self, player_name, player_character):
        super().__init__()
        self.player_name = player_name

        # Identity
        self.char_id = player_character.char_id
        self.character_display_name = player_character.display_name
        self.character_full_name = player_character.full_name
        self.character_description = player_character.description
        self.character_base_type = player_character.base_type
        self.character_scale = player_character.scale

        self._effects = EffectManager(self)
        self.states = set()

        # Flatten base stats
        for key in ["strength", "endurance", "dexterity", "intelligence", "nerve", "luck"]:
            value = getattr(player_character, key, 0)
            setattr(self, f"{key}_base", value)
            setattr(self, f"{key}_modified", value)

        # Derived stats
        self.health_base = player_character.health_base
        self.health_modified = self.health_base
        self.health_current = self.health_modified

        self.move_points_base = player_character.move_points_base
        self.move_points_modified = self.move_points_base
        self.move_points_current = self.move_points_modified

        self.attack_base = player_character.attack_base
        self.attack_modified = self.attack_base
        self.attack_current = self.attack_base

    @property
    def type(self):
        return "player"

    @property
    def is_alive(self):
        return self.health_current > 0

    @property
    def effects(self):
        return self._effects

    # --- State Helpers ---

    def is_state(self, key: str) -> bool:
        return key in self.states

    def add_state(self, key: str):
        self.states.add(key)

    def remove_state(self, key: str):
        self.states.discard(key)

    def get_visual_state(self) -> str:
        states = []
        if "combat" in self.states:
            states.append("combat")
        if self.health_current < (self.health_modified * 0.5):
            states.append("injured")
        return "_".join(states) if states else "default"

    # --- Portrait & Standee Access (returns cache keys only) ---

    def get_portrait(self):
        key = f"{self.char_id}_portrait_{self.get_visual_state()}"
        return key if has_image(key) else "nemo"

    def get_standee(self):
        key = f"{self.char_id}_standee_{self.get_visual_state()}"
        return key if has_image(key) else "nemo"

    def __setattr__(self, name, value):
        if getattr(G, "DEBUG_ATTR_WARNINGS", False) and not hasattr(self, name):
            log_warn("Player", f"{self.__class__.__name__} has no attribute '{name}'", file=__file__)
        super().__setattr__(name, value)

    def __repr__(self):
        return f"<Player {self.player_name} with {self.character_display_name}>"
