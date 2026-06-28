
import math
import random

def manhattan(a, b):

    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def euclidean(a, b):

    return math.hypot(a[0] - b[0], a[1] - b[1])

def clamp(value, lo, hi):
    return max(lo, min(hi, value))

NEIGHBOR_DELTAS_4 = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # len, xuong, trai, phai

def get_neighbors(pos, grid, shuffle=False):

    x, y = pos
    deltas = list(NEIGHBOR_DELTAS_4)
    if shuffle:
        random.shuffle(deltas)
    result = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if grid.is_walkable(nx, ny):
            result.append((nx, ny))
    return result

def random_free_cell(grid, occupied, rng=None):

    rng = rng or random
    free_cells = [
        (x, y)
        for x in range(grid.width)
        for y in range(grid.height)
        if grid.is_walkable(x, y) and (x, y) not in occupied
    ]
    if not free_cells:
        return None
    return rng.choice(free_cells)
