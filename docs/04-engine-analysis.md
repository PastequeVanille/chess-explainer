# Engine Analysis

## What I added

The app now does more than "show an evaluation".

When `STOCKFISH_PATH` is configured, the backend:

1. asks Stockfish for the best move in the current position
2. evaluates the move you actually played
3. compares both evaluations
4. computes an approximate centipawn loss
5. assigns a label such as:
   `Best move`, `Good move`, `Interesting`, `Inaccuracy`, `Mistake`, `Blunder`

## How to think about centipawn loss

- `100` centipawns = about `1` pawn
- small loss = move is close to the engine choice
- big loss = move gives away part of the advantage or worsens the position

## Current heuristic

The labels are based on the gap between:

- the engine's best move
- your played move

Approximate thresholds:

- `0-30`: good
- `31-90`: inaccuracy
- `91-220`: mistake
- `221+`: blunder

Special cases:

- exact engine first choice -> `Best move`
- playable tactical or unusual idea with low cost -> `Interesting`

## Where it lives in the code

- engine logic: `backend/app/logic/engine.py`
- main move explanation: `backend/app/logic/game.py`
- visual bar and badge: `frontend/study.js`

## Why this is useful

Your project now has three distinct explanation sources:

- rules and heuristics from Python
- opening context from Wikibooks
- evaluation judgment from Stockfish

Then, if OpenAI is enabled, the AI can summarize all that in more natural language.
