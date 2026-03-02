# file: game/update_system.py

from utils import globals as G

def update_all(dt):
    """Updates all systems that require time-based logic."""
    G.dialogue_manager.update(dt)
    G.movement_animator.update(dt)
    G.message_manager.update(dt)
    G.gamestate.ambience.update(dt)

    for player in G.gamestate.players:
        player.effects.update_tile_effects(G.effect_catalog)

    # Future systems can be added here:
    # - G.status_effect_manager.update(dt)
    # - G.enemy_ai.update(dt)
    # - G.weather_system.update(dt)
