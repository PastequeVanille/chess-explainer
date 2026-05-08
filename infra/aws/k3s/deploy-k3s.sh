#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-$HOME/chess-explainer}"

cd "$PROJECT_DIR"

docker build -t chess-explainer:k3s .
docker save chess-explainer:k3s | sudo k3s ctr images import -

kubectl apply -f infra/k3s/namespace.yaml
kubectl apply -f infra/k3s/configmap.yaml
kubectl apply -f infra/k3s/deployment.yaml
kubectl apply -f infra/k3s/service.yaml

kubectl -n chess-explainer rollout status deployment/chess-explainer
kubectl -n chess-explainer get svc chess-explainer

echo "K3s deployment completed."
