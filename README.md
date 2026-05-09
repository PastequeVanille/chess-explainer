# Chess Study

This project is a web-based chess study tool built around Python.

## What it does

- validates and explains moves through a FastAPI backend
- shows opening context from Wikibooks when a page exists
- uses Stockfish for an evaluation bar, best move, candidate continuations, and move labels
- optionally uses OpenAI to write a more natural coaching summary
- lets the user save studies, add comments, edit explanations, and draw board annotations

## Project structure

- `backend/`: API, chess logic, Stockfish integration, Wikibooks integration, study storage
- `frontend/`: browser-based study interface
- `tests/`: automated tests
- `scripts/`: Python scripts for running and testing locally
- `infra/`: Docker and Kubernetes deployment files
- `docs/`: short learning-oriented notes

## Run locally

```bash
cd /Users/guillaume/Documents/CODEX/chess-explainer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_local.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Environment

The backend reads `.env` automatically.

Useful variables:

```bash
STOCKFISH_PATH=/opt/homebrew/bin/stockfish
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5
WIKIBOOKS_USER_AGENT=ChessExplainer/0.1 (your-email@example.com)
```

The AI feature uses `OPENAI_API_KEY`.
It will not work with `APE_KEY`.

## Learning path

1. [01-project-map.md](/Users/guillaume/Documents/CODEX/chess-explainer/docs/01-project-map.md)
2. [02-run-locally.md](/Users/guillaume/Documents/CODEX/chess-explainer/docs/02-run-locally.md)
3. [03-learning-path.md](/Users/guillaume/Documents/CODEX/chess-explainer/docs/03-learning-path.md)
4. [04-engine-analysis.md](/Users/guillaume/Documents/CODEX/chess-explainer/docs/04-engine-analysis.md)
5. [05-aws-free-deploy.md](/Users/guillaume/Documents/CODEX/chess-explainer/docs/05-aws-free-deploy.md)
6. [06-k3s-dynatrace.md](/Users/guillaume/Documents/CODEX/chess-explainer/docs/06-k3s-dynatrace.md)

## Deploy on AWS

For a free-friendly demo, the recommended deployment is a single EC2 instance with Docker Compose.

Use:

- [docker-compose.aws.yml](/Users/guillaume/Documents/CODEX/chess-explainer/docker-compose.aws.yml)
- [bootstrap-ubuntu.sh](/Users/guillaume/Documents/CODEX/chess-explainer/infra/aws/ec2/bootstrap-ubuntu.sh)
- [deploy-from-github.sh](/Users/guillaume/Documents/CODEX/chess-explainer/infra/aws/ec2/deploy-from-github.sh)
- [05-aws-free-deploy.md](/Users/guillaume/Documents/CODEX/chess-explainer/docs/05-aws-free-deploy.md)

This is much cheaper and simpler than Amazon EKS for a first public demo.

## Kubernetes demo path

If you want a real Kubernetes demo without Amazon EKS cost, use:

- [bootstrap-ubuntu.sh](/Users/guillaume/Documents/CODEX/chess-explainer/infra/aws/k3s/bootstrap-ubuntu.sh)
- [deploy-k3s.sh](/Users/guillaume/Documents/CODEX/chess-explainer/infra/aws/k3s/deploy-k3s.sh)
- [06-k3s-dynatrace.md](/Users/guillaume/Documents/CODEX/chess-explainer/docs/06-k3s-dynatrace.md)

For the smallest and most reliable Kubernetes demo on EC2:

- use the K3s path above
- keep Dynatrace optional
- expose the app through the fixed NodePort `31410`
- allow TCP `31410` in the EC2 security group

## GitHub workflow

The repository now includes a CI workflow:

- [.github/workflows/ci.yml](/Users/guillaume/Documents/CODEX/chess-explainer/.github/workflows/ci.yml)

This gives you a clean story:

- develop locally
- push to GitHub
- let GitHub Actions run the tests
- redeploy on EC2 from GitHub
