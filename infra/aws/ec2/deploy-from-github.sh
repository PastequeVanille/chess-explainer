#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-$HOME/chess-explainer}"
BRANCH="${2:-main}"

cd "$PROJECT_DIR"

git fetch origin
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"
docker compose -f docker-compose.aws.yml up -d --build

echo "Deployment finished from GitHub branch: $BRANCH"
