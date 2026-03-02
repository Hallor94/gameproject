# file: entities/enemy_marker.py

from utils.logger import log_warn

# === Define all available marks (as keys to cached images) ===
class VisualMark:
    def __init__(self, key: str):
        self.key = key  # e.g., "mark_1"

    def __repr__(self):
        return self.key

    def __eq__(self, other):
        return isinstance(other, VisualMark) and self.key == other.key

    def __hash__(self):
        return hash(self.key)


# Ordered list of available tag keys
ALL_MARKS = [VisualMark(f"mark_{i}") for i in range(1, 10)]

# Tracks used marks during the game session
_used_marks = set()


def assign_next_available_mark(enemy):
    for mark in ALL_MARKS:
        if mark not in _used_marks:
            enemy.visual_mark = mark
            _used_marks.add(mark)
            return
    log_warn("EnemyMarker", "Ran out of unique marks to assign.")


def reset_marks():
    """Clears used marks — useful between levels or for restart."""
    _used_marks.clear()


def get_entity_mark(entity):
    return getattr(entity, "visual_mark", None)


def get_entity_mark_icon(entity):
    from utils.image_cache import icon_cache
    mark = get_entity_mark(entity)
    if mark and mark.key in icon_cache:
        return icon_cache[mark.key]
    return None
