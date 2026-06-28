
from algorithms import get_decision_function

# Animation constants
ANIM_RUN    = "run"
ANIM_ATTACK = "attack"
ANIM_DEATH  = "death"
ANIM_FRAMES = 4          # frames per animation cycle
ANIM_FPS    = 10         # frames per second for the animation playback


class Agent:

    _next_id = 1

    def __init__(self, role, algo_key, pos, color, label=None):
        self.role = role
        self.algo_key = algo_key
        self.pos = pos
        self.start_pos = pos
        self.color = color
        self.label = label or f"{role.capitalize()} {Agent._next_id}"
        self.id = Agent._next_id
        Agent._next_id += 1
        self.alive = True
        self.dying = False           # True = caught but waiting for attack anim
        self._killing_hunter_id = None
        self.trail = [pos]
        self.last_decision_time_ms = 0.0
        self.visual_overlay = {"type": None, "cells": set()}

        # ── animation state ──────────────────────────────────────────────────
        self.anim         = ANIM_RUN   # current animation clip
        self.anim_dir     = "down"     # "up" | "down" | "left" | "right"
        self.anim_frame   = 0          # 0..ANIM_FRAMES-1
        self.anim_timer   = 0.0        # accumulated ms since last frame advance
        self._attack_done = False      # True once attack clip has finished once
        self._death_done  = False      # True once death clip has finished once

    def reset(self, pos):
        self.pos = pos
        self.start_pos = pos
        self.alive = True
        self.dying = False
        self._killing_hunter_id = None
        self.trail = [pos]
        self.last_decision_time_ms = 0.0
        self.visual_overlay = {"type": None, "cells": set()}
        self.anim         = ANIM_RUN
        self.anim_dir     = "down"
        self.anim_frame   = 0
        self.anim_timer   = 0.0
        self._attack_done = False
        self._death_done  = False

    # ── animation helpers ────────────────────────────────────────────────────
    def _direction_from_move(self, old_pos, new_pos):
        dx = new_pos[0] - old_pos[0]
        dy = new_pos[1] - old_pos[1]
        if dx > 0:
            return "right"
        if dx < 0:
            return "left"
        if dy > 0:
            return "down"
        if dy < 0:
            return "up"
        return self.anim_dir   # didn't move — keep current

    def trigger_attack(self, target_pos):
        self.anim         = ANIM_ATTACK
        self.anim_dir     = self._direction_from_move(self.pos, target_pos)
        self.anim_frame   = 0
        self.anim_timer   = 0.0
        self._attack_done = False

    def trigger_death(self):
        self.anim         = ANIM_DEATH
        self.anim_frame   = 0
        self.anim_timer   = 0.0
        self._death_done  = False

    def tick_animation(self, dt_ms):
        ms_per_frame = 1000.0 / ANIM_FPS
        self.anim_timer += dt_ms
        if self.anim_timer >= ms_per_frame:
            self.anim_timer -= ms_per_frame
            self.anim_frame += 1
            if self.anim_frame >= ANIM_FRAMES:
                if self.anim == ANIM_ATTACK:
                    self._attack_done = True
                    self.anim       = ANIM_RUN
                    self.anim_frame = 0
                elif self.anim == ANIM_DEATH:
                    # Hold on last frame — _resolve_dying_runners will clear
                    self._death_done = True
                    self.anim_frame  = ANIM_FRAMES - 1
                else:
                    self.anim_frame = 0   # run loops

    # ── core logic ───────────────────────────────────────────────────────────
    def decide_next_position(self, opponents_positions, grid, rng=None):
        func = get_decision_function(self.algo_key)
        result = func(self.pos, opponents_positions, grid, self.role, rng=rng)

        if self.algo_key == "sensorless":
            from algorithms.belief_search import get_belief_state_for_display
            cells = get_belief_state_for_display(opponents_positions, grid, belief_age=2)
            self.visual_overlay = {"type": "belief", "cells": cells}
        elif self.algo_key == "and_or":
            from algorithms.belief_search import get_and_or_reachable_zone
            if opponents_positions:
                nearest = min(opponents_positions,
                              key=lambda o: abs(o[0]-self.pos[0])+abs(o[1]-self.pos[1]))
                dist_map = get_and_or_reachable_zone(nearest, grid)
            else:
                dist_map = {}
            self.visual_overlay = {"type": "reachable_zone", "cells": dist_map}
        else:
            self.visual_overlay = {"type": None, "cells": set()}

        return result

    def move_to(self, new_pos):
        if new_pos != self.pos and self.anim != ANIM_ATTACK:
            self.anim_dir = self._direction_from_move(self.pos, new_pos)
            self.anim     = ANIM_RUN
        self.pos = new_pos
        self.trail.append(new_pos)
        if len(self.trail) > 200:
            self.trail.pop(0)

    def __repr__(self):
        return f"<Agent {self.label} role={self.role} algo={self.algo_key} pos={self.pos}>"
