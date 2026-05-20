# Python interview oral script

## Goal

This note is meant to help you present the project in 10 to 15 minutes.
It focuses on:

- Python
- engineering method
- documentation
- Git
- teamwork

## Short version of the project

This project is a web-based chess study application.
The goal is to help a player understand a move, study an opening or a position,
and build personal study notes directly in the interface.

Python is the core of the project because it handles:

- the backend API
- move validation
- chess rules
- Stockfish integration
- opening and Wikibooks data retrieval
- study persistence

## Suggested 10 to 15 minute structure

### 1. Context and motivation: 1 to 2 minutes

You can say:

> I restarted a personal chess project that I had begun earlier.
> At first it was a local Python application, but I wanted to turn it into a
> real web application that could be used as a study tool.
> The goal was not only to display moves, but to explain them and help the user
> build a personal training workflow.

### 2. What the application does: 1 to 2 minutes

You can say:

> The application lets a user play through a position on a chessboard, analyze
> moves, see the engine evaluation, detect openings when relevant, and save
> personal notes and annotations.
> It also supports a study mode, a play mode, and a mode against the computer.

### 3. Why Python is central: 2 to 3 minutes

You can say:

> Python is the main language of the project because the core logic is chess
> logic and backend logic.
> I used FastAPI for the web API, Pydantic for data validation, python-chess
> for board representation and legal move handling, and chess.engine for
> Stockfish integration.
> I also used HTTP and HTML parsing libraries to retrieve opening context from
> Wikibooks.

Important libraries to mention:

- `fastapi`
- `pydantic`
- `python-chess`
- `chess.engine`
- `httpx`
- `beautifulsoup4`
- `pytest`

### 4. How the code is organized: 2 minutes

You can say:

> I tried to separate the project into clear responsibilities.
> The frontend is in a dedicated folder, and the backend contains the API and
> the Python logic modules.
> Inside the backend, I separated logic modules such as chess analysis, engine
> integration, opening lookup, Wikibooks retrieval, AI summary generation, and
> study persistence.
> This makes the code easier to maintain and easier for another developer to
> understand.

### 5. Engineering method: 2 minutes

You can say:

> My method was to start from concrete user-facing behaviors.
> For example, if a move was not displayed immediately, or if a position was
> incorrectly still treated as an opening, I traced the behavior, isolated the
> cause, fixed the logic, and then added tests when possible.
> I prefer to work in small iterations: understand the bug, isolate the
> responsibility, implement the fix, verify the result, and document the change.

### 6. Documentation and maintainability: 1 to 2 minutes

You can say:

> I documented the project at several levels.
> There is a README for the project overview, a docs folder for learning notes,
> run instructions, deployment notes, and interview preparation.
> I also tried to keep the naming and file structure simple enough so that the
> project remains understandable even after several months.

### 7. Git and version control: 1 minute

You can say:

> I used Git and GitHub to version the project.
> I kept secrets out of the repository, wrote explicit commits, and used the
> repository not only to store code but also to document deployment and CI.
> I also added a GitHub Actions workflow so that the project has a cleaner and
> more professional workflow.

### 8. Teamwork angle: 1 minute

You can say:

> Even though this is a personal project, I tried to structure it in a way that
> supports collaboration.
> The responsibilities are separated, the documentation is written so another
> developer can pick it up, and the tests reduce the risk of regressions when
> someone else changes a part of the project.

### 9. Technical challenge to highlight: 1 to 2 minutes

Best challenge to mention:

> One interesting challenge was deployment.
> I wanted the project to be publicly accessible, so I containerized it and
> deployed it on AWS.
> Then I also prepared a Kubernetes-based deployment using K3s on EC2.
> During that process I had to debug real infrastructure issues such as low
> memory, swap usage, image availability in K3s, and network exposure through
> the AWS security group.

That is a strong example because it shows:

- debugging
- practical Python deployment
- systems understanding
- ability to go beyond local development

### 10. Honest improvement areas: 1 minute

You can say:

> There are still useful improvements I would like to make, especially around
> performance, production-grade authentication, richer caching, and a more
> advanced deployment pipeline.
> But the project already has a working Python backend, tests, version control,
> documentation, and a real cloud deployment.

## Ready-to-say 3 minute compact version

> I would like to present a chess study web application that I built mainly in
> Python.
> The goal of the project is to help a user understand a move, study an opening
> or a position, and save personal notes directly in the interface.
>
> Python is central in the project because it handles the backend API with
> FastAPI, move validation and chess logic with python-chess, Stockfish engine
> integration, and the retrieval of opening information.
> I also used Pydantic for validation, pytest for tests, and supporting
> libraries for HTTP calls and HTML parsing.
>
> In terms of engineering method, I tried to split the project into clear
> logic modules and to work iteratively from concrete user-facing behaviors.
> For example, I fixed issues around move display timing, opening detection, and
> deployment reliability, then documented the result.
>
> I also used Git and GitHub to structure the work properly, keep secrets out of
> the repository, and maintain a cleaner development workflow.
> Finally, I deployed the application on AWS and prepared a Kubernetes-based
> version using K3s, which gave me practical experience with debugging memory,
> container image handling, and service exposure.

## What not to do in the presentation

- Do not spend too much time on chess theory itself.
- Do not try to explain every feature.
- Do not hide the difficulties.
- Do not say "I just used AI to do it".

Instead:

- explain your decisions
- explain your debugging process
- explain how Python was used
- explain how you made the project easier to maintain
