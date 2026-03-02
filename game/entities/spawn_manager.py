# file: entities/spawn_manager.py

import random
from entities.player import Player
from entities.enemy_marker import assign_next_available_mark
from map.tile import assign_entity_to_tile, TileVisibility
from utils import globals as G
from utils.logger import log_info, log_warn, log_error

ENEMY_CAP = 7  # Max allowed on map at once

def init_spawn_manager():
    """
    Hook into global event system. Should be called from init_helper.
    """
    G.gamestate.register_listener("round_started", on_round_started)

def spawn_players(player_data_list, spawn_tile_func):
    """
    Given player setup data and a tile selector, creates and places players on the map.
    """
    players = []

    for data in player_data_list:
        name = data["name"]
        character = data["character"]
        player = Player(name, character)

        tile = spawn_tile_func()
        if assign_entity_to_tile(player, tile):
            player.world_x, player.world_y = tile.get_world_position_for(player)
            players.append(player)
            log_info("SpawnManager", f"Spawned player {name} at {tile.grid_pos}", file=__file__)
        else:
            log_error("SpawnManager", f"Could not assign player {name} to tile {tile.grid_pos}", file=__file__)

    return players

def spawn_initial_enemies(count=3):
    """
    Spawns a number of enemies on unseen tiles at game start.
    """
    for _ in range(count):
        _spawn_enemy_on_unseen_tile()

def on_round_started(_data=None):
    """
    Called at the start of each round. Spawns a new enemy with 60% chance.
    """
    active_enemies = [e for e in G.gamestate.enemies if e.health_current > 0]
    if len(active_enemies) >= ENEMY_CAP:
        return

    if random.random() < 0.6:
        spawned = _spawn_enemy_on_unseen_tile()
        if spawned:
            G.gamestate.ambience.trigger_map_flicker(duration=3.0)

def _spawn_enemy_on_unseen_tile():
    """
    Internal: Spawns a single enemy from the pool on a random unseen tile.
    Returns True if an enemy was spawned.
    """
    if not G.enemy_pool:
        log_warn("SpawnManager", "No enemies left in pool.", file=__file__)
        return False

    tiles = [
        tile for row in G.gamemap.tiles for tile in row
        if tile.visibility_state != TileVisibility.VISIBLE and tile.occupants.count(None) > 0
    ]

    if not tiles:
        log_warn("SpawnManager", "No valid tiles to spawn enemy.", file=__file__)
        return False

    tile = random.choice(tiles)
    enemy = G.enemy_pool.pop()
    if assign_entity_to_tile(enemy, tile):
        enemy.world_x, enemy.world_y = tile.get_world_position_for(enemy)
        assign_next_available_mark(enemy)
        G.gamestate.enemies.append(enemy)
        log_info("SpawnManager", f"Spawned enemy {enemy.character_display_name} at {tile.grid_pos}", file=__file__)
        return True
    else:
        log_error("SpawnManager", f"Could not assign enemy {enemy.character_display_name} to tile {tile.grid_pos}", file=__file__)
        return False
