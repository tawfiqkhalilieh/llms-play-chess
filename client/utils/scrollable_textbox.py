import pygame


DEFAULT_COLORS = {
    "background": (57, 56, 54),
    "border": (78, 76, 74),
    "title": (245, 245, 245),
    "text": (255, 255, 255),
    "scrollbar_track": (70, 69, 67),
    "scrollbar_thumb": (132, 132, 130),
}


class ScrollableTextBox:
    def __init__(
        self,
        rect: pygame.Rect,
        title: str,
        text: str,
        title_font,
        body_font,
        colors: dict | None = None,
        padding: int = 10,
        scroll_step: int = 22,
        scrollbar_width: int = 8,
        scrollbar_gap: int = 6,
    ):
        self.rect = rect.copy()
        self.title = title
        self.text = text or ""
        self.title_font = title_font
        self.body_font = body_font
        self.colors = {**DEFAULT_COLORS, **(colors or {})}
        self.padding = padding
        self.scroll_step = scroll_step
        self.scrollbar_width = scrollbar_width
        self.scrollbar_gap = scrollbar_gap
        self.scroll_offset = 0
        self.max_scroll = 0

        self._title_gap = 6
        self._wrapped_lines: list[str] = []
        self._wrap_cache: dict[tuple[str, int, int], list[str]] = {}
        self._text_rect = pygame.Rect(0, 0, 0, 0)
        self._content_rect = pygame.Rect(0, 0, 0, 0)
        self._line_height = self.body_font.get_linesize()
        self._total_text_height = 0
        self._show_scrollbar = False

    def set_rect(self, rect: pygame.Rect):
        self.rect = rect.copy()

    def set_text(self, text: str):
        normalized = text or ""
        if normalized != self.text:
            self.text = normalized
            self._wrap_cache.clear()

    def set_body_font(self, body_font):
        if body_font != self.body_font:
            self.body_font = body_font
            self._line_height = self.body_font.get_linesize()
            self._wrap_cache.clear()

    def set_title_font(self, title_font):
        if title_font != self.title_font:
            self.title_font = title_font

    def reset_scroll(self):
        self.scroll_offset = 0

    def handle_mouse_wheel(self, mouse_pos: tuple[int, int], wheel_y: int) -> bool:
        if not self.rect.collidepoint(mouse_pos):
            return False
        if self.max_scroll <= 0:
            return False

        updated = self.scroll_offset - (wheel_y * self.scroll_step)
        self.scroll_offset = max(0, min(updated, self.max_scroll))
        return True

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.colors["background"], self.rect, border_radius=8)
        pygame.draw.rect(surface, self.colors["border"], self.rect, width=1, border_radius=8)

        title_x = self.rect.x + self.padding
        title_y = self.rect.y + self.padding
        title_surface = self.title_font.render(self.title, True, self.colors["title"])
        surface.blit(title_surface, (title_x, title_y))

        self._prepare_layout()
        if self._text_rect.width <= 0 or self._text_rect.height <= 0:
            return

        previous_clip = surface.get_clip()
        surface.set_clip(self._text_rect)

        first_line = max(0, self.scroll_offset // self._line_height)
        last_line = min(
            len(self._wrapped_lines),
            ((self.scroll_offset + self._text_rect.height) // self._line_height) + 2,
        )
        y = self._text_rect.y - (self.scroll_offset - (first_line * self._line_height))

        for index in range(first_line, last_line):
            line_surface = self.body_font.render(self._wrapped_lines[index], True, self.colors["text"])
            surface.blit(line_surface, (self._text_rect.x, y))
            y += self._line_height

        surface.set_clip(previous_clip)

        if self._show_scrollbar:
            self._draw_scrollbar(surface)

    def _prepare_layout(self):
        self._line_height = self.body_font.get_linesize()

        content_x = self.rect.x + self.padding
        content_y = self.rect.y + self.padding + self.title_font.get_linesize() + self._title_gap
        content_width = self.rect.width - (self.padding * 2)
        content_height = self.rect.height - (self.padding * 2) - self.title_font.get_linesize() - self._title_gap

        self._content_rect = pygame.Rect(content_x, content_y, max(0, content_width), max(0, content_height))
        if self._content_rect.width <= 0 or self._content_rect.height <= 0:
            self._text_rect = pygame.Rect(0, 0, 0, 0)
            self.max_scroll = 0
            self.scroll_offset = 0
            self._show_scrollbar = False
            return

        lines = self._get_wrapped_lines(self._content_rect.width)
        total_height = len(lines) * self._line_height
        max_scroll = max(0, total_height - self._content_rect.height)
        show_scrollbar = (
            max_scroll > 0
            and self._content_rect.width > (self.scrollbar_width + self.scrollbar_gap + 8)
        )

        if show_scrollbar:
            text_width = self._content_rect.width - self.scrollbar_width - self.scrollbar_gap
            lines = self._get_wrapped_lines(text_width)
            total_height = len(lines) * self._line_height
            max_scroll = max(0, total_height - self._content_rect.height)
            self._text_rect = pygame.Rect(
                self._content_rect.x,
                self._content_rect.y,
                max(0, text_width),
                self._content_rect.height,
            )
        else:
            self._text_rect = self._content_rect.copy()

        self._wrapped_lines = lines
        self._total_text_height = total_height
        self.max_scroll = max_scroll
        self._show_scrollbar = show_scrollbar and self.max_scroll > 0

        if self.max_scroll <= 0:
            self.scroll_offset = 0
        else:
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

    def _draw_scrollbar(self, surface: pygame.Surface):
        track_rect = pygame.Rect(
            self._text_rect.right + self.scrollbar_gap,
            self._content_rect.y,
            self.scrollbar_width,
            self._content_rect.height,
        )
        pygame.draw.rect(surface, self.colors["scrollbar_track"], track_rect, border_radius=4)

        thumb_height = max(
            18,
            int(track_rect.height * (track_rect.height / max(1, self._total_text_height))),
        )
        thumb_height = min(track_rect.height, thumb_height)
        travel = max(0, track_rect.height - thumb_height)

        thumb_y = track_rect.y
        if self.max_scroll > 0 and travel > 0:
            thumb_y += int((self.scroll_offset / self.max_scroll) * travel)

        thumb_rect = pygame.Rect(track_rect.x, thumb_y, track_rect.width, thumb_height)
        pygame.draw.rect(surface, self.colors["scrollbar_thumb"], thumb_rect, border_radius=4)

    def _get_wrapped_lines(self, max_width: int) -> list[str]:
        safe_width = max(1, int(max_width))
        cache_key = (self.text, safe_width, id(self.body_font))
        cached = self._wrap_cache.get(cache_key)
        if cached is not None:
            return cached

        wrapped = self._wrap_text(self.text, safe_width)
        self._wrap_cache[cache_key] = wrapped
        return wrapped

    def _wrap_text(self, text: str, max_width: int) -> list[str]:
        if not text:
            return [""]

        wrapped: list[str] = []
        paragraphs = str(text).splitlines()
        if not paragraphs:
            return [""]

        for paragraph in paragraphs:
            if not paragraph.strip():
                wrapped.append("")
                continue

            words = paragraph.split()
            current_line = ""

            for word in words:
                chunks = [word]
                if self.body_font.size(word)[0] > max_width:
                    chunks = self._split_long_word(word, max_width)

                for chunk in chunks:
                    if not current_line:
                        current_line = chunk
                        continue

                    candidate = f"{current_line} {chunk}"
                    if self.body_font.size(candidate)[0] <= max_width:
                        current_line = candidate
                    else:
                        wrapped.append(current_line)
                        current_line = chunk

            if current_line:
                wrapped.append(current_line)

        return wrapped if wrapped else [""]

    def _split_long_word(self, word: str, max_width: int) -> list[str]:
        if max_width <= 0:
            return [word]

        chunks: list[str] = []
        remaining = word

        while remaining:
            if self.body_font.size(remaining)[0] <= max_width:
                chunks.append(remaining)
                break

            low = 1
            high = len(remaining)
            best = 1

            while low <= high:
                mid = (low + high) // 2
                piece = remaining[:mid]
                if self.body_font.size(piece)[0] <= max_width:
                    best = mid
                    low = mid + 1
                else:
                    high = mid - 1

            chunks.append(remaining[:best])
            remaining = remaining[best:]

        return chunks
