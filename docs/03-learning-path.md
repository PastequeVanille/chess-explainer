# Learning Path

## Step 1: understand the backend

Read:

- `backend/app/main.py`
- `backend/app/models.py`
- `backend/app/services/chess_service.py`

Questions to ask yourself:

- which route does what?
- where is move legality checked?
- where is the structured explanation created?

## Step 2: understand the frontend

Read:

- `frontend/index.html`
- `frontend/app.js`

Questions to ask yourself:

- where is the current study state stored?
- how does undo and redo work?
- how are notes and annotations saved?

## Step 3: understand the extra knowledge layers

Read:

- `backend/app/services/wikibooks_service.py`
- `backend/app/services/engine_service.py`
- `backend/app/services/ai_service.py`

Key idea:

- the app combines local Python logic, Wikibooks context, engine judgment, and optional AI

## Step 4: understand persistence

Read:

- `backend/app/services/study_service.py`

Key idea:

- a study is saved as structured JSON so the website can remember moves, notes, and annotations
