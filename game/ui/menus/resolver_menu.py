# file: ui/menus/resolver_menu.py

import random
from ui.menus.base_menu import BaseMenu
from actions.cards.card_loader import get_all_cards, get_card_by_id
from utils import globals as G
from utils.enums import UIMode


class ResolverMenu(BaseMenu):
    def __init__(self):
        super().__init__()
        self.selected_index = 0
        self.update_options()

    def update_options(self):
        resolver = G.active_resolver
        if not resolver:
            return

        self.options.clear()
        self.selected_index = 0
        phase = resolver.phase

        print(f"[ResolverMenu] Updating for phase: {phase}")

        if phase == "select_option":
            for i, option in enumerate(resolver.options):
                label = option.get("label", f"Option {i+1}")
                self.options.append({
                    "label": f"{i+1}: {label}",
                    "callback": lambda idx=i: self._choose_option(idx)
                })

        if phase in ("prepare_modifiers", "select_card"):
            if resolver.template is None:
                # Step 1: pick main card
                all_cards = get_all_cards()

                        
                print("[DEBUG] total cards:", len(all_cards))
                for card in all_cards:
                    print("→", card["id"], [opt.get("usage") for opt in card.get("options", [])])

                action_cards = [
                    c for c in all_cards
                    if any("action" in opt.get("usage", []) for opt in c.get("options", []))
    ]
                print("[DEBUG] action cards:", [c["id"] for c in action_cards])

                for card in action_cards:
                    label = card.get("name", "Unnamed Card")
                    self.options.append({
                        "label": f"Use: {label}",
                        "callback": (lambda cid=card["id"]: self._apply_card(cid))
                    })
            else:
                # Step 2: select modifiers
                all_cards = get_all_cards()
                modifier_cards = [
                    c for c in all_cards
                    if any("modifier" in opt.get("usage", []) for opt in c.get("options", []))
                ]

                for card in modifier_cards:
                    label = card.get("name", "Unnamed Modifier")
                    self.options.append({
                        "label": f"Add Modifier: {label}",
                        "callback": lambda c=card: self._add_card(c["id"])
                    })

                for card_id in resolver.card_ids:
                    self.options.append({
                        "label": f"Remove: {card_id}",
                        "callback": lambda cid=card_id: self._remove_card(cid)
                    })

                self.options.append({
                    "label": "Confirm Cards",
                    "callback": self._confirm_cards
                })

        elif phase == "_dice":
            for i in range(1, 7):
                self.options.append({
                    "label": f"Roll {i}",
                    "callback": lambda v=i: self._roll_dice(v)
                })
            self.options.append({
                "label": "Roll Random",
                "callback": self._roll_random
            })

        elif phase == "resolved":
            self.options.append({
                "label": "Done",
                "callback": self._exit_resolver
            })

    def _apply_card(self, card_id):
        resolver = G.active_resolver
        if not resolver:
            return
        resolver.apply_card(card_id)
        self.update_options()

    def _add_card(self, card_id):
        resolver = G.active_resolver
        if not resolver:
            return
        if card_id not in resolver.card_ids:
            resolver.apply_card(card_id)
            self.update_options()

    def _remove_card(self, card_id):
        resolver = G.active_resolver
        if not resolver:
            return
        resolver.remove_card(card_id)
        self.update_options()

    def _confirm_cards(self):
        resolver = G.active_resolver
        if not resolver or not resolver.template:
            G.message_manager.show_floating("Pick a card first!", duration=2.0)
            return
        resolver.phase = "prepare_dice"
        self.update_options()

    def _roll_dice(self, value):
        resolver = G.active_resolver
        if not resolver:
            return
        resolver.lock_in()
        resolver.resolve(value)
        self.update_options()

    def _roll_random(self):
        self._roll_dice(random.randint(1, 6))

    def _choose_option(self, index):
        resolver = G.active_resolver
        if not resolver:
            return
        resolver.select_option(index)
        self.update_options()

    def _exit_resolver(self):
        resolver = G.active_resolver
        if resolver:
            resolver.exit()

    def handle_confirm(self):
        return super().handle_confirm()

    def handle_back(self):
        resolver = G.active_resolver
        if resolver:
            resolver.exit()
        return True
    
    def draw(self, surface, x=0, y=0):
        super().draw(surface, x=x, y=y)
