# Learning Path

## Step 1: understand the backend

Read:

- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/logic/game.py`

Questions to ask yourself:

- which route does what?
- where is move legality checked?
- where is the structured explanation created?

## Step 2: understand the frontend

Read:

- `frontend/index.html`
- `frontend/study.js`

Questions to ask yourself:

- where is the current study state stored?
- how does undo and redo work?
- how are notes and annotations saved?

## Step 3: understand the extra knowledge layers

Read:

- `backend/app/logic/wikibooks_openings.py`
- `backend/app/logic/engine.py`
- `backend/app/logic/ai_coach.py`

Key idea:

- the app combines local Python logic, Wikibooks context, engine judgment, and optional AI

## Step 4: understand persistence

Read:

- `backend/app/logic/studies.py`

Key idea:

- a study is saved as structured JSON so the website can remember moves, notes, and annotations
