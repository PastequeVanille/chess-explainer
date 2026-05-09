#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 git curl

sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker "${SUDO_USER:-ubuntu}"

if [ ! -f /swapfile ]; then
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
fi

if ! sudo swapon --show | grep -q '^/swapfile'; then
  sudo swapon /swapfile
fi

if ! grep -q '^/swapfile ' /etc/fstab; then
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
fi

curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644

echo "K3s bootstrap complete."
echo "Log out and back in once so docker group permissions apply."
echo "kubectl is available through k3s at /usr/local/bin/kubectl"
echo "A persistent 2G swapfile is enabled to keep small demo instances stable."
