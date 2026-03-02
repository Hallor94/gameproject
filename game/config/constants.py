# file: config/constants.py

# === Engine & Timing ===
FPS = 60
BASE_RESOLUTION = (1280, 720)

# === Map Tile Layout ===
TILE_BASE_HEIGHT = 300          # Base tile height in pixels
TILE_WIDTH_RATIO = 1.5          # Tile width relative to height
HOLY_PADDING = 315              # Padding between map and HUD edges
GROUP_CAMERA_MARGIN_TILES = 1   # When centering, allow each player to see this many tiles around them

# === Font Sizes ===
FONT_DEFAULT = 28
FONT_TITLE = 48
FONT_MENU = 30
FONT_STAT = 56
FONT_INSPECT = 42
FONT_LABEL = 28
FONT_COST = 42
FONT_FLAVOR = 20
FONT_HUD = 30
FONT_SMALL_UI = 18
FONT_CONTEXT = 30
FONT_FLOATING = 40
FONT_DIALOGUE = 32
FONT_SPEECH = 32
FONT_BUFF = 36

# === Portrait Rendering ===
PORTRAIT_BASE_RES = (256, 256)   # Original asset size
PORTRAIT_SIZE = (96, 96)         # Scaled size for UI display

# === Standee Rendering ===
STANDEE_BASE_SIZE = (128, 256)   # Original asset size
STANDEE_DISPLAY_SIZE = (64, 128) # Default render target size
STANDEE_HEIGHT_RATIO = 0.65      # Portion of tile height a standee occupies visually
STANDEE_SLOT_WIDTH_RATIO = 0.25  # How much we space out the standees on the tiles.

# NOTE: Standee width will be derived automatically from image aspect ratio.
# Character-specific size variation should be handled via `character.scale`