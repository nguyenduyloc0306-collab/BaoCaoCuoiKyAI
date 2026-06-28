
import sys
import pygame

import config
from game_engine import GameEngine, GameResult
from ui.menu import SetupScreen
from ui.renderer import BoardRenderer
from ui.hud import HUD

STATE_SETUP = "setup"
STATE_PLAYING = "playing"

def load_fonts():
    pygame.font.init()
    # Try a crisp modern font, fall back to arial
    for name in ("segoeui", "calibri", "arial"):
        if pygame.font.match_font(name):
            chosen = name
            break
    else:
        chosen = None
    def F(size, bold=False):
        if chosen:
            return pygame.font.SysFont(chosen, size, bold=bold)
        return pygame.font.SysFont("arial", size, bold=bold)
    return {
        "title":  F(20, bold=True),
        "normal": F(16, bold=True),
        "small":  F(14),
        "tiny":   F(12),
    }

class Application:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
            pygame.RESIZABLE,
        )
        pygame.display.set_caption("AI Hunter vs Runner")
        self.clock = pygame.time.Clock()
        self.fonts = load_fonts()

        self.win_w = config.WINDOW_WIDTH
        self.win_h = config.WINDOW_HEIGHT

        self.state = STATE_SETUP
        self.setup_screen = SetupScreen((self.win_w, self.win_h), self.fonts)

        self.engine = None
        self.board_renderer = None
        self.hud = None

        self.paused = False
        self.step_interval_ms = config.DEFAULT_STEP_INTERVAL_MS
        self.time_since_last_step = 0.0

        self.capture_effects = []
        self.hovered_cell = None

        self.running = True

    def run(self):
        while self.running:
            dt_ms = self.clock.tick(config.FPS)
            dt = dt_ms / 1000.0

            self._handle_events()

            if self.state == STATE_SETUP:
                self.setup_screen.update(dt)
            elif self.state == STATE_PLAYING:
                self._update_playing(dt_ms)

            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _on_resize(self, w, h):

        # Enforce a sensible minimum size
        w = max(w, 640)
        h = max(h, 480)
        self.win_w = w
        self.win_h = h
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        if self.state == STATE_SETUP:
            self.setup_screen.on_resize(w, h)
        elif self.state == STATE_PLAYING and self.engine is not None:
            self._rebuild_playing_layout()

    def _rebuild_playing_layout(self):

        sidebar_w = config.SIDEBAR_WIDTH
        board_area = pygame.Rect(
            config.BOARD_MARGIN, config.TOPBAR_HEIGHT + config.BOARD_MARGIN,
            self.win_w - sidebar_w - 2 * config.BOARD_MARGIN,
            self.win_h - config.TOPBAR_HEIGHT - 2 * config.BOARD_MARGIN,
        )
        self.board_renderer.set_board_rect(board_area)
        hud_rect = pygame.Rect(self.win_w - sidebar_w, 0, sidebar_w, self.win_h)
        self.hud.on_resize(hud_rect)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            # Handle window resize
            if event.type == pygame.VIDEORESIZE:
                self._on_resize(event.w, event.h)
                continue
            if event.type == pygame.WINDOWRESIZED:
                self._on_resize(event.x, event.y)
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state == STATE_PLAYING:
                    self._go_to_setup()
                continue

            if self.state == STATE_SETUP:
                start_requested = self.setup_screen.handle_event(event)
                if start_requested:
                    self._start_match()
            elif self.state == STATE_PLAYING:
                self._handle_playing_event(event)

    def _handle_playing_event(self, event):
        if self.hud.handle_event(event):
            return
        if event.type == pygame.MOUSEMOTION:
            self.hovered_cell = self.board_renderer.pixel_to_cell(*event.pos)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.hud._toggle_pause_internal()

    def _start_match(self):
        self.setup_screen.finalize_positions()
        s = self.setup_screen

        self.engine = GameEngine(s.grid_size, s.grid_size, max_steps=s.max_steps)
        self.engine.grid = s.grid.copy()

        for cfg in s.hunter_configs:
            self.engine.add_agent("hunter", cfg.algo_key, cfg.pos, cfg.color, cfg.label)
        for cfg in s.runner_configs:
            self.engine.add_agent("runner", cfg.algo_key, cfg.pos, cfg.color, cfg.label)

        sidebar_w = config.SIDEBAR_WIDTH
        board_area = pygame.Rect(
            config.BOARD_MARGIN, config.TOPBAR_HEIGHT + config.BOARD_MARGIN,
            self.win_w - sidebar_w - 2 * config.BOARD_MARGIN,
            self.win_h - config.TOPBAR_HEIGHT - 2 * config.BOARD_MARGIN,
        )
        self.board_renderer = BoardRenderer(board_area, s.grid_size, s.grid_size)

        hud_rect = pygame.Rect(
            self.win_w - sidebar_w, 0, sidebar_w, self.win_h)
        self.hud = HUD(
            hud_rect, self.fonts,
            on_toggle_pause=self._on_toggle_pause,
            on_restart=self._restart_match,
            on_back=self._go_to_setup,
            on_speed_change=self._on_speed_change,
        )
        self.hud.set_paused(False)

        self.paused = False
        self.time_since_last_step = 0.0
        self.capture_effects = []
        self.state = STATE_PLAYING

    def _restart_match(self):
        self._start_match()

    def _go_to_setup(self):
        self.state = STATE_SETUP

    def _on_toggle_pause(self, paused):
        self.paused = paused

    def _on_speed_change(self, value):
        self.step_interval_ms = value

    def _update_playing(self, dt_ms):
        if self.paused or self.engine.is_finished():
            # Still tick animations even when game is "finished" so the
            # attack clip can play out before the result banner takes over
            if self.engine.is_finished():
                for agent in self.engine.agents:
                    if hasattr(agent, "tick_animation"):
                        agent.tick_animation(dt_ms)
                # Clear dying runners whose killer has finished the attack clip
                self._resolve_dying_runners()
            return

        # Tick all animations every frame (smooth, independent of step clock)
        for agent in self.engine.agents:
            if hasattr(agent, "tick_animation"):
                agent.tick_animation(dt_ms)
        self._resolve_dying_runners()

        # Advance capture ring effects every frame (time-based, ~500ms total)
        EFFECT_DURATION_MS = 500.0
        new_effects = []
        for fx in self.capture_effects:
            fx["t"] += dt_ms / EFFECT_DURATION_MS
            if fx["t"] < 1.0:
                new_effects.append(fx)
        self.capture_effects = new_effects

        self.time_since_last_step += dt_ms
        if self.time_since_last_step >= self.step_interval_ms:
            self.time_since_last_step = 0.0
            self._advance_one_step()

    def _resolve_dying_runners(self):
        for agent in self.engine.agents:
            if agent.role != "runner" or not getattr(agent, "dying", False):
                continue
            killer_id = getattr(agent, "_killing_hunter_id", None)
            killer = next((a for a in self.engine.agents if a.id == killer_id), None) if killer_id else None

            hunter_done = (killer is None or getattr(killer, "_attack_done", True))
            runner_done = getattr(agent, "_death_done", True)

            if hunter_done and runner_done:
                agent.dying = False

    def _advance_one_step(self):
        self.engine.step()
        for hunter_id, runner_id in self.engine.caught_pairs:
            runner = next((a for a in self.engine.agents if a.id == runner_id), None)
            if runner:
                self.capture_effects.append({"pos": runner.pos, "t": 0.0})

    def _draw(self):
        if self.state == STATE_SETUP:
            self.setup_screen.draw(self.screen)
        elif self.state == STATE_PLAYING:
            self._draw_playing()

    def _draw_playing(self):
        self.screen.fill(config.COLOR_BG)
        self._draw_topbar()

        self.board_renderer.draw_background(self.screen)
        self.board_renderer.draw_grid_lines(self.screen)
        self.board_renderer.draw_obstacles(self.screen, self.engine.grid)
        self.board_renderer.draw_walls(self.screen, self.engine.grid)

        # Draw partial-observability overlays (sensorless belief / and_or zone)
        # underneath the agents so they never obscure the shapes
        self.board_renderer.draw_belief_overlays(
            self.screen, self.engine.agents, self.fonts["tiny"],
            game_finished=self.engine.is_finished())

        self.board_renderer.draw_all_agents(self.screen, self.engine.agents, self.fonts["tiny"])

        for fx in self.capture_effects:
            self.board_renderer.draw_capture_effect(self.screen, fx["pos"], fx["t"])

        self.board_renderer.draw_border(self.screen)
        self.board_renderer.draw_hover_highlight(self.screen, self.hovered_cell)

        self.hud.draw(self.screen, self.engine)

    def _draw_topbar(self):
        rect = pygame.Rect(0, 0, self.win_w - config.SIDEBAR_WIDTH, config.TOPBAR_HEIGHT)
        pygame.draw.rect(self.screen, config.COLOR_PANEL, rect)
        # Bottom separator line
        pygame.draw.line(self.screen, config.COLOR_PANEL_BORDER,
                         (0, rect.bottom), (rect.width, rect.bottom), 2)
        # Left accent bar
        pygame.draw.rect(self.screen, config.COLOR_ACCENT,
                         pygame.Rect(12, 12, 3, config.TOPBAR_HEIGHT - 24))

        title = self.fonts["title"].render("AI HUNTER vs RUNNER", True, config.COLOR_TEXT_ACCENT)
        self.screen.blit(title, (22, (config.TOPBAR_HEIGHT - title.get_height()) // 2))

        n_hunters       = len(self.engine.hunters())
        n_runners_alive = len(self.engine.alive_runners())
        n_runners_total = len(self.engine.runners())
        info_text = f"Hunters: {n_hunters}    Runners alive: {n_runners_alive} / {n_runners_total}"
        info_surf = self.fonts["small"].render(info_text, True, config.COLOR_TEXT_DIM)
        self.screen.blit(info_surf, (rect.width - info_surf.get_width() - 20,
                                     (config.TOPBAR_HEIGHT - info_surf.get_height()) // 2))

def main():
    app = Application()
    app.run()

if __name__ == "__main__":
    main()
