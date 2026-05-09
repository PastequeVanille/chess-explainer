# Kubernetes demo path (Dynatrace optional)

This is the best path if you want:

- AWS
- Kubernetes
- and an inexpensive public demo

while still keeping the demo small and realistic.

## Recommendation

Use:

- one Ubuntu EC2 instance
- K3s on that instance
- the app deployed to Kubernetes

This gives you a real Kubernetes deployment without paying the fixed Amazon EKS control-plane cost.

Official references:

- [Amazon EKS pricing](https://aws.amazon.com/eks/pricing/)
- [K3s installation](https://docs.k3s.io/installation)
- [Set up Dynatrace on Kubernetes](https://docs.dynatrace.com/docs/ingest-from/setup-on-k8s)
- [Dynatrace Kubernetes quickstart](https://docs.dynatrace.com/docs/ingest-from/setup-on-k8s/quickstart)
- [Dynatrace Operator](https://docs.dynatrace.com/docs/ingest-from/setup-on-k8s/how-it-works/components/dynatrace-operator)
- [Get started with Dynatrace trial](https://docs.dynatrace.com/docs/get-started/introduction/how-do-i-get-started/)

## Why this path is good

- cheaper than EKS for a demo
- still a real Kubernetes deployment
- easier to explain than a full managed-cluster setup
- enough to show manifests, rollout, health checks, and networking
- stable enough to run on a very small EC2 instance when swap is enabled

## 1. Create the EC2 instance

- Ubuntu LTS
- security group:
  - port 22 for SSH
  - port 31410 for the Kubernetes NodePort demo

## 2. Connect and install K3s

```bash
ssh -i /path/to/your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
git clone https://github.com/PastequeVanille/chess-explainer.git
cd chess-explainer
bash infra/aws/k3s/bootstrap-ubuntu.sh
exit
```

Reconnect once:

```bash
ssh -i /path/to/your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
cd chess-explainer
```

The bootstrap script also creates a persistent 2G swapfile. This matters on small demo instances because K3s is memory-sensitive.

## 3. Deploy the app to K3s

```bash
bash infra/aws/k3s/deploy-k3s.sh
```

Check the deployment:

```bash
kubectl -n chess-explainer get pods
kubectl -n chess-explainer get svc
```

Open the app at:

```text
http://YOUR_EC2_PUBLIC_IP:31410
```

Why `31410`?

- on a small single-node K3s cluster, the simplest reliable public exposure is a `NodePort`
- it avoids the confusion of a cloud load balancer that is not actually provisioned in this demo setup

## 4. Dynatrace is optional

Dynatrace can be added later, but it is not recommended on a tiny 1 GB instance.

What we observed in practice:

- the app plus K3s can run on a very small EC2 instance when swap is enabled
- Dynatrace Operator and related components need more headroom
- for a reliable Dynatrace demo, a larger EC2 instance is the better path

Recommended minimum if you want Dynatrace too:

- `t3.small` as a floor
- `t3.medium` is safer

## 5. What to say in an interview

You can say:

- the public demo runs on AWS EC2
- the orchestration layer is Kubernetes via K3s
- the app is containerized and deployed through manifests
- the deployment is intentionally minimal and robust for a low-cost demo
- Dynatrace was evaluated as the next observability layer, but it needs a slightly larger instance to be reliable
- Amazon EKS is the logical next step if the project needs a managed production-grade control plane

That is a strong answer because it shows staged engineering choices rather than expensive default tooling.
