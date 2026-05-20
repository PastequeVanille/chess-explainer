import pygame
import pygame_gui
import chess
import openai
import os
from pathlib import Path
from stockfish_functions import engine
from Explain_openings_wikibook import fetch_opening_explanation_from_wikichess, generate_wikichess_url
from find_opening import load_openings_from_tsv, find_opening_by_fen
from chess_graphics import draw_board, draw_pieces, draw_annotations, load_piece_images
import time

PROJECT_ROOT = Path(__file__).resolve().parent

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Chargement des ouvertures
tsv_file_path = PROJECT_ROOT / "chess-openings-master" / "all.tsv"
openings_db = load_openings_from_tsv(str(tsv_file_path)) if tsv_file_path.exists() else []


# Initialiser le "clock"
clock = pygame.time.Clock()

# Orientation de l'échiquier
board_flipped = False  # False : Vue classique (blanc en bas), True : Vue inversée (noir en bas)




# Nouvelle hauteur pour inclure la bande supérieure
WIDTH, HEIGHT = 1400, 740  # Hauteur augmentée
SQUARE_SIZE = 80
BOARD_SIZE = SQUARE_SIZE * 8
BAND_HEIGHT = 100  # Hauteur de la bande supérieure

# Nouveaux offsets pour positionner les éléments sous la bande
BOARD_OFFSET_Y = BAND_HEIGHT + 10
TEXT_BOX_OFFSET_Y = BAND_HEIGHT + 10
BOARD_OFFSET_X = 10

# Couleurs
BACKGROUND_COLOR = (20, 20, 20)

# Charger les images des pièces
piece_images = load_piece_images(str(PROJECT_ROOT / "lichess-org lila master public-piece" / "alpha"), SQUARE_SIZE)

try:
    # Optionally, initialize just the mixer module
    pygame.mixer.init()
    # Musique d'arcade
    pygame.mixer.music.load(str(PROJECT_ROOT / "save-as-115826.mp3"))  # Remplacez par le chemin vers votre fichier de musique
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, 0.0)  # Joue la musique en boucle
except pygame.error:
    pass

# Initialisation de Pygame
# Initialize Pygame
pygame.init()


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Échecs interactifs éducatifs")

# Initialisation du gestionnaire Pygame GUI
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

def get_square_from_mouse_pos(pos, board_flipped):
    x, y = pos
    col = (x - BOARD_OFFSET_X) // SQUARE_SIZE
    row = (y - BOARD_OFFSET_Y) // SQUARE_SIZE
    if 0 <= col < 8 and 0 <= row < 8:  # Vérifier que le clic est dans les limites de l'échiquier
        if board_flipped:
            return chess.square(7 - col, row)
        else:
            return chess.square(col, 7 - row)
    return None  # Si clic en dehors de l'échiquier



def show_settings(manager):
    # Crée une fenêtre de réglages
    settings_window_rect = pygame.Rect(400, 200, 600, 400)
    settings_window = pygame_gui.elements.UIWindow(
        rect=settings_window_rect,
        manager=manager,
        window_display_title="Réglages",
        object_id="#settings_window",
    )

    # Contrôle du volume
    volume_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(10, 10, 200, 30),
        text="Volume de la musique :",
        container=settings_window,
        manager=manager,
    )

    volume_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect(220, 10, 300, 30),
        start_value=pygame.mixer.music.get_volume(),
        value_range=(0.0, 1.0),
        container=settings_window,
        manager=manager,
    )

    # Bouton pour fermer le menu
    close_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(200, 350, 200, 40),
        text="Fermer",
        container=settings_window,
        manager=manager,
    )

    # Boucle d'attente pour gérer les interactions avec le menu
    settings_open = True
    while settings_open:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == close_button:
                    settings_open = False

            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == volume_slider:
                    pygame.mixer.music.set_volume(volume_slider.get_current_value())

            manager.process_events(event)

        manager.update(clock.tick(30) / 1000.0)
        screen.fill((50, 50, 50))  # Fond du menu de réglages
        manager.draw_ui(screen)
        pygame.display.flip()
    return True





# Ajuster les positions dans le jeu
text_area_rect = pygame.Rect(BOARD_SIZE + 20, TEXT_BOX_OFFSET_Y, WIDTH - BOARD_SIZE - 30, HEIGHT - BAND_HEIGHT - 20)
text_box = pygame_gui.elements.UITextBox(
    html_text="Bienvenue dans le jeu d'échecs interactif.",
    relative_rect=text_area_rect,
    manager=manager,
    object_id="#scrollable_text_box",
    wrap_to_height=False,
)



# Animation de texte ASCII
def draw_ascii_text(text, y_offset, color=(255, 255, 255)):
    # Définir les couleurs et la police
    FONT = pygame.font.SysFont("Courier New", 24)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        text_surface = FONT.render(line, True, color)
        screen.blit(text_surface, (10, y_offset + i * 30))

# Fonction pour afficher un effet de machine à écrire
def type_effect(text, y_offset, color=(255, 255, 0), speed=0.1):
    # Définir les couleurs et la police
    FONT = pygame.font.SysFont("Courier New", 24)
    lines = text.split("\n")
    for line in lines:
        for i in range(len(line) + 1):
            screen.fill(BACKGROUND_COLOR)  # Efface l'écran pour le rafraîchissement
            draw_board(screen, SQUARE_SIZE,board_flipped)
            draw_ascii_text(line[:i], y_offset, color)
            pygame.display.flip()
            time.sleep(speed)



# Fonction d'écran d'accueil interactif
def show_welcome_screen():
    screen.fill((0, 0, 0))  # Fond noir pour l'écran d'accueil
    type_effect("Bienvenue dans le jeu d'échecs rétro !\nAppuyez ici pour commencer.", 50, color=(0, 255, 0), speed=0.1)
    pygame.display.flip()

    # Ajout d'un bouton pour démarrer le jeu
    start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((BOARD_SIZE // 4, BOARD_SIZE // 1.5), (BOARD_SIZE // 2, 40)),
                                                text='Appuyez ici pour démarrer', manager=manager)
    
    pygame.display.flip()

    # Dans la fonction show_welcome_screen
   # Ajouter un bouton de réglages dans la bande supérieure
    settings_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((10, 10), (200, 40)),  # Position dans la bande supérieure
        text="Réglages",
        manager=manager,
    )




    # Boucle pour l'écran d'accueil
    waiting_for_start = True
    while waiting_for_start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False  # Si on quitte, on arrête le jeu
            manager.process_events(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.rect.collidepoint(event.pos):  # Vérifie si le bouton a été cliqué
                    start_button.kill()
                    return True  # Démarrer le jeu
                if settings_button.rect.collidepoint(event.pos):
                    show_settings(manager)

        manager.update(clock.tick(30) / 1000.0)
        manager.draw_ui(screen)
        pygame.display.flip()

def update_text_box(messages, text_box):
    """
    Met à jour le contenu du text_box avec les messages fournis.

    :param messages: Liste de dictionnaires contenant les messages à afficher.
                     Chaque dictionnaire a une clé 'title' et une clé 'content'.
    :param text_box: Référence à l'objet UITextBox à mettre à jour.
    """
    html_content = "<br>".join(
        [f"<b>{msg['title']}</b><br>{msg['content']}" for msg in messages]
    )
    text_box.html_text = html_content
    text_box.rebuild()
    
    
    
    

def evaluate_position(board, messages):
    # Réinitialisation des messages pour chaque évaluation
    messages.clear()

    # Section 1 : Coup joué
    messages.append({
        "title": "=== Coup joué ===",
        "content": f"Position actuelle (FEN) : {board.fen()}",
        "color": (255, 215, 0)  # Jaune pour le titre
    })

    # Section 2 : Analyse Stockfish
    analysis = engine.analyse(board, chess.engine.Limit(time=1), multipv=3)
    stockfish_content = ""
    evaluation = None  # Pour stocker l'évaluation de la position

    for idx, result in enumerate(analysis, start=1):
        best_move = result["pv"][:5]
        score = result["score"].relative
        score_display = f"M{score.mate()}" if score.is_mate() else f"{score.score() / 100:.2f}"
        stockfish_content += f"{idx}. Coup : {best_move}, Score : {score_display}\n"
        
        if evaluation is None:
            evaluation = score  # On récupère la première évaluation pour l'afficher dans la barre de statistiques

    messages.append({
        "title": "=== Analyse Stockfish ===",
        "content": stockfish_content.strip(),
        "color": (255, 215, 0)  # Jaune pour le titre
    })

    # Section 3 : Informations sur l'ouverture
    fen = board.fen()
    result = find_opening_by_fen(fen, openings_db)
    opening_content = ""
    if result:
        opening_content = f"Ouverture : {result['name']}\nCode ECO : {result['eco']}\nPGN : {result['pgn']}"
    else:
        opening_content = "Aucune ouverture reconnue."
    
    messages.append({
        "title": "=== Informations sur l'ouverture ===",
        "content": opening_content,
        "color": (255, 215, 0)  # Jaune pour le titre
    })

    # Section 4 : Explication Wikibooks
    moves = [move.uci() for move in board.move_stack]
    url = generate_wikichess_url(moves)
    explanation = fetch_opening_explanation_from_wikichess(url)
    if explanation and explanation['explanation']:
        wikibooks_content = explanation['explanation']
    else:
        wikibooks_content = "Explication Wikibooks non disponible.\nVoulez-vous une analyse ChatGPT ?"

    messages.append({
        "title": "=== Explication Wikibooks ===",
        "content": wikibooks_content,
        "color": (255, 215, 0)  # Jaune pour le titre
    })

    # Mettre à jour la zone de texte avec les nouveaux messages
    update_text_box(messages, text_box)

    # Retourner l'évaluation pour afficher la barre de statistiques
    return evaluation

def draw_statistics_bar(screen, evaluation):
    # Dimensions et position
    bar_width = 800
    bar_height = 30
    x = 230  # Après le bouton "Réglages"
    y = (BAND_HEIGHT - bar_height) // 2  # Centrer verticalement dans la bande supérieure

    # Calcul de la largeur et couleur en fonction de l'évaluation
    if evaluation is not None:
        if evaluation == 50.0:
            score = 0.0
        else:
            if evaluation.score() is None:
                score = 10.0
            else:
                score = evaluation.score() / 100
        bar_fill = max(0, min(bar_width, bar_width * abs(score / 10)))
        bar_color = (0, 255, 0) if score > 0 else (255, 0, 0)

        # Dessiner la barre de fond
        pygame.draw.rect(screen, (0, 0, 0), (x - 2, y - 2, bar_width + 4, bar_height + 4))  # Ombre
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 3)  # Bordure blanche rétro

        # Dessiner la barre de progression
        if score < 0:
            pygame.draw.rect(screen, bar_color, (x + bar_width - bar_fill, y, bar_fill, bar_height))
        else:
            pygame.draw.rect(screen, bar_color, (x, y, bar_fill, bar_height))

        # Texte d'évaluation
        font = pygame.font.Font(None, 28)
        text = f"Évaluation : {score:.2f}"
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (x + bar_width + 15, y + 5))


