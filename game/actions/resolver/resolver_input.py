# file: actions/resolver/resolver_input.py

import random
from actions.cards.card_loader import get_all_cards
from actions.resolver.modifiers import Modifier
from utils import globals as G
from utils.enums import UIMode
from utils.logger import log_debug

def handle_action_resolution_input(action: str) -> bool:
    if G.gamestate.ui_mode != UIMode.RESOLVER:
        return False

    resolver = getattr(G, "active_resolver", None)
    if not resolver:
        return False

    if action == "back":
        resolver.exit()
        return True

    if resolver.phase == "card":
        if not resolver.selected_option:
            if action.isdigit():
                idx = int(action) - 1
                resolver.select_option(idx)
                return True
        elif resolver.selector and not resolver.target:
            if action == "move_left":
                resolver.previous_target()
            elif action == "move_right":
                resolver.next_target()
            elif action == "confirm":
                resolver.confirm_target()
            return True
        elif action == "confirm" and resolver.selected_option and resolver.target:
            resolver.lock_in()
            return True
        return False

    if resolver.phase == "dice":
        if action.isdigit():
            val = int(action)
            if 1 <= val <= 6:
                resolver.resolve([val])
            elif val == 9:
                count = resolver.selected_option.get("dice_count", 1)
                rolls = [random.randint(1, 6) for _ in range(count)]
                resolver.resolve(rolls)
            return True
        elif action == "confirm":
            if resolver.dice_rolls:
                resolver.resolve(resolver.dice_rolls)
                return True
        return False

    if resolver.phase == "done":
        if action == "confirm":
            resolver.exit()
            return True

    return False


def create_modifier_from_card(card):
    label = card.get("name", "Unnamed")
    stat = None
    amount = 0
    duration = 0
    flat_bonus = 0
    dice_bonus = 0

    for option in card.get("options", []):
        effect = option.get("effect", {})
        if effect.get("type") == "add_modifier":
            stat = effect.get("stat")
            amount = effect.get("amount", 0)
            duration = effect.get("duration", 0)
        elif effect.get("type") == "add_dice":
            dice_bonus = effect.get("amount", 0)

    return Modifier(
        id=card["id"],
        label=label,
        stat=stat,
        amount=amount,
        duration=duration,
        flat_bonus=flat_bonus,
        dice_bonus=dice_bonus,
        source_card=card["id"]
    )
