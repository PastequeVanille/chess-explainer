# Kubernetes + Dynatrace demo path

This is the best path if you want all three at once:

- AWS
- Kubernetes
- Dynatrace

while still keeping the demo small and realistic.

## Recommendation

Use:

- one Ubuntu EC2 instance
- K3s on that instance
- the app deployed to Kubernetes
- Dynatrace trial connected to the cluster

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
- enough to show manifests, rollout, health checks, and observability

## 1. Create the EC2 instance

- Ubuntu LTS
- security group:
  - port 22 for SSH
  - port 80 for HTTP

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

## 3. Deploy the app to K3s

```bash
bash infra/aws/k3s/deploy-k3s.sh
```

Check the service:

```bash
kubectl -n chess-explainer get pods
kubectl -n chess-explainer get svc
```

## 4. Add Dynatrace

Dynatrace is not permanently free, but Dynatrace documentation currently points to a 15-day trial.

For a demo, that is often enough.

High-level flow:

1. Create a Dynatrace trial environment
2. Generate the required tokens in Dynatrace
3. Install Dynatrace Operator in the cluster
4. Create the `DynaKube` resource for the cluster

Start from the official quickstart:

- [Dynatrace Kubernetes quickstart](https://docs.dynatrace.com/docs/ingest-from/setup-on-k8s/quickstart)

## 5. What to say in an interview

You can say:

- the public demo runs on AWS EC2
- the orchestration layer is Kubernetes via K3s
- the app is containerized and deployed through manifests
- Dynatrace provides observability for the cluster and workload
- Amazon EKS is the logical next step if the project needs a managed production-grade control plane

That is a strong answer because it shows staged engineering choices rather than expensive default tooling.