def main():
    if not show_welcome_screen():
        return  # Si l'utilisateur quitte l'écran d'accueil, on arrête le jeu

    # Initialisation de l'échiquier et des outils de gestion
    # Initialisation de l'échiquier et des outils de gestion
    board = chess.Board()
    board_flipped = False

    history = [board.fen()]  # Historique des coups, commence avec l'état initial
    current_index = 0  # Indice de la position actuelle dans l'historique
    running = True
    selected_square = None
    
    # Messages pour l'affichage
    messages = []
    # Messages d'accueil
    messages = [
        {"title": "Bonjour Guillaume", "content": "Utilisez l'échiquier pour jouer vos coups."}
    ]
    update_text_box(messages, text_box)
    
    evaluation = 50.0    
    reverted = False  # Indicateur si nous avons effectué un retour
    
    
    
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.process_events(event)  # Cette ligne permet de traiter les événements de pygame_gui

            # Flèche gauche (Retour en arrière)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:  # Si on appuie sur la flèche gauche pour revenir
                    if current_index > 0:
                        current_index -= 1
                        board.set_fen(history[current_index])  # Revenir à la position précédente
                        messages.append({"title": "Retour", "content": "Retour à la position précédente."})
                        update_text_box(messages, text_box)

                        reverted = True  # Nous avons effectué un retour

            # Flèche droite (Avancer)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:  # Si on appuie sur la flèche droite pour avancer
                    if current_index < len(history) - 1:
                        current_index += 1
                        board.set_fen(history[current_index])  # Revenir à la position suivante
                        messages.append({"title": "Avancer", "content": "Avancé à la position suivante."})
                        update_text_box(messages, text_box)

                        reverted = False  # Annuler l'indicateur de retour


        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # R pour "rotate"
                    board_flipped = not board_flipped


            # Gestion des clics sur l'échiquier
            


            
            
            
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                square = get_square_from_mouse_pos(event.pos, board_flipped)
                if square is not None:
                    if selected_square is not None:  # Déplacement d'une pièce
                        clicked_piece = board.piece_at(square)
                        if clicked_piece and clicked_piece.color == board.turn:
                            selected_square = square
                            messages.append({
                                "title": "Sélection",
                                "content": f"Pièce sélectionnée : {chess.square_name(square)}",
                            })
                            update_text_box(messages, text_box)
                            continue

                        move = chess.Move(selected_square, square)
                        if move in board.legal_moves:
                            board.push(move)
                            # Déplacer la pièce immédiatement (sans attendre le calcul)
                            selected_square = None
                            # Message "Calcul en cours" affiché juste après le déplacement
                            messages = [
                                {"title": "Calcul en cours", "content": "Calcul en cours ..."}# , "color": (255, 255, 255), "bg_color": (0, 0, 0), "font_size": 20, "style": "italic"}
                            ]
                            update_text_box(messages, text_box)
                            pygame.display.flip()
                          
                            if reverted:
                                # Si nous avons effectué un retour, l'historique est réinitialisé.
                                history = history[:current_index + 1]  # Supprimer les coups après le retour
                                reverted = False  # Réinitialiser l'indicateur de retour
                            
                            history.append(board.fen())  # Sauvegarder l'état actuel de la partie
                            current_index += 1  # Mettre à jour l'indice de l'historique
                            # Rafraîchir l'affichage immédiatement après le coup
                            draw_board(screen, SQUARE_SIZE, board_flipped, selected_square)
                            draw_pieces(screen, board, piece_images, SQUARE_SIZE, board_flipped)
                            pygame.display.flip()  # Rafraîchir l'écran tout de suite
      
                            # Effectuer le calcul d'évaluation après avoir déplacé la pièce
                            evaluation = evaluate_position(board, messages)
                            
                            
                            
                            # Ajouter les messages après le calcul
                            messages.append({"title": "Coup joué", "content": f"{move.uci()}", "color": (255, 215, 0)})
                        else:
                            messages.append({"title": "Erreur", "content": "Coup illégal, recommencez.", "color": (255, 0, 0)})
                            selected_square = None
                        # Vérifier si la partie est terminée
                        if board.is_game_over():
                            messages.append({"title": "Fin de la Partie", "content": "La partie est terminée.", "color": (255, 0, 0)})

                        # Mettre à jour les messages après chaque coup
                        update_text_box(messages, text_box)
                        
                    else:  # Sélection d'une pièce
                        if board.piece_at(square) and board.piece_at(square).color == board.turn:
                            selected_square = square
                            messages.append({
                                "title": "Sélection",
                                "content": f"Pièce sélectionnée : {chess.square_name(square)}",
                            })
                            update_text_box(messages, text_box)

        # Mise à jour de l'interface
        screen.fill(BACKGROUND_COLOR)
        draw_board(screen, SQUARE_SIZE, board_flipped, selected_square)
        draw_pieces(screen, board, piece_images, SQUARE_SIZE, board_flipped)
        draw_annotations(screen, SQUARE_SIZE)
        
        # Dessiner la barre de statistiques
        draw_statistics_bar(screen, evaluation)

        manager.update(clock.tick(30) / 1000.0)
        manager.draw_ui(screen)

        pygame.display.flip()

    pygame.quit()

# Lancer le programme
if __name__ == "__main__":
    main()
