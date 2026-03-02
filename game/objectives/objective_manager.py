import pygame
from utils import globals as G

class ObjectivesManager:
    def __init__(self):
        self.trackers = []

    def add_tracker(self, label, conditions, on_success=None, on_fail=None, **options):
        tracker = {
            "label": label,
            "conditions": conditions,
            "on_success": on_success,
            "on_fail": on_fail,
            "category": options.get("category", "Main"),
            "visible": options.get("visible", True),
            "repeatable": options.get("repeatable", False),
            "display_value": options.get("display_value"),
            "depends_on": options.get("depends_on", [])
        }
        self.trackers.append(tracker)

    def increment(self, label, condition_key, amount=1):
        tracker = self._find(label)
        if not tracker:
            return
        condition = tracker["conditions"].get(condition_key)
        if condition and isinstance(condition["value"], (int, float)):
            condition["value"] += amount

    def set_value(self, label, condition_key, value):
        tracker = self._find(label)
        if not tracker:
            return
        if condition_key in tracker["conditions"]:
            tracker["conditions"][condition_key]["value"] = value

    def _find(self, label):
        for t in self.trackers:
            if t["label"] == label:
                return t
        return None

    def update(self, dt):
        for tracker in self.trackers[:]:
            if not tracker["visible"]:
                continue

            all_conditions = tracker["conditions"]
            success, fail = False, False

            for key, cond in all_conditions.items():
                if cond.get("auto_increment"):
                    cond["timer"] = cond.get("timer", cond["interval"])
                    cond["timer"] -= dt
                    if cond["timer"] <= 0:
                        cond["value"] += 1
                        cond["timer"] = cond["interval"]

                # Success check
                if cond.get("on_met") == "success" and cond["value"] >= cond["target"]:
                    success = True
                # Fail check
                if cond.get("on_exceed") == "fail" and cond["value"] > cond["target"]:
                    fail = True

            if success and tracker["on_success"]:
                tracker["on_success"]()
                self.trackers.remove(tracker)
            elif fail and tracker["on_fail"]:
                tracker["on_fail"]()
                self.trackers.remove(tracker)

    def draw(self, screen):
        font = G.font
        padding = 10
        x = screen.get_width()/2
        y = 100

        visible_trackers = [t for t in self.trackers if t["visible"]]
        categories = {}

        # Group trackers by category
        for tracker in visible_trackers:
            cat = tracker["category"]
            categories.setdefault(cat, []).append(tracker)

        # Draw categories in reverse order so bottom stacks properly
        for category in reversed(sorted(categories.keys())):
            cat_label = f"*** {category} Objective{'s' if category.lower() != 'main' else ''} ***"
            cat_text = font.render(cat_label, True, (200, 200, 255))
            cat_rect = cat_text.get_rect(bottomright=(x, y))
            screen.blit(cat_text, cat_rect)
            y -= cat_rect.height + 6

            for tracker in reversed(categories[category]):
                label = tracker["label"]
                display_val = tracker["display_value"]

                if not display_val:
                    conds = tracker["conditions"]
                    display_val = " | ".join(
                        f"{key}: {c['value']}/{c['target']}" if isinstance(c["value"], (int, float)) else f"{key}: {c['value']}"
                        for key, c in conds.items() if "target" in c
                    )

                full_label = f"{label}: {display_val}"
                text = font.render(full_label, True, (255, 255, 255))
                rect = text.get_rect(bottomright=(x, y))
                pygame.draw.rect(screen, (0, 0, 0), rect.inflate(12, 8))
                pygame.draw.rect(screen, (255, 255, 255), rect.inflate(12, 8), 2)
                screen.blit(text, rect)
                y -= rect.height + 10

