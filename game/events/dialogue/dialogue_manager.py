# file: events/dialogue/dialogue_manager.py

from events.broadcaster import subscribe
import random
from utils import globals as G
from utils.logger import log_info, log_debug, log_warn


class DialogueTrigger:
    def __init__(self, event, condition, lines, who=None, chance=1.0, flags=None):
        self.event = event
        self.condition = condition
        self.lines = lines if isinstance(lines, list) else [lines]
        self.who = who  # optional char_id filter
        self.chance = chance
        self.flags = flags or []
        self._triggered = False

    def is_valid(self, context):
        entity = context.get("entity")

        if "once" in self.flags and self._triggered:
            log_debug("Dialogue", f"Trigger skipped (already triggered once): {self.lines}", file=__file__)
            return False

        if not entity or not hasattr(entity, "char_id"):
            log_warn("Dialogue", f"Entity missing or invalid in context: {entity}", file=__file__)
            return False

        if self.who and entity.char_id != self.who:
            log_debug("Dialogue", f"Trigger char_id mismatch: {entity.char_id} != {self.who}", file=__file__)
            return False

        if not self.condition(context):
            log_debug("Dialogue", f"Trigger condition returned False for {entity}", file=__file__)
            return False

        roll = random.random()
        if roll > self.chance:
            log_debug("Dialogue", f"Trigger chance failed: rolled {roll:.2f}, needed ≤ {self.chance}", file=__file__)
            return False

        return True

    def mark_triggered(self):
        if "once" in self.flags:
            self._triggered = True


class DialogueManager:
    def __init__(self):
        self.triggers = []
        self.pending_lines = []
        self.delay_timer = 0

    def subscribe_to_events(self):
        for event_name in ["turn_started", "turn_ended", "character_moved"]:
            subscribe(event_name, self.handle_event)
        log_debug("Dialogue", "Subscribed to character and turn events", file=__file__)

    def register_trigger(self, trigger):
        self.triggers.append(trigger)

    def handle_event(self, context):
        event_type = context.get("event")
        entity = context.get("entity")

        if not event_type or not entity or not hasattr(entity, "char_id"):
            log_warn("Dialogue", f"Skipping event; missing type or entity: {event_type}, {entity}", file=__file__)
            return

        base_name = entity.char_id
        log_debug("Dialogue", f"Event detected: {event_type} for {base_name}", file=__file__)

        valid_triggers = []
        for trig in self.triggers:
            if trig.event != event_type:
                continue
            if trig.is_valid(context):
                valid_triggers.append(trig)

        if not valid_triggers:
            log_debug("Dialogue", f"No valid triggers matched for event {event_type} and {base_name}", file=__file__)
            return

        best_trigger = random.choice(valid_triggers)
        line = random.choice(best_trigger.lines)
        self.pending_lines.append((entity, line))
        best_trigger.mark_triggered()

        log_info("Dialogue", f"Trigger matched! Queued line: '{line}' for {entity}", file=__file__)

    def update(self, dt):
        self.delay_timer -= dt
        if self.pending_lines and self.delay_timer <= 0:
            entity, line = self.pending_lines.pop(0)
            G.message_manager.show_speech(line, entity)
            log_info("Dialogue", f"Speech shown: '{line}' for {entity}, pos=({getattr(entity, 'world_x', '?')}, {getattr(entity, 'world_y', '?')})", file=__file__)
            self.delay_timer = 1.5

    def __setattr__(self, name, value):
        if getattr(G, "DEBUG_ATTR_WARNINGS", False) and not hasattr(self, name):
            log_warn("Dialogue", f"{self.__class__.__name__} has no attribute '{name}'", file=__file__)
        super().__setattr__(name, value)
