# GameStateManager for turn control and phase handling
from enum import Enum, auto

class Phase(Enum):
    SETUP = auto()
    PLAYER_TURN = auto()
    ENEMY_TURN = auto()
    ROUND_END = auto()
    GAME_OVER = auto()

class GameStateManager:
    def __init__(self, players, enemies, map_ref):
        self.turn_count = 0
        self.players = players
        self.enemies = enemies
        self.current_player_index = 0
        self.phase = Phase.SETUP
        self.map = map_ref

    def start_turn(self):
        self.turn_count += 1
        self.phase = Phase.PLAYER_TURN
        print(f'Turn {self.turn_count} begins.')
        self.current_player_index = 0

    def process_player_turn(self):
        return self.players[self.current_player_index]

    def end_player_turn(self):
        self.current_player_index += 1
        if self.current_player_index >= len(self.players):
            self.phase = Phase.ENEMY_TURN
            self.process_enemy_turns()

    def process_enemy_turns(self):
        for enemy in self.enemies:
            enemy.take_turn(self.map, self.players)
        self.end_round()

    def end_round(self):
        self.phase = Phase.ROUND_END
        self.start_turn()
