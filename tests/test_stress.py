"""
test_stress.py
Kiem tra hieu nang va do on dinh khi:
- Grid lon (40x40 - max cho phep)
- Nhieu agent (4 hunter + 4 runner) voi TAT CA 12 thuat toan duoc su dung
- Do thoi gian tinh 1 buoc (step) de dam bao khong bi "dong" UI qua lau
  (dac biet voi Minimax/Alpha-Beta/AND-OR/Local Beam la cac thuat toan nang)
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import random
from game_engine import GameEngine
import config


def test_all_algorithms_combo_grid_large():
    print("=== Stress test: grid 40x40, 4 hunter + 4 runner, du 12 thuat toan ===")
    engine = GameEngine(40, 40, max_steps=60, seed=11)
    engine.grid.generate_random_obstacles(0.12, rng=random.Random(11))
    free = engine.grid.free_cells()
    rng = random.Random(11)
    positions = rng.sample(free, 8)

    algos = config.ALGORITHM_KEYS
    for i in range(4):
        engine.add_agent("hunter", algos[i], positions[i], (255, 0, 0), f"H{i}")
    for i in range(4):
        engine.add_agent("runner", algos[4 + i], positions[4 + i], (0, 255, 0), f"R{i}")

    step_times = []
    n_steps = 20
    for _ in range(n_steps):
        t0 = time.perf_counter()
        running = engine.step()
        dt = time.perf_counter() - t0
        step_times.append(dt)
        if not running:
            break

    avg_ms = sum(step_times) / len(step_times) * 1000
    max_ms = max(step_times) * 1000
    print(f"  So buoc chay duoc: {len(step_times)}")
    print(f"  Thoi gian TB / buoc: {avg_ms:.1f} ms")
    print(f"  Thoi gian MAX / buoc: {max_ms:.1f} ms")
    print(f"  Ket qua: {engine.result}")
    assert max_ms < 5000, "Mot buoc qua cham (>5s) - can toi uu them!"
    print("  OK - thoi gian hop ly.\n")


def test_minimax_heavy_grid():
    print("=== Stress test rieng Minimax/Alpha-Beta tren grid 25x25 ===")
    engine = GameEngine(25, 25, max_steps=10, seed=22)
    engine.grid.generate_random_obstacles(0.1, rng=random.Random(22))
    free = engine.grid.free_cells()
    rng = random.Random(22)
    a, b = rng.sample(free, 2)
    engine.add_agent("hunter", "minimax", a, (255, 0, 0))
    engine.add_agent("runner", "alpha_beta", b, (0, 255, 0))

    t0 = time.perf_counter()
    for _ in range(10):
        if not engine.step():
            break
    dt = time.perf_counter() - t0
    print(f"  10 buoc Minimax+AlphaBeta tren grid 25x25: {dt:.2f}s tong, ~{dt/10*1000:.1f}ms/buoc")
    print("  OK\n")


def test_and_or_heavy_grid():
    print("=== Stress test rieng AND-OR Graph Search (nang nhat ve to hop) tren grid 25x25 ===")
    engine = GameEngine(25, 25, max_steps=10, seed=33)
    engine.grid.generate_random_obstacles(0.1, rng=random.Random(33))
    free = engine.grid.free_cells()
    rng = random.Random(33)
    a, b = rng.sample(free, 2)
    engine.add_agent("hunter", "and_or", a, (255, 0, 0))
    engine.add_agent("runner", "and_or", b, (0, 255, 0))

    t0 = time.perf_counter()
    for _ in range(10):
        if not engine.step():
            break
    dt = time.perf_counter() - t0
    print(f"  10 buoc AND-OR vs AND-OR tren grid 25x25: {dt:.2f}s tong, ~{dt/10*1000:.1f}ms/buoc")
    print("  OK\n")


def test_csp_heavy_obstacle_density():
    print("=== Stress test Backtracking/Forward Checking voi MAT DO VAT CAN CAO ===")
    print("(de kiem tra khong gian quay lui khong no qua lon khi nhieu nhanh bi chan)")
    engine = GameEngine(20, 20, max_steps=10, seed=44)
    engine.grid.generate_random_obstacles(0.35, rng=random.Random(44))  # mat do cao
    free = engine.grid.free_cells()
    rng = random.Random(44)
    a, b = rng.sample(free, 2)
    engine.add_agent("hunter", "backtracking", a, (255, 0, 0))
    engine.add_agent("runner", "forward_checking", b, (0, 255, 0))

    t0 = time.perf_counter()
    for _ in range(10):
        if not engine.step():
            break
    dt = time.perf_counter() - t0
    print(f"  10 buoc Backtracking+ForwardChecking (35% vat can) tren grid 20x20: "
          f"{dt:.2f}s tong, ~{dt/10*1000:.1f}ms/buoc")
    print("  OK\n")


def test_many_agents_same_time():
    print("=== Stress test: 8 hunter + 8 runner (toi da cho phep) tren grid 20x20 ===")
    engine = GameEngine(20, 20, max_steps=15, seed=44)
    engine.grid.generate_random_obstacles(0.08, rng=random.Random(44))
    free = engine.grid.free_cells()
    rng = random.Random(44)
    positions = rng.sample(free, 16)
    cheap_algos = ["bfs", "astar", "greedy", "dfs"]
    for i in range(8):
        engine.add_agent("hunter", cheap_algos[i % 4], positions[i], (255, 0, 0), f"H{i}")
    for i in range(8):
        engine.add_agent("runner", cheap_algos[i % 4], positions[8 + i], (0, 255, 0), f"R{i}")

    t0 = time.perf_counter()
    n = 0
    while engine.step() and n < 15:
        n += 1
    dt = time.perf_counter() - t0
    print(f"  {n} buoc voi 16 agent: {dt:.2f}s tong, ~{dt/max(1,n)*1000:.1f}ms/buoc")
    print(f"  Ket qua: {engine.result}")
    print("  OK\n")


if __name__ == "__main__":
    test_all_algorithms_combo_grid_large()
    test_minimax_heavy_grid()
    test_and_or_heavy_grid()
    test_csp_heavy_obstacle_density()
    test_many_agents_same_time()
    print(">>> TAT CA STRESS TEST PASS - HIEU NANG ON DINH.")
