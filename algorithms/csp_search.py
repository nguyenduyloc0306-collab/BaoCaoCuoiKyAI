
import random
from utils import get_neighbors, manhattan
import config

DIRS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # len, xuong, trai, phai

CSP_PLAN_LENGTH = 5  # so bien (buoc) cua bai toan CSP - du nho de duyet du 4^K

def _apply_dir(pos, dir_code, grid):

    dx, dy = DIRS[dir_code]
    nxt = (pos[0] + dx, pos[1] + dy)
    if grid.is_walkable(*nxt):
        return nxt, True
    return pos, False

def _final_position_violates_constraint(end_pos, opponents, role):

    if role == "runner":
        return end_pos in opponents
    return False

def _bfs_distance_map(start, grid):

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

def _score_plan(start_pos, plan, grid, opponents, role, dist_map=None):

    pos = start_pos
    for d in plan:
        pos, _ = _apply_dir(pos, d, grid)

    if dist_map is not None:
        dist = dist_map.get(pos)
        if dist is None:
            dist = grid.width * grid.height  # khong toi duoc tu doi thu -> rat xa
    else:
        nearest = min(opponents, key=lambda o: manhattan(pos, o))
        dist = manhattan(pos, nearest)

    return dist if role == "runner" else -dist

# ----------------------------------------------------------------------------
# BACKTRACKING SEARCH
# ----------------------------------------------------------------------------
def _backtracking_search(start_pos, grid, opponents, role, plan_length, rng, dist_map=None):

    solutions = []

    def backtrack(depth, pos, plan):
        if depth == plan_length:
            if not _final_position_violates_constraint(pos, opponents, role):
                solutions.append(list(plan))
            return

        order = list(range(4))
        rng.shuffle(order)
        for dir_code in order:
            new_pos, ok = _apply_dir(pos, dir_code, grid)
            if not ok:
                continue  # vi pham rang buoc 1 -> thu gia tri khac (quay lui ngay)
            plan.append(dir_code)
            backtrack(depth + 1, new_pos, plan)
            plan.pop()  # QUAY LUI: go bo gia tri da gan, thu huong khac

    backtrack(0, start_pos, [])

    if not solutions:
        return None
    best_plan = max(solutions, key=lambda p: _score_plan(start_pos, p, grid, opponents, role, dist_map))
    return best_plan

def backtracking_decide(agent_pos, targets, grid, role, rng=None, **kwargs):
    rng = rng or random
    if not targets:
        return agent_pos

    nearest_opponent = min(targets, key=lambda t: manhattan(agent_pos, t))
    dist_map = _bfs_distance_map(nearest_opponent, grid)

    best_plan = _backtracking_search(agent_pos, grid, targets, role, CSP_PLAN_LENGTH, rng, dist_map)
    if not best_plan:
        return agent_pos

    new_pos, ok = _apply_dir(agent_pos, best_plan[0], grid)
    return new_pos if ok else agent_pos

# ----------------------------------------------------------------------------
# FORWARD CHECKING
# ----------------------------------------------------------------------------
def _forward_checking_search(start_pos, grid, opponents, role, plan_length, rng, dist_map=None):

    solutions = []

    def domain_of(pos):

        return [d for d in range(4) if _apply_dir(pos, d, grid)[1]]

    def forward_check(depth, pos, plan):
        if depth == plan_length:
            if not _final_position_violates_constraint(pos, opponents, role):
                solutions.append(list(plan))
            return

        order = domain_of(pos)  # mien gia tri HIEN TAI (da loai huong vi pham rang buoc 1)
        rng.shuffle(order)
        for dir_code in order:
            new_pos, ok = _apply_dir(pos, dir_code, grid)
            if not ok:
                continue

            # FORWARD CHECKING: nhin truoc 1 buoc - neu day chua phai buoc
            # cuoi va vi tri moi KHONG CON huong di hop le nao (mien gia tri
            # cua bien tiep theo rong), nhanh nay chac chan thatbai du co di
            # sau hay khong -> cat tia ngay.
            if depth + 1 < plan_length:
                next_domain = domain_of(new_pos)
                if not next_domain:
                    continue  # domain wipeout - bo qua nhanh nay ngay lap tuc

            plan.append(dir_code)
            forward_check(depth + 1, new_pos, plan)
            plan.pop()

    forward_check(0, start_pos, [])

    if not solutions:
        return None
    best_plan = max(solutions, key=lambda p: _score_plan(start_pos, p, grid, opponents, role, dist_map))
    return best_plan

def forward_checking_decide(agent_pos, targets, grid, role, rng=None, **kwargs):
    rng = rng or random
    if not targets:
        return agent_pos

    nearest_opponent = min(targets, key=lambda t: manhattan(agent_pos, t))
    dist_map = _bfs_distance_map(nearest_opponent, grid)

    best_plan = _forward_checking_search(agent_pos, grid, targets, role, CSP_PLAN_LENGTH, rng, dist_map)
    if not best_plan:
        return agent_pos

    new_pos, ok = _apply_dir(agent_pos, best_plan[0], grid)
    return new_pos if ok else agent_pos
