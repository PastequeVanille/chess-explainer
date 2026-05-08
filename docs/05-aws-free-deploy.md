# AWS free-friendly deployment

This is the best simple AWS path for this project if you want something cheap, easy to demo, and fast to deploy.

It also uses GitHub cleanly:

- GitHub stores the source code
- GitHub Actions runs the test suite automatically
- the EC2 server pulls the latest version from GitHub and rebuilds the container

## Recommended path

Use one small Ubuntu EC2 instance and run the whole app with Docker Compose.

Why this path:

- it is much cheaper than Amazon EKS
- it is easier to explain in an interview
- it is enough to show a real public website
- the project already serves frontend and backend from one FastAPI app

## What is not free

Amazon EKS is not really free for a normal demo because the cluster control plane has its own hourly cost.

Official AWS references:

- [Amazon EKS pricing](https://aws.amazon.com/eks/pricing/)
- [AWS Free Tier](https://aws.amazon.com/free/)
- [Track your EC2 Free Tier usage](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html)

## Best demo setup

- 1 EC2 Ubuntu instance
- Docker
- Docker Compose
- Stockfish installed on the VM
- App exposed on port 80

## 1. Create the EC2 instance

Suggested instance:

- free-tier eligible instance if your account allows it
- Ubuntu LTS
- security group:
  - port 22 for SSH
  - port 80 for HTTP

## 2. Connect to the server

```bash
ssh -i /path/to/your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

## 3. Install Docker and Stockfish

From inside the EC2 instance:

```bash
git clone https://github.com/PastequeVanille/chess-explainer.git
cd chess-explainer
bash infra/aws/ec2/bootstrap-ubuntu.sh
exit
```

Reconnect once after that so Docker group permissions apply:

```bash
ssh -i /path/to/your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
cd chess-explainer
```

## 4. Create the production `.env`

Create `.env` on the EC2 instance:

```bash
cat > .env <<'EOF'
STOCKFISH_PATH=/usr/games/stockfish
WIKIBOOKS_USER_AGENT=ChessExplainer/0.1 (your-email@example.com)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5
EOF
```

You can leave `OPENAI_API_KEY` empty if you want to demo without AI.

## 5. Start the app

```bash
docker compose -f docker-compose.aws.yml up -d --build
```

Then open:

```text
http://YOUR_EC2_PUBLIC_IP/
```

## 6. Use GitHub as the source of truth

Recommended workflow:

1. Make your changes locally
2. Commit them
3. Push to GitHub
4. Pull and redeploy on EC2

Local commands:

```bash
git add .
git commit -m "Describe your change"
git push origin main
```

On the EC2 server:

```bash
cd ~/chess-explainer
bash infra/aws/ec2/deploy-from-github.sh
```

That script will:

- fetch from GitHub
- fast-forward pull `main`
- rebuild the Docker image
- restart the app

## 7. GitHub Actions

The project now includes a GitHub Actions workflow:

- [.github/workflows/ci.yml](/Users/guillaume/Documents/CODEX/chess-explainer/.github/workflows/ci.yml)

What it does:

- runs on each push to `main`
- runs on pull requests
- installs Python dependencies
- installs Stockfish
- runs the test suite

This is useful for a portfolio or interview because it shows that GitHub is not only used as storage, but also for automated validation.

## 8. Useful commands

See logs:

```bash
docker compose -f docker-compose.aws.yml logs -f
```

Restart:

```bash
docker compose -f docker-compose.aws.yml up -d --build
```

Stop:

```bash
docker compose -f docker-compose.aws.yml down
```

## 9. What to say in an interview

You can honestly say:

- today, the demo deployment is optimized for simplicity and cost on one EC2 instance
- GitHub is the source repository and GitHub Actions validates the project automatically
- the application is already containerized
- Kubernetes manifests are already present in `infra/k8s/`
- the next production step would be EKS when the project needs scaling and managed orchestration

That is a good engineering answer because it shows cost awareness and staged architecture, not just tool stacking.
