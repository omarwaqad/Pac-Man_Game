import pygame
import sys
import random
from queue import PriorityQueue


# Initialize pygame
pygame.init()



# Screen dimensions
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
CELL_SIZE = WIDTH // GRID_SIZE



# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)



# Directions
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]



# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man with AI Ghosts")




# Pac-Man class
class PacMan:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x = (self.x + dx) % GRID_SIZE
        self.y = (self.y + dy) % GRID_SIZE

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)




# Ghost class
class Ghost:
    def __init__(self, x, y, color, algorithm):
        self.x = x
        self.y = y
        self.color = color
        self.algorithm = algorithm

    def move(self, pacman, grid):
        if self.algorithm == "a_star":
            self.a_star_move(pacman, grid)
        elif self.algorithm == "minimax":
            self.minimax_move(pacman, grid)

    def a_star_move(self, pacman, grid):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        start = (self.x, self.y)
        goal = (pacman.x, pacman.y)
        open_set = PriorityQueue()
        open_set.put((0, start))
        came_from = {}
        g_score = {start: 0}

        while not open_set.empty():
            _, current = open_set.get()

            if current == goal:
                break

            for dx, dy in DIRECTIONS:
                neighbor = ((current[0] + dx) % GRID_SIZE, (current[1] + dy) % GRID_SIZE)
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    priority = tentative_g_score + heuristic(neighbor, goal)
                    open_set.put((priority, neighbor))
                    came_from[neighbor] = current

        # Reconstruct path
        current = goal
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()

        if path:
            self.x, self.y = path[0]

    def minimax_move(self, pacman, grid):
        def minimax(position, depth, maximizing_player):
            if depth == 0 or position == (pacman.x, pacman.y):
                return -abs(position[0] - pacman.x) - abs(position[1] - pacman.y)

            if maximizing_player:
                max_eval = float('-inf')
                for dx, dy in DIRECTIONS:
                    neighbor = ((position[0] + dx) % GRID_SIZE, (position[1] + dy) % GRID_SIZE)
                    eval = minimax(neighbor, depth - 1, False)
                    max_eval = max(max_eval, eval)
                return max_eval
            else:
                min_eval = float('inf')
                for dx, dy in DIRECTIONS:
                    neighbor = ((position[0] + dx) % GRID_SIZE, (position[1] + dy) % GRID_SIZE)
                    eval = minimax(neighbor, depth - 1, True)
                    min_eval = min(min_eval, eval)
                return min_eval

        best_move = None
        best_score = float('-inf')
        for dx, dy in DIRECTIONS:
            neighbor = ((self.x + dx) % GRID_SIZE, (self.y + dy) % GRID_SIZE)
            score = minimax(neighbor, 3, False)
            if score > best_score:
                best_score = score
                best_move = neighbor

        if best_move:
            self.x, self.y = best_move

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))







# Show end screen
def show_end_screen(message):
    font = pygame.font.SysFont(None, 75)
    text = font.render(message, True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    screen.fill(BLACK)
    screen.blit(text, text_rect)
    pygame.display.flip()

    pygame.time.delay(3000)
    pygame.quit()
    sys.exit()







# Main game loop
def main():
    clock = pygame.time.Clock()
    pacman = PacMan(GRID_SIZE // 2, GRID_SIZE // 2)
    ghost_a_star = Ghost(0, 0, RED, "a_star")
    ghost_minimax = Ghost(GRID_SIZE - 1, GRID_SIZE - 1, BLUE, "minimax")
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Create dots
    dots = set()
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if (x, y) != (pacman.x, pacman.y):
                dots.add((x, y))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            pacman.move(0, -1)
        if keys[pygame.K_DOWN]:
            pacman.move(0, 1)
        if keys[pygame.K_LEFT]:
            pacman.move(-1, 0)
        if keys[pygame.K_RIGHT]:
            pacman.move(1, 0)

        ghost_a_star.move(pacman, grid)
        ghost_minimax.move(pacman, grid)

        # Pac-Man eats dots
        if (pacman.x, pacman.y) in dots:
            dots.remove((pacman.x, pacman.y))

        # Check for game over
        if (pacman.x, pacman.y) == (ghost_a_star.x, ghost_a_star.y) or (pacman.x, pacman.y) == (ghost_minimax.x, ghost_minimax.y):
            show_end_screen("Game Over!")

        # Check for win
        if not dots:
            show_end_screen("You Win!")

        screen.fill(BLACK)

        # Draw dots
        for dot in dots:
            pygame.draw.circle(screen, WHITE, (dot[0] * CELL_SIZE + CELL_SIZE // 2, dot[1] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 6)

        pacman.draw()
        ghost_a_star.draw()
        ghost_minimax.draw()
        pygame.display.flip()
        clock.tick(10)




if __name__ == "__main__":
    main()