# file: actions/resolver/display_chain.py

from utils import globals as G

STAT_LABELS = {
    "strength": "STR", "endurance": "END", "dexterity": "DEX", "intelligence": "INT",
    "nerve": "NRV", "luck": "LCK", "attack": "ATK"
}

def build_display_chain(resolver, stat_sources):
    if not resolver.template:
        return [], {"stat_total": 0, "dice_needed": 0, "comparison_symbol": ">="}

    parts = []
    actor = resolver.actor

    desired_order = ["strength", "endurance", "intelligence", "nerve", "dexterity", "luck"]
    for stat in desired_order:
        if stat in stat_sources:
            base, bonus = stat_sources[stat]
            # Get the true modified stat value (from effects/buffs)
            modified = actor.get_modified_stat(stat)

            icon = stat.lower()
            label = STAT_LABELS.get(stat.lower(), stat.upper())
            color = actor.effects.get_stat_color(stat, modified, base)

            parts.append({
                "icon": icon,
                "label": label,
                "value": f"{base + bonus}",
                "base": base,
                "bonus": bonus,
                "color": color,
            })


    # === Dice Display (before or after roll)
    base_dice = resolver.template.get("dice_count", 1 if resolver.template.get("use_dice", True) else 0)
    bonus_dice = sum(getattr(m, "dice_bonus", 0) for m in getattr(resolver, "modifiers", []))
    total_dice = base_dice + bonus_dice

    if not getattr(resolver, "dice_rolls", []):
        luck = actor.get_modified_stat("luck")
        for i in range(total_dice):
            chance = int(upgrade_chance(luck, i) * 100)
            parts.append({
                "icon": "dice_d6_q",
                "label": "D6",
                "value": "",
                "color": (180, 180, 180),
                "upgraded": False,
                "upgrade_chance": f"{chance}%"
            })
    else:
        for i, val in enumerate(resolver.dice_rolls):
            upgraded_val = resolver.dice_upgraded[i]
            is_upgraded = upgraded_val != val
            parts.append({
                "icon": f"dice_d6_{upgraded_val}",
                "label": "D6",
                "value": "",  # show icon instead of value text
                "color": (255, 255, 255) if not is_upgraded else (0, 255, 128),
                "upgraded": is_upgraded
            })

    return parts, _build_summary(resolver)


def _build_summary(resolver):
    if not resolver.template:
        return {
            "stat_total": 0,
            "dice_needed": 0,
        }
    total_stats = sum(base + bonus for base, bonus in resolver.get_stat_breakdown().values())

    threshold = resolver.template.get("threshold", 0)

    return {
        "stat_total": total_stats,
        "dice_needed": threshold,
        "comparison_symbol": get_comparison_symbol(resolver.template)
    }

def get_comparison_symbol(template):
    return {
        "greater": ">",
        "greater_equal": ">=",
        "less": "<",
        "less_equal": "<=",
        "equal": "=",
        "not_equal": "!="
    }.get(template.get("comparison_type", "greater_equal"), "≥")


def format_result_text(success, result_data):
    if not result_data:
        return {"text": "No effect", "color": (180, 180, 180)}

    if isinstance(result_data, str):
        return {"text": result_data, "color": (0, 255, 0) if success else (255, 0, 0)}

    rtype = result_data.get("type")

    if rtype == "deal_damage":
        return {"text": "Hit! Damage dealt.", "color": (0, 255, 0) if success else (255, 0, 0)}
    elif rtype == "open_loot":
        count = result_data.get("cards", 0)
        keep = result_data.get("keep", 0)
        return {"text": f"Loot {count} cards, keep {keep}", "color": (0, 255, 0)} if success else {"text": "No loot", "color": (255, 0, 0)}
    elif rtype == "heal":
        amt = result_data.get("amount", 0)
        return {"text": f"Heal {amt} HP", "color": (0, 255, 0)}
    elif rtype == "alarm":
        return {"text": result_data.get("message", "Alarm triggered!"), "color": (255, 0, 0)}
    elif rtype == "damage":
        return {"text": result_data.get("message", "You take damage!"), "color": (255, 0, 0)}
    elif rtype == "open_vent_menu":
        return {"text": "Entered the vent successfully!", "color": (0, 255, 0)}
    elif rtype == "complete_objective":
        return {"text": "Objective Completed!", "color": (0, 255, 0)}
    else:
        return {"text": "Action complete" if success else "Action failed", "color": (0, 255, 0) if success else (255, 0, 0)}


def upgrade_chance(luck, die_index):
    """Returns the base upgrade chance shown to user"""
    """Each point of luck gives 10% chance to upgrade die to next value, each additional dice gets halved chance."""
    chance_multiplier = 1.0 / (2 ** die_index)
    return 1.0 - (1.0 - 0.1 * luck) ** chance_multiplier
