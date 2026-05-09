#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-$HOME/chess-explainer}"
export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"

cd "$PROJECT_DIR"

docker build -t chess-explainer:k3s .
docker save chess-explainer:k3s | sudo k3s ctr images import -

kubectl apply -f infra/k3s/namespace.yaml
kubectl apply -f infra/k3s/configmap.yaml
kubectl apply -f infra/k3s/deployment.yaml
kubectl apply -f infra/k3s/service.yaml

kubectl -n chess-explainer rollout status deployment/chess-explainer --timeout=180s
kubectl -n chess-explainer get pods -o wide
kubectl -n chess-explainer get svc chess-explainer

echo "K3s deployment completed."
echo "Open the app at http://YOUR_EC2_PUBLIC_IP:31410 after allowing TCP/31410 in the EC2 security group."
