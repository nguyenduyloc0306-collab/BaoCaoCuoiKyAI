
import pygame
import config
from ui.widgets import Button, Slider, draw_rounded_rect

class HUD:
    def __init__(self, rect, fonts, on_toggle_pause, on_restart, on_back, on_speed_change):
        self.rect = pygame.Rect(rect)
        self.fonts = fonts
        self.paused = False
        self._on_restart = on_restart
        self._on_back = on_back
        self._on_speed_change = on_speed_change
        self._external_toggle_pause = on_toggle_pause
        self._build_widgets()

    def _build_widgets(self):
        pad = 16
        btn_h = 36
        y = self.rect.y + pad

        self.btn_pause = Button(
            (self.rect.x + pad, y, self.rect.width - 2 * pad, btn_h),
            "Resume" if self.paused else "Pause",
            self.fonts["normal"], on_click=self._toggle_pause_internal, style="accent",
        )
        y += btn_h + 8

        half_w = (self.rect.width - 2 * pad - 8) / 2
        self.btn_restart = Button(
            (self.rect.x + pad, y, half_w, btn_h),
            "Play Again", self.fonts["small"], on_click=self._on_restart,
        )
        self.btn_back = Button(
            (self.rect.x + pad + half_w + 8, y, half_w, btn_h),
            "Menu", self.fonts["small"], on_click=self._on_back,
        )
        y += btn_h + 20

        # Speed slider label drawn separately; slider itself is thin
        self._speed_label_y = y
        y += 18
        self.speed_slider = Slider(
            (self.rect.x + pad, y, self.rect.width - 2 * pad, 8),
            config.MIN_STEP_INTERVAL_MS, config.MAX_STEP_INTERVAL_MS,
            config.DEFAULT_STEP_INTERVAL_MS, self.fonts["small"],
            label="", on_change=self._on_speed_change,
        )
        y += 32

        self._content_top = y + 8
        self.scroll_offset = 0

    def on_resize(self, new_rect):
        self.rect = pygame.Rect(new_rect)
        self._build_widgets()

    def _toggle_pause_internal(self):
        self.paused = not self.paused
        self.btn_pause.text = "Resume" if self.paused else "Pause"
        self._external_toggle_pause(self.paused)

    def set_paused(self, value):
        self.paused = value
        self.btn_pause.text = "Resume" if self.paused else "Pause"

    def handle_event(self, event):
        consumed = False
        consumed |= self.btn_pause.handle_event(event)
        consumed |= self.btn_restart.handle_event(event)
        consumed |= self.btn_back.handle_event(event)
        consumed |= self.speed_slider.handle_event(event)
        return consumed

    # ------------------------------------------------------------------
    def _section_header(self, surface, text, y, pad):
        """Draw a subtle section divider with label."""
        lx = self.rect.x + pad
        rx = self.rect.right - pad
        label = self.fonts["tiny"].render(text.upper(), True, config.COLOR_TEXT_DIM)
        lw = label.get_width()
        mid = lx + (rx - lx) // 2
        line_y = y + label.get_height() // 2
        pygame.draw.line(surface, config.COLOR_GRID_LINE, (lx, line_y), (mid - lw // 2 - 6, line_y), 1)
        pygame.draw.line(surface, config.COLOR_GRID_LINE, (mid + lw // 2 + 6, line_y), (rx, line_y), 1)
        surface.blit(label, (mid - lw // 2, y))
        return y + label.get_height() + 6

    def draw(self, surface, engine):
        # Panel background + left border line
        draw_rounded_rect(surface, self.rect, config.COLOR_PANEL, radius=0)
        pygame.draw.line(surface, config.COLOR_GRID_LINE,
                         (self.rect.x, self.rect.y), (self.rect.x, self.rect.bottom), 2)

        pad = 16

        self.btn_pause.draw(surface)
        self.btn_restart.draw(surface)
        self.btn_back.draw(surface)

        # Speed label
        speed_ms = int(self.speed_slider.value)
        speed_lbl = self.fonts["tiny"].render(
            f"Step interval: {speed_ms} ms", True, config.COLOR_TEXT_DIM)
        surface.blit(speed_lbl, (self.rect.x + pad, self._speed_label_y))
        self.speed_slider.draw(surface)

        y = self._content_top

        # --- Step progress ---
        y = self._section_header(surface, "Progress", y, pad)
        step_lbl = self.fonts["small"].render(
            f"Step  {engine.step_count} / {engine.max_steps}", True, config.COLOR_TEXT)
        surface.blit(step_lbl, (self.rect.x + pad, y))
        y += 20
        bar_rect = pygame.Rect(self.rect.x + pad, y, self.rect.width - 2 * pad, 8)
        draw_rounded_rect(surface, bar_rect, config.COLOR_PANEL_LIGHT, radius=4)
        fill_w = int(bar_rect.width * engine.progress_ratio())
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_w, bar_rect.height)
            draw_rounded_rect(surface, fill_rect, config.COLOR_ACCENT, radius=4)
        y += 20

        # --- Result banner ---
        if engine.is_finished():
            from game_engine import GameResult
            if engine.result == GameResult.HUNTER_WIN:
                result_text, result_color = "HUNTER WINS", config.COLOR_DANGER
            else:
                result_text, result_color = "RUNNER WINS", config.COLOR_SUCCESS
            banner_rect = pygame.Rect(self.rect.x + pad, y, self.rect.width - 2 * pad, 38)
            draw_rounded_rect(surface, banner_rect, config.COLOR_PANEL_LIGHT, radius=8,
                               border_color=result_color, border_width=2)
            lbl = self.fonts["title"].render(result_text, True, result_color)
            surface.blit(lbl, lbl.get_rect(center=banner_rect.center))
            y += 48

        # --- Agents list ---
        y = self._section_header(surface, "Agents", y, pad)
        for agent in engine.agents:
            if y + 26 > self.rect.bottom - 60:
                break
            is_dead = agent.role == "runner" and not agent.alive
            color = config.COLOR_TEXT_DIM if is_dead else agent.color
            shape_cx = self.rect.x + pad + 9

            if agent.role == "hunter":
                r = 7
                pts = [(shape_cx, y + 5 - r + 12),
                       (shape_cx + r, y + 12),
                       (shape_cx, y + 5 + r + 7),
                       (shape_cx - r, y + 12)]
                pygame.draw.polygon(surface, color, pts)
            else:
                pygame.draw.circle(surface, color, (shape_cx, y + 12), 7)

            algo_short = config.ALGORITHM_SHORT_LABELS.get(agent.algo_key, agent.algo_key)
            status = "  ✗" if is_dead else ""
            text = f"{agent.label}  [{algo_short}]{status}"
            text_color = config.COLOR_TEXT_DIM if is_dead else config.COLOR_TEXT
            lbl = self.fonts["small"].render(text, True, text_color)
            max_w = self.rect.width - 2 * pad - 22
            if lbl.get_width() > max_w:
                while lbl.get_width() > max_w and len(text) > 4:
                    text = text[:-1]
                    lbl = self.fonts["small"].render(text + "…", True, text_color)
            surface.blit(lbl, (self.rect.x + pad + 22, y + 4))

            # tiny ms label on the right
            if hasattr(agent, "last_decision_time_ms"):
                ms_txt = f"{agent.last_decision_time_ms:.1f}ms"
                ms_lbl = self.fonts["tiny"].render(ms_txt, True, config.COLOR_TEXT_DIM)
                surface.blit(ms_lbl, (self.rect.right - pad - ms_lbl.get_width(), y + 6))

            y += 26

        # --- Overlay legend ---
        overlay_agents = [a for a in engine.agents
                          if a.algo_key in ("sensorless", "and_or") and a.alive]
        if overlay_agents:
            y = self._section_header(surface, "Overlay", y, pad)
            seen = set()
            for a in overlay_agents:
                if a.algo_key == "sensorless" and "belief" not in seen:
                    seen.add("belief")
                    sq = pygame.Rect(self.rect.x + pad, y + 2, 10, 10)
                    pygame.draw.rect(surface, (160, 200, 255), sq, border_radius=2)
                    surface.blit(self.fonts["tiny"].render(
                        "Fog = possible opponent location", True, config.COLOR_TEXT_DIM),
                        (self.rect.x + pad + 16, y))
                    y += 18
                if a.algo_key == "and_or" and "zone" not in seen:
                    seen.add("zone")
                    sq = pygame.Rect(self.rect.x + pad, y + 2, 10, 10)
                    pygame.draw.rect(surface, (255, 150, 40), sq, border_radius=2)
                    surface.blit(self.fonts["tiny"].render(
                        "Heat = opponent reachable zone", True, config.COLOR_TEXT_DIM),
                        (self.rect.x + pad + 16, y))
                    y += 18

        # --- Event log ---
        y = self._section_header(surface, "Event Log", y, pad)
        log_bottom = self.rect.bottom - 8
        for entry in reversed(engine.event_log[-14:]):
            if y + 16 > log_bottom:
                break
            lbl = self.fonts["tiny"].render(entry, True, config.COLOR_TEXT_DIM)
            max_w = self.rect.width - 2 * pad
            if lbl.get_width() > max_w:
                text = entry
                while lbl.get_width() > max_w and len(text) > 4:
                    text = text[:-1]
                    lbl = self.fonts["tiny"].render(text + "…", True, config.COLOR_TEXT_DIM)
            surface.blit(lbl, (self.rect.x + pad, y))
            y += 16
