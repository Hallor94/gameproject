# file: entities/effects/effects_manager.py

from utils.logger import log_debug, log_warn

ALLOWED_STATS = {
    "strength", "endurance", "dexterity", "intelligence", "nerve", "luck",
    "health", "max_health", "move_points", "max_move_points", "attack", "base_attack",
}


class EffectManager:
    def __init__(self, owner):
        self.owner = owner
        self.effects = []
        log_debug("Effects", f"EffectManager initialized for {owner}", file=__file__)

    def add_effect(self, effect):
        if getattr(self.owner, "type", None) == "enemy" and not effect.allow_enemy:
            log_debug("Effects", f"Effect '{effect.name}' skipped for enemy {self.owner}", file=__file__)
            return
        self.effects.append(effect.copy())
        log_debug("Effects", f"Effect added: {effect.name} to {self.owner}", file=__file__)
        self._handle_applied_effect(effect)

    def remove_effect_by_id(self, effect_id):
        before = len(self.effects)
        self.effects = [e for e in self.effects if e.id != effect_id]
        after = len(self.effects)
        if before != after:
            log_debug("Effects", f"Effect removed: {effect_id} from {self.owner}", file=__file__)

    def tick_round_effects(self):
        expired = []
        for effect in self.effects:
            if not effect.per_turn:
                effect.tick()
                if effect.is_expired():
                    expired.append(effect)

        for e in expired:
            self._handle_expired_effect(e)

        self._enforce_stat_clamps()
        self.effects = [e for e in self.effects if not e.is_expired()]

        if expired:
            log_debug("Effects", f"{len(expired)} effects expired on {self.owner}", file=__file__)

    def get_total_modifier(self, key):
        return sum(e.modifiers.get(key, 0) if isinstance(e.modifiers.get(key), (int, float)) else 0 for e in self.effects)

    def get_modified_value(self, key, base_value):
        if key not in ALLOWED_STATS:
            log_warn("Effects", f"Requested unknown stat: {key}", file=__file__)
            return base_value

        add = 0
        mul = 1.0
        set_val = None

        for effect in self.effects:
            mod = effect.modifiers.get(key)
            if isinstance(mod, dict):
                add += mod.get("add", 0)
                mul *= mod.get("mul", 1.0)
                if mod.get("set") is not None:
                    set_val = mod["set"]
            elif isinstance(mod, (int, float)):
                add += mod

        result = (base_value * mul) + add
        final = set_val if set_val is not None else (int(result) if isinstance(base_value, int) else result)
        return max(0, final)

    def get_all_effects(self):
        return list(self.effects)

    def is_stat_overridden(self, key):
        for effect in self.effects:
            mod = effect.modifiers.get(key)
            if isinstance(mod, dict) and mod.get("set") is not None:
                return True
        return False

    def get_stat_color(self, key, modified, base):
        if self.is_stat_overridden(key):
            return (80, 160, 255)
        if modified > base:
            return (80, 255, 80)
        elif modified < base:
            return (255, 80, 80)
        return (255, 255, 255)

    def _adjust_stat_pair(self, key):
        cur_key = f"{key}_current"
        mod_key = f"{key}_modified"
        base_key = f"{key}_base"

        if hasattr(self.owner, cur_key) and hasattr(self.owner, mod_key) and hasattr(self.owner, base_key):
            cur = getattr(self.owner, cur_key)
            mod = getattr(self.owner, mod_key)
            base = getattr(self.owner, base_key)

            if cur > mod:
                setattr(self.owner, cur_key, mod)
            elif cur == base:
                setattr(self.owner, cur_key, mod)

    def _handle_applied_effect(self, effect):
        log_debug("Effects", f"Applying effect: {effect.name} to {self.owner}", file=__file__)
        self._apply_effect_modifiers(effect)

    def _handle_expired_effect(self, effect):
        log_debug("Effects", f"Effect expired: {effect.name} on {self.owner}", file=__file__)
        self._apply_effect_modifiers(effect)

    def _apply_effect_modifiers(self, effect):
        for key, mod in effect.modifiers.items():
            # Direct damage / instant stat impact
            if key == "health_current" and hasattr(self.owner, "health_current"):
                self.owner.health_current += mod
                self.owner.health_current = max(0, self.owner.health_current)
                log_debug("Effects", f"{self.owner} takes {mod} damage → HP: {self.owner.health_current}", file=__file__)
                continue

            if key == "move_points_current" and hasattr(self.owner, "move_points_current"):
                self.owner.move_points_current += mod
                self.owner.move_points_current = max(0, self.owner.move_points_current)
                log_debug("Effects", f"{self.owner} gains {mod} MP → MP: {self.owner.move_points_current}", file=__file__)
                continue

            # Regular stat mods
            if key in ALLOWED_STATS and hasattr(self.owner, f"{key}_base"):
                base = getattr(self.owner, f"{key}_base")
                modified = self.get_modified_value(key, base)
                setattr(self.owner, f"{key}_modified", modified)
                log_debug("Effects", f"{self.owner} stat updated: {key} → {modified}", file=__file__)
            else:
                log_warn("Effects", f"{self.owner} missing base stat for: {key}", file=__file__)

        self._adjust_stat_pair("health")
        self._adjust_stat_pair("move_points")
        self._enforce_stat_clamps()

    def _enforce_stat_clamps(self):
        if hasattr(self.owner, "health_current") and hasattr(self.owner, "health_modified"):
            if self.owner.health_current > self.owner.health_modified:
                log_debug("Effects", f"{self.owner} HP clamped: {self.owner.health_current} → {self.owner.health_modified}", file=__file__)
                self.owner.health_current = self.owner.health_modified

        if hasattr(self.owner, "move_points_current") and hasattr(self.owner, "move_points_modified"):
            if self.owner.move_points_current > self.owner.move_points_modified:
                log_debug("Effects", f"{self.owner} MP clamped: {self.owner.move_points_current} → {self.owner.move_points_modified}", file=__file__)
                self.owner.move_points_current = self.owner.move_points_modified

    def update_tile_effects(self, effect_lookup):
        tile = getattr(self.owner, "tile", None)
        if not tile:
            log_warn("Effects", f"{self.owner} has no tile for tile effect evaluation", file=__file__)
            return

        current_ids = {e.id for e in self.effects}

        for effect in effect_lookup.values():
            if "environment" not in effect.tags:
                continue

            should_apply = True
            for expr, expected in effect.conditions.items():
                try:
                    parts = expr.split(".")
                    value = self.owner
                    for part in parts:
                        value = getattr(value, part)
                    if value != expected:
                        should_apply = False
                        break
                except AttributeError:
                    log_warn("Effects", f"Failed to resolve condition '{expr}' on {self.owner}", file=__file__)
                    should_apply = False
                    break

            already_applied = effect.id in current_ids

            if getattr(self.owner, "type", None) == "enemy" and not effect.allow_enemy:
                continue

            if should_apply and not already_applied:
                log_debug("Effects", f"Applying tile effect: {effect.name} to {self.owner}", file=__file__)
                copied = effect.copy()
                self.effects.append(copied)
                self._handle_applied_effect(copied)
            elif not should_apply and already_applied:
                self.remove_effect_by_id(effect.id)
