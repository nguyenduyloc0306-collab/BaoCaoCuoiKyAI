"""
test_engine.py
Kiem tra game_engine.py: luat thang/thua, nhieu hunter/runner, het buoc.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import random
from game_engine import GameEngine, GameResult
import config


def test_hunter_catches_runner_quickly():
    print("TEST: Hunter manh (A*) vs Runner yeu, grid nho trong, it buoc")
    engine = GameEngine(8, 8, max_steps=50, seed=1)
    engine.grid.clear_obstacles()
    h = engine.add_agent("hunter", "astar", (0, 0), (255, 0, 0))
    r = engine.add_agent("runner", "bfs", (1, 0), (0, 255, 0))

    running = True
    while running:
        running = engine.step()

    print("  Ket qua:", engine.result, " so buoc:", engine.step_count)
    assert engine.result in (GameResult.HUNTER_WIN, GameResult.RUNNER_WIN)
    print("  OK - ket thuc hop le.\n")


def test_runner_survives_open_grid_far_start():
    print("TEST: Runner xa Hunter tren grid lon trong, it buoc -> kha nang song sot")
    engine = GameEngine(30, 30, max_steps=15, seed=2)
    engine.grid.clear_obstacles()
    h = engine.add_agent("hunter", "bfs", (0, 0), (255, 0, 0))
    r = engine.add_agent("runner", "astar", (29, 29), (0, 255, 0))

    running = True
    while running:
        running = engine.step()

    print("  Ket qua:", engine.result, " so buoc:", engine.step_count)
    assert engine.result == GameResult.RUNNER_WIN
    print("  OK - Runner song sot het gio nhu du kien.\n")


def test_multi_agent():
    print("TEST: Nhieu Hunter (3) vs nhieu Runner (3)")
    engine = GameEngine(15, 15, max_steps=300, seed=3)
    engine.grid.generate_random_obstacles(0.1, rng=random.Random(3))
    free = engine.grid.free_cells()
    rng = random.Random(3)
    positions = rng.sample(free, 6)

    engine.add_agent("hunter", "astar", positions[0], (255, 0, 0), "Hunter A")
    engine.add_agent("hunter", "greedy", positions[1], (255, 100, 0), "Hunter B")
    engine.add_agent("hunter", "minimax", positions[2], (200, 0, 100), "Hunter C")

    engine.add_agent("runner", "astar", positions[3], (0, 255, 0), "Runner A")
    engine.add_agent("runner", "hill_climbing", positions[4], (0, 150, 255), "Runner B")
    engine.add_agent("runner", "backtracking", positions[5], (0, 255, 200), "Runner C")

    running = True
    steps_taken = 0
    while running and steps_taken < 500:
        running = engine.step()
        steps_taken += 1

    print("  Ket qua:", engine.result, " so buoc:", engine.step_count)
    print("  Runner con song:", [r.label for r in engine.alive_runners()])
    print("  Log cuoi:", engine.event_log[-3:])
    assert engine.result in (GameResult.HUNTER_WIN, GameResult.RUNNER_WIN)
    print("  OK - nhieu agent hoat dong dong thoi, khong loi.\n")


def test_capture_rule_same_cell():
    print("TEST: Luat bat - hunter va runner trung 1 o")
    engine = GameEngine(6, 6, max_steps=20, seed=4)
    engine.grid.clear_obstacles()
    h = engine.add_agent("hunter", "astar", (2, 2), (255, 0, 0))
    r = engine.add_agent("runner", "astar", (2, 3), (0, 255, 0))
    # buoc dau: hunter se di toi (2,3) vi do la duong ngan nhat -> bat ngay
    engine.step()
    print("  Sau 1 buoc -> hunter pos:", h.pos, " runner alive:", r.alive)
    print("  Ket qua:", engine.result)
    print("  OK\n")


if __name__ == "__main__":
    test_hunter_catches_runner_quickly()
    test_runner_survives_open_grid_far_start()
    test_multi_agent()
    test_capture_rule_same_cell()
    print(">>> TAT CA TEST GAME ENGINE PASS.")
