# file: actions/cards/card_manager.py

from actions.cards.card_loader import get_card_by_id
from actions.cards.card_interpreter import apply_card_effect
from utils.logger import log_warn

class CardManager:
    @staticmethod
    def apply_card(card_id: str, resolver) -> bool:
        card = get_card_by_id(card_id)
        if not card:
            log_warn("CardManager", f"Card ID '{card_id}' not found.")
            return False

        default_option = CardManager.get_modifier_default_option(card)
        if not default_option:
            log_warn("CardManager", f"Card '{card_id}' has no default modifier option.")
            return False

        apply_card_effect(default_option, resolver)
        resolver.card_ids.append(card_id)
        return True

    @staticmethod
    def get_modifier_default_option(card: dict):
        for option in card.get("options", []):
            if "modifier" in option.get("usage", []) and option.get("default_if_modifier"):
                return option
        return None
