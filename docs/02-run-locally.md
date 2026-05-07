# Run Locally

## 1. Activate the Python environment

```bash
cd /Users/guillaume/Documents/CODEX/chess-explainer
source .venv/bin/activate
```

## 2. Start the app

```bash
python scripts/run_local.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## 3. Run the tests

```bash
python scripts/run_tests.py
```

## 4. Optional AI setup

Copy `.env.example` to `.env` and set at least:

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5
```
