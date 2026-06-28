
import random
import pygame

import config
from grid import Grid
from utils import random_free_cell
from ui.widgets import Button, Slider, SegmentedControl, ScrollArea, draw_rounded_rect
from ui.renderer import BoardRenderer

PLACEMENT_RANDOM = "random"
PLACEMENT_CUSTOM = "custom"

TOOL_NONE = "none"
TOOL_OBSTACLE = "obstacle"
TOOL_PLACE_AGENT = "place_agent"

class AgentConfig:
    def __init__(self, role, algo_key, color, label, pos=None):
        self.role = role
        self.algo_key = algo_key
        self.color = color
        self.label = label
        self.pos = pos

class SetupScreen:
    def __init__(self, screen_size, fonts):
        self.screen_w, self.screen_h = screen_size
        self.fonts = fonts

        self.grid_size = config.DEFAULT_GRID_SIZE
        self.max_steps = config.DEFAULT_MAX_STEPS
        self.obstacle_density = config.DEFAULT_OBSTACLE_DENSITY
        self.placement_mode = PLACEMENT_RANDOM

        self.grid = Grid(self.grid_size, self.grid_size)

        self.hunter_configs = []
        self.runner_configs = []
        self._add_default_agents()

        self.active_tool = TOOL_NONE
        self.tool_target_index = None
        self.obstacle_paint_mode = None

        self.message = ""
        self.message_timer = 0.0
        self.start_requested = False

        self._build_layout()

    def _add_default_agents(self):
        self.hunter_configs.append(
            AgentConfig("hunter", config.DEFAULT_HUNTER_ALGO,
                        config.HUNTER_PALETTE[0], "Hunter 1"))
        self.runner_configs.append(
            AgentConfig("runner", config.DEFAULT_RUNNER_ALGO,
                        config.RUNNER_PALETTE[0], "Runner 1"))

    def _relabel(self):
        for i, c in enumerate(self.hunter_configs, start=1):
            c.label = f"Hunter {i}"
        for i, c in enumerate(self.runner_configs, start=1):
            c.label = f"Runner {i}"

    def _build_layout(self):
        self.sidebar_rect = pygame.Rect(0, 0, 380, self.screen_h)
        self.board_panel_rect = pygame.Rect(
            self.sidebar_rect.width, 0,
            self.screen_w - self.sidebar_rect.width, self.screen_h,
        )
        board_area = self.board_panel_rect.inflate(-80, -160)
        board_area.top = self.board_panel_rect.top + 90
        self.board_renderer = BoardRenderer(board_area, self.grid_size, self.grid_size)
        self._build_sidebar_widgets()

    def on_resize(self, new_w, new_h):
        self.screen_w = new_w
        self.screen_h = new_h
        self._build_layout()

    def _build_sidebar_widgets(self):
        pad = 20
        x = pad
        w = self.sidebar_rect.width - 2 * pad
        y = 24

        self.title_y = y
        y += 46

        self.label_grid_y = y
        y += 22
        self.slider_grid = Slider(
            (x, y, w, 8), config.MIN_GRID_SIZE, config.MAX_GRID_SIZE,
            self.grid_size, self.fonts["small"], label="",
            on_change=self._on_grid_size_change,
        )
        y += 40

        self.label_steps_y = y
        y += 22
        self.slider_steps = Slider(
            (x, y, w, 8), config.MIN_MAX_STEPS, config.MAX_MAX_STEPS,
            self.max_steps, self.fonts["small"], label="",
            on_change=self._on_max_steps_change,
        )
        y += 40

        self.label_density_y = y
        y += 22
        slider_w = w - 96
        self.slider_density = Slider(
            (x, y, slider_w, 8), 0, 50, int(self.obstacle_density * 100),
            self.fonts["small"], label="", on_change=self._on_density_change,
        )
        self.btn_random_obstacles = Button(
            (x + slider_w + 12, y - 10, 84, 28), "Randomize", self.fonts["small"],
            on_click=self._generate_random_obstacles,
        )
        y += 30
        self.btn_clear_obstacles = Button(
            (x, y, w, 30), "Clear Obstacles", self.fonts["small"],
            on_click=self._clear_obstacles,
        )
        y += 44

        self.label_placement_y = y
        y += 22
        self.segment_placement = SegmentedControl(
            (x, y, w, 32),
            [(PLACEMENT_RANDOM, "Random"), (PLACEMENT_CUSTOM, "Manual (click)")],
            self.fonts["small"], selected_index=0 if self.placement_mode == PLACEMENT_RANDOM else 1,
            on_change=self._on_placement_mode_change,
        )
        y += 44

        self.label_obstacle_tool_y = y
        y += 22
        self.btn_paint_obstacle = Button(
            (x, y, w, 32), "Tool: Draw Obstacles (click map)", self.fonts["small"],
            on_click=self._toggle_paint_tool,
        )
        y += 44

        BOTTOM_RESERVE = 176
        self.agent_list_top = y
        self.agent_list_bottom = max(y + 40, self.sidebar_rect.height - BOTTOM_RESERVE)
        self.agent_scroll = ScrollArea(
            (x, self.agent_list_top, w, self.agent_list_bottom - self.agent_list_top),
            content_height=0,
        )
        self._layout_agent_buttons()

        bottom_y = self.agent_list_bottom + 8
        self.btn_add_hunter = Button(
            (x, bottom_y, (w - 10) / 2, 34), "+ Hunter", self.fonts["small"],
            on_click=self._add_hunter,
        )
        self.btn_add_runner = Button(
            (x + (w - 10) / 2 + 10, bottom_y, (w - 10) / 2, 34), "+ Runner", self.fonts["small"],
            on_click=self._add_runner,
        )
        bottom_y += 42

        self.btn_random_positions = Button(
            (x, bottom_y, w, 34), "Randomize All Positions", self.fonts["small"],
            on_click=self._randomize_all_positions,
        )
        bottom_y += 42

        self.btn_start = Button(
            (x, bottom_y, w, 44), "START MATCH", self.fonts["normal"],
            on_click=self._request_start, style="accent",
        )

    def _layout_agent_buttons(self):
        pad = 20
        x = pad
        w = self.sidebar_rect.width - 2 * pad
        SCROLLBAR_RESERVE = 14
        ew = w - SCROLLBAR_RESERVE
        y = 0
        row_h = 64
        row_gap = 6
        self._agent_rows = []

        all_configs = [("hunter", i, c) for i, c in enumerate(self.hunter_configs)] + \
                      [("runner", i, c) for i, c in enumerate(self.runner_configs)]

        for role, idx, cfg in all_configs:
            base_y = y
            row = {
                "role": role,
                "index": idx,
                "config": cfg,
                "base_y": base_y,
                "card_rect": pygame.Rect(x, self.agent_list_top + base_y, ew, row_h - row_gap),
                "algo_prev_rect": pygame.Rect(x + 4, self.agent_list_top + base_y + 34, 22, 20),
                "algo_next_rect": pygame.Rect(x + ew - 26, self.agent_list_top + base_y + 34, 22, 20),
                "place_btn": Button((x + ew - 62, self.agent_list_top + base_y, 36, 22), "Place", self.fonts["small"]),
                "remove_btn": Button((x + ew - 22, self.agent_list_top + base_y, 22, 22), "x", self.fonts["small"], style="danger"),
            }
            row["place_btn"].on_click = (lambda r=role, i=idx: self._start_place_agent(r, i))
            row["remove_btn"].on_click = (lambda r=role, i=idx: self._remove_agent(r, i))
            self._agent_rows.append(row)
            y += row_h

        total_content_height = max(0, y - row_gap)
        self.agent_scroll.set_content_height(total_content_height)
        self._sync_agent_row_positions()

    def _sync_agent_row_positions(self):
        top = self.agent_list_top
        offset = int(self.agent_scroll.offset)
        for row in self._agent_rows:
            actual_y = top + row["base_y"] - offset
            row["card_rect"].y = actual_y
            row["algo_prev_rect"].y = actual_y + 34
            row["algo_next_rect"].y = actual_y + 34
            row["place_btn"].rect.y = actual_y
            row["remove_btn"].rect.y = actual_y
            row["_visible_y"] = actual_y

    # ------------------------------------------------------------------
    def _on_grid_size_change(self, value):
        self.grid_size = int(value)
        self.grid = Grid(self.grid_size, self.grid_size)
        self.board_renderer.set_grid_size(self.grid_size, self.grid_size)
        for c in self.hunter_configs + self.runner_configs:
            c.pos = None

    def _on_max_steps_change(self, value):
        self.max_steps = int(value)

    def _on_density_change(self, value):
        self.obstacle_density = value / 100.0

    def _on_placement_mode_change(self, mode):
        self.placement_mode = mode
        if mode == PLACEMENT_RANDOM:
            self.active_tool = TOOL_NONE
            self.tool_target_index = None

    def _toggle_paint_tool(self):
        if self.active_tool == TOOL_OBSTACLE:
            self.active_tool = TOOL_NONE
            self.btn_paint_obstacle.text = "Tool: Draw Obstacles (click map)"
        else:
            self.active_tool = TOOL_OBSTACLE
            self.tool_target_index = None
            self.btn_paint_obstacle.text = "Drawing obstacles — click again to stop"

    def _generate_random_obstacles(self):
        protected = set()
        for c in self.hunter_configs + self.runner_configs:
            if c.pos:
                protected.add(c.pos)
        self.grid.generate_random_obstacles(self.obstacle_density, protected_cells=protected)
        self._show_message("Obstacles generated randomly.")

    def _clear_obstacles(self):
        self.grid.clear_obstacles()
        self._show_message("All obstacles cleared.")

    def _add_hunter(self):
        if len(self.hunter_configs) >= 8:
            self._show_message("Maximum 8 hunters.")
            return
        idx = len(self.hunter_configs)
        self.hunter_configs.append(
            AgentConfig("hunter", config.DEFAULT_HUNTER_ALGO,
                        config.HUNTER_PALETTE[idx % len(config.HUNTER_PALETTE)],
                        f"Hunter {idx + 1}"))
        self._relabel()
        self._layout_agent_buttons()

    def _add_runner(self):
        if len(self.runner_configs) >= 8:
            self._show_message("Maximum 8 runners.")
            return
        idx = len(self.runner_configs)
        self.runner_configs.append(
            AgentConfig("runner", config.DEFAULT_RUNNER_ALGO,
                        config.RUNNER_PALETTE[idx % len(config.RUNNER_PALETTE)],
                        f"Runner {idx + 1}"))
        self._relabel()
        self._layout_agent_buttons()

    def _remove_agent(self, role, index):
        target_list = self.hunter_configs if role == "hunter" else self.runner_configs
        if len(target_list) <= 1:
            self._show_message(f"Need at least 1 {role}.")
            return
        del target_list[index]
        self._relabel()
        self._layout_agent_buttons()

    def _start_place_agent(self, role, index):
        if self.placement_mode != PLACEMENT_CUSTOM:
            self._show_message("Switch to Manual mode to place agents.")
            return
        self.active_tool = TOOL_PLACE_AGENT
        self.tool_target_index = (role, index)
        self._show_message("Click the map to place the agent.")

    def _randomize_all_positions(self):
        occupied = set()
        rng = random.Random()
        for c in self.hunter_configs + self.runner_configs:
            pos = random_free_cell(self.grid, occupied, rng=rng)
            if pos is None:
                self._show_message("Not enough free cells! Reduce obstacle density.")
                return
            c.pos = pos
            occupied.add(pos)
        self._show_message("All agent positions randomized.")

    def _show_message(self, text):
        self.message = text
        self.message_timer = 2.6

    def _request_start(self):
        self.start_requested = True

    # ------------------------------------------------------------------
    def handle_event(self, event):
        self.start_requested = False

        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEWHEEL):
            consumed = False
            consumed |= self.slider_grid.handle_event(event)
            consumed |= self.slider_steps.handle_event(event)
            consumed |= self.slider_density.handle_event(event)
            consumed |= self.btn_random_obstacles.handle_event(event)
            consumed |= self.btn_clear_obstacles.handle_event(event)
            consumed |= self.segment_placement.handle_event(event)
            consumed |= self.btn_paint_obstacle.handle_event(event)
            consumed |= self.btn_add_hunter.handle_event(event)
            consumed |= self.btn_add_runner.handle_event(event)
            consumed |= self.btn_random_positions.handle_event(event)
            consumed |= self.btn_start.handle_event(event)

            # Check arrow buttons and row buttons BEFORE letting scrollbar handle the event
            list_visible_rect = pygame.Rect(
                self.sidebar_rect.x, self.agent_list_top,
                self.sidebar_rect.width, self.agent_list_bottom - self.agent_list_top,
            )
            arrow_consumed = False
            for row in self._agent_rows:
                row_rect = pygame.Rect(
                    self.sidebar_rect.x, row["_visible_y"],
                    self.sidebar_rect.width, 64,
                )
                fully_visible = (row_rect.y >= list_visible_rect.y - 4 and
                                  row_rect.y + 58 <= list_visible_rect.bottom + 4)
                if not fully_visible:
                    continue
                consumed |= row["place_btn"].handle_event(event)
                consumed |= row["remove_btn"].handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if row["algo_prev_rect"].collidepoint(event.pos):
                        self._cycle_algo(row["config"], -1)
                        consumed = True
                        arrow_consumed = True
                    elif row["algo_next_rect"].collidepoint(event.pos):
                        self._cycle_algo(row["config"], 1)
                        consumed = True
                        arrow_consumed = True

            if not arrow_consumed:
                scroll_consumed = self.agent_scroll.handle_event(event)
                if scroll_consumed:
                    self._sync_agent_row_positions()
                consumed |= scroll_consumed

            if not consumed and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_board_click(event.pos)
                if self.active_tool == TOOL_OBSTACLE:
                    cell = self.board_renderer.pixel_to_cell(*event.pos)
                    if cell:
                        self.obstacle_paint_mode = not self.grid.is_obstacle(*cell)

            if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                if self.active_tool == TOOL_OBSTACLE and self.obstacle_paint_mode is not None:
                    cell = self.board_renderer.pixel_to_cell(*event.pos)
                    if cell and not self._cell_has_agent(cell):
                        self.grid.set_obstacle(cell[0], cell[1], self.obstacle_paint_mode)

            if event.type == pygame.MOUSEBUTTONUP:
                self.obstacle_paint_mode = None

        return self.start_requested

    def _cycle_algo(self, agent_cfg, direction):
        keys = config.ALGORITHM_KEYS
        idx = keys.index(agent_cfg.algo_key)
        agent_cfg.algo_key = keys[(idx + direction) % len(keys)]

    def _cell_has_agent(self, cell):
        for c in self.hunter_configs + self.runner_configs:
            if c.pos == cell:
                return True
        return False

    def _handle_board_click(self, mouse_pos):
        cell = self.board_renderer.pixel_to_cell(*mouse_pos)
        if cell is None:
            return

        if self.active_tool == TOOL_OBSTACLE:
            if self._cell_has_agent(cell):
                self._show_message("This cell already has an agent.")
                return
            self.grid.toggle_obstacle(*cell)

        elif self.active_tool == TOOL_PLACE_AGENT and self.tool_target_index:
            if self.grid.is_obstacle(*cell):
                self._show_message("Cannot place agent on an obstacle.")
                return
            if self._cell_has_agent(cell):
                self._show_message("This cell is already occupied.")
                return
            role, index = self.tool_target_index
            target_list = self.hunter_configs if role == "hunter" else self.runner_configs
            if index < len(target_list):
                target_list[index].pos = cell
            self.active_tool = TOOL_NONE
            self.tool_target_index = None
            self._show_message("Position set.")

    # ------------------------------------------------------------------
    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def finalize_positions(self):
        occupied = set()
        rng = random.Random()
        for c in self.hunter_configs + self.runner_configs:
            valid = (c.pos is not None and self.grid.is_walkable(*c.pos)
                     and c.pos not in occupied)
            if not valid:
                pos = random_free_cell(self.grid, occupied, rng=rng)
                c.pos = pos
            occupied.add(c.pos)

    # ------------------------------------------------------------------
    def draw(self, surface):
        surface.fill(config.COLOR_BG)
        self._draw_sidebar(surface)
        self._draw_board_panel(surface)

    def _draw_sidebar(self, surface):
        pygame.draw.rect(surface, config.COLOR_PANEL, self.sidebar_rect)

        # Subtle right border line on the sidebar
        border_x = self.sidebar_rect.right - 1
        pygame.draw.line(
            surface, config.COLOR_PANEL_BORDER,
            (border_x, self.sidebar_rect.top),
            (border_x, self.sidebar_rect.bottom),
            2,
        )

        pad = 20
        x = self.sidebar_rect.x + pad

        # Small colored left-accent bar next to the title
        accent_bar_rect = pygame.Rect(x, self.title_y + 2, 3, self.fonts["title"].get_height() - 4)
        pygame.draw.rect(surface, config.COLOR_ACCENT, accent_bar_rect)

        # Title drawn in COLOR_TEXT_ACCENT, offset right of accent bar
        title = self.fonts["title"].render("MATCH SETUP", True, config.COLOR_TEXT_ACCENT)
        surface.blit(title, (x + 8, self.title_y))

        f = self.fonts["small"]
        surface.blit(f.render(f"Grid size: {self.grid_size} x {self.grid_size}",
                               True, config.COLOR_TEXT), (x, self.label_grid_y))
        self.slider_grid.draw(surface)

        surface.blit(f.render(f"Max steps: {self.max_steps}",
                               True, config.COLOR_TEXT), (x, self.label_steps_y))
        self.slider_steps.draw(surface)

        surface.blit(f.render(f"Obstacle density: {int(self.obstacle_density * 100)}%",
                               True, config.COLOR_TEXT), (x, self.label_density_y))
        self.slider_density.draw(surface)
        self.btn_random_obstacles.draw(surface)
        self.btn_clear_obstacles.draw(surface)

        surface.blit(f.render("Starting positions", True, config.COLOR_TEXT),
                     (x, self.label_placement_y))
        self.segment_placement.draw(surface)

        if self.placement_mode == PLACEMENT_CUSTOM:
            self.btn_paint_obstacle.draw(surface)
        else:
            dim_rect = self.btn_paint_obstacle.rect
            draw_rounded_rect(surface, dim_rect, config.COLOR_PANEL_LIGHT, radius=8)
            note = f.render("Enable Manual mode to draw obstacles / place agents",
                            True, config.COLOR_TEXT_DIM)
            surface.blit(note, note.get_rect(center=dim_rect.center))

        self._draw_agent_rows(surface)

        self.btn_add_hunter.draw(surface)
        self.btn_add_runner.draw(surface)
        self.btn_random_positions.draw(surface)
        self.btn_start.draw(surface)

        if self.message:
            msg_surf = self.fonts["small"].render(self.message, True, config.COLOR_WARNING)
            msg_y = self.btn_start.rect.bottom + 4
            if msg_y + msg_surf.get_height() > self.sidebar_rect.height:
                msg_y = self.sidebar_rect.height - msg_surf.get_height() - 4
            surface.blit(msg_surf, (x, msg_y))

    def _draw_agent_rows(self, surface):
        self._sync_agent_row_positions()

        clip_rect = pygame.Rect(
            self.sidebar_rect.x, self.agent_list_top,
            self.sidebar_rect.width, self.agent_list_bottom - self.agent_list_top,
        )
        f = self.fonts["small"]

        for row in self._agent_rows:
            cfg = row["config"]
            card_rect = row["card_rect"]

            if card_rect.bottom < clip_rect.y or card_rect.y > clip_rect.bottom:
                continue

            # Always draw with the full clip_rect active
            surface.set_clip(clip_rect)

            # Card with border
            draw_rounded_rect(surface, card_rect, config.COLOR_PANEL_LIGHT, radius=8,
                               border_color=config.COLOR_PANEL_BORDER, border_width=1)

            color_dot_center = (card_rect.x + 12, card_rect.y + 14)
            if cfg.role == "hunter":
                r = 7
                pts = [
                    (color_dot_center[0], color_dot_center[1] - r),
                    (color_dot_center[0] + r, color_dot_center[1]),
                    (color_dot_center[0], color_dot_center[1] + r),
                    (color_dot_center[0] - r, color_dot_center[1]),
                ]
                outline_pts = [
                    (color_dot_center[0], color_dot_center[1] - (r + 2)),
                    (color_dot_center[0] + (r + 2), color_dot_center[1]),
                    (color_dot_center[0], color_dot_center[1] + (r + 2)),
                    (color_dot_center[0] - (r + 2), color_dot_center[1]),
                ]
                pygame.draw.polygon(surface, (255, 255, 255), outline_pts, 1)
                pygame.draw.polygon(surface, cfg.color, pts)
            else:
                pygame.draw.circle(surface, (255, 255, 255), color_dot_center, 9, 1)
                pygame.draw.circle(surface, cfg.color, color_dot_center, 7)

            # Name — clip to a narrow column so it doesn't overwrite the right-side buttons
            name_area_w = max(20, card_rect.width - 26 - 70)
            name_label = f.render(cfg.label, True, config.COLOR_TEXT)
            name_clip = pygame.Rect(card_rect.x + 26, card_rect.y + 4,
                                    name_area_w, 20).clip(clip_rect)
            surface.set_clip(name_clip)
            surface.blit(name_label, (card_rect.x + 26, card_rect.y + 4))

            # Position text
            surface.set_clip(clip_rect)
            pos_text = f"{cfg.pos}" if cfg.pos else "(not placed)"
            pos_color = config.COLOR_TEXT_DIM if not cfg.pos else config.COLOR_SUCCESS
            pos_label = f.render(pos_text, True, pos_color)
            pos_clip = pygame.Rect(card_rect.x + 26, card_rect.y + 20,
                                   name_area_w, 16).clip(clip_rect)
            surface.set_clip(pos_clip)
            surface.blit(pos_label, (card_rect.x + 26, card_rect.y + 20))

            # Algorithm name centred between arrows — restore full clip first
            surface.set_clip(clip_rect)
            algo_label_text = config.ALGORITHM_SHORT_LABELS.get(cfg.algo_key, cfg.algo_key)
            available_w = row["algo_next_rect"].x - row["algo_prev_rect"].right - 8
            algo_font = f
            algo_surf = algo_font.render(algo_label_text, True, config.COLOR_TEXT_ACCENT)
            if algo_surf.get_width() > available_w and "tiny" in self.fonts:
                algo_font = self.fonts["tiny"]
                algo_surf = algo_font.render(algo_label_text, True, config.COLOR_TEXT_ACCENT)
            algo_center_x = (row["algo_prev_rect"].right + row["algo_next_rect"].x) / 2
            algo_rect_pos = algo_surf.get_rect(center=(algo_center_x, card_rect.y + 44))
            surface.blit(algo_surf, algo_rect_pos)

            # Arrow buttons and action buttons — always on full clip_rect
            surface.set_clip(clip_rect)
            draw_rounded_rect(surface, row["algo_prev_rect"], config.COLOR_BUTTON, radius=5,
                               border_color=config.COLOR_BUTTON_BORDER, border_width=1)
            prev_arrow = f.render("<", True, config.COLOR_TEXT)
            surface.blit(prev_arrow, prev_arrow.get_rect(center=row["algo_prev_rect"].center))

            draw_rounded_rect(surface, row["algo_next_rect"], config.COLOR_BUTTON, radius=5,
                               border_color=config.COLOR_BUTTON_BORDER, border_width=1)
            next_arrow = f.render(">", True, config.COLOR_TEXT)
            surface.blit(next_arrow, next_arrow.get_rect(center=row["algo_next_rect"].center))

            row["place_btn"].draw(surface)
            row["remove_btn"].draw(surface)

        surface.set_clip(None)
        self.agent_scroll.draw(surface)

    def _draw_board_panel(self, surface):
        panel = self.board_panel_rect

        # Subtle inner border/frame around the board panel
        pygame.draw.rect(surface, config.COLOR_PANEL_BORDER, panel, 1)

        # "MAP PREVIEW" header in COLOR_TEXT_ACCENT
        header = self.fonts["title"].render("MAP PREVIEW", True, config.COLOR_TEXT_ACCENT)
        surface.blit(header, (panel.x + 40, 28))

        hint = self.fonts["small"].render(
            "Manual mode: use Draw Obstacles tool or Place button per agent, then click the map.",
            True, config.COLOR_TEXT_DIM)
        surface.blit(hint, (panel.x + 40, 64))

        self.board_renderer.draw_background(surface)
        self.board_renderer.draw_grid_lines(surface)
        self.board_renderer.draw_obstacles(surface, self.grid)
        self.board_renderer.draw_walls(surface, self.grid)
        self.board_renderer.draw_border(surface)

        for c in self.hunter_configs + self.runner_configs:
            if c.pos is None:
                continue
            cx, cy = self.board_renderer.cell_center(*c.pos)
            radius = max(4, int(self.board_renderer.cell_size * 0.36))
            if c.role == "hunter":
                pts = [(cx, cy - radius), (cx + radius, cy), (cx, cy + radius), (cx - radius, cy)]
                pygame.draw.polygon(surface, c.color, pts)
                pygame.draw.polygon(surface, config.COLOR_TEXT_ACCENT, pts, width=2)
            else:
                pygame.draw.circle(surface, c.color, (cx, cy), radius)
                pygame.draw.circle(surface, config.COLOR_TEXT_ACCENT, (cx, cy), radius, width=2)

        if self.active_tool in (TOOL_OBSTACLE, TOOL_PLACE_AGENT):
            mouse_pos = pygame.mouse.get_pos()
            cell = self.board_renderer.pixel_to_cell(*mouse_pos)
            self.board_renderer.draw_hover_highlight(surface, cell)
