# config.py

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
FPS = 30

ROAD_WIDTH = 80

CAR_LENGTH = 40
CAR_WIDTH = 20
CAR_SPEED = 2.5          # pixels per frame

SPAWN_PROB_PER_FRAME = 0.05

PHASE_MIN_DURATION_SEC = 3.0
MAX_RED_TIME_SEC = 20.0   # max time any side can stay red

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (40, 40, 40)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (220, 50, 50)
COLOR_GREEN = (50, 200, 50)
COLOR_YELLOW = (220, 220, 50)
COLOR_BLUE = (50, 150, 220)

# Directions
DIR_EAST = "EAST"
DIR_SOUTH = "SOUTH"

# Safety
SAFETY_MARGIN = 40  # stop before intersection center
