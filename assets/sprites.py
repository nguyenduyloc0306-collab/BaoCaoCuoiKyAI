import os
import pygame

_ASSET_DIR = os.path.dirname(os.path.abspath(__file__))

# ── raw cache: path -> Surface (loaded once, original size) ──────────────────
_raw = {}

# ── scaled cache: (path, size) -> Surface ────────────────────────────────────
_scaled = {}


def _load_raw(rel_path):
    if rel_path not in _raw:
        full = os.path.join(_ASSET_DIR, rel_path)
        try:
            surf = pygame.image.load(full).convert_alpha()
        except Exception:
            surf = None
        _raw[rel_path] = surf
    return _raw[rel_path]


def get(rel_path, size):
    key = (rel_path, size)
    if key not in _scaled:
        raw = _load_raw(rel_path)
        if raw is None:
            _scaled[key] = None
        else:
            _scaled[key] = pygame.transform.smoothscale(raw, (size, size))
    return _scaled[key]


def invalidate_cache():
    _scaled.clear()


# ── Floor / obstacle names (relative to assets/) ─────────────────────────────
FLOOR_NAMES    = ["Floors/walls_floor 2.png", "Floors/walls_floor.png"]
OBSTACLE_NAMES = ["Obstacles/obstacle.png", "Obstacles/obstacle 2.png", "Obstacles/obstacle 3.png"]

# ── Wall / corner names (relative to assets/) ────────────────────────────────
# Keys match the logical position on the border.
WALL_NAMES = {
    "top":          "Walls/upper wall.png",
    "bottom":       "Walls/down wall.png",
    "left":         "Walls/left wall.png",
    "right":        "Walls/right wall.png",
    "top_left":     "Walls/left up corner wall.png",
    "top_right":    "Walls/right up corner wall.png",
    "bottom_left":  "Walls/left down corner wall.png",
    "bottom_right": "Walls/right down corner wall.png",
}


# ── Hunter animation frames ───────────────────────────────────────────────────
# Structure: HUNTER_FRAMES[anim][direction] = [rel_path, ...]
# anim      : "run" | "attack"
# direction : "up" | "down" | "left" | "right"
# frames are ordered 1..4

def _hunter_frames(anim, direction, count=4):
    folder = os.path.join("Hunter", f"{anim} animations", f"{anim} {direction}")
    return [os.path.join(folder, f"{anim} {direction} {i}.png") for i in range(1, count + 1)]


HUNTER_FRAMES = {
    "run": {
        "up":    _hunter_frames("run", "up"),
        "down":  _hunter_frames("run", "down"),
        "left":  _hunter_frames("run", "left"),
        "right": _hunter_frames("run", "right"),
    },
    "attack": {
        "up":    _hunter_frames("attack", "up"),
        "down":  _hunter_frames("attack", "down"),
        "left":  _hunter_frames("attack", "left"),
        "right": _hunter_frames("attack", "right"),
    },
}


def get_hunter_frame(anim, direction, frame_index, size):
    paths = HUNTER_FRAMES.get(anim, {}).get(direction)
    if not paths:
        return None
    path = paths[frame_index % len(paths)]
    return get(path, size)


# ── Runner animation frames ───────────────────────────────────────────────────
def _runner_frames(anim, direction, count=4):
    folder = os.path.join("Runner", f"{anim} animations", f"{anim} {direction}")
    return [os.path.join(folder, f"{anim} {direction} {i}.png") for i in range(1, count + 1)]


RUNNER_FRAMES = {
    "run": {
        "up":    _runner_frames("run", "up"),
        "down":  _runner_frames("run", "down"),
        "left":  _runner_frames("run", "left"),
        "right": _runner_frames("run", "right"),
    },
    "death": {
        "up":    _runner_frames("death", "up"),
        "down":  _runner_frames("death", "down"),
        "left":  _runner_frames("death", "left"),
        "right": _runner_frames("death", "right"),
    },
}


def get_runner_frame(anim, direction, frame_index, size):
    paths = RUNNER_FRAMES.get(anim, {}).get(direction)
    if not paths:
        return None
    # death plays once — clamp to last frame rather than looping
    if anim == "death":
        idx = min(frame_index, len(paths) - 1)
    else:
        idx = frame_index % len(paths)
    return get(paths[idx], size)
