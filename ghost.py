"""
Ghost AI implementation
"""
import pygame
import random
from queue import PriorityQueue
from typing import List, Tuple
from position import Position
from constants import Colors, CELL_SIZE, DIRECTIONS

class Ghost:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int], algorithm: str):
        self.pos = Position(x, y)
        self.color = color
        self.algorithm = algorithm
        self.move_timer = 0
        self.move_delay = 12  # Moves every 12 frames (slower than Pac-Man)
    
    def update(self, pacman, maze):
        """Update ghost position"""
        self.move_timer += 1
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            self.move(pacman, maze)
    
    def move(self, pacman, maze):
        """Move ghost based on AI algorithm"""
        if self.algorithm == "a_star":
            self.a_star_move(pacman, maze)
        elif self.algorithm == "minimax":
            self.minimax_move(pacman, maze)
    
    def get_valid_neighbors(self, pos: Position, maze) -> List[Position]:
        """Get all valid neighboring positions"""
        neighbors = []
        for dx, dy in DIRECTIONS:
            new_x, new_y = pos.x + dx, pos.y + dy
            if maze.is_valid_position(new_x, new_y):
                neighbors.append(Position(new_x, new_y))
        return neighbors
    
    def a_star_move(self, pacman, maze):
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
    
    def minimax_move(self, pacman, maze):
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