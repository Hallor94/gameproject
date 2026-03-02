# file: actions/resolver/modifiers.py

class Modifier:
    def __init__(self, source_id, label=None, stat_bonuses=None, flat_bonus=0, dice_bonus=0, description=None):
        self.source_id = source_id  # The card or item that created this modifier
        self.label = label or source_id  # Display name
        self.stat_bonuses = stat_bonuses or {}  # e.g., {"dexterity": 2}
        self.flat_bonus = flat_bonus  # Constant bonus added to resolution
        self.dice_bonus = dice_bonus  # Adds extra dice (future use)
        self.description = description or ""

    def get_stat_bonus(self, stat):
        return self.stat_bonuses.get(stat, 0)
    
    def get_display_label(self):
        return self.label
    
    def get_dice_bonus(self):
        return self.dice_bonus or 0

    def __repr__(self):
        bonus_parts = [f"+{v} {k.upper()}" for k, v in self.stat_bonuses.items()]
        if self.flat_bonus:
            bonus_parts.append(f"+{self.flat_bonus} flat")
        return f"Modifier({self.label}: {' | '.join(bonus_parts)})"
