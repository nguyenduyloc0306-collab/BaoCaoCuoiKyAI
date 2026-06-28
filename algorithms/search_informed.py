
import heapq
import random
from collections import deque
from utils import get_neighbors, manhattan

def _nearest_target(pos, targets):
    if not targets:
        return None
    return min(targets, key=lambda t: manhattan(pos, t))

def _bfs_distance_all(start, grid):

    dist = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in get_neighbors(current, grid):
            if nxt not in dist:
                dist[nxt] = dist[current] + 1
                queue.append(nxt)
    return dist

# ----------------------------------------------------------------------------
# Greedy Best-First Search (chi dung heuristic h(n), khong xet chi phi g(n))
# ----------------------------------------------------------------------------
def _greedy_path(start, goal, grid):
    frontier = [(manhattan(start, goal), start)]
    came_from = {start: None}
    visited = {start}
    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            break
        for nxt in get_neighbors(current, grid):
            if nxt not in visited:
                visited.add(nxt)
                came_from[nxt] = current
                heapq.heappush(frontier, (manhattan(nxt, goal), nxt))
    if goal not in came_from:
        return None
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path

def greedy_decide(agent_pos, targets, grid, role, rng=None, **kwargs):
    rng = rng or random
    if role == "hunter":
        target = _nearest_target(agent_pos, targets)
        if target is None:
            return agent_pos
        path = _greedy_path(agent_pos, target, grid)
        if path and len(path) > 1:
            return path[1]
        return agent_pos
    else:
        # Runner "greedy": chon ngay hang xom co heuristic lon nhat, KHONG
        # tinh chi phi da di (dac trung cua Greedy Best-First). Heuristic o
        # day la khoang cach THUC qua duong di (BFS tu hunter gan nhat) thay
        # vi Manhattan thuan - vi Manhattan la duong chim bay, khong biet
        # vat can co the chan huong "nhin co ve xa nhat" lam Runner tu chay
        # vao ngo cut. Dung BFS-distance van dung tinh chat Greedy (chon
        # ngay theo 1 ham uoc luong, khong cong don chi phi g(n)), chi la
        # ham uoc luong tot hon, biet ne vat can.
        if not targets:
            return agent_pos
        nearest_hunter = _nearest_target(agent_pos, targets)
        neighbors = get_neighbors(agent_pos, grid, shuffle=True)
        if not neighbors:
            return agent_pos
        dist_map = _bfs_distance_all(nearest_hunter, grid)
        best = max(neighbors, key=lambda n: dist_map.get(n, manhattan(n, nearest_hunter)))
        return best

# ----------------------------------------------------------------------------
# A* Search (g(n) + h(n))
# ----------------------------------------------------------------------------
def _astar_path(start, goal, grid):
    frontier = [(manhattan(start, goal), 0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    while frontier:
        _, g, current = heapq.heappop(frontier)
        if current == goal:
            break
        for nxt in get_neighbors(current, grid):
            new_g = cost_so_far[current] + 1
            if nxt not in cost_so_far or new_g < cost_so_far[nxt]:
                cost_so_far[nxt] = new_g
                came_from[nxt] = current
                f = new_g + manhattan(nxt, goal)
                heapq.heappush(frontier, (f, new_g, nxt))
    if goal not in came_from:
        return None
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path

def _astar_distance(start, goal, grid):

    path = _astar_path(start, goal, grid)
    if path is None:
        return float("inf")
    return len(path) - 1

def astar_decide(agent_pos, targets, grid, role, rng=None, **kwargs):
    rng = rng or random
    if role == "hunter":
        target = _nearest_target(agent_pos, targets)
        if target is None:
            return agent_pos
        path = _astar_path(agent_pos, target, grid)
        if path and len(path) > 1:
            return path[1]
        return agent_pos
    else:
        if not targets:
            return agent_pos
        nearest_hunter = _nearest_target(agent_pos, targets)
        neighbors = get_neighbors(agent_pos, grid, shuffle=True)
        if not neighbors:
            return agent_pos
        # Dung A* de do khoang cach THUC (qua duong di, tinh obstacle) tu moi
        # hang xom toi hunter gan nhat, chon huong xa nhat.
        best = max(neighbors, key=lambda n: _astar_distance(n, nearest_hunter, grid))
        return best
