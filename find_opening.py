import chess
import csv
from typing import List, Dict

def normalize_fen(fen: str) -> str:
    """
    Normalise un FEN en supprimant les informations non essentielles
    pour la comparaison d'états d'échiquier.
    Cela peut inclure la suppression des informations sur le nombre de coups
    et les droits de roque, tout en gardant l'échiquier.
    :param fen: FEN à normaliser.
    :return: FEN normalisé sans les informations inutiles pour la comparaison.
    """
    board = chess.Board(fen)
    # Retourne un FEN normalisé : sans les informations sur le nombre de coups, les roques, etc.
    return board.fen().split(' ')[0] + " w - -"

def clean_string(s: str) -> str:
    """
    Nettoie une chaîne en supprimant les espaces et les retours à la ligne.
    :param s: chaîne à nettoyer.
    :return: chaîne nettoyée.
    """
    return s.strip()

def find_opening_by_fen(fen: str, openings_db: List[Dict]) -> Dict:
    """
    Trouve une ouverture correspondant à un FEN donné.
    :param fen: FEN à rechercher.
    :param openings_db: Base de données d'ouvertures (liste de dictionnaires).
    :return: Informations sur l'ouverture (ou "Inconnue").
    """
    normalized_fen_input = normalize_fen(fen)

    # Recherche de l'ouverture correspondante
    for opening in openings_db:
        opening_epd = clean_string(opening.get('epd', ''))
        normalized_opening_epd = normalize_fen(opening_epd)
        # print("normalized_opening_epd = ",normalized_opening_epd)
        # print("normalized_fen_input = ",normalized_fen_input)

        if normalized_fen_input == normalized_opening_epd:
            return {
                "name": opening.get("name", "Inconnue"),
                "eco": opening.get("eco", "N/A"),
                "pgn": opening.get("pgn", ""),
            }
    
    # Si aucune ouverture n'a été trouvée
    return {"name": "Inconnue", "eco": "N/A", "pgn": ""}

def load_openings_from_tsv(file_path: str) -> List[Dict]:
    """
    Charge les données d'ouvertures depuis un fichier TSV.
    :param file_path: chemin vers le fichier TSV.
    :return: Liste de dictionnaires contenant les ouvertures.
    """
    openings = []
    with open(file_path, "r", encoding="utf-8") as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter="\t")
        for row in reader:
            openings.append(row)
    return openings

# Exemple d'utilisation
# fen_input = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
# tsv_file_path = "chess-openings-master/all.tsv"

# Chargement de la base de données des ouvertures
# openings_db = load_openings_from_tsv(tsv_file_path)

# Recherche de l'ouverture correspondant au FEN
# result = find_opening_by_fen(fen_input, openings_db)

# Affichage du résultat
# print(f"Nom de l'ouverture: {result['name']}")
# print(f"Code ECO: {result['eco']}")
# print(f"PGN: {result['pgn']}")
