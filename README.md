# Guldan Chess V1

First local pygame version of the chess study project.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
python main.py
```

The app expects Stockfish at:

```bash
/opt/homebrew/bin/stockfish
```

Optional API variables:

```bash
export OPENAI_API_KEY="..."
export LICHESS_TOKEN="..."
```

The app can run without those API variables.

