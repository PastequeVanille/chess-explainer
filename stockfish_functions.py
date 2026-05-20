import chess.engine
import chess
from pathlib import Path

# Configuration Stockfish
STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)



def evaluate_position_with_bar(fen: str):
    """
    Évalue une position FEN et affiche une barre visuellement agréable indiquant si les Blancs ou les Noirs gagnent.
    :param fen: Position en FEN.
    :param stockfish_path: Chemin vers l'exécutable de Stockfish.
    """
    try:
        # Charger l'échiquier avec la position FEN
        board = chess.Board(fen)
        
        # Démarrer le moteur Stockfish
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            # Obtenir l'évaluation de Stockfish
            evaluation = engine.analyse(board, chess.engine.Limit(time=0.1))
            score = evaluation["score"].white().score(mate_score=10000)  # Score pour les blancs
            
            if score is None:
                print("Position trop complexe pour une évaluation.")
                return
            
            # Normaliser le score
            normalized_score = max(min(score / 100, 10), -10)
            
            # Construire la barre de score
            bar_length = 30
            white_length = int((normalized_score + 10) / 20 * bar_length)
            black_length = bar_length - white_length
            
            bar = f"{'█' * white_length}{'░' * black_length}"
            
            # Créer un affichage centré
            print("\n" + "=" * 50)
            print(" Évaluation de la position actuelle ".center(50, " "))
            print("=" * 50)
            print("\n")
            
            # Afficher le score et la barre centrés
            print(f"    Score (positif = avantage Blancs) : {score / 100:.2f}".center(50, " "))
            print(f"    [{bar}]".center(50, " "))
            print("\n" + "=" * 50 + "\n")
    
    except Exception as e:
        print(f"Erreur : {e}")

# Exemple d'utilisation
# fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"

# evaluate_position_with_bar(fen)
