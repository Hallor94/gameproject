# file: events/dialogue/dialogue_loader.py

import json
import os
from .dialogue_manager import DialogueTrigger
from . import conditions
from utils.logger import log_info, log_warn, log_error


def load_all_triggers(directory="data/dialogue/triggers"):
    """Load all dialogue triggers from all .json files in the given directory and subdirectories."""
    condition_map = {
        k: v for k, v in vars(conditions).items()
        if callable(v) and not k.startswith("__")
    }

    triggers = []
    json_files = []

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".json"):
                json_files.append(os.path.join(root, filename))

    if not json_files:
        log_warn("Dialogue", f"No dialogue trigger files found in: {directory}", file=__file__)
        return []

    for filepath in json_files:
        try:
            with open(filepath, "r") as f:
                raw_entries = json.load(f)
        except Exception as e:
            log_error("Dialogue", f"Failed to load {filepath}: {e}", file=__file__)
            continue

        for item in raw_entries:
            cond_str = item.get("condition", "")
            if ":" in cond_str:
                name, param = cond_str.split(":", 1)
                base_func = condition_map.get(name)
                condition_func = base_func(param) if base_func else lambda ctx: True
            else:
                condition_func = condition_map.get(cond_str, lambda ctx: True)

            trigger = DialogueTrigger(
                event=item["event"],
                condition=condition_func,
                lines=item["lines"],
                who=item.get("who"),
                chance=item.get("chance", 1.0),
                flags=item.get("flags", [])
            )
            triggers.append(trigger)

    log_info("Dialogue", f"Loaded {len(triggers)} triggers from {len(json_files)} file(s)", file=__file__)
    return triggers
