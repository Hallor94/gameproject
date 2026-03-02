from enum import Enum

class TileVisibility(Enum):
    HIDDEN = 0
    DISCOVERED = 1
    VISIBLE = 2

class FogOfWarMode(Enum):
    NORMAL = "normal"
    KNOWN_LAYOUT = "known_layout"
    BOARDGAME = "boardgame"
