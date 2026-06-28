
import pygame
import math
import config
import assets.sprites as sprites

# Deterministic per-cell floor variant selection.
# walls_floor 2 is the majority tile (~85%), walls_floor 1 is the accent (~15%).
# Using a hash so the pattern is stable (no flicker) but looks organic.
def _floor_index(x, y):
    h = (x * 2246822519 ^ y * 3266489917) & 0xFFFFFFFF
    # ~15% chance of variant 0 (walls_floor.png), ~85% variant 1 (walls_floor 2.png)
    return 0 if (h % 100) < 15 else 1

# Deterministic obstacle variant (3 options, even split is fine for obstacles)
def _obs_index(x, y, count):
    return (x * 31 + y * 17) % count


class BoardRenderer:
    def __init__(self, board_rect, grid_width, grid_height):
        self.board_rect = pygame.Rect(board_rect)
        self.grid_width = grid_width
        self.grid_height = grid_height
        self._recompute_cell_size()
        self._pulse_t = 0.0
        self._last_cell_size = -1  # track when we need to invalidate sprite cache

    def _recompute_cell_size(self):
        cell_w = self.board_rect.width / self.grid_width
        cell_h = self.board_rect.height / self.grid_height
        self.cell_size = max(config.MIN_CELL_PX, int(min(cell_w, cell_h)))
        self.board_px_w = self.cell_size * self.grid_width
        self.board_px_h = self.cell_size * self.grid_height
        self.origin_x = self.board_rect.x + (self.board_rect.width - self.board_px_w) // 2
        self.origin_y = self.board_rect.y + (self.board_rect.height - self.board_px_h) // 2

    def set_board_rect(self, board_rect):
        self.board_rect = pygame.Rect(board_rect)
        self._recompute_cell_size()

    def set_grid_size(self, width, height):
        self.grid_width = width
        self.grid_height = height
        self._recompute_cell_size()

    # ------------------------------------------------------------------
    def cell_rect(self, x, y):
        return pygame.Rect(
            self.origin_x + x * self.cell_size,
            self.origin_y + y * self.cell_size,
            self.cell_size,
            self.cell_size,
        )

    def cell_center(self, x, y):
        r = self.cell_rect(x, y)
        return r.centerx, r.centery

    def pixel_to_cell(self, px, py):
        if not self._board_pixel_rect().collidepoint(px, py):
            return None
        cx = int((px - self.origin_x) // self.cell_size)
        cy = int((py - self.origin_y) // self.cell_size)
        if 0 <= cx < self.grid_width and 0 <= cy < self.grid_height:
            return cx, cy
        return None

    def _board_pixel_rect(self):
        return pygame.Rect(self.origin_x, self.origin_y, self.board_px_w, self.board_px_h)

    # ------------------------------------------------------------------
    def draw_background(self, surface):
        cs = self.cell_size
        floor_surfs = [sprites.get(n, cs) for n in sprites.FLOOR_NAMES]

        if not any(floor_surfs):
            pygame.draw.rect(surface, config.COLOR_GRID_CELL, self._board_pixel_rect())
            return

        for gy in range(self.grid_height):
            for gx in range(self.grid_width):
                idx = _floor_index(gx, gy)
                # clamp in case only one variant loaded
                idx = min(idx, len(floor_surfs) - 1)
                tile = floor_surfs[idx]
                if tile is None:
                    tile = next((s for s in floor_surfs if s is not None), None)
                if tile:
                    surface.blit(tile, self.cell_rect(gx, gy).topleft)
                else:
                    pygame.draw.rect(surface, config.COLOR_GRID_CELL, self.cell_rect(gx, gy))

    def draw_grid_lines(self, surface):
        if self.cell_size < 6:
            return
        for x in range(self.grid_width + 1):
            px = self.origin_x + x * self.cell_size
            pygame.draw.line(surface, config.COLOR_GRID_LINE,
                              (px, self.origin_y), (px, self.origin_y + self.board_px_h))
        for y in range(self.grid_height + 1):
            py = self.origin_y + y * self.cell_size
            pygame.draw.line(surface, config.COLOR_GRID_LINE,
                              (self.origin_x, py), (self.origin_x + self.board_px_w, py))

    def draw_obstacles(self, surface, grid):
        cs = self.cell_size
        obs_surfs = [sprites.get(n, cs) for n in sprites.OBSTACLE_NAMES]

        for gy in range(grid.height):
            for gx in range(grid.width):
                # Skip border cells — they are drawn by draw_walls()
                if grid.is_border(gx, gy):
                    continue
                if grid.is_obstacle(gx, gy):
                    r = self.cell_rect(gx, gy)
                    loaded = [s for s in obs_surfs if s is not None]
                    if loaded:
                        idx = _obs_index(gx, gy, len(loaded))
                        surface.blit(loaded[idx], r.topleft)
                    else:
                        pad = max(1, cs // 10)
                        fr = r.inflate(-pad * 2, -pad * 2)
                        pygame.draw.rect(surface, config.COLOR_OBSTACLE, fr, border_radius=3)
                        pygame.draw.rect(surface, config.COLOR_OBSTACLE_BORDER, fr,
                                         width=1, border_radius=3)

    def draw_walls(self, surface, grid):
        """Draw the border wall tiles around the entire map using cell-sized sprites."""
        cs = self.cell_size
        W  = grid.width
        H  = grid.height
        wn = sprites.WALL_NAMES

        # Pre-load all wall surfaces scaled to cell size
        surfs = {key: sprites.get(path, cs) for key, path in wn.items()}

        for gy in range(H):
            for gx in range(W):
                if not grid.is_border(gx, gy):
                    continue

                top    = (gy == 0)
                bottom = (gy == H - 1)
                left   = (gx == 0)
                right  = (gx == W - 1)

                if top and left:
                    key = "top_left"
                elif top and right:
                    key = "top_right"
                elif bottom and left:
                    key = "bottom_left"
                elif bottom and right:
                    key = "bottom_right"
                elif top:
                    key = "top"
                elif bottom:
                    key = "bottom"
                elif left:
                    key = "left"
                else:
                    key = "right"

                r    = self.cell_rect(gx, gy)
                tile = surfs.get(key)
                if tile:
                    surface.blit(tile, r.topleft)
                else:
                    pygame.draw.rect(surface, config.COLOR_OBSTACLE, r)
                    pygame.draw.rect(surface, config.COLOR_OBSTACLE_BORDER, r, width=1)

    def draw_border(self, surface):
        pygame.draw.rect(surface, config.COLOR_GRID_LINE, self._board_pixel_rect(), width=2)

    # ------------------------------------------------------------------
    def draw_trail(self, surface, agent, max_points=12):
        if len(agent.trail) < 2:
            return
        pts = agent.trail[-max_points:]
        n = len(pts)
        for i in range(n - 1):
            alpha_ratio = (i + 1) / n
            cx1, cy1 = self.cell_center(*pts[i])
            cx2, cy2 = self.cell_center(*pts[i + 1])
            color = tuple(int(c * (0.25 + 0.35 * alpha_ratio)) for c in agent.color)
            width = max(1, int(self.cell_size * 0.06))
            pygame.draw.line(surface, color, (cx1, cy1), (cx2, cy2), width)

    def draw_agent(self, surface, agent, font_small):
        # Skip runners that are fully gone (not alive AND not in dying animation)
        if agent.role == "runner" and not agent.alive and not getattr(agent, "dying", False):
            return

        cx, cy = self.cell_center(*agent.pos)
        cs = self.cell_size
        radius = max(4, int(cs * 0.36))

        if agent.role == "hunter":
            # Try to draw sprite frame — drawn larger than the cell and centred
            anim  = getattr(agent, "anim",      "run")
            direc = getattr(agent, "anim_dir",  "down")
            frame = getattr(agent, "anim_frame", 0)
            draw_size = int(cs * 1.8)   # 80% bigger than the cell
            sprite = sprites.get_hunter_frame(anim, direc, frame, draw_size)
            if sprite:
                # Centre the oversized sprite on the cell centre
                sx = cx - draw_size // 2
                sy = cy - draw_size // 2
                surface.blit(sprite, (sx, sy))
            else:
                # Fallback: diamond shape
                points = [
                    (cx, cy - radius), (cx + radius, cy),
                    (cx, cy + radius), (cx - radius, cy),
                ]
                pygame.draw.polygon(surface, agent.color, points)
                pygame.draw.polygon(surface, config.COLOR_TEXT_ACCENT, points, width=2)
        else:
            # Runner: try sprite first
            anim  = getattr(agent, "anim",      "run")
            direc = getattr(agent, "anim_dir",  "down")
            frame = getattr(agent, "anim_frame", 0)
            draw_size = int(cs * 1.8)
            sprite = sprites.get_runner_frame(anim, direc, frame, draw_size)
            if sprite:
                sx = cx - draw_size // 2
                sy = cy - draw_size // 2
                surface.blit(sprite, (sx, sy))
            else:
                pygame.draw.circle(surface, agent.color, (cx, cy), radius)
                pygame.draw.circle(surface, config.COLOR_TEXT_ACCENT, (cx, cy), radius, width=2)

        if cs >= 16:
            # Small colour dot at bottom-right corner of the cell to identify the agent
            # Size: ~18% of cell, min 4px, max 8px — visible but won't cover the sprite
            dot_r = max(3, min(5, int(cs * 0.13)))
            cell_r = self.cell_rect(*agent.pos)
            dot_cx = cell_r.right  - dot_r - 2
            dot_cy = cell_r.bottom - dot_r - 2
            # Thin dark outline so it's readable on any background
            pygame.draw.circle(surface, (0, 0, 0),        (dot_cx, dot_cy), dot_r + 1)
            pygame.draw.circle(surface, agent.color,      (dot_cx, dot_cy), dot_r)

    def draw_capture_effect(self, surface, pos, t_ratio):

        cx, cy = self.cell_center(*pos)
        max_radius = self.cell_size * 1.6
        radius = int(max_radius * t_ratio)
        alpha = max(0, int(255 * (1 - t_ratio)))
        if radius <= 0:
            return
        ring_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring_surface, (*config.COLOR_DANGER, alpha),
                            (radius + 2, radius + 2), radius, width=3)
        surface.blit(ring_surface, (cx - radius - 2, cy - radius - 2))

    def draw_all_agents(self, surface, agents, font_small, show_trail=True):
        if show_trail:
            for agent in agents:
                # Don't draw trail for dead or dying runners
                if agent.role == "runner" and (not agent.alive or getattr(agent, "dying", False)):
                    continue
                self.draw_trail(surface, agent)
        for agent in agents:
            self.draw_agent(surface, agent, font_small)

    def draw_hover_highlight(self, surface, cell):
        if cell is None:
            return
        r = self.cell_rect(*cell)
        s = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        s.fill((*config.COLOR_ACCENT, 70))
        surface.blit(s, r.topleft)

    # ------------------------------------------------------------------
    def draw_belief_overlays(self, surface, agents, font_small, game_finished=False):

        if self.cell_size < 6:
            return

        # No overlays once the match is over
        if game_finished:
            return

        board = self._board_pixel_rect()

        for agent in agents:
            # Don't draw overlay for dead/dying agents
            if not getattr(agent, "alive", True) or getattr(agent, "dying", False):
                continue
            overlay = getattr(agent, "visual_overlay", None)
            if not overlay or overlay["type"] is None or not overlay.get("cells"):
                continue

            otype = overlay["type"]
            data  = overlay["cells"]  # set for belief, dict{cell:dist} for and_or

            # ----------------------------------------------------------------
            # SENSORLESS: fog-of-war
            # ----------------------------------------------------------------
            if otype == "belief":
                belief_set = data  # set of (x, y)

                # 1. Dark fog over the whole board
                fog = pygame.Surface((board.width, board.height), pygame.SRCALPHA)
                fog.fill((0, 0, 0, 140))  # heavy dark overlay
                surface.blit(fog, board.topleft)

                # 2. Cut the fog out for belief cells — paint them with a
                #    semi-transparent tint in the agent's color so they glow.
                for (cx, cy) in belief_set:
                    r = self.cell_rect(cx, cy)
                    if not board.colliderect(r):
                        continue
                    # bright "visible" patch using agent color
                    patch = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                    ar, ag_, ab = agent.color
                    patch.fill((ar, ag_, ab, 55))
                    surface.blit(patch, r.topleft)

                # 3. Glowing border around the belief cloud boundary
                cell_set = belief_set
                for (cx, cy) in belief_set:
                    r = self.cell_rect(cx, cy)
                    if not board.colliderect(r):
                        continue
                    ar, ag_, ab = agent.color
                    for (nx, ny), (p1, p2) in [
                        ((cx, cy-1), (r.topleft,    r.topright)),
                        ((cx, cy+1), (r.bottomleft,  r.bottomright)),
                        ((cx-1, cy), (r.topleft,     r.bottomleft)),
                        ((cx+1, cy), (r.topright,    r.bottomright)),
                    ]:
                        if (nx, ny) not in cell_set:
                            pygame.draw.line(surface, (ar, ag_, ab, 200), p1, p2, 2)

            # ----------------------------------------------------------------
            # AND-OR: distance-based heatmap
            # ----------------------------------------------------------------
            elif otype == "reachable_zone":
                dist_map = data  # {(x,y): distance 0..depth}
                if not dist_map:
                    continue

                max_dist = max(dist_map.values()) or 1

                for (cx, cy), dist in dist_map.items():
                    r = self.cell_rect(cx, cy)
                    if not board.colliderect(r):
                        continue

                    # Gradient: distance 0 = hot (full opacity), max = faint
                    # Colour sweeps orange → yellow → barely visible
                    t = dist / max_dist          # 0.0 (closest) .. 1.0 (furthest)
                    alpha = int(180 * (1.0 - t * 0.85))   # 180 → ~27

                    # orange (255,120,20) at t=0, pale yellow (255,220,100) at t=1
                    red   = 255
                    green = int(120 + 100 * t)
                    blue  = int(20  +  80 * t)

                    patch = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                    patch.fill((red, green, blue, alpha))
                    surface.blit(patch, r.topleft)

                # Solid border only around dist==1 ring (immediate danger edge)
                d1_cells = {c for c, d in dist_map.items() if d <= 1}
                for (cx, cy) in d1_cells:
                    r = self.cell_rect(cx, cy)
                    if not board.colliderect(r):
                        continue
                    for (nx, ny), (p1, p2) in [
                        ((cx, cy-1), (r.topleft,    r.topright)),
                        ((cx, cy+1), (r.bottomleft,  r.bottomright)),
                        ((cx-1, cy), (r.topleft,     r.bottomleft)),
                        ((cx+1, cy), (r.topright,    r.bottomright)),
                    ]:
                        if (nx, ny) not in d1_cells:
                            pygame.draw.line(surface, (255, 140, 40, 200), p1, p2, 2)
