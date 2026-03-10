# game settings
WIDTH = 1280
HEIGHT = 705
FPS = 60
TITLE = "Echoes of the Labyrinth"

# colors we use everywhere
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

# player stuff
PLAYER_SPEED = 5
PLAYER_JUMP_STRENGTH = 15
PLAYER_GRAVITY = 0.8
PLAYER_SIZE = (50, 80)

# level stuff - just tile size 4 now
TILE_SIZE = 64

# memory types - duration in ms, None = never fades
MEMORY_TYPES = {
    'red': {'color': RED, 'duration': None},  # permanent
    'blue': {'color': BLUE, 'duration': 10000},  # 10 secs
    'green': {'color': GREEN, 'duration': 20000},  # 20 secs
    'purple': {'color': PURPLE, 'duration': 15000},  # 15 secs
    'yellow': {'color': YELLOW, 'duration': 30000}  # 30 secs
}