import requests
from lxml import html
from bs4 import BeautifulSoup
import chess
import chess.pgn

def generate_wikichess_url(moves):
    """
    Génère l'URL correcte pour la page d'ouverture de Wikibooks en fonction des coups joués.
    Convertit les coups UCI en notation SAN.
    :param moves: Liste des coups en UCI (exemple : ["e2e4", "e7e5", "g1f3"]).
    :return: URL complète vers Wikibooks.
    """
    try:
        # Base de l'URL
        url_base = "https://en.wikibooks.org/wiki/Chess_Opening_Theory/"
        
        # Créer un échiquier
        board = chess.Board()
        
        # Initialiser les parties de l'URL
        url_parts = []
        
        for i, move_uci in enumerate(moves):
            # Créer un objet coup à partir de UCI
            move = chess.Move.from_uci(move_uci)
            
            # Vérifier si le coup est légal pour l'échiquier
            if not move in board.legal_moves:
                raise ValueError(f"Le coup {move_uci} n'est pas légal dans la position actuelle.")
            
            # Jouer le coup et convertir en notation algébrique (SAN)
            san_move = board.san(move)
            
            # Ajouter le coup au bon format
            if i % 2 == 0:  # Blancs
                url_parts.append(f"{i // 2 + 1}._{san_move}")
            else:  # Noirs
                url_parts.append(f"{i // 2 + 1}...{san_move}")
            
            # Appliquer le coup à l'échiquier
            board.push(move)
        
        # Joindre les parties de l'URL avec "/"
        url = url_base + '/'.join(url_parts)
        return url
    
    except Exception as e:
        return f"Erreur lors de la génération de l'URL : {str(e)}"





def fetch_opening_explanation_from_wikichess(url):
    """
    Récupère une explication sur une ouverture à partir de Wikichess, en excluant les sections indésirables comme les liens et bas de page.
    :param url: URL de la page Wikibooks pour l'ouverture.
    :return: Dictionnaire contenant le titre, une explication détaillée et l'URL source.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vérifie si la requête est réussie
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraction du titre de la page
        title = soup.find('h1')
        title = title.get_text().strip() if title else "Titre non trouvé"

        # Suppression des éléments de bas de page, menu de navigation, etc.
        for unwanted_tag in soup(['footer', 'nav', 'aside', 'span']):
            unwanted_tag.decompose()  # Supprime l'élément de l'arbre HTML

        # Nous récupérons maintenant tous les éléments dans le contenu principal
        main_content = soup.find_all(['div', 'article'])

        explanation = ""
        seen_texts = set()  # Ensemble pour stocker les textes déjà ajoutés

        # Traitement des sections pertinentes (div ou article)
        for section in main_content:
            # Traiter les paragraphes <p>
            for paragraph in section.find_all('p'):
                text = paragraph.get_text().strip()
                if text and text not in seen_texts:  # Vérifie si le texte est unique
                    explanation += text + "\n"
                    seen_texts.add(text)

            # Traitement des listes <ul> dans les sections
            for ul in section.find_all('ul'):
                for li in ul.find_all('li'):
                    # Récupérer le texte des éléments <li>
                    text = li.get_text().strip()
                    if text and text not in seen_texts:  # Vérifie si le texte est unique
                        explanation += f"- {text}\n"
                        seen_texts.add(text)

        # Si aucune explication n'a été trouvée, on fournit un message par défaut
        if not explanation:
            explanation = "Aucune explication disponible."

        # Amélioration de l'affichage : mise en forme du message
        explanation = f"**{title}**\n\n" + explanation

        return {
            "title": title,
            "explanation": explanation,
            "source": url
        }

    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return {
                "title": "Page non trouvée",
                "explanation": "La page Wikichess pour cette séquence de coups n'existe pas.",
                "source": url
            }
        return {
            "title": "Erreur HTTP",
            "explanation": f"Erreur d'accès à Wikichess : {e}",
            "source": url
        }
    except Exception as e:
        return {
            "title": "Erreur inconnue",
            "explanation": f"Une erreur est survenue : {e}",
            "source": url
        }
    
    
#url ="https://en.wikibooks.org/wiki/Chess_Opening_Theory/1._d4"     
#explanation = fetch_opening_explanation_from_wikichess(url)
#print(explanation)

#moves = ["e4", "c5", "c3"]
#result = fetch_opening_explanation_from_wikichess(moves)
#print("Titre :", result["title"])
#print("Explication :", result["explanation"])
#print("Source :", result["source"])
