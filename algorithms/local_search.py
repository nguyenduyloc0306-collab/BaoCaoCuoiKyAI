
import random
from utils import get_neighbors, manhattan
import config

def _simulate_plan(start, plan, grid):

    pos = start
    path = [pos]
    for nxt in plan:
        if nxt in get_neighbors(pos, grid):
            pos = nxt
        # neu buoc khong hop le (vi du do random sinh tu vi tri cu), giu nguyen
        path.append(pos)
    return pos, path

def _random_plan(start, grid, length, rng):

    plan = []
    pos = start
    for _ in range(length):
        neighbors = get_neighbors(pos, grid)
        if not neighbors:
            plan.append(pos)
            continue
        nxt = rng.choice(neighbors)
        plan.append(nxt)
        pos = nxt
    return plan

def _mutate_plan(start, plan, grid, rng):

    if not plan:
        return plan
    idx = rng.randrange(len(plan))
    new_plan = plan[:idx]
    # vi tri truoc buoc bi thay doi
    pos, _ = _simulate_plan(start, new_plan, grid)
    neighbors = get_neighbors(pos, grid)
    if neighbors:
        new_plan.append(rng.choice(neighbors))
    else:
        new_plan.append(pos)
    # giu phan con lai tu vi tri moi, mo phong tiep voi cac lua chon ngau nhien
    pos2 = new_plan[-1]
    for _ in range(len(plan) - len(new_plan)):
        nb = get_neighbors(pos2, grid)
        if not nb:
            new_plan.append(pos2)
            continue
        nxt = rng.choice(nb)
        new_plan.append(nxt)
        pos2 = nxt
    return new_plan

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

def _fitness(start, plan, grid, opponents, role, dist_map=None):

    end_pos, _ = _simulate_plan(start, plan, grid)
    if not opponents:
        return 0

    if dist_map is not None:
        # khoang cach THUC (qua duong di, co tinh vat can) toi doi thu gan
        # nhat - tranh bi vat can "lua" giong khi dung Manhattan thuan, vi
        # mot vi tri co the nhin "xa" theo duong chim bay nhung thuc te phai
        # di vong rat xa (hoac khong the toi) do bi vat can chan.
        d = dist_map.get(end_pos)
        if d is None:
            # end_pos khong nam trong vung BFS toi duoc tu doi thu (bi vat
            # can ngan cach hoan toan) -> coi nhu rat xa/rat gan tuy vai tro
            d = grid.width * grid.height  # gia tri lon, coi nhu "vo cung xa"
    else:
        nearest = min(opponents, key=lambda o: manhattan(end_pos, o))
        d = manhattan(end_pos, nearest)

    if role == "hunter":
        return -d   # hunter muon d nho -> fitness cao khi -d lon (d nho)
    else:
        return d    # runner muon d lon

# ----------------------------------------------------------------------------
# Hill Climbing (voi random-restart de tranh ket o local optimum)
# ----------------------------------------------------------------------------
def hill_climbing_decide(agent_pos, targets, grid, role, rng=None, **kwargs):
    rng = rng or random
    if not targets:
        return agent_pos

    nearest_opponent = min(targets, key=lambda t: manhattan(agent_pos, t))
    dist_map = _bfs_distance_map(nearest_opponent, grid)

    plan_length = 5
    best_plan = None
    best_score = float("-inf")

    for _ in range(config.HC_RESTARTS):
        current_plan = _random_plan(agent_pos, grid, plan_length, rng)
        current_score = _fitness(agent_pos, current_plan, grid, targets, role, dist_map)

        improved = True
        steps = 0
        while improved and steps < 30:
            improved = False
            steps += 1
            neighbor_plan = _mutate_plan(agent_pos, current_plan, grid, rng)
            neighbor_score = _fitness(agent_pos, neighbor_plan, grid, targets, role, dist_map)
            if neighbor_score > current_score:
                current_plan = neighbor_plan
                current_score = neighbor_score
                improved = True

        if current_score > best_score:
            best_score = current_score
            best_plan = current_plan

    if not best_plan:
        return agent_pos
    first_step = best_plan[0]
    if first_step in get_neighbors(agent_pos, grid):
        return first_step
    return agent_pos

# ----------------------------------------------------------------------------
# Local Beam Search
# ----------------------------------------------------------------------------
def local_beam_search_decide(agent_pos, targets, grid, role, rng=None, **kwargs):
    rng = rng or random
    if not targets:
        return agent_pos

    nearest_opponent = min(targets, key=lambda t: manhattan(agent_pos, t))
    dist_map = _bfs_distance_map(nearest_opponent, grid)

    plan_length = 5
    beam_width = config.LOCAL_BEAM_WIDTH
    n_iterations = config.LOCAL_BEAM_ITERATIONS

    # khoi tao k trang thai (ke hoach) ngau nhien - day la "beam" ban dau
    beam = [_random_plan(agent_pos, grid, plan_length, rng) for _ in range(beam_width)]

    best_plan = max(beam, key=lambda p: _fitness(agent_pos, p, grid, targets, role, dist_map))
    best_score = _fitness(agent_pos, best_plan, grid, targets, role, dist_map)

    for _ in range(n_iterations):
        # sinh hang xom cho TAT CA k trang thai trong beam hien tai, gop
        # chung vao 1 tap ung vien lon (khong tach rieng tung "lan" nhu
        # chay nhieu Hill Climbing doc lap)
        candidates = []
        for plan in beam:
            for _ in range(3):  # vai lang gieng cho moi trang thai trong beam
                candidates.append(_mutate_plan(agent_pos, plan, grid, rng))
        candidates.extend(beam)  # giu lai beam cu trong tap ung vien (elitism nhe)

        scored = [
            (p, _fitness(agent_pos, p, grid, targets, role, dist_map))
            for p in candidates
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)

        # CHON LAI k trang thai TOT NHAT trong TOAN BO tap ung vien gop chung
        # (dac trung cot loi cua Local Beam Search, khac Hill Climbing nhieu
        # lan doc lap: cac "tia" beam co the cung hoi tu vao 1 vung tot nhat)
        beam = [p for p, _ in scored[:beam_width]]

        if scored[0][1] > best_score:
            best_score = scored[0][1]
            best_plan = scored[0][0]

    first_step = best_plan[0]
    if first_step in get_neighbors(agent_pos, grid):
        return first_step
    return agent_pos
