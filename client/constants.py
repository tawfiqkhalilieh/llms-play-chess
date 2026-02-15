import os

BOARD_WIDTH, BOARD_HEIGHT = 800, 800
PANEL_WIDTH = 400
WIDTH, HEIGHT = BOARD_WIDTH + PANEL_WIDTH, BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_WIDTH // DIMENSION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_PATH = os.path.join(BASE_DIR, "assets", "pieces")
SERVER_URL = "http://localhost:8000/move"


# this might be better placed in a different file, will leave it for now
import chess

PIECES = [
        (chess.PAWN, "P"),
        (chess.KNIGHT, "N"),
        (chess.BISHOP, "B"),
        (chess.ROOK, "R"),
        (chess.QUEEN, "Q"),
        (chess.KING, "K"),
    ]
COLORS = [(chess.WHITE, "w"), (chess.BLACK, "b")]
output_dir = ASSET_PATH
