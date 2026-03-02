# file: entities/effects/effect_loader.py

from utils.json_loader import load_all_json_entries
from .effect import Effect
from utils.logger import log_warn

EFFECT_DIRS = [
    "data/effects/base",
    "data/effects/items",
    "data/effects/enemies"
]

def load_effects():
    effects = {}

    for folder in EFFECT_DIRS:
        entries = load_all_json_entries(folder)

        for data in entries:
            if "id" not in data:
                log_warn("EffectLoader", f"Skipping effect without ID in {folder}", file=__file__)
                continue

            # Normalize modifiers: accept both flat and nested
            raw_mods = data.get("modifiers", {})
            modifiers = {}
            for stat, val in raw_mods.items():
                if isinstance(val, dict):
                    modifiers[stat] = val
                else:
                    modifiers[stat] = {"add": val}

            try:
                effects[data["id"]] = Effect(
                    id=data["id"],
                    name=data["name"],
                    description=data.get("description", ""),
                    icon=data.get("icon"),
                    duration=data.get("duration", None),
                    modifiers=modifiers,
                    per_turn=data.get("per_turn", False),
                    tags=data.get("tags", []),
                    source=data.get("source"),
                    stackable=data.get("stackable", False),
                    conditions=data.get("conditions", {}),
                    allow_enemy=data.get("allow_enemy", True)
                )
            except TypeError as e:
                log_warn("EffectLoader", f"Failed to load effect '{data.get('id', '?')}' in {folder}: {e}", file=__file__)

    return effects
