# file: actions/cards/card_loader.py

import os
from utils.logger import log_info, log_warn
from utils.json_loader import load_all_json_entries

CARD_DATA_ROOT = "data/cards"

_card_lookup = {}

def _initialize_card_cache():
    total = 0
    cards = load_all_json_entries(CARD_DATA_ROOT)
    for card in cards:
        card_id = card.get("id")
        if not card_id:
            log_warn("CardLoader", f"Missing 'id'")
            continue
        if card_id in _card_lookup:
            log_warn("CardLoader", f"Duplicate card ID '{card_id}'")

        # Inherit base fields into each option
        for i, option in enumerate(card.get("options", [])):
            for key in ("base_stat", "icon", "required_stats", "threshold", "comparison_type"):
                if key not in option and key in card:
                    option[key] = card[key]

            if "effect" not in option:
                log_warn("CardLoader", f"Option {i} in '{card_id}' is missing 'effect'")
            if "usage" not in option:
                log_warn("CardLoader", f"Option {i} in '{card_id}' missing 'usage'")

        _card_lookup[card_id] = card
        total += 1

    log_info("CardLoader", f"Loaded {total} cards from '{CARD_DATA_ROOT}'")

_initialize_card_cache()

def get_card_by_id(card_id: str):
    return _card_lookup.get(card_id)

def get_all_cards():
    return list(_card_lookup.values())

def get_cards_by_usage(tag: str):
    result = []
    for card in _card_lookup.values():
        for option in card.get("options", []):
            if tag in option.get("usage", []):
                result.append(card)
                break
    return result

def get_cards_with_action():
    return get_cards_by_usage("action")

def get_cards_with_modifier():
    return get_cards_by_usage("modifier")
