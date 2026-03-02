import json
from utils import globals as G

def load_objectives(path, trigger_map):
    with open(path, 'r') as f:
        data = json.load(f)

    for entry in data:
        label = entry.get("label")
        category = entry.get("category", "Main")
        visible = entry.get("visible", True)
        repeatable = entry.get("repeatable", False)
        display_value = entry.get("display_value")
        depends_on = entry.get("depends_on", [])

        # Resolve callbacks if named
        on_success = trigger_map.get(entry.get("on_success"))
        on_fail = trigger_map.get(entry.get("on_fail"))

        conditions = entry.get("conditions", {})
        for cond in conditions.values():
            if cond.get("auto_increment"):
                cond["timer"] = cond.get("interval", 1.0)

        G.objectives_manager.add_tracker(
            label=label,
            conditions=conditions,
            on_success=on_success,
            on_fail=on_fail,
            category=category,
            visible=visible,
            repeatable=repeatable,
            display_value=display_value,
            depends_on=depends_on
        )
