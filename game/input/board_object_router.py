# file: input/board_object_router.py

from actions.cards.card_loader import get_card_by_id
from actions.resolver.apply_card_effects import apply_card_effects, create_modifier_from_card
from actions.resolver.resolver_manager import start_resolver
from actions.resolver.targeting import get_valid_targets
from utils import globals as G
from utils.logger import log_info, log_warn

def play_card(card_id):
    card = get_card_by_id(card_id)
    if not card:
        log_warn("CardRouter", f"Unknown card ID: {card_id}")
        return

    resolver = getattr(G, "active_resolver", None)
    phase = resolver.phase if resolver else None
    actor = G.gamestate.get_active_player()

    # Flatten usage tags from all options
    valid_usages = {u for opt in card.get("options", []) for u in opt.get("usage", [])}

    # === MODIFIER ===
    if "modifier" in valid_usages:
        if not resolver or phase != "prepare_modifiers":
            log_info("CardRouter", f"Modifier card {card_id} ignored — not in valid resolver phase")
            return
        for option in card.get("options", []):
            if "modifier" in option.get("usage", []):
                mod = create_modifier_from_card(card, option)
                resolver.add_modifier(mod)
                G.message_manager.show_floating(f"Modifier added: {mod.label}", duration=1.5)
                return

    # === INSTANT ===
    if "instant" in valid_usages and not resolver:
        for option in card.get("options", []):
            if option.get("effect_type") != "instant":
                continue

            # If targeting required
            targeting = option.get("targeting", "self")
            targets = get_valid_targets(actor, option)
            if len(targets) == 1:
                apply_card_effects(option.get("effect", {}), actor, targets[0])
                G.message_manager.show_floating(f"{card['name']} used!", duration=2.0)
                return
            elif len(targets) > 1:
                log_info("CardRouter", f"Instant card {card_id} needs target picker UI (unimplemented)")
                return
            else:
                log_warn("CardRouter", f"No valid targets for instant card {card_id}")
                return

    # === ACTION ===
    if ("action" in valid_usages or "resolver" in valid_usages) and not resolver:
        log_info("CardRouter", f"Launching resolver with card {card_id}")
        start_resolver(actor, card_id, test_mode=False)
        return

    log_info("CardRouter", f"Card {card_id} ignored — no matching context")


def watch_board_state_for_objects(state):
    if not isinstance(state, list):
        return

    seen_card_ids = set()
    dice_values = []

    for obj in state:
        if not obj.get("is_confident", True):
            continue

        if obj.get("type") == "card":
            card_id = obj.get("label")
            if card_id and card_id not in seen_card_ids:
                play_card(card_id)
                seen_card_ids.add(card_id)

        elif obj.get("type") == "dice":
            try:
                val = int(obj.get("value"))
                if 1 <= val <= 6:
                    dice_values.append(val)
            except Exception:
                continue

    # If we're in a resolver and in the prepare_dice phase, store these
    resolver = getattr(G, "active_resolver", None)
    if resolver and resolver.phase == "prepare_dice" and dice_values:
        resolver.dice_rolls = dice_values  # Just preview, not resolved yet
