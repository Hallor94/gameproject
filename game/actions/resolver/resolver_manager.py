# file: actions/resolver/resolver_manager.py

import random

from actions.cards.card_loader import get_card_by_id
from actions.resolver.targeting import TargetSelector
from actions.resolver.apply_card_effects import apply_card_effects, create_modifier_from_card
from actions.resolver.display_chain import format_result_text
from utils import globals as G
from utils.enums import UIMode
from utils.logger import log_debug, log_warn
from utils.ui_mode_manager import set_ui_mode


class ActionResolver:
    def __init__(self, actor, template_dict=None, test_mode=False):
        self.actor = actor
        self.test_mode = test_mode

        self.card_template = template_dict  # full card with options
        self.selected_option = None         # selected option dict
        self.selected_option_index = None

        self.target = None
        self.selector = None

        self.modifiers = []
        self.dice_result = None
        self.dice_rolls = []
        self.dice_upgraded = []
        self.was_success = None
        self.result_data = None

        self.card_ids = []
        self.main_card_id = None

        self.phase = "card"

        G.gamemap.camera.camera_mode_override = "player"

        if self.card_template:
            self.apply_card(self.card_template["id"])

    def apply_card(self, card_id):
        card = get_card_by_id(card_id)
        if not card:
            log_warn("Resolver", f"Tried to apply unknown card: {card_id}", file=__file__)
            return

        if not self.card_template:
            self.card_template = card
            self.main_card_id = card_id
            self.update_card_logic()
        else:
            added = False
            for option in card.get("options", []):
                if "modifier" in option.get("usage", []):
                    mod = create_modifier_from_card(card, option)
                    self.add_modifier(mod)
                    added = True
            if not added:
                log_warn("Resolver", f"No modifier option found on card '{card_id}'")

        if card_id not in self.card_ids:
            self.card_ids.append(card_id)

    def update_card_logic(self):
        if not self.card_template:
            return

        options = self.card_template.get("options", [])
        if len(options) == 1:
            self.selected_option_index = 0
            self.selected_option = options[0]
        elif len(options) > 1:
            self.selected_option = None  # wait for user
            self.selected_option_index = None
            return

        self._update_targeting()

    def select_option(self, index):
        options = self.card_template.get("options", [])
        if 0 <= index < len(options):
            self.selected_option_index = index
            self.selected_option = options[index]
            self._update_targeting()

    def _update_targeting(self):
        targeting = self.selected_option.get("targeting", "self") if self.selected_option else "self"
        if targeting == "self":
            self.target = self.actor
            self.selector = None
        else:
            self.selector = TargetSelector(self.actor, self.selected_option)
            self.target = self.selector.auto_confirm()

    def next_target(self):
        if self.selector:
            self.selector.next()

    def previous_target(self):
        if self.selector:
            self.selector.previous()

    def get_current_target(self):
        if self.selector:
            return self.selector.get()
        return self.target

    def confirm_target(self):
        if self.selector:
            self.target = self.get_current_target()

    def add_modifier(self, modifier):
        self.modifiers.append(modifier)

    def remove_card(self, card_id: str):
        if card_id in self.card_ids:
            self.card_ids.remove(card_id)
            if card_id == self.main_card_id:
                self.exit()

    def lock_in(self):
        if self.phase == "card" and self.selected_option and self.target:
            self.phase = "dice"

    def resolve(self, dice_input):
        if self.phase != "dice" or not self.selected_option:
            return None

        base_dice = self.selected_option.get("dice_count", 1 if self.selected_option.get("use_dice", True) else 0)
        bonus_dice = sum(m.get_dice_bonus() for m in self.modifiers)
        total_dice = base_dice + bonus_dice

        if isinstance(dice_input, int):
            dice_results = [dice_input] * total_dice
        else:
            dice_results = dice_input[:total_dice]
            while len(dice_results) < total_dice:
                dice_results.append(1)

        self.dice_rolls = dice_results

        luck = getattr(self.actor, "luck_base", 0)
        upgraded = [
            min(v + 1, 6) if v < 6 and random.random() < 0.1 * luck else v
            for v in dice_results
        ]

        self.dice_result = sum(upgraded)
        self.dice_upgraded = upgraded

        total = self.compute_total()
        threshold = self.selected_option.get("threshold", 0)
        comparison = self.selected_option.get("comparison_type", "greater_equal")

        if comparison == "greater":
            self.was_success = total > threshold
        elif comparison == "greater_equal":
            self.was_success = total >= threshold
        elif comparison == "less":
            self.was_success = total < threshold
        elif comparison == "less_equal":
            self.was_success = total <= threshold
        elif comparison == "equal":
            self.was_success = total == threshold
        elif comparison == "not_equal":
            self.was_success = total != threshold
        else:
            self.was_success = total >= threshold

        self.phase = "done"

        effect = self.selected_option.get("effect") if self.was_success else self.selected_option.get("failure_effect")
        if effect:
            apply_card_effects(effect, self.actor, self.target)

        self.result_data = effect
        summary = format_result_text(self.was_success, self.result_data)
        G.message_manager.show_floating(summary["text"], duration=2.0)

        return self.was_success

    def compute_total(self):
        if not self.selected_option:
            return 0

        keys = self.selected_option.get("required_stats") or [self.selected_option.get("base_stat", "")]
        stats_total = sum(getattr(self.actor, f"{k}_base", 0) for k in keys if k)
        bonus = sum(m.get_stat_bonus(k) for m in self.modifiers for k in keys if k)
        flat = sum(m.flat_bonus for m in self.modifiers)

        return stats_total + bonus + flat + (self.dice_result or 0)

    def get_display_info(self):
        if self.phase == "card":
            return "Configure card: pick option, target, confirm."
        elif self.phase == "dice":
            return "Roll dice or scan result."
        elif self.phase == "done":
            return "Action resolved. Press Enter to close."
        return ""

    def exit(self):
        log_debug("Resolver", f"Exiting resolver.")
        G.active_resolver = None
        G.active_menu = None
        set_ui_mode(UIMode.MAIN)
        G.gamemap.camera.camera_mode_override = None


def start_resolver(actor, card_id: str, test_mode=False):
    if G.active_resolver:
        log_warn("Resolver", "Already active resolver in progress.")
        return

    G.active_resolver = ActionResolver(actor, template_dict=None, test_mode=test_mode)
    G.active_resolver.apply_card(card_id)

    G.active_menu = G.resolver_menu
    G.active_menu.update_options()
    set_ui_mode(UIMode.RESOLVER)
