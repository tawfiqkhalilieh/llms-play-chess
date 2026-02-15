import pygame

from constants import BOARD_WIDTH, HEIGHT
from styles import CLOCK_COLOR, PANEL_COLOR
from utils.get_font import get_font
from utils.scrollable_textbox import ScrollableTextBox


SECTION_BG_COLOR = (57, 56, 54)
SECTION_BORDER_COLOR = (78, 76, 74)
SECTION_TITLE_COLOR = (245, 245, 245)
SECTION_TEXT_COLOR = (255, 255, 255)
ERROR_TEXT_COLOR = (236, 132, 132)
FLOW_TEXT = "Client -> MCP Server -> LLM Agent -> Move Response"

SECTION_SPECS = [
    ("move_chosen", "Move Chosen", 68, "body"),
    ("ai_thinking", "AI Thinking", 210, "body"),
    ("ai_commentary", "AI Commentary", 88, "body"),
    ("decision_transparency", "Decision Transparency", 126, "small"),
    ("mcp_flow", "MCP Flow", 64, "small"),
    ("metrics", "Metrics", 78, "small"),
]


class ExplainPanel:
    def __init__(self, width: int = 360, margin: int = 20):
        self.width = width
        self.margin = margin
        self.x = BOARD_WIDTH + margin
        self.y = margin
        self.height = HEIGHT - (margin * 2)

        self.move = "N/A"
        self.explanation = "AI reasoning will appear here."
        self.comment = "N/A"
        self.legal_moves: list[str] = []
        self.thinking_time_ms = "N/A"
        self.token_usage = "N/A"
        self.connection_error = False

        self.title_font = get_font(30)
        self.section_title_font = get_font(20)
        self.body_font = get_font(17)
        self.small_font = get_font(16)
        self.header_font = get_font(16)

        self.section_colors = {
            "background": SECTION_BG_COLOR,
            "border": SECTION_BORDER_COLOR,
            "title": SECTION_TITLE_COLOR,
            "text": SECTION_TEXT_COLOR,
            "scrollbar_track": (70, 69, 67),
            "scrollbar_thumb": (132, 132, 130),
        }

        self.section_boxes: dict[str, ScrollableTextBox] = {}
        for key, title, _, font_size in SECTION_SPECS:
            body_font = self.body_font if font_size == "body" else self.small_font
            self.section_boxes[key] = ScrollableTextBox(
                rect=pygame.Rect(0, 0, 0, 0),
                title=title,
                text="N/A",
                title_font=self.section_title_font,
                body_font=body_font,
                colors=self.section_colors,
                padding=10,
            )

    def update(self, move: str, explanation: str, comment: str):
        self.move = move or "N/A"
        self.explanation = explanation or "No explanation provided."
        self.comment = comment or "N/A"
        self.connection_error = False
        self._reset_scroll_positions()

    def set_legal_moves(self, legal_moves: list[str]):
        self.legal_moves = legal_moves[:]

    def set_metrics(self, thinking_time_ms: int | None = None, token_usage: int | None = None):
        self.thinking_time_ms = f"{thinking_time_ms} ms" if thinking_time_ms is not None else "N/A"
        self.token_usage = str(token_usage) if token_usage is not None else "N/A"

    def mark_connection_error(self):
        self.connection_error = True
        self.move = "N/A"
        self.explanation = "N/A"
        self.comment = "N/A"
        self.legal_moves = []
        self.thinking_time_ms = "N/A"
        self.token_usage = "N/A"
        self._reset_scroll_positions()

    def handle_mouse_wheel(self, mouse_pos: tuple[int, int], wheel_y: int):
        for key, _, _, _ in SECTION_SPECS:
            if self.section_boxes[key].handle_mouse_wheel(mouse_pos, wheel_y):
                break

    def draw(self, surface: pygame.Surface):
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, PANEL_COLOR, panel_rect, border_radius=10)
        pygame.draw.rect(surface, CLOCK_COLOR, panel_rect, width=1, border_radius=10)

        inner_rect = pygame.Rect(
            panel_rect.x + 12,
            panel_rect.y + 12,
            panel_rect.width - 24,
            panel_rect.height - 24,
        )

        title_surface = self.title_font.render("Explain Mode", True, SECTION_TITLE_COLOR)
        surface.blit(title_surface, (inner_rect.x, inner_rect.y))

        header_height = self.title_font.get_linesize() + 12
        if self.connection_error:
            error_surface = self.header_font.render("Could not connect to MCP server", True, ERROR_TEXT_COLOR)
            surface.blit(error_surface, (inner_rect.x, inner_rect.y + self.title_font.get_linesize() + 2))
            header_height += self.header_font.get_linesize() + 4

        section_gap = 10
        section_start_y = inner_rect.y + header_height
        available_height = inner_rect.bottom - section_start_y - (section_gap * (len(SECTION_SPECS) - 1))
        if available_height <= 0:
            return

        section_heights = self._scaled_section_heights(available_height)
        section_text = self._section_text()

        cursor_y = section_start_y
        for index, (key, _, _, font_size) in enumerate(SECTION_SPECS):
            section_rect = pygame.Rect(inner_rect.x, cursor_y, inner_rect.width, section_heights[index])
            body_font = self.body_font if font_size == "body" else self.small_font
            section_box = self.section_boxes[key]
            section_box.set_rect(section_rect)
            section_box.set_body_font(body_font)
            section_box.set_text(section_text[key])
            section_box.draw(surface)
            cursor_y += section_heights[index] + section_gap

    def _reset_scroll_positions(self):
        for section_box in self.section_boxes.values():
            section_box.reset_scroll()

    def _section_text(self) -> dict[str, str]:
        if self.connection_error:
            move_text = "N/A"
            explanation_text = "N/A"
            comment_text = "N/A"
            legal_moves_text = "N/A"
            thinking_time_text = "N/A"
            token_usage_text = "N/A"
        else:
            move_text = self.move or "N/A"
            explanation_text = self.explanation or "N/A"
            comment_text = self.comment or "N/A"
            legal_moves_text = ", ".join(self.legal_moves) if self.legal_moves else "N/A"
            thinking_time_text = self.thinking_time_ms or "N/A"
            token_usage_text = self.token_usage or "N/A"

        return {
            "move_chosen": move_text,
            "ai_thinking": explanation_text,
            "ai_commentary": comment_text,
            "decision_transparency": legal_moves_text,
            "mcp_flow": FLOW_TEXT,
            "metrics": f"Thinking time: {thinking_time_text}\nToken usage: {token_usage_text}",
        }

    def _scaled_section_heights(self, available_height: int) -> list[int]:
        min_height = 56
        base_heights = [spec[2] for spec in SECTION_SPECS]
        total_base = sum(base_heights)
        if total_base <= 0:
            return [min_height] * len(SECTION_SPECS)

        scale = available_height / total_base
        section_heights = [max(min_height, int(height * scale)) for height in base_heights]

        overflow = sum(section_heights) - available_height
        for index in [1, 3, 2, 5, 4, 0]:
            if overflow <= 0:
                break
            if index >= len(section_heights):
                continue
            reducible = section_heights[index] - min_height
            if reducible <= 0:
                continue
            reduction = min(reducible, overflow)
            section_heights[index] -= reduction
            overflow -= reduction

        if overflow > 0 and section_heights:
            section_heights[-1] = max(24, section_heights[-1] - overflow)

        remaining_height = available_height - sum(section_heights)
        if remaining_height > 0 and len(section_heights) > 1:
            section_heights[1] += remaining_height

        return section_heights

