# Interview study sheet

## Main message to remember

This project is not only a chess project.
It is a Python engineering project with:

- backend logic
- API design
- external integrations
- testing
- documentation
- Git and GitHub
- cloud deployment

## 1. One-sentence pitch

Use this sentence if you need a very short intro:

> I built a Python-based web application that helps users study chess moves and
> positions, save their notes, and access engine and opening context through a
> structured interface.

## 2. Technologies to know by heart

Be comfortable explaining:

- `FastAPI`
- `Pydantic`
- `python-chess`
- `Stockfish`
- `pytest`
- `Git`
- `GitHub`
- `Docker`
- `AWS EC2`
- `K3s`

## 3. Why each technology is there

- `FastAPI`: expose the backend as a clean web API
- `Pydantic`: validate request and response data
- `python-chess`: legal moves, board state, FEN, SAN, UCI
- `Stockfish`: evaluation and candidate moves
- `pytest`: protect the project from regressions
- `Git`: version control
- `GitHub`: repository, sharing, CI
- `Docker`: package the app for deployment
- `AWS EC2`: host the public demo
- `K3s`: lightweight Kubernetes for orchestration

## 4. Good technical points to mention

- separation of frontend and backend
- Python logic modules with focused responsibilities
- local fallback behavior when external logic modules fail
- caching and saved study state
- handling asynchronous-feeling UX even when analysis takes time
- deployment debugging on a small cloud instance

## 5. Good examples of problems you solved

Use one or two of these, not all of them.

- A move was not displayed immediately in the UI, so the user experience felt
  laggy. I changed the flow so the board updates first and the analysis follows.
- The app was still showing opening context after the game had left opening
  theory. I changed the logic so Wikibooks is treated only as an opening source.
- The Kubernetes deployment failed for several different reasons, and I debugged
  them one by one: low memory, swap, image handling, taints, and public network
  exposure.

## 6. Good answers to likely interview questions

### Why did you choose Python?

Because the project is heavily centered on backend logic, chess libraries, and
 rapid iteration.
Python has a strong ecosystem for APIs, testing, parsing, and chess tooling.

### How did you organize your code?

I separated responsibilities by feature and by layer: frontend, backend
logic modules, tests, docs, and infrastructure.
Inside the backend I split the logic into smaller logic modules such as chess
analysis, engine integration, opening lookup, and study persistence.

### How do you document your work?

I document at several levels: README for overview, docs for learning and
deployment notes, and code structure/naming for readability.
The idea is that the project should still be understandable after a long break
or by another developer.

### How do you use Git?

I use Git to keep a clean history, isolate secrets from the repository, track
changes, and make the work easier to review and resume later.
I also use GitHub as the central remote repository and added CI for a more
professional workflow.

### How do you work with others?

Even on a personal project, I try to structure the code in a collaborative way:
clear modules, tests, docs, and explicit project organization so another person
can quickly understand where the logic lives.

### What did you learn from this project?

I strengthened both my Python backend skills and my deployment/debugging skills.
I also learned how quickly infrastructure constraints appear in real-world
deployments, especially with Kubernetes on a small machine.

## 7. Good words and phrases for the interview

Useful phrases:

- "I separated responsibilities"
- "I focused on maintainability"
- "I worked iteratively from user-facing behavior"
- "I added tests to reduce regressions"
- "I tried to keep the project easy to resume later"
- "I used GitHub not only for storage, but for workflow and deployment support"
- "I diagnosed the issue step by step rather than changing many things at once"

## 8. Things to revise before the interview

- What `FastAPI` does
- What `Pydantic` does
- Difference between `FEN`, `SAN`, and `UCI`
- What `Stockfish` is and how it is integrated
- What a `REST API` is
- What `Docker` does
- What `Kubernetes` does at a high level
- What a `pod`, `deployment`, and `service` are
- Difference between `EC2` and `Kubernetes`

## 9. Simple explanation of Kubernetes terms

- `Pod`: the running unit that contains the app container
- `Deployment`: tells Kubernetes how many copies of the app should run
- `Service`: exposes the app inside or outside the cluster
- `NodePort`: exposes the service through a port on the machine
- `Taint`: a rule that can prevent pods from being scheduled on a node

## 10. Best final message

If the discussion opens up at the end, a strong closing idea is:

> What I like about this project is that it combines Python application logic,
> user-oriented product thinking, and practical deployment work.
> It gave me a chance to build something end to end instead of stopping at the
> prototype stage.
