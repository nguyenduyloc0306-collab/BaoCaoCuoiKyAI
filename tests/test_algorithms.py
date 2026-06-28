"""
test_algorithms.py
Kiem tra nhanh (khong can pygame) cho dung 12 thuat toan hien tai:
BFS, DFS, Greedy, A*, Local Beam Search, Hill Climbing, Backtracking,
Forward Checking, Sensorless Search, AND-OR Graph Search, Minimax, Alpha-Beta.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import random
import time
from grid import Grid
from utils import get_neighbors, manhattan
from algorithms import ALGORITHM_FUNCS


def make_test_grid(seed=1):
    rng = random.Random(seed)
    g = Grid(12, 12)
    g.generate_random_obstacles(0.12, rng=rng)
    return g


def is_valid_move(old_pos, new_pos, grid):
    if new_pos == old_pos:
        return True
    if not grid.is_walkable(*new_pos):
        return False
    return new_pos in get_neighbors(old_pos, grid)


def run_basic_validity_tests():
    print("=" * 70)
    print("TEST 1: Tinh hop le cua nuoc di (moi thuat toan, ca 2 vai tro)")
    print("=" * 70)
    grid = make_test_grid(seed=42)
    rng = random.Random(7)

    all_ok = True
    timings = {}
    for name, func in ALGORITHM_FUNCS.items():
        t_start = time.perf_counter()
        for role in ("hunter", "runner"):
            agent_pos = (1, 1)
            targets = [(8, 8)]
            if not grid.is_walkable(*agent_pos) or not grid.is_walkable(*targets[0]):
                continue
            try:
                new_pos = func(agent_pos, targets, grid, role, rng=rng)
            except Exception as e:
                print(f"  [LOI]  {name:20s} role={role:7s} -> EXCEPTION: {e}")
                all_ok = False
                continue
            ok = is_valid_move(agent_pos, new_pos, grid)
            status = "OK " if ok else "SAI"
            if not ok:
                all_ok = False
            print(f"  [{status}] {name:20s} role={role:7s} -> {agent_pos} => {new_pos}")
        timings[name] = (time.perf_counter() - t_start) * 1000
    print()
    print("KET QUA TEST 1:", "TAT CA HOP LE" if all_ok else "CO LOI")
    print()
    print("Thoi gian tinh toan (2 vai tro, ms):")
    for name, t in sorted(timings.items(), key=lambda x: -x[1]):
        print(f"  {name:20s} {t:7.2f} ms")
    print()
    return all_ok


def run_behavior_tests(n_trials=15):
    print("=" * 70)
    print("TEST 2: Xu huong hanh vi (Hunter tien gan / Runner tron xa)")
    print("=" * 70)

    rng = random.Random(123)

    for name, func in ALGORITHM_FUNCS.items():
        hunter_correct = 0
        hunter_total = 0
        runner_correct = 0
        runner_total = 0

        for trial in range(n_trials):
            grid = make_test_grid(seed=trial)
            free = grid.free_cells()
            if len(free) < 2:
                continue
            a, b = rng.sample(free, 2)

            try:
                new_a = func(a, [b], grid, "hunter", rng=rng)
            except Exception:
                new_a = a
            old_d = manhattan(a, b)
            new_d = manhattan(new_a, b)
            hunter_total += 1
            if new_d <= old_d:
                hunter_correct += 1

            try:
                new_a2 = func(a, [b], grid, "runner", rng=rng)
            except Exception:
                new_a2 = a
            new_d2 = manhattan(new_a2, b)
            runner_total += 1
            if new_d2 >= old_d:
                runner_correct += 1

        h_pct = 100.0 * hunter_correct / max(1, hunter_total)
        r_pct = 100.0 * runner_correct / max(1, runner_total)
        print(f"  {name:20s}  Hunter dung huong: {h_pct:5.1f}%   "
              f"Runner dung huong: {r_pct:5.1f}%")
    print()


def run_capture_simulation():
    print("=" * 70)
    print("TEST 3: Mo phong 1 tran Hunter vs Runner full den khi bat duoc")
    print("hoac het 200 buoc (dung A* cho Hunter, Greedy cho Runner)")
    print("=" * 70)
    grid = make_test_grid(seed=5)
    rng = random.Random(99)

    free = grid.free_cells()
    hunter_pos, runner_pos = rng.sample(free, 2)

    hunter_func = ALGORITHM_FUNCS["astar"]
    runner_func = ALGORITHM_FUNCS["greedy"]

    max_steps = 200
    caught = False
    for step in range(1, max_steps + 1):
        hunter_pos = hunter_func(hunter_pos, [runner_pos], grid, "hunter", rng=rng)
        if hunter_pos == runner_pos:
            caught = True
            break
        runner_pos = runner_func(runner_pos, [hunter_pos], grid, "runner", rng=rng)
        if hunter_pos == runner_pos:
            caught = True
            break

    if caught:
        print(f"  Hunter bat duoc Runner sau {step} buoc.")
    else:
        print(f"  Runner SONG SOT sau {max_steps} buoc (Runner thang).")
    print()


if __name__ == "__main__":
    ok = run_basic_validity_tests()
    run_behavior_tests()
    run_capture_simulation()
    if ok:
        print(">>> TAT CA 12 THUAT TOAN HOAT DONG HOP LE (khong loi, nuoc di hop le).")
    else:
        print(">>> CO THUAT TOAN LOI - XEM LAI BEN TREN.")
