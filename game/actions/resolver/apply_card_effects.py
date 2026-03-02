# file: actions/resolver/apply_card_effects.py

from actions.resolver.modifiers import Modifier
from entities.effects.effect import Effect
from utils.logger import log_warn

def apply_card_effects(effect_dict, source, target):
    """
    Applies a card effect to a target.
    Supports:
        - type: heal
        - type: damage
        - type: add_modifier
    """
    if not target:
        log_warn("CardEffect", "No target to apply effect to")
        return

    effect_type = effect_dict.get("type")
    if effect_type == "heal":
        amount = effect_dict.get("amount", 0)
        if hasattr(target, "health_current"):
            target.health_current = min(target.health_modified, target.health_current + amount)

    elif effect_type == "damage":
        amount = effect_dict.get("amount", 0)
        if hasattr(target, "health_current"):
            target.health_current = max(0, target.health_current - amount)

    elif effect_type == "add_modifier":
        stat = effect_dict.get("stat")
        amount = effect_dict.get("amount", 0)
        duration = effect_dict.get("duration", 1)
        if hasattr(target, "_effects"):
            effect = Effect(
                id="card_buff_" + stat,
                name="Card Buff",
                description=f"+{amount} {stat.title()}",
                modifiers={stat: amount},
                duration=duration,
                tags=["card"]
            )
            target._effects.add_effect(effect)

    else:
        log_warn("CardEffect", f"Unhandled effect type: {effect_type}")

def create_modifier_from_card(card, option):
    """
    Extracts a Modifier object from a card + option (used before resolution).
    """
    effect = option.get("effect", {})
    stat_bonuses = {}
    flat_bonus = 0
    dice_bonus = 0

    if effect.get("type") == "add_modifier":
        stat = effect.get("stat")
        amount = effect.get("amount", 0)
        if stat:
            stat_bonuses[stat] = amount

    elif effect.get("type") == "add_flat":
        flat_bonus = effect.get("amount", 0)

    elif effect.get("type") == "add_dice":
        dice_bonus = effect.get("amount", 0)

    return Modifier(
        source_id=card.get("id", "unknown"),
        label=option.get("label", card.get("name", "Modifier")),
        stat_bonuses=stat_bonuses,
        flat_bonus=flat_bonus,
        dice_bonus=dice_bonus,
        description=card.get("description", "")
    )
