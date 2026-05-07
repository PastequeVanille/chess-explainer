# Chess Study: support de presentation

## 1. Resume du projet

Ce projet est une application web d'etude d'echecs.
L'objectif est d'aider un joueur a comprendre un coup, une position, une ouverture, puis a construire sa propre fiche d'etude.

Python joue un role central dans:

- l'analyse des coups
- l'integration de Stockfish
- la recuperation du contexte d'ouverture
- la persistence des etudes
- l'API backend avec FastAPI

## 2. Architecture simple

- `backend/`: API FastAPI en Python
- `frontend/`: interface web HTML/CSS/JavaScript
- `tests/`: tests automatises
- `docs/`: documentation projet
- `scripts/`: scripts pour lancer localement et tester

## 3. Ce que vous pouvez raconter sur Python

### Modules et bibliotheques utiles

- `fastapi`: creation de l'API web
- `pydantic`: validation des donnees
- `python-chess`: representation du plateau, legalite des coups, FEN, SAN, UCI
- `chess.engine`: integration de Stockfish
- `httpx`: appels HTTP
- `beautifulsoup4`: parsing HTML pour Wikibooks
- `sqlite3`: base legere pour l'authentification locale
- `pytest`: tests

### Pourquoi Python etait central

- Python permet de prototyper vite
- l'ecosysteme est tres bon pour les API, le parsing, les tests et les outils d'echecs
- le code metier est clairement separe de l'interface

## 4. Methode de travail

Vous pouvez expliquer quelque chose comme:

1. Je pars d'un comportement concret a obtenir.
2. Je separe le projet en petites responsabilites.
3. Je mets la logique metier dans des services Python.
4. J'ajoute des tests pour eviter les regressions.
5. Je documente les choix pour pouvoir reprendre le projet plus tard.

## 5. Documentation

Points a mettre en avant:

- `README.md` pour presenter le projet
- `docs/` pour garder une trace du fonctionnement
- noms de fichiers et de fonctions explicites
- structure du projet simple a relire plusieurs mois plus tard

## 6. Git et gestion de versions

Ce que vous pouvez dire:

- j'utilise Git pour versionner le projet
- je garde hors depot les secrets et donnees generees (`.env`, bases locales, etudes perso)
- je fais des commits propres et explicites
- cela facilite les retours en arriere et les revues

## 7. Travail en equipe

Bon angle pour l'entretien:

- separation backend/frontend pour mieux collaborer
- structure claire pour qu'un autre developpeur retrouve vite la logique
- documentation et tests pour rendre le projet transmissible
- Git pour partager, relire et integrer les changements

## 8. Defis interessants a raconter

- rendre l'application reactive meme quand l'analyse prend du temps
- integrer Stockfish proprement
- gerer des sources externes comme Wikibooks
- rendre la page utile pour l'etude et pas seulement pour afficher un resultat

## 9. Axes d'amelioration honnêtes

Vous pouvez dire que vous voyez encore des evolutions utiles:

- optimisation des performances
- meilleure gestion du cache
- authentification de production
- deploiement cloud plus pousse
- interface encore plus fluide

## 10. Structure possible pour 15 minutes

### 2 minutes

Contexte et objectif du projet.

### 4 minutes

Architecture et place de Python.

### 4 minutes

Modules Python importants et logique metier.

### 3 minutes

Methode de travail, tests, documentation, Git.

### 2 minutes

Ce que vous avez appris et ce que vous feriez ensuite.
