# file: actions/cards/card_interpreter.py

from actions.resolver.modifiers import Modifier
from utils.logger import log_warn, log_debug


def apply_card_effect(option: dict, resolver):
    """
    Applies a single effect entry from a selected card option.
    Each option contains:
    - 'effect_type': one of 'instant', 'modifier', 'effect'
    - 'effect': dict describing what to do
    """

    effect_type = option.get("effect_type")
    effect = option.get("effect")

    if not effect_type or not effect:
        log_warn("CardInterpreter", f"Missing effect_type or effect in option: {option}")
        return

    if effect_type == "instant":
        _apply_instant_effect(effect, resolver)

    elif effect_type == "modifier":
        _apply_modifier_effect(effect, resolver)

    elif effect_type == "effect":
        _apply_persistent_effect(effect, resolver)

    else:
        log_warn("CardInterpreter", f"Unknown effect_type: {effect_type}")


def _apply_instant_effect(effect, resolver):
    etype = effect.get("type")
    amount = effect.get("amount", 0)

    if etype == "heal":
        target = resolver.target or resolver.actor
        if target:
            target.heal(amount)
            log_debug("CardInterpreter", f"Healed {target} for {amount}")
        else:
            log_warn("CardInterpreter", "No valid target for heal instant effect")

    elif etype == "deal_damage":
        target = resolver.target
        if target:
            target.take_damage(amount)
            log_debug("CardInterpreter", f"Dealt {amount} damage to {target}")
        else:
            log_warn("CardInterpreter", "No valid target for deal_damage effect")

    else:
        log_warn("CardInterpreter", f"Unknown instant effect type: {etype}")


def _apply_modifier_effect(effect, resolver):
    etype = effect.get("type")

    if etype == "add_stat":
        resolver.queued_modifiers.append(Modifier(
            source_id="card",
            label=effect.get("label", "Modifier"),
            stat_bonuses={effect["stat"]: effect["value"]}
        ))

    elif etype == "add_dice":
        resolver.queued_dice.append({
            "dice_type": effect.get("dice_type", "d6"),
            "count": effect.get("count", 1),
        })

    else:
        log_warn("CardInterpreter", f"Unknown modifier effect type: {etype}")


def _apply_persistent_effect(effect, resolver):
    if resolver.actor and hasattr(resolver.actor, "_effects"):
        resolver.actor._effects.apply_named(
            effect.get("effect"),
            duration=effect.get("duration", 1)
        )
    else:
        log_warn("CardInterpreter", "Missing _effects manager for persistent effect")
