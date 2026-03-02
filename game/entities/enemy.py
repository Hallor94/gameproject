# file: entities/enemy.py

from entities.tile_occupant import TileOccupant
from entities.effects.effects_manager import EffectManager
from utils import globals as G
from utils.image_cache import has_image
from utils.logger import log_warn


class Enemy(TileOccupant):
    def __init__(self, char_id, character, respawn_allowed=False):
        super().__init__()
        self.char_id = char_id
        self._effects = EffectManager(self)
        self.respawn_allowed = respawn_allowed
        self.states = set()

        # Identity and display info
        self.character_display_name = character.display_name
        self.character_description = character.description
        self.character_base_type = character.base_type
        self.character_scale = character.scale
        self.character_faction = character.faction
        self.behaviors = character.behaviors or []
        self.visual_mark = None

        # Image keys
        self.variant_suffix = character.variant_suffix
        self.standee_key = character.standee_key
        self.portrait_key = character.portrait_key

        # Core stats flattened from character
        for key in ["strength", "endurance", "dexterity", "intelligence", "nerve", "luck"]:
            value = getattr(character, key)
            setattr(self, f"{key}_base", value)
            setattr(self, f"{key}_modified", value)

        # Derived stats
        self.health_base = character.health_base
        self.health_modified = self.health_base
        self.health_current = self.health_modified

        self.move_points_base = character.move_points_base
        self.move_points_modified = self.move_points_base
        self.move_points_current = self.move_points_modified

        self.attack_base = character.attack_base
        self.attack_modified = self.attack_base
        self.attack_current = self.attack_base

    @property
    def type(self):
        return "enemy"

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

    def get_portrait(self):
        key = self.portrait_key or self.standee_key
        return key if has_image(key) else "nemoEvil"

    def get_standee(self):
        key = self.standee_key
        return key if has_image(key) else "nemoEvil"

    def __setattr__(self, name, value):
        if getattr(G, "DEBUG_ATTR_WARNINGS", False) and not hasattr(self, name):
            log_warn("Enemy", f"{self.__class__.__name__} has no attribute '{name}'", file=__file__)
        super().__setattr__(name, value)

    def __repr__(self):
        return f"<Enemy {getattr(self, 'char_id', '?')} ({getattr(self, 'character_display_name', '?')})>"

