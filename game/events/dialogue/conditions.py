def tile_is_combat_zone(context):
    tile = context.get("tile")
    return tile and tile.type == "combat"

def tile_is_named(name):
    def check(context):
        tile = context.get("tile")
        return tile and tile.name.lower() == name.lower()
    return check

def tile_is_type(tile_type):
    def check(context):
        tile = context.get("tile")
        return tile and getattr(tile, "type", "").lower() == tile_type.lower()
    return check


def is_first_time_in_room(context):
    char = context.get("character")
    tile = context.get("tile")
    if not char or not tile:
        return False
    seen_key = f"seen_{tile.grid_pos}"
    if getattr(char, seen_key, False):
        return False
    setattr(char, seen_key, True)
    return True

def player_is_near_enemy(context):
    player_tile = context.get("tile")
    enemies = context.get("enemies", [])
    return any(enemy.tile in player_tile.get_adjacent_tiles() for enemy in enemies)

def tile_is_type(tile_type):
    def check(context):
        tile = context.get("tile")
        return tile and getattr(tile, "type", "").lower() == tile_type.lower()
    return check

def is_first_time_in_room(context):
    char = context.get("character")
    tile = context.get("tile")
    if not char or not tile:
        return False
    seen_key = f"seen_{tile.grid_pos}"
    if getattr(char, seen_key, False):
        return False
    setattr(char, seen_key, True)
    return True

def meeting_another_player(context):
    tile = context.get("tile")
    char = context.get("character")
    if not tile or not char:
        return False
    # Must be at least one other player here
    return any(o for o in tile.occupants if getattr(o, "character", None) != char)
