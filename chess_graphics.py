import pygame
import chess

SQUARE_SIZE = 80
COLORS = [(240, 240, 240), (50, 50, 50)]  # Noir et blanc

BOARD_OFFSET_X = 10  # Décalage horizontal (par exemple, bord gauche)
BOARD_OFFSET_Y = 110  # Décalage vertical (juste sous la bande supérieure)

board_flipped = False

# Chargement des images des pièces
def load_svg_as_surface(svg_path, size):
    """
    Charge un fichier SVG, le convertit en PNG, et retourne une surface compatible avec Pygame.
    :param svg_path: Chemin du fichier SVG.
    :param size: Taille souhaitée de l'image (largeur et hauteur).
    :return: Surface Pygame contenant l'image convertie.
    """
    image = pygame.image.load(svg_path)
    return pygame.transform.smoothscale(image, (size, size))

def load_piece_images(svg_folder_path, square_size):
    """
    Charge toutes les images des pièces d'échecs à partir de fichiers SVG.
    :param svg_folder_path: Dossier contenant les fichiers SVG des pièces.
    :param square_size: Taille des cases de l'échiquier.
    :return: Dictionnaire des surfaces Pygame associées aux pièces.
    """
    piece_images = {}
    piece_filenames = {
        'r': 'bR.svg', 'n': 'bN.svg', 'b': 'bB.svg',
        'q': 'bQ.svg', 'k': 'bK.svg', 'p': 'bP.svg',
        'R': 'wR.svg', 'N': 'wN.svg', 'B': 'wB.svg',
        'Q': 'wQ.svg', 'K': 'wK.svg', 'P': 'wP.svg',
    }
    for piece, filename in piece_filenames.items():
        piece_images[piece] = load_svg_as_surface(f"{svg_folder_path}/{filename}", square_size)
    return piece_images

# Dessiner l'échiquier
def draw_board(screen, square_size, board_flipped, selected_square=None):
    for row in range(8):
        for col in range(8):
            display_row = row if board_flipped else 7 - row
            display_col = 7 - col if board_flipped else col

            x = BOARD_OFFSET_X + display_col * square_size
            y = BOARD_OFFSET_Y + display_row * square_size
            color = COLORS[(row + col) % 2]

            pygame.draw.rect(screen, color, pygame.Rect(x, y, square_size, square_size))

            if selected_square == chess.square(col, row):
                highlight_color = (255, 0, 0)  # Rouge pour la case sélectionnée
                pygame.draw.rect(screen, highlight_color, pygame.Rect(x, y, square_size, square_size), 3)


def draw_pieces(screen, board, piece_images, square_size, board_flipped=False):
    if not isinstance(square_size, int):
        raise TypeError(f"square_size doit être un entier, reçu : {type(square_size)}")
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)  # Index de colonne (0 à 7)
            row = chess.square_rank(square)  # Index de rangée (0 à 7)
            display_col = 7 - col if board_flipped else col
            display_row = row if board_flipped else 7 - row
            x = display_col * square_size + BOARD_OFFSET_X
            y = display_row * square_size + BOARD_OFFSET_Y
            if piece.symbol() in piece_images:
                screen.blit(piece_images[piece.symbol()], (x, y))


# Dessiner les annotations
def draw_annotations(screen, square_size):
    font = pygame.font.Font(None, 24)
    for row in range(8):
        text = font.render(str(8 - row), True, (0, 0, 0))
        screen.blit(text, (BOARD_OFFSET_X - 20, row * square_size + BOARD_OFFSET_Y + square_size // 2 - 10))
    for col in range(8):
        text = font.render(chr(ord('a') + col), True, (0, 0, 0))
        screen.blit(text, (col * square_size + BOARD_OFFSET_X + square_size // 2 - 5, BOARD_OFFSET_Y + 8 * square_size + 5))
