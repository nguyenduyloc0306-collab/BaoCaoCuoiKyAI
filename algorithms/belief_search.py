
import random
from utils import get_neighbors, manhattan
import config

SENSORLESS_HORIZON = 6     # so buoc "khong quan sat" toi da truoc khi gia dinh lai
AND_OR_DEPTH = 3           # do sau cay AND-OR (so cap OR-AND luan phien)

# ----------------------------------------------------------------------------
# SENSORLESS SEARCH
# ----------------------------------------------------------------------------
def _expand_belief_state(belief_state, grid, steps=1):

    current = set(belief_state)
    for _ in range(steps):
        nxt = set(current)
        for pos in current:
            nxt.add(pos)  # doi phuong co the dung yen
            for n in get_neighbors(pos, grid):
                nxt.add(n)
        current = nxt
    return current

def get_belief_state_for_display(targets, grid, belief_age=2):

    if not targets:
        return set()
    initial_belief = set(targets)
    return _expand_belief_state(initial_belief, grid, steps=min(belief_age, SENSORLESS_HORIZON))

def get_and_or_reachable_zone(opp_pos, grid, depth=None):

    if depth is None:
        depth = AND_OR_DEPTH
    dist_map = {opp_pos: 0}
    frontier = [opp_pos]
    for d in range(1, depth + 1):
        next_frontier = []
        for pos in frontier:
            for n in get_neighbors(pos, grid):
                if n not in dist_map:
                    dist_map[n] = d
                    next_frontier.append(n)
        frontier = next_frontier
    return dist_map

def sensorless_decide(agent_pos, targets, grid, role, rng=None, belief_age=2, **kwargs):

    rng = rng or random
    if not targets:
        return agent_pos

    # belief state ban dau: gia dinh doi phuong dang o quanh vi tri quan sat
    # duoc cach day `belief_age` buoc (mo phong "mat dau" doi phuong tu do)
    initial_belief = set(targets)
    belief_state = _expand_belief_state(initial_belief, grid, steps=min(belief_age, SENSORLESS_HORIZON))

    neighbors = get_neighbors(agent_pos, grid, shuffle=True)
    if not neighbors:
        return agent_pos

    def worst_case_value(candidate_pos):

        nearest_in_belief = min(belief_state, key=lambda b: manhattan(candidate_pos, b))
        d = manhattan(candidate_pos, nearest_in_belief)
        return d if role == "runner" else -d

    best = max(neighbors, key=worst_case_value)
    return best

# ----------------------------------------------------------------------------
# AND-OR GRAPH SEARCH
# ----------------------------------------------------------------------------
def _and_or_value(self_pos, opp_pos, role, depth, grid):

    if depth == 0 or self_pos == opp_pos:
        d = manhattan(self_pos, opp_pos)
        return d if role == "runner" else -d

    # OR-node: self chon huong di tot nhat
    or_moves = get_neighbors(self_pos, grid) or [self_pos]
    or_value = float("-inf")
    for m in or_moves:
        # AND-node: doi phuong "khong xac dinh" co the di toi bat ky lan can
        and_moves = get_neighbors(opp_pos, grid) or [opp_pos]
        and_value = float("inf")
        for opp_m in and_moves:
            val = _and_or_value(m, opp_m, role, depth - 1, grid)
            and_value = min(and_value, val)
        or_value = max(or_value, and_value)

    return or_value

def and_or_decide(agent_pos, targets, grid, role, rng=None, **kwargs):
    rng = rng or random
    if not targets:
        return agent_pos

    opp = min(targets, key=lambda t: manhattan(agent_pos, t))

    moves = get_neighbors(agent_pos, grid, shuffle=True)
    if not moves:
        return agent_pos

    best_move = agent_pos
    best_value = float("-inf")
    for m in moves:
        val = _and_or_value(m, opp, role, AND_OR_DEPTH, grid)
        if val > best_value:
            best_value = val
            best_move = m

    return best_move
