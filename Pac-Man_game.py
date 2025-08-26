import pygame
import sys
import random
from queue import PriorityQueue
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Set, Optional

# Initialize pygame
pygame.init()

# Constants
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

# Directions
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # UP, DOWN, LEFT, RIGHT

@dataclass
class Position:
    x: int
    y: int
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def tuple(self):
        return (self.x, self.y)

class Maze:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.walls = set()
        self.generate_maze()
    
    def generate_maze(self):
        """Generate a simple, open maze pattern"""
        # Create border walls
        for x in range(self.width):
            self.walls.add((x, 0))
            self.walls.add((x, self.height - 1))
        for y in range(self.height):
            self.walls.add((0, y))
            self.walls.add((self.width - 1, y))
        
        # Add some internal walls - much more sparse and open
        # Horizontal walls with gaps
        for x in range(3, self.width - 3, 8):
            for y in range(3, self.height - 3, 6):
                # Short horizontal walls with gaps
                for i in range(3):
                    if x + i < self.width - 1:
                        self.walls.add((x + i, y))
                # Leave gaps for movement
                
        # Vertical walls with gaps  
        for x in range(6, self.width - 6, 8):
            for y in range(4, self.height - 4, 6):
                # Short vertical walls with gaps
                for i in range(2):
                    if y + i < self.height - 1:
                        self.walls.add((x, y + i))
        
        # Add a few strategic single walls
        strategic_walls = [
            (self.width // 4, self.height // 2),
            (3 * self.width // 4, self.height // 2),
            (self.width // 2, self.height // 4),
            (self.width // 2, 3 * self.height // 4),
        ]
        
        for wall in strategic_walls:
            if 1 < wall[0] < self.width - 2 and 1 < wall[1] < self.height - 2:
                self.walls.add(wall)
    
    def is_wall(self, x: int, y: int) -> bool:
        return (x, y) in self.walls
    
    def is_valid_position(self, x: int, y: int) -> bool:
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                not self.is_wall(x, y))

class PacMan:
    def __init__(self, x: int, y: int):
        self.pos = Position(x, y)
        self.move_timer = 0
        self.move_delay = 6  # Moves every 4 frames (slower movement)
    
    def move(self, dx: int, dy: int, maze: Maze):
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

class Ghost:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int], algorithm: str):
        self.pos = Position(x, y)
        self.color = color
        self.algorithm = algorithm
        self.move_timer = 0
        self.move_delay = 12  # Moves every 6 frames (slower than Pac-Man)
    
    def update(self, pacman: PacMan, maze: Maze):
        """Update ghost position"""
        self.move_timer += 1
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            self.move(pacman, maze)
    
    def move(self, pacman: PacMan, maze: Maze):
        """Move ghost based on AI algorithm"""
        if self.algorithm == "a_star":
            self.a_star_move(pacman, maze)
        elif self.algorithm == "minimax":
            self.minimax_move(pacman, maze)
    
    def get_valid_neighbors(self, pos: Position, maze: Maze) -> List[Position]:
        """Get all valid neighboring positions"""
        neighbors = []
        for dx, dy in DIRECTIONS:
            new_x, new_y = pos.x + dx, pos.y + dy
            if maze.is_valid_position(new_x, new_y):
                neighbors.append(Position(new_x, new_y))
        return neighbors
    
    def a_star_move(self, pacman: PacMan, maze: Maze):
        """A* pathfinding to chase Pac-Man"""
        def heuristic(a: Position, b: Position) -> int:
            return abs(a.x - b.x) + abs(a.y - b.y)
        
        start = self.pos
        goal = pacman.pos
        
        if start == goal:
            return
        
        open_set = PriorityQueue()
        open_set.put((0, id(start), start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        
        visited = set()
        
        while not open_set.empty():
            _, _, current = open_set.get()
            
            if current in visited:
                continue
            visited.add(current)
            
            if current == goal:
                break
            
            for neighbor in self.get_valid_neighbors(current, maze):
                if neighbor in visited:
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    open_set.put((f_score[neighbor], id(neighbor), neighbor))
        
        # Reconstruct path and take first step
        if goal in came_from:
            current = goal
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            
            if len(path) > 0:
                next_pos = path[-1]  # First step in path
                self.pos = next_pos
    
    def minimax_move(self, pacman: PacMan, maze: Maze):
        """Improved minimax for ghost movement"""
        def evaluate_position(pos: Position) -> float:
            # Distance to Pac-Man (negative because ghost wants to minimize distance)
            distance = abs(pos.x - pacman.pos.x) + abs(pos.y - pacman.pos.y)
            if distance == 0:
                return 1000  # Caught Pac-Man!
            
            # Prefer positions closer to Pac-Man
            closeness_score = -distance
            
            # Add some randomness to avoid getting stuck
            randomness = random.uniform(-0.1, 0.1)
            
            return closeness_score + randomness
        
        def minimax(pos: Position, depth: int, maximizing: bool, alpha: float = float('-inf'), beta: float = float('inf')) -> float:
            if depth == 0:
                return evaluate_position(pos)
            
            neighbors = self.get_valid_neighbors(pos, maze)
            if not neighbors:
                return evaluate_position(pos)
            
            if maximizing:
                max_eval = float('-inf')
                for neighbor in neighbors:
                    eval_score = minimax(neighbor, depth - 1, False, alpha, beta)
                    max_eval = max(max_eval, eval_score)
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break  # Alpha-beta pruning
                return max_eval
            else:
                min_eval = float('inf')
                for neighbor in neighbors:
                    eval_score = minimax(neighbor, depth - 1, True, alpha, beta)
                    min_eval = min(min_eval, eval_score)
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break  # Alpha-beta pruning
                return min_eval
        
        best_move = None
        best_score = float('-inf')
        
        neighbors = self.get_valid_neighbors(self.pos, maze)
        for neighbor in neighbors:
            # Ghost is maximizing (trying to get closer to Pac-Man)
            score = minimax(neighbor, 3, False)  # Depth of 3 for better planning
            if score > best_score:
                best_score = score
                best_move = neighbor
        
        if best_move:
            self.pos = best_move
    
    def draw(self, screen: pygame.Surface):
        rect = pygame.Rect(self.pos.x * CELL_SIZE + 2, 
                          self.pos.y * CELL_SIZE + 2, 
                          CELL_SIZE - 4, CELL_SIZE - 4)
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, Colors.WHITE, rect, 2)

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
        
        # Update Pac-Man (no need to call update, movement is direct from input)
        
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
    
    def run(self):
        """Main game loop"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.state in [GameState.GAME_OVER, GameState.WON]:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
            
            if self.state == GameState.PLAYING:
                self.handle_input()
                self.update()
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()