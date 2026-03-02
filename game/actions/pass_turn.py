# file: actions/pass_turn.py

from utils import globals as G
from utils.logger import log_info

def execute_pass_turn():
    current_player = G.gamestate.get_active_player()

    if G.gamestate.is_player_turn(current_player):
        log_info("Turn", f"{current_player.player_name} ended their turn.", file=__file__)
        G.gamestate.end_player_turn(current_player)
