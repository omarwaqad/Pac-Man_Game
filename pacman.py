import pygame
from position import Position
from constants import Colors, CELL_SIZE

class PacMan:
    def __init__(self, x: int, y: int):
        self.pos = Position(x, y)
        self.move_timer = 0
        self.move_delay = 6  # Moves every 6 frames (slower movement)
    
    def move(self, dx: int, dy: int, maze):
        """Move Pac-Man directly if valid and timer allows"""
        self.move_timer += 1
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            new_x = self.pos.x + dx
            new_y = self.pos.y + dy
            if maze.is_valid_position(new_x, new_y):
                self.pos.x = new_x
                self.pos.y = new_y
    
    def draw(self, screen: pygame.Surface):
        center_x = self.pos.x * CELL_SIZE + CELL_SIZE // 2
        center_y = self.pos.y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, Colors.YELLOW, (center_x, center_y), CELL_SIZE // 3)