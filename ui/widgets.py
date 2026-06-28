
import pygame
import config

def draw_rounded_rect(surface, rect, color, radius=10, border_color=None, border_width=0):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=radius)

def draw_section_label(surface, font, text, x, y, width):
    """Draw a section header: label centred between two thin rules."""
    lbl = font.render(text.upper(), True, config.COLOR_TEXT_DIM)
    lw  = lbl.get_width()
    mid = x + width // 2
    cy  = y + lbl.get_height() // 2
    gap = 8
    if mid - lw // 2 - gap > x:
        pygame.draw.line(surface, config.COLOR_PANEL_BORDER,
                         (x, cy), (mid - lw // 2 - gap, cy), 1)
    if mid + lw // 2 + gap < x + width:
        pygame.draw.line(surface, config.COLOR_PANEL_BORDER,
                         (mid + lw // 2 + gap, cy), (x + width, cy), 1)
    surface.blit(lbl, (mid - lw // 2, y))
    return y + lbl.get_height() + 6


class Button:
    def __init__(self, rect, text, font, on_click=None, style="default"):
        self.rect    = pygame.Rect(rect)
        self.text    = text
        self.font    = font
        self.on_click = on_click
        self.style   = style   # "default" | "accent" | "danger"
        self.hovered = False
        self.enabled = True

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface):
        if not self.enabled:
            bg           = config.COLOR_PANEL_LIGHT
            text_color   = config.COLOR_TEXT_DIM
            border_color = config.COLOR_PANEL_BORDER
        elif self.style == "accent":
            bg           = config.COLOR_ACCENT      if self.hovered else config.COLOR_ACCENT_DARK
            text_color   = config.COLOR_TEXT_ACCENT
            border_color = config.COLOR_ACCENT
        elif self.style == "danger":
            bg           = config.COLOR_DANGER      if self.hovered else (160, 60, 60)
            text_color   = config.COLOR_TEXT_ACCENT
            border_color = config.COLOR_DANGER
        else:
            bg           = config.COLOR_BUTTON_HOVER if self.hovered else config.COLOR_BUTTON
            text_color   = config.COLOR_TEXT if self.hovered else config.COLOR_BUTTON_TEXT
            border_color = config.COLOR_ACCENT if self.hovered else config.COLOR_BUTTON_BORDER

        draw_rounded_rect(surface, self.rect, bg, radius=8,
                          border_color=border_color, border_width=1)
        label      = self.font.render(self.text, True, text_color)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)


class SegmentedControl:
    def __init__(self, rect, options, font, selected_index=0, on_change=None, columns=None):
        self.rect           = pygame.Rect(rect)
        self.options        = options
        self.font           = font
        self.selected_index = selected_index
        self.on_change      = on_change
        self.columns        = columns or len(options)
        self._item_rects    = []
        self._hovered       = -1
        self._layout()

    def _layout(self):
        n      = len(self.options)
        cols   = self.columns
        rows   = (n + cols - 1) // cols
        gap    = 4
        item_w = (self.rect.width  - gap * (cols - 1)) / cols
        item_h = (self.rect.height - gap * (rows - 1)) / rows
        self._item_rects = []
        for i in range(n):
            row = i // cols
            col = i % cols
            x   = self.rect.x + col * (item_w + gap)
            y   = self.rect.y + row * (item_h + gap)
            self._item_rects.append(pygame.Rect(int(x), int(y), int(item_w), int(item_h)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hovered = next((i for i, r in enumerate(self._item_rects)
                                  if r.collidepoint(event.pos)), -1)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._item_rects):
                if r.collidepoint(event.pos):
                    if i != self.selected_index:
                        self.selected_index = i
                        if self.on_change:
                            self.on_change(self.options[i][0])
                    return True
        return False

    def selected_key(self):
        return self.options[self.selected_index][0]

    def set_selected_key(self, key):
        for i, (k, _) in enumerate(self.options):
            if k == key:
                self.selected_index = i
                return

    def draw(self, surface):
        # Background track
        draw_rounded_rect(surface, self.rect, config.COLOR_PANEL_LIGHT, radius=9,
                          border_color=config.COLOR_PANEL_BORDER, border_width=1)
        for i, r in enumerate(self._item_rects):
            active  = i == self.selected_index
            hovered = i == self._hovered and not active
            if active:
                bg         = config.COLOR_ACCENT_DARK
                text_color = config.COLOR_TEXT_ACCENT
                border     = config.COLOR_ACCENT
            elif hovered:
                bg         = config.COLOR_BUTTON_HOVER
                text_color = config.COLOR_TEXT
                border     = config.COLOR_BUTTON_BORDER
            else:
                bg         = None
                text_color = config.COLOR_TEXT_DIM
                border     = None
            if bg:
                draw_rounded_rect(surface, r, bg, radius=7,
                                  border_color=border, border_width=1)
            label      = self.font.render(self.options[i][1], True, text_color)
            label_rect = label.get_rect(center=r.center)
            clip = r.clip(surface.get_clip()) if surface.get_clip() else r
            surface.set_clip(r)
            surface.blit(label, label_rect)
            surface.set_clip(None)


class Slider:
    def __init__(self, rect, min_value, max_value, value, font,
                 label="", on_change=None, integer=True):
        self.rect      = pygame.Rect(rect)
        self.min_value = min_value
        self.max_value = max_value
        self.value     = value
        self.font      = font
        self.label     = label
        self.on_change = on_change
        self.integer   = integer
        self.dragging  = False

    def _value_to_x(self):
        ratio = (self.value - self.min_value) / max(1e-9, (self.max_value - self.min_value))
        return self.rect.x + ratio * self.rect.width

    def _x_to_value(self, x):
        ratio = (x - self.rect.x) / max(1, self.rect.width)
        ratio = max(0.0, min(1.0, ratio))
        value = self.min_value + ratio * (self.max_value - self.min_value)
        return int(round(value)) if self.integer else round(value, 2)

    def handle_event(self, event):
        handle_x    = self._value_to_x()
        handle_rect = pygame.Rect(handle_x - 10, self.rect.centery - 10, 20, 20)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                new_val = self._x_to_value(event.pos[0])
                if new_val != self.value:
                    self.value = new_val
                    if self.on_change:
                        self.on_change(self.value)
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_val = self._x_to_value(event.pos[0])
            if new_val != self.value:
                self.value = new_val
                if self.on_change:
                    self.on_change(self.value)
            return True
        return False

    def draw(self, surface):
        # Track background
        track_h    = 6
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - track_h // 2,
                                 self.rect.width, track_h)
        draw_rounded_rect(surface, track_rect, config.COLOR_PANEL_LIGHT, radius=3,
                          border_color=config.COLOR_PANEL_BORDER, border_width=1)

        # Filled portion
        fill_w = max(0, int(self._value_to_x() - self.rect.x))
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.centery - track_h // 2,
                                    fill_w, track_h)
            draw_rounded_rect(surface, fill_rect, config.COLOR_ACCENT, radius=3)

        # Handle knob
        hx = int(self._value_to_x())
        hy = self.rect.centery
        pygame.draw.circle(surface, config.COLOR_ACCENT_DARK, (hx, hy), 10)
        pygame.draw.circle(surface, config.COLOR_TEXT_ACCENT,  (hx, hy), 7)
        pygame.draw.circle(surface, config.COLOR_ACCENT,       (hx, hy), 10, width=2)

        if self.label:
            label_surf = self.font.render(f"{self.label}: {self.value}",
                                          True, config.COLOR_TEXT)
            surface.blit(label_surf, (self.rect.x, self.rect.y - 22))


class ScrollArea:
    def __init__(self, rect, content_height=0, scrollbar_width=5):
        self.rect           = pygame.Rect(rect)
        self.content_height = max(0, content_height)
        self.scrollbar_width = scrollbar_width
        self.offset         = 0.0
        self._dragging_bar  = False
        self._drag_grab_dy  = 0.0

    def set_content_height(self, content_height):
        self.content_height = max(0, content_height)
        self.offset = min(self.offset, self.max_offset())

    def max_offset(self):
        return max(0.0, self.content_height - self.rect.height)

    def needs_scroll(self):
        return self.content_height > self.rect.height + 1

    def _bar_geometry(self):
        track_h      = self.rect.height
        visible_ratio = min(1.0, self.rect.height / max(1, self.content_height))
        bar_h        = max(28, int(track_h * visible_ratio))
        max_off      = self.max_offset()
        ratio        = (self.offset / max_off) if max_off > 0 else 0.0
        bar_y        = self.rect.y + int((track_h - bar_h) * ratio)
        bar_x        = self.rect.right - self.scrollbar_width - 2
        return pygame.Rect(bar_x, bar_y, self.scrollbar_width, bar_h)

    def scroll_by(self, dy_px):
        if not self.needs_scroll():
            self.offset = 0.0
            return
        self.offset = max(0.0, min(self.max_offset(), self.offset + dy_px))

    def handle_event(self, event):
        if not self.needs_scroll():
            return False

        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_by(-event.y * 40)
                return True
            return False

        bar_rect = self._bar_geometry()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if bar_rect.collidepoint(event.pos):
                self._dragging_bar  = True
                self._drag_grab_dy  = event.pos[1] - bar_rect.y
                return True
            return False

        elif event.type == pygame.MOUSEBUTTONUP:
            if self._dragging_bar:
                self._dragging_bar = False
                return True

        elif event.type == pygame.MOUSEMOTION and self._dragging_bar:
            track_h = self.rect.height
            bar_h   = bar_rect.height
            ratio   = (event.pos[1] - self._drag_grab_dy - self.rect.y) / max(1, track_h - bar_h)
            self.offset = max(0.0, min(self.max_offset(), ratio * self.max_offset()))
            return True

        return False

    def draw(self, surface):
        if not self.needs_scroll():
            return
        sw = self.scrollbar_width
        track_rect = pygame.Rect(self.rect.right - sw - 2, self.rect.y, sw, self.rect.height)
        draw_rounded_rect(surface, track_rect, config.COLOR_PANEL_LIGHT, radius=sw // 2,
                          border_color=config.COLOR_PANEL_BORDER, border_width=1)
        bar_rect  = self._bar_geometry()
        bar_color = config.COLOR_ACCENT if self._dragging_bar else (100, 108, 140)
        draw_rounded_rect(surface, bar_rect, bar_color, radius=sw // 2)


class Checkbox:
    def __init__(self, rect, text, font, checked=False, on_change=None):
        self.rect      = pygame.Rect(rect)
        self.text      = text
        self.font      = font
        self.checked   = checked
        self.on_change = on_change

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.on_change:
                    self.on_change(self.checked)
                return True
        return False

    def draw(self, surface):
        box_rect = pygame.Rect(self.rect.x, self.rect.y, 20, 20)
        bg       = config.COLOR_ACCENT_DARK if self.checked else config.COLOR_PANEL_LIGHT
        draw_rounded_rect(surface, box_rect, bg, radius=5,
                          border_color=config.COLOR_ACCENT if self.checked else config.COLOR_PANEL_BORDER,
                          border_width=2)
        if self.checked:
            pygame.draw.line(surface, config.COLOR_TEXT_ACCENT,
                             (box_rect.x + 4, box_rect.centery),
                             (box_rect.x + 8, box_rect.bottom - 5), 2)
            pygame.draw.line(surface, config.COLOR_TEXT_ACCENT,
                             (box_rect.x + 8, box_rect.bottom - 5),
                             (box_rect.right - 4, box_rect.y + 4), 2)
        label = self.font.render(self.text, True, config.COLOR_TEXT)
        surface.blit(label, (box_rect.right + 10, self.rect.y + 1))


class TextInput:
    def __init__(self, rect, font, text="", numeric=False, max_len=6):
        self.rect    = pygame.Rect(rect)
        self.font    = font
        self.text    = text
        self.numeric = numeric
        self.max_len = max_len
        self.active  = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            return self.active
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB):
                self.active = False
            else:
                ch = event.unicode
                if ch and len(self.text) < self.max_len:
                    if self.numeric:
                        if ch.isdigit():
                            self.text += ch
                    else:
                        if ch.isprintable():
                            self.text += ch
            return True
        return False

    def draw(self, surface):
        border_color = config.COLOR_ACCENT if self.active else config.COLOR_PANEL_BORDER
        draw_rounded_rect(surface, self.rect, config.COLOR_PANEL_LIGHT, radius=7,
                          border_color=border_color, border_width=2)
        label = self.font.render(self.text, True, config.COLOR_TEXT)
        surface.blit(label, label.get_rect(midleft=(self.rect.x + 10, self.rect.centery)))
