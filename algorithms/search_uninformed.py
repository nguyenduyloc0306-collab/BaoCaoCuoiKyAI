
import random
from utils import get_neighbors, manhattan

def _nearest_target(pos, targets):
    if not targets:
        return None
    return min(targets, key=lambda t: manhattan(pos, t))

# ----------------------------------------------------------------------------
# BFS - Breadth-First Search
# ----------------------------------------------------------------------------
def _bfs_path(start, goal, grid):

    if start == goal:
        return [start]
    from collections import deque
    visited = {start}
    queue = deque([start])
    parent = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for nxt in get_neighbors(current, grid):
            if nxt not in visited:
                visited.add(nxt)
                parent[nxt] = current
                queue.append(nxt)
    if goal not in parent:
        return None
    # truy nguoc duong di
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path

def _bfs_distance_all(start, grid):

    from collections import deque
    dist = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in get_neighbors(current, grid):
            if nxt not in dist:
                dist[nxt] = dist[current] + 1
                queue.append(nxt)
    return dist

def bfs_decide(agent_pos, targets, grid, role, rng=None, **kwargs):
    rng = rng or random
    if role == "hunter":
        target = _nearest_target(agent_pos, targets)
        if target is None:
            return agent_pos
        path = _bfs_path(agent_pos, target, grid)
        if path and len(path) > 1:
            return path[1]
        return agent_pos
    else:  # runner: tron xa Hunter gan nhat
        if not targets:
            return agent_pos
        nearest_hunter = _nearest_target(agent_pos, targets)
        dist_map = _bfs_distance_all(nearest_hunter, grid)
        neighbors = get_neighbors(agent_pos, grid, shuffle=True)
        if not neighbors:
            return agent_pos
        # chon hang xom co khoang cach (thuc, qua BFS) lon nhat den hunter
        best = max(neighbors, key=lambda n: dist_map.get(n, -1))
        return best

# ----------------------------------------------------------------------------
# DFS - Depth-First Search
# ----------------------------------------------------------------------------
def _dfs_path(start, goal, grid, depth_limit=None):

    stack = [(start, [start])]
    visited = {start}
    while stack:
        current, path = stack.pop()
        if current == goal:
            return path
        if depth_limit is not None and len(path) > depth_limit:
            continue
        for nxt in get_neighbors(current, grid):
            if nxt not in visited:
                visited.add(nxt)
                stack.append((nxt, path + [nxt]))
    return None

def dfs_decide(agent_pos, targets, grid, role, rng=None, **kwargs):
    rng = rng or random
    if role == "hunter":
        target = _nearest_target(agent_pos, targets)
        if target is None:
            return agent_pos
        path = _dfs_path(agent_pos, target, grid, depth_limit=grid.width * grid.height)
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
        # Runner van giu dac trung DFS o cach KHAM PHA (duyet sau, tham lam
        # cuc bo, khong toi uu toan cuc) nhung danh gia "huong nao tot" bang
        # KHOANG CACH THUC qua duong di (BFS tu hunter), khong dung Manhattan
        # thuan - de tranh bi vat can "lua" chon huong nhin co ve xa nhung
        # thuc te bi chan/phai di vong rat xa moi toi duoc.
        dist_map = _bfs_distance_all(nearest_hunter, grid)
        best = max(neighbors, key=lambda n: dist_map.get(n, manhattan(n, nearest_hunter)))
        return best
