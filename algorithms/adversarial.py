
import random
from collections import deque
from utils import get_neighbors, manhattan
import config

def _nearest(pos, others):
    if not others:
        return None
    return min(others, key=lambda o: manhattan(pos, o))

def _bfs_distance_map(start, grid):

    dist = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in get_neighbors(current, grid):
            if nxt not in dist:
                dist[nxt] = dist[current] + 1
                queue.append(nxt)
    return dist

def _self_value(self_pos, opp_pos, role, dist_map=None):

    if dist_map is not None and self_pos in dist_map:
        d = dist_map[self_pos]
    else:
        d = manhattan(self_pos, opp_pos)

    if role == "runner":
        return d
    else:
        return -d

def _minimax(self_pos, opp_pos, role, depth, maximizing_self_turn, grid, dist_map):

    if depth == 0 or self_pos == opp_pos:
        return _self_value(self_pos, opp_pos, role, dist_map)

    if maximizing_self_turn:
        best = float("-inf")
        moves = get_neighbors(self_pos, grid) or [self_pos]
        for m in moves:
            val = _minimax(m, opp_pos, role, depth - 1, False, grid, dist_map)
            best = max(best, val)
        return best
    else:
        worst = float("inf")
        moves = get_neighbors(opp_pos, grid) or [opp_pos]
        for m in moves:
            val = _minimax(self_pos, m, role, depth - 1, True, grid, dist_map)
            worst = min(worst, val)
        return worst

def minimax_decide(agent_pos, targets, grid, role, rng=None, **kwargs):
    rng = rng or random
    opp = _nearest(agent_pos, targets)
    if opp is None:
        return agent_pos

    moves = get_neighbors(agent_pos, grid, shuffle=True)
    if not moves:
        return agent_pos

    # ban do khoang cach thuc (co tinh vat can), tinh 1 lan tu vi tri doi
    # thu HIEN TAI truoc khi duyet cay - dung lam uoc luong tai cac nut la
    dist_map = _bfs_distance_map(opp, grid)

    best_move = agent_pos
    best_value = float("-inf")
    depth = max(2, config.MINIMAX_DEPTH - 1)  # tru 1 vi da xet 1 lop o day

    for m in moves:
        val = _minimax(m, opp, role, depth, False, grid, dist_map)
        if val > best_value:
            best_value = val
            best_move = m

    return best_move

# ----------------------------------------------------------------------------
# Alpha-Beta Pruning - giong Minimax nhung cat nhanh khong can thiet
# ----------------------------------------------------------------------------
def _alpha_beta(self_pos, opp_pos, role, depth, alpha, beta, maximizing_self_turn, grid, dist_map):
    if depth == 0 or self_pos == opp_pos:
        return _self_value(self_pos, opp_pos, role, dist_map)

    if maximizing_self_turn:
        value = float("-inf")
        moves = get_neighbors(self_pos, grid) or [self_pos]
        for m in moves:
            value = max(value, _alpha_beta(m, opp_pos, role, depth - 1, alpha, beta, False, grid, dist_map))
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # beta cutoff
        return value
    else:
        value = float("inf")
        moves = get_neighbors(opp_pos, grid) or [opp_pos]
        for m in moves:
            value = min(value, _alpha_beta(self_pos, m, role, depth - 1, alpha, beta, True, grid, dist_map))
            beta = min(beta, value)
            if alpha >= beta:
                break  # alpha cutoff
        return value

def alpha_beta_decide(agent_pos, targets, grid, role, rng=None, **kwargs):
    rng = rng or random
    opp = _nearest(agent_pos, targets)
    if opp is None:
        return agent_pos

    moves = get_neighbors(agent_pos, grid, shuffle=True)
    if not moves:
        return agent_pos

    dist_map = _bfs_distance_map(opp, grid)

    best_move = agent_pos
    best_value = float("-inf")
    depth = max(2, config.ALPHA_BETA_DEPTH - 1)

    alpha, beta = float("-inf"), float("inf")
    for m in moves:
        val = _alpha_beta(m, opp, role, depth, alpha, beta, False, grid, dist_map)
        if val > best_value:
            best_value = val
            best_move = m
        alpha = max(alpha, best_value)

    return best_move
