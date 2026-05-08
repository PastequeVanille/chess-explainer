#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 git curl

sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker "${SUDO_USER:-ubuntu}"

curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644

echo "K3s bootstrap complete."
echo "Log out and back in once so docker group permissions apply."
echo "kubectl is available through k3s at /usr/local/bin/kubectl"
