"""
Main game class
"""
import pygame
import random
from constants import WIDTH, HEIGHT, GRID_WIDTH, GRID_HEIGHT, Colors, GameState, CELL_SIZE
from maze import Maze
from pacman import PacMan
from ghost import Ghost

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Enhanced Pac-Man with AI Ghosts")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 36)
        self.small_font = pygame.font.SysFont('Arial', 24)
        
        self.maze = Maze(GRID_WIDTH, GRID_HEIGHT)
        self.reset_game()
    
    def reset_game(self):
        """Reset game to initial state"""
        self.state = GameState.PLAYING
        self.score = 0
        
        # Find valid starting positions
        valid_positions = []
        for x in range(1, self.maze.width - 1):
            for y in range(1, self.maze.height - 1):
                if self.maze.is_valid_position(x, y):
                    valid_positions.append((x, y))
        
        # Place Pac-Man
        start_pos = random.choice(valid_positions)
        self.pacman = PacMan(start_pos[0], start_pos[1])
        
        # Place ghosts away from Pac-Man
        ghost_positions = random.sample([pos for pos in valid_positions 
                                       if abs(pos[0] - start_pos[0]) + abs(pos[1] - start_pos[1]) > 8], 
                                      min(2, len(valid_positions) - 1))
        
        self.ghosts = [
            Ghost(ghost_positions[0][0], ghost_positions[0][1], Colors.RED, "a_star"),
            Ghost(ghost_positions[1][0], ghost_positions[1][1], Colors.BLUE, "minimax")
        ]
        
        # Create dots
        self.dots = set()
        for x in range(self.maze.width):
            for y in range(self.maze.height):
                if (self.maze.is_valid_position(x, y) and 
                    (x, y) != (self.pacman.pos.x, self.pacman.pos.y) and
                    (x, y) not in [(g.pos.x, g.pos.y) for g in self.ghosts]):
                    self.dots.add((x, y))
    
    def handle_input(self):
        """Handle user input"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.pacman.move(0, -1, self.maze)
        if keys[pygame.K_DOWN]:
            self.pacman.move(0, 1, self.maze)
        if keys[pygame.K_LEFT]:
            self.pacman.move(-1, 0, self.maze)
        if keys[pygame.K_RIGHT]:
            self.pacman.move(1, 0, self.maze)
    
    def update(self):
        """Update game state"""
        if self.state != GameState.PLAYING:
            return
        
        # Update ghosts
        for ghost in self.ghosts:
            ghost.update(self.pacman, self.maze)
        
        # Check dot collection
        if self.pacman.pos.tuple() in self.dots:
            self.dots.remove(self.pacman.pos.tuple())
            self.score += 10
        
        # Check collisions with ghosts
        for ghost in self.ghosts:
            if self.pacman.pos == ghost.pos:
                self.state = GameState.GAME_OVER
                return
        
        # Check win condition
        if not self.dots:
            self.state = GameState.WON
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(Colors.BLACK)
        
        # Draw maze walls
        for wall_x, wall_y in self.maze.walls:
            rect = pygame.Rect(wall_x * CELL_SIZE, wall_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, Colors.WALL, rect)
        
        # Draw dots
        for dot_x, dot_y in self.dots:
            center_x = dot_x * CELL_SIZE + CELL_SIZE // 2
            center_y = dot_y * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, Colors.WHITE, (center_x, center_y), 2)
        
        # Draw game entities
        self.pacman.draw(self.screen)
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        
        # Draw UI
        score_text = self.small_font.render(f"Score: {self.score}", True, Colors.WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw game over/win screen
        if self.state == GameState.GAME_OVER:
            self.draw_end_screen("GAME OVER!")
        elif self.state == GameState.WON:
            self.draw_end_screen("YOU WIN!")
    
    def draw_end_screen(self, message: str):
        """Draw end game screen"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        text = self.font.render(message, True, Colors.WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        
        restart_text = self.small_font.render("Press R to restart, Q to quit", True, Colors.WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(restart_text, restart_rect)