# Game settings
WIDTH = 1280
HEIGHT = 705
FPS = 60
TITLE = "Echoes of the Labyrinth"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
BG_COLOR = (20, 20, 40)

# Player settings
PLAYER_SPEED = 5
PLAYER_JUMP_STRENGTH = 15
PLAYER_GRAVITY = 0.8
PLAYER_SIZE = (50, 80)

# Level settings
TILE_SIZE = 64

# Memory settings
MEMORY_TYPES = {
    'red': {'color': RED, 'duration': None},  # Permanent
    'blue': {'color': BLUE, 'duration': 10000},  # 10 seconds
    'green': {'color': GREEN, 'duration': 20000},  # 20 seconds
    'purple': {'color': PURPLE, 'duration': 15000},  # 15 seconds
    'yellow': {'color': YELLOW, 'duration': 30000}
}