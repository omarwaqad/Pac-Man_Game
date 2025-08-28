"""
Maze generation and management
"""

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