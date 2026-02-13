import pygame
import chess
import os
import requests
import sys
import time
try:
    from PIL import Image
except ImportError:
    Image = None
from constants import BOARD_WIDTH, BOARD_HEIGHT, PANEL_WIDTH, WIDTH, HEIGHT, DIMENSION, SQ_SIZE, ASSET_PATH, SERVER_URL, INITIAL_TIME
from styles import LIGHT_SQ_COLOR, DARK_SQ_COLOR, HIGHLIGHT_COLOR, POPUP_BG_COLOR, POPUP_TEXT_COLOR, PANEL_COLOR, PANEL_TEXT_COLOR, BUTTON_COLOR, BUTTON_TEXT_COLOR, CLOCK_COLOR
from utils.get_font import get_font
from explain_panel import ExplainPanel

class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")
        self.board = chess.Board()
        self.pieces = self.load_piece_images()
        self.selected_square = None
        self.player_turn = chess.WHITE
        self.game_mode = None
        self.popup_message = None
        self.popup_timer = 0
        self.explanation_message = "Welcome to Chess! Select a mode to start."
        self.move_list = []
        self.white_time = INITIAL_TIME
        self.black_time = INITIAL_TIME
        self.last_move_time = time.time()
        self.is_thinking = False # New flag to block input
        self.explain_panel = ExplainPanel(width=300)
        self.explain_panel.update("-", "Welcome to Chess! Select a mode to start.", "No commentary yet.")

    def load_piece_images(self):
        pieces = {}
        for filename in os.listdir(ASSET_PATH):
            if filename.endswith(".png"):
                piece_name = filename[:-4]
                path = os.path.join(ASSET_PATH, filename)
                try:
                    image = pygame.image.load(path)
                except pygame.error:
                    if Image:
                        pil_img = Image.open(path)
                        image = pygame.image.fromstring(pil_img.tobytes(), pil_img.size, pil_img.mode)
                    else:
                        raise

                pieces[piece_name] = pygame.transform.scale(
                    image, (SQ_SIZE, SQ_SIZE)
                )
        return pieces

    def draw_board(self):
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                color = LIGHT_SQ_COLOR if (r + c) % 2 == 0 else DARK_SQ_COLOR
                pygame.draw.rect(
                    self.screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                )

    def draw_pieces(self):
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                square = chess.square(c, DIMENSION - 1 - r)
                piece = self.board.piece_at(square)
                if piece:
                    piece_symbol = piece.symbol()
                    color_prefix = "w" if piece.color == chess.WHITE else "b"
                    image_key = color_prefix + piece_symbol.upper()
                    self.screen.blit(
                        self.pieces[image_key],
                        pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE),
                    )

    def draw_highlights(self):
        if self.selected_square is not None:
            r, c = self.selected_square // 8, self.selected_square % 8
            r = DIMENSION - 1 - r
            s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
            s.fill(HIGHLIGHT_COLOR)
            self.screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            for move in self.board.legal_moves:
                if move.from_square == self.selected_square:
                    to_r, to_c = move.to_square // 8, move.to_square % 8
                    to_r = DIMENSION - 1 - to_r
                    pygame.draw.circle(
                        self.screen,
                        HIGHLIGHT_COLOR,
                        (to_c * SQ_SIZE + SQ_SIZE // 2, to_r * SQ_SIZE + SQ_SIZE // 2),
                        SQ_SIZE // 6,
                    )

    def draw_panel(self):
        panel_rect = pygame.Rect(BOARD_WIDTH, 0, PANEL_WIDTH, HEIGHT)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel_rect)
        self.explain_panel.draw(self.screen)

    def draw_player_info(self, white_name, black_name):
        white_name_text = get_font(24).render(white_name, True, PANEL_TEXT_COLOR)
        black_name_text = get_font(24).render(black_name, True, PANEL_TEXT_COLOR)
        
        self.screen.blit(black_name_text, (BOARD_WIDTH + 20, 20))
        self.screen.blit(white_name_text, (BOARD_WIDTH + 20, HEIGHT - 80))
    
    def draw_clocks(self):
        white_minutes, white_seconds = divmod(self.white_time, 60)
        black_minutes, black_seconds = divmod(self.black_time, 60)
        
        white_time_str = f"{int(white_minutes):02}:{int(white_seconds):02}"
        black_time_str = f"{int(black_minutes):02}:{int(black_seconds):02}"
        
        font = get_font(30)
        white_time_text = font.render(white_time_str, True, PANEL_TEXT_COLOR)
        black_time_text = font.render(black_time_str, True, PANEL_TEXT_COLOR)
        
        pygame.draw.rect(self.screen, CLOCK_COLOR, (BOARD_WIDTH + 250, HEIGHT - 80, 120, 40), border_radius=5)
        pygame.draw.rect(self.screen, CLOCK_COLOR, (BOARD_WIDTH + 250, 20, 120, 40), border_radius=5)
        
        self.screen.blit(white_time_text, (BOARD_WIDTH + 260, HEIGHT - 75))
        self.screen.blit(black_time_text, (BOARD_WIDTH + 260, 25))


    def draw_move_list(self):
        font = get_font(22)
        y_offset = 80
        for i, move in enumerate(self.move_list):
            move_number = (i // 2) + 1
            if i % 2 == 0:
                text = f"{move_number}. {move}"
                self.screen.blit(font.render(text, True, PANEL_TEXT_COLOR), (BOARD_WIDTH + 20, y_offset))
            else:
                self.screen.blit(font.render(move, True, PANEL_TEXT_COLOR), (BOARD_WIDTH + 150, y_offset))
                y_offset += 30


    def draw_explanation(self):
        font = get_font(20)
        words = self.explanation_message.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < PANEL_WIDTH - 40:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        y = HEIGHT - 200
        for line in lines:
            text = font.render(line, True, PANEL_TEXT_COLOR)
            self.screen.blit(text, (BOARD_WIDTH + 20, y))
            y += font.get_linesize()


    def handle_mouse_click(self, pos):
        if self.game_mode == "pva" and self.player_turn == self.board.turn:
            if pos[0] < BOARD_WIDTH:
                c = pos[0] // SQ_SIZE
                r = DIMENSION - 1 - (pos[1] // SQ_SIZE)
                clicked_square = chess.square(c, r)

                if self.selected_square is None:
                    piece = self.board.piece_at(clicked_square)
                    if piece is not None and piece.color == self.player_turn:
                        self.selected_square = clicked_square
                else:
                    move = chess.Move(self.selected_square, clicked_square)
                    if move in self.board.legal_moves:
                        self.move_list.append(self.board.san(move))
                        self.board.push(move)
                        self.selected_square = None
                        self.explanation_message = "Thinking..."
                        self.explain_panel.update("-", "Thinking...", "Agent is preparing a response.")
                        self.last_move_time = time.time()
                    elif self.board.piece_at(clicked_square) and self.board.piece_at(clicked_square) and self.board.piece_at(clicked_square).color == self.player_turn: # type: ignore
                        self.selected_square = clicked_square
                    else:
                        self.selected_square = None

    def agent_turn(self):
        pgn = str(self.board)
        possible_moves = [move.uci() for move in self.board.legal_moves]
        context = f"{self.game_mode} game. It's your turn."
        request_start = time.time()

        try:
            response = requests.post(SERVER_URL, json={
                "pgn": pgn, "possible_moves": possible_moves, "context": context
            })
            response.raise_for_status()
            data = response.json()
            move = chess.Move.from_uci(data["move"])
            self.move_list.append(self.board.san(move))
            self.board.push(move)
            self.show_popup(data["comment"])
            self.explanation_message = data["explanation"]
            elapsed_ms = int((time.time() - request_start) * 1000)
            thinking_time_ms = data.get("thinking_time_ms", elapsed_ms)
            token_usage = data.get("token_usage")
            self.explain_panel.update(data["move"], data["explanation"], data["comment"])
            self.explain_panel.set_legal_moves(possible_moves)
            self.explain_panel.set_metrics(thinking_time_ms=thinking_time_ms, token_usage=token_usage)
            self.last_move_time = time.time()
        except requests.exceptions.RequestException as e:
            self.show_popup("Error: Could not connect to server.")
            self.explain_panel.update("-", "Could not connect to MCP server.", "No AI response available.")
            self.explain_panel.set_legal_moves(possible_moves)
            self.explain_panel.set_metrics()
            print(e)


    def show_popup(self, message):
        self.popup_message = message
        self.popup_timer = pygame.time.get_ticks()

    def draw_popup(self):
        if self.popup_message and pygame.time.get_ticks() - self.popup_timer < 3000:
            font = get_font(30)
            text = font.render(self.popup_message, True, POPUP_TEXT_COLOR)
            text_rect = text.get_rect(center=(BOARD_WIDTH // 2, BOARD_HEIGHT // 2))
            bg_rect = text_rect.inflate(20, 20)
            pygame.draw.rect(self.screen, POPUP_BG_COLOR, bg_rect, border_radius=10)
            self.screen.blit(text, text_rect)
        else:
            self.popup_message = None

    def select_game_mode(self):
        font = get_font(50)
        pva_text = font.render("Player vs. Agent", True, BUTTON_TEXT_COLOR)
        ava_text = font.render("Agent vs. Agent", True, BUTTON_TEXT_COLOR)
        pva_button = pva_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        ava_button = ava_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

        selecting = True
        while selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pva_button.collidepoint(event.pos):
                        self.game_mode = "pva"
                        selecting = False
                    elif ava_button.collidepoint(event.pos):
                        self.game_mode = "ava"
                        selecting = False
            
            self.screen.fill(PANEL_COLOR)
            pygame.draw.rect(self.screen, BUTTON_COLOR, pva_button.inflate(20, 20), border_radius=10)
            pygame.draw.rect(self.screen, BUTTON_COLOR, ava_button.inflate(20, 20), border_radius=10)
            self.screen.blit(pva_text, pva_button)
            self.screen.blit(ava_text, ava_button)
            pygame.display.flip()

    def run(self):
        self.select_game_mode()
        self.last_move_time = time.time()

        running = True
        while running and not self.board.is_game_over():
            
            # Update clocks
            current_time = time.time()
            time_delta = current_time - self.last_move_time
            if self.board.turn == chess.WHITE:
                self.white_time -= time_delta
            else:
                self.black_time -= time_delta
            self.last_move_time = current_time

            if self.white_time < 0 or self.black_time < 0:
                running = False


            if self.game_mode == "pva" and self.board.turn != self.player_turn:
                self.agent_turn()
            elif self.game_mode == "ava":
                self.explanation_message = f"{'White' if self.board.turn == chess.WHITE else 'Black'} is thinking..."
                self.agent_turn()
                pygame.time.wait(1000)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(pygame.mouse.get_pos())

            self.screen.fill(PANEL_COLOR)
            self.draw_board()
            self.draw_highlights()
            self.draw_pieces()
            self.draw_panel()
            self.draw_popup()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    gui = ChessGUI()
    gui.run()
