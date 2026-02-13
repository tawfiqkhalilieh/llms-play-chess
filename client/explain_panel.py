import pygame

from constants import BOARD_WIDTH, HEIGHT
from styles import PANEL_COLOR, PANEL_TEXT_COLOR, CLOCK_COLOR
from utils.get_font import get_font


class ExplainPanel:
    def __init__(self, width: int = 300, margin: int = 20):
        self.width = width
        self.margin = margin
        self.x = BOARD_WIDTH + margin
        self.y = margin
        self.height = HEIGHT - (margin * 2)

        self.move = "-"
        self.explanation = "AI reasoning will appear here."
        self.comment = "-"
        self.legal_moves: list[str] = []
        self.thinking_time_ms = "N/A"
        self.token_usage = "N/A"

    def update(self, move: str, explanation: str, comment: str):
        self.move = move or "-"
        self.explanation = explanation or "No explanation provided."
        self.comment = comment or "-"

    def set_legal_moves(self, legal_moves: list[str]):
        self.legal_moves = legal_moves[:]

    def set_metrics(self, thinking_time_ms: int | None = None, token_usage: int | None = None):
        self.thinking_time_ms = f"{thinking_time_ms} ms" if thinking_time_ms is not None else "N/A"
        self.token_usage = str(token_usage) if token_usage is not None else "N/A"

    def draw(self, surface: pygame.Surface):
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, PANEL_COLOR, panel_rect, border_radius=10)
        pygame.draw.rect(surface, CLOCK_COLOR, panel_rect, width=1, border_radius=10)

        title_font = get_font(28)
        heading_font = get_font(22)
        body_font = get_font(18)
        small_font = get_font(16)

        cursor_y = self.y + 16
        cursor_y = self._draw_text(
            surface, title_font, "Explain Mode", PANEL_TEXT_COLOR, self.x + 14, cursor_y
        ) + 8
        cursor_y = self._draw_divider(surface, cursor_y)

        cursor_y = self._draw_section_label(surface, heading_font, "Move Chosen:", cursor_y)
        cursor_y = self._draw_text(
            surface, body_font, self.move, PANEL_TEXT_COLOR, self.x + 14, cursor_y
        ) + 8

        cursor_y = self._draw_section_label(surface, heading_font, "AI Thinking:", cursor_y)
        cursor_y = self._draw_wrapped_text(
            surface, body_font, self.explanation, PANEL_TEXT_COLOR, self.x + 14, cursor_y, self.width - 28
        ) + 8

        cursor_y = self._draw_section_label(surface, heading_font, "AI Commentary:", cursor_y)
        cursor_y = self._draw_wrapped_text(
            surface, body_font, self.comment, PANEL_TEXT_COLOR, self.x + 14, cursor_y, self.width - 28
        ) + 8

        cursor_y = self._draw_section_label(surface, heading_font, "Decision Transparency:", cursor_y)
        legal_moves_preview = ", ".join(self.legal_moves[:8]) if self.legal_moves else "No legal moves captured."
        if len(self.legal_moves) > 8:
            legal_moves_preview += " ..."
        cursor_y = self._draw_wrapped_text(
            surface, small_font, legal_moves_preview, PANEL_TEXT_COLOR, self.x + 14, cursor_y, self.width - 28
        ) + 8

        cursor_y = self._draw_section_label(surface, heading_font, "MCP Flow:", cursor_y)
        cursor_y = self._draw_wrapped_text(
            surface,
            small_font,
            "Client -> MCP Server -> LLM Agent -> Move Response",
            PANEL_TEXT_COLOR,
            self.x + 14,
            cursor_y,
            self.width - 28,
        ) + 8

        cursor_y = self._draw_section_label(surface, heading_font, "Metrics:", cursor_y)
        cursor_y = self._draw_text(
            surface,
            small_font,
            f"Time: {self.thinking_time_ms}",
            PANEL_TEXT_COLOR,
            self.x + 14,
            cursor_y,
        )
        cursor_y = self._draw_text(
            surface,
            small_font,
            f"Tokens: {self.token_usage}",
            PANEL_TEXT_COLOR,
            self.x + 14,
            cursor_y + 4,
        )

    def _draw_divider(self, surface: pygame.Surface, y: int) -> int:
        pygame.draw.line(
            surface,
            CLOCK_COLOR,
            (self.x + 12, y),
            (self.x + self.width - 12, y),
            1,
        )
        return y + 10

    def _draw_section_label(self, surface: pygame.Surface, font, text: str, y: int) -> int:
        return self._draw_text(surface, font, text, PANEL_TEXT_COLOR, self.x + 14, y)

    def _draw_text(self, surface: pygame.Surface, font, text: str, color, x: int, y: int) -> int:
        rendered = font.render(text, True, color)
        surface.blit(rendered, (x, y))
        return y + font.get_linesize()

    def _draw_wrapped_text(self, surface: pygame.Surface, font, text: str, color, x: int, y: int, max_width: int) -> int:
        words = text.split()
        if not words:
            return y

        lines: list[str] = []
        current_line = words[0]
        for word in words[1:]:
            candidate = f"{current_line} {word}"
            if font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)

        for line in lines:
            rendered = font.render(line, True, color)
            surface.blit(rendered, (x, y))
            y += font.get_linesize()

        return y
