import chess
import chess.svg
import cairosvg
import os
from constants import PIECES, COLORS, output_dir

def generate_piece_images():

    os.makedirs(output_dir, exist_ok=True)

    for piece_type, piece_symbol in PIECES:
        for color, color_prefix in COLORS:
            piece = chess.Piece(piece_type, color)
            svg_data = chess.svg.piece(piece)
            output_path = os.path.join(output_dir, f"{color_prefix}{piece_symbol}.png")
            cairosvg.svg2png(bytestring=svg_data, write_to=output_path)
            print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_piece_images()
