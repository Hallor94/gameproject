# utils/enums.py

from enum import Enum, auto

class UIMode(Enum):
    SETUP = auto()
    MAIN = auto()
    PAUSED = auto()
    MOVEMENT = auto()
    DIALOGUE = auto()
    CONTEXT = auto()
    INSPECTION = auto()
    VENT = auto()
    RESOLVER = auto()

class TurnPhase(Enum):
    PLAYER_TURN = auto()
    ENEMY_TURN = auto()
    ROUND_END = auto()

class TileVisibility(Enum):
    HIDDEN = auto()
    DISCOVERED = auto()
    VISIBLE = auto()
    SECRET = 99

class Difficulty(Enum):
    CASUAL = auto()
    NORMAL = auto()
    HARDCORE = auto()

class FogOfWarMode(Enum):
    NORMAL = "normal"
    KNOWN_LAYOUT = "known_layout"
    BOARDGAME = "boardgame"

class TileOverlayState(Enum):
    NONE = 0
    FIRE = 1
    FLOODED = 2
    GAS = 3
    ALARM = 4
    RADIATION = 5
    POWER_OFF = 6