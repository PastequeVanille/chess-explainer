#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 git stockfish

sudo systemctl enable docker
sudo systemctl start docker

sudo usermod -aG docker "${SUDO_USER:-ubuntu}"

echo "Bootstrap complete."
echo "Log out and back in once so docker group permissions apply."
echo "Stockfish path is usually: /usr/games/stockfish"
