# file: entities/player_character_loader.py

import os
from entities.player_character import PlayerCharacter
from utils.json_loader import load_all_json_entries
from utils.logger import log_info, log_error

PLAYER_CHARACTER_JSON_DIR = "data/characters"

def load_player_characters():
    """
    Loads all player character templates from JSON and returns a list of Character objects.
    """
    characters = []
    entries = load_all_json_entries(PLAYER_CHARACTER_JSON_DIR)

    for entry in entries:
        try:
            char_id = entry["char_id"]  # Required
            stats = entry["stats"]

            # Required base stats
            strength = stats["strength"]
            endurance = stats["endurance"]
            dexterity = stats["dexterity"]
            intelligence = stats["intelligence"]
            nerve = stats["nerve"]
            luck = stats["luck"]

            # Auto-calculate derived stats
            health_base = strength + endurance
            move_points_base = int((endurance + dexterity) / 2)
            attack_base = int((strength + dexterity) / 2)

            character = PlayerCharacter(
                char_id=char_id,
                display_name=entry.get("display_name", char_id),
                full_name=entry.get("full_name", char_id),
                description=entry.get("description", ""),
                base_type=entry.get("base_type", char_id),
                scale=entry.get("scale", 1.0),
                strength=strength,
                endurance=endurance,
                dexterity=dexterity,
                intelligence=intelligence,
                nerve=nerve,
                luck=luck,
                health_base=health_base,
                move_points_base=move_points_base,
                attack_base=attack_base
            )

            characters.append(character)

        except Exception as e:
            log_error("CharacterLoader", f"Failed to load character: {entry.get('char_id', '?')} → {e}", file=__file__)

    log_info("CharacterLoader", f"Loaded {len(characters)} player characters.", file=__file__)
    return characters
