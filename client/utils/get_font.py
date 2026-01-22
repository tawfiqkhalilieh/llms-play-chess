import pygame

def get_font(size):
    font_path = pygame.font.match_font('helvetica')
    if font_path:
        return pygame.font.Font(font_path, size)
    return pygame.font.Font(None, size)


