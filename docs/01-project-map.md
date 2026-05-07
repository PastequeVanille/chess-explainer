# Project Map

## Main folders

- `backend/`: Python API and chess logic
- `frontend/`: the web interface
- `tests/`: automated checks
- `scripts/`: simple Python entry points
- `infra/`: Docker and Kubernetes files

## Main flow

1. The user clicks or annotates on the board.
2. The frontend sends requests to the Python backend.
3. The backend validates the move.
4. The backend builds a structured explanation.
5. Wikibooks adds opening context when available.
6. Stockfish adds evaluation, candidate moves, and move quality.
7. OpenAI can turn that into a smoother coaching summary.
8. The frontend stores notes, annotations, and study state.
