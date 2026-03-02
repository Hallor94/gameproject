# file: entities/enemy_character.py

import random
from utils import globals as G
from utils.logger import log_debug

class EnemyCharacter:
    def __init__(self, char_id, display_name, description, base_type, scale,
                strength, endurance, dexterity, intelligence, nerve, luck,
                health_base, move_points_base, attack_base,
                faction="ENEMY", behaviors=None,
                variant_suffix=None, standee_key=None, portrait_key=None):
        self.char_id = char_id
        self.display_name = display_name
        self.description = description
        self.base_type = base_type
        self.scale = scale

        # Core stats
        self.strength = strength
        self.endurance = endurance
        self.dexterity = dexterity
        self.intelligence = intelligence
        self.nerve = nerve
        self.luck = luck

        # Derived stats
        self.health_base = health_base
        self.move_points_base = move_points_base
        self.attack_base = attack_base

        # Metadata
        self.faction = faction
        self.behaviors = behaviors or []

        # Images
        self.variant_suffix = variant_suffix
        self.standee_key = standee_key
        self.portrait_key = portrait_key

    def __repr__(self):
        return f"<EnemyCharacter {self.char_id} ({self.base_type})>"

    # --- Loader Support ---
    @classmethod
    def from_json_entry(cls, entry, variant_suffix=None, standee_key=None, portrait_key=None):
        char_id = entry["char_id"]
        display_name = entry.get("display_name", char_id)
        description = entry.get("description", "")
        base_type = entry.get("base_type", char_id)
        scale = cls._generate_scale(entry.get("scale", 1.0))
        faction = entry.get("faction", "ENEMY")
        behaviors = entry.get("behaviors", [])
        stats_def = entry.get("stats", {})

        use_random = str(entry.get("random_stats")).lower() == "true"
        stats = cls._generate_stats(stats_def) if use_random else stats_def

        log_debug("EnemyCharacter", f"{'Randomized' if use_random else 'Static'} stats for {char_id}: {stats}", file=__file__)

        # ✅ Unpack stats before return
        strength = stats.get("strength", 0)
        endurance = stats.get("endurance", 0)
        dexterity = stats.get("dexterity", 0)
        intelligence = stats.get("intelligence", 0)
        nerve = stats.get("nerve", 0)
        luck = stats.get("luck", 0)

        health_base = strength + endurance
        move_points_base = int((endurance + dexterity) / 2)
        attack_base = int((strength + dexterity) / 2)

        return cls(
            char_id, display_name, description, base_type, scale,
            strength, endurance, dexterity, intelligence, nerve, luck,
            health_base, move_points_base, attack_base,
            faction, behaviors,
            variant_suffix=variant_suffix,
            standee_key=standee_key,
            portrait_key=portrait_key
        )

    @staticmethod
    def _generate_stats(stats_def):
        final = {}
        for k, v in stats_def.items():
            if isinstance(v, list) and len(v) == 2:
                final[k] = random.randint(v[0], v[1])
            else:
                final[k] = v
        return final

    @staticmethod
    def _generate_scale(scale_def):
        if isinstance(scale_def, list) and len(scale_def) == 2:
            return round(random.uniform(scale_def[0], scale_def[1]), 2)
        return float(scale_def)
