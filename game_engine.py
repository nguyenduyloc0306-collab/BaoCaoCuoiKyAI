
import random
import time

from grid import Grid
from agent import Agent
import config

class GameResult:
    ONGOING = "ongoing"
    RUNNER_WIN = "runner_win"
    HUNTER_WIN = "hunter_win"

class GameEngine:
    def __init__(self, grid_width, grid_height, max_steps=config.DEFAULT_MAX_STEPS, seed=None):
        self.grid = Grid(grid_width, grid_height)
        self.max_steps = max_steps
        self.step_count = 0
        self.agents = []          # list[Agent]
        self.result = GameResult.ONGOING
        self.rng = random.Random(seed)
        self.event_log = []       # list cac thong bao (string) de hien thi UI
        self.caught_pairs = []    # list (hunter_id, runner_id) cho hieu ung ve

    # ------------------------------------------------------------------
    def add_agent(self, role, algo_key, pos, color, label=None):
        agent = Agent(role, algo_key, pos, color, label=label)
        self.agents.append(agent)
        return agent

    def hunters(self):
        return [a for a in self.agents if a.role == "hunter"]

    def runners(self):
        return [a for a in self.agents if a.role == "runner"]

    def alive_runners(self):
        return [a for a in self.agents if a.role == "runner" and a.alive]

    # ------------------------------------------------------------------
    def log(self, message):
        timestamp = f"[Step {self.step_count}]"
        self.event_log.append(f"{timestamp} {message}")
        if len(self.event_log) > 100:
            self.event_log.pop(0)

    # ------------------------------------------------------------------
    def step(self):

        if self.result != GameResult.ONGOING:
            return False

        self.step_count += 1
        self.caught_pairs = []

        hunters = self.hunters()
        alive_runners = self.alive_runners()

        if not alive_runners:
            self.result = GameResult.HUNTER_WIN
            self.log("All runners caught. HUNTER WINS.")
            return False

        # --- Hunter di truoc (duoi theo cac Runner con song) ---
        for hunter in hunters:
            targets = [r.pos for r in alive_runners]
            t0 = time.perf_counter()
            new_pos = hunter.decide_next_position(targets, self.grid, rng=self.rng)
            hunter.last_decision_time_ms = (time.perf_counter() - t0) * 1000.0
            hunter.move_to(new_pos)

        # --- kiem tra bat sau khi hunter di chuyen ---
        self._check_captures()

        alive_runners = self.alive_runners()
        if not alive_runners:
            self.result = GameResult.HUNTER_WIN
            self.log("All runners caught. HUNTER WINS.")
            return False

        # --- Runner di (tron cac Hunter) ---
        hunter_positions = [h.pos for h in hunters]
        for runner in alive_runners:
            t0 = time.perf_counter()
            new_pos = runner.decide_next_position(hunter_positions, self.grid, rng=self.rng)
            runner.last_decision_time_ms = (time.perf_counter() - t0) * 1000.0
            runner.move_to(new_pos)

        # --- kiem tra bat sau khi runner di chuyen ---
        self._check_captures()

        alive_runners = self.alive_runners()
        if not alive_runners:
            self.result = GameResult.HUNTER_WIN
            self.log("All runners caught. HUNTER WINS.")
            return False

        # --- kiem tra het gio ---
        if self.step_count >= self.max_steps:
            self.result = GameResult.RUNNER_WIN
            self.log(f"Reached {self.max_steps} steps. Runner survived — RUNNER WINS.")
            return False

        return True

    # ------------------------------------------------------------------
    def _check_captures(self):
        for hunter in self.hunters():
            for runner in self.alive_runners():
                if hunter.pos == runner.pos:
                    runner.alive = False
                    runner.dying = True
                    self.caught_pairs.append((hunter.id, runner.id))
                    self.log(f"{hunter.label} caught {runner.label} at {runner.pos}.")
                    if hasattr(hunter, "trigger_attack"):
                        hunter.trigger_attack(runner.pos)
                    if hasattr(runner, "trigger_death"):
                        runner.trigger_death()
                    runner._killing_hunter_id = hunter.id

    # ------------------------------------------------------------------
    def is_finished(self):
        return self.result != GameResult.ONGOING

    def progress_ratio(self):
        return min(1.0, self.step_count / max(1, self.max_steps))
