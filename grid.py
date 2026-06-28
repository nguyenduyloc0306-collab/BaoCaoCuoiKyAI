
import random

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # obstacles[y][x] = True neu la vat can
        self.obstacles = [[False for _ in range(width)] for _ in range(height)]

    # ------------------------------------------------------------------
    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def is_border(self, x, y):
        """Return True if (x, y) is on the outer wall ring."""
        return (x == 0 or x == self.width - 1 or
                y == 0 or y == self.height - 1)

    def is_obstacle(self, x, y):
        if not self.in_bounds(x, y):
            return True
        if self.is_border(x, y):
            return True
        return self.obstacles[y][x]

    def is_walkable(self, x, y):
        return (self.in_bounds(x, y) and
                not self.is_border(x, y) and
                not self.obstacles[y][x])

    # ------------------------------------------------------------------
    def set_obstacle(self, x, y, value=True):
        if self.in_bounds(x, y):
            self.obstacles[y][x] = value

    def toggle_obstacle(self, x, y):
        if self.in_bounds(x, y):
            self.obstacles[y][x] = not self.obstacles[y][x]

    def clear_obstacles(self):
        self.obstacles = [[False for _ in range(self.width)] for _ in range(self.height)]

    # ------------------------------------------------------------------
    def generate_random_obstacles(self, density, rng=None, protected_cells=None):

        rng = rng or random
        protected_cells = protected_cells or set()
        self.clear_obstacles()
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in protected_cells:
                    continue
                if self.is_border(x, y):   # border is always a wall, never an obstacle tile
                    continue
                if rng.random() < density:
                    self.obstacles[y][x] = True

    # ------------------------------------------------------------------
    def copy(self):
        g = Grid(self.width, self.height)
        g.obstacles = [row[:] for row in self.obstacles]
        return g

    def free_cells(self):
        return [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if not self.is_border(x, y) and not self.obstacles[y][x]
        ]
