"""
Game constants and configuration
"""
from enum import Enum

# Display constants
WIDTH, HEIGHT = 800, 600
GRID_WIDTH, GRID_HEIGHT = 25, 19
CELL_SIZE = min(WIDTH // GRID_WIDTH, HEIGHT // GRID_HEIGHT)

# Colors
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    PURPLE = (128, 0, 128)
    ORANGE = (255, 165, 0)
    WALL = (0, 0, 139)

# Game states
class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2
    WON = 3
    PAUSED = 4

# Movement directions
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # UP, DOWN, LEFT, RIGHT