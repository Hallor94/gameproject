# file: actions/resolver/targeting.py

from utils.logger import log_debug


def get_valid_targets(actor, template):
    """
    Returns a list of valid target entities based on the action template.
    Supported targeting types: "self", "tile", "enemy", "ally", "adjacent", "object", "self_tile"
    """
    tile = actor.tile
    if not tile:
        return []
    

    targeting = template.get("targeting", None)
    all_entities = tile.occupants

    log_debug("Targeting", f"Actor = {actor}, Targeting = {targeting}, Found = {len(all_entities)} entities", file=__file__)
    log_debug("Targeting", f"Valid targets: {[getattr(e, 'name', repr(e)) for e in all_entities]}", file=__file__)


    if targeting == "self":
        return [actor]

    elif targeting == "tile":
        return all_entities

    elif targeting == "self_tile":
        return all_entities  # same as tile targeting

    elif targeting == "enemy":
        return [e for e in all_entities if _is_enemy(actor, e)]

    elif targeting == "ally":
        return [e for e in all_entities if _is_ally(actor, e) and e != actor]
    
    elif targeting == "ally_or_self":
        return [e for e in all_entities if _is_ally(actor, e) or e == actor]

    elif targeting == "adjacent":
        adjacent_entities = []
        for neighbor in tile.adjacent_tiles:
            adjacent_entities.extend(neighbor.occupants)
        return adjacent_entities

    elif targeting == "object":
        # Placeholder — use tile.tags or interactive object system
        return []

    log_debug("Targeting", f"Unhandled targeting type: {targeting}", file=__file__)
    return []


def _is_enemy(actor, other):
    return getattr(actor, "type", None) != getattr(other, "type", None)


def _is_ally(actor, other):
    return getattr(actor, "type", None) == getattr(other, "type", None)


class TargetSelector:
    def __init__(self, actor, template):
        self.valid_targets = get_valid_targets(actor, template)
        self.index = 0 if self.valid_targets else None

    def next(self):
        if self.valid_targets:
            self.index = (self.index + 1) % len(self.valid_targets)

    def previous(self):
        if self.valid_targets:
            self.index = (self.index - 1) % len(self.valid_targets)

    def get(self):
        if self.index is not None and self.valid_targets:
            return self.valid_targets[self.index]
        return None

    def auto_confirm(self):
        if len(self.valid_targets) == 1:
            return self.valid_targets[0]
        return None