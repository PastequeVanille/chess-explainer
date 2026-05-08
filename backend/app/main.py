from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from .models import (
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthStatusResponse,
    GameStateResponse,
    HealthResponse,
    EngineStatusResponse,
    AiStatusResponse,
    AuthUserResponse,
    LegalMovesResponse,
    EngineMoveRequest,
    EngineMoveResponse,
    MoveExplanationRequest,
    MoveExplanationResponse,
    StudyCreateRequest,
    StudyResponse,
    StudySummaryResponse,
    StudyUpdateRequest,
)
from .services.chess_service import (
    build_game_timeline,
    compute_engine_move,
    explain_move,
    initial_game_state,
    legal_targets,
)
from .config import get_settings
from .services.study_service import create_study, export_study_markdown, get_study, list_studies, save_study
from .services.auth_service import (
    SESSION_COOKIE_NAME,
    clear_session,
    get_user_for_session,
    login_user,
    owner_key_for_user,
    register_user,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(title="Chess Study")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse()


@app.get("/api/game", response_model=GameStateResponse)
def game() -> GameStateResponse:
    return GameStateResponse(**initial_game_state())


@app.get("/api/engine-status", response_model=EngineStatusResponse)
def engine_status() -> EngineStatusResponse:
    settings = get_settings()
    return EngineStatusResponse(enabled=bool(settings.stockfish_path), path=settings.stockfish_path)


@app.get("/api/ai-status", response_model=AiStatusResponse)
def ai_status() -> AiStatusResponse:
    settings = get_settings()
    return AiStatusResponse(enabled=bool(settings.openai_api_key), model=settings.openai_model)


@app.get("/api/auth/me", response_model=AuthStatusResponse)
def auth_me(request: Request) -> AuthStatusResponse:
    user = _current_user(request)
    return AuthStatusResponse(authenticated=user is not None, user=user)


@app.post("/api/auth/register", response_model=AuthStatusResponse)
def auth_register(payload: AuthRegisterRequest, response: Response) -> AuthStatusResponse:
    try:
        user, session_token = register_user(payload.email, payload.password, payload.display_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _set_session_cookie(response, session_token)
    return AuthStatusResponse(authenticated=True, user=user)


@app.post("/api/auth/login", response_model=AuthStatusResponse)
def auth_login(payload: AuthLoginRequest, response: Response) -> AuthStatusResponse:
    try:
        user, session_token = login_user(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _set_session_cookie(response, session_token)
    return AuthStatusResponse(authenticated=True, user=user)


@app.post("/api/auth/logout", response_model=AuthStatusResponse)
def auth_logout(request: Request, response: Response) -> AuthStatusResponse:
    clear_session(request.cookies.get(SESSION_COOKIE_NAME))
    response.delete_cookie(SESSION_COOKIE_NAME)
    return AuthStatusResponse(authenticated=False, user=None)


@app.get("/api/legal-moves", response_model=LegalMovesResponse)
def get_legal_moves(fen: str, from_square: str) -> LegalMovesResponse:
    return LegalMovesResponse(
        from_square=from_square,
        legal_targets=legal_targets(fen, from_square),
    )


@app.post("/api/explain-move", response_model=MoveExplanationResponse)
def explain(payload: MoveExplanationRequest) -> MoveExplanationResponse:
    try:
        result = explain_move(
            payload.fen,
            payload.from_square,
            payload.to_square,
            payload.promotion,
            payload.move_history_uci,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return MoveExplanationResponse(**result)


@app.post("/api/engine-move", response_model=EngineMoveResponse)
def engine_move(payload: EngineMoveRequest) -> EngineMoveResponse:
    try:
        result = compute_engine_move(payload.fen, payload.move_history_uci)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return EngineMoveResponse(**result)


@app.get("/api/fen-history")
def fen_history(move_history_uci: list[str] = Query(default_factory=list)) -> dict[str, list]:
    try:
        return build_game_timeline(move_history_uci)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/studies", response_model=list[StudySummaryResponse])
def studies(request: Request) -> list[StudySummaryResponse]:
    return list_studies(_owner_key(request))


@app.post("/api/studies", response_model=StudyResponse)
def create_study_endpoint(payload: StudyCreateRequest, request: Request) -> StudyResponse:
    return create_study(payload.title, _owner_key(request))


@app.get("/api/studies/{study_id}", response_model=StudyResponse)
def get_study_endpoint(study_id: str, request: Request) -> StudyResponse:
    try:
        return get_study(study_id, _owner_key(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Study not found") from exc


@app.put("/api/studies/{study_id}", response_model=StudyResponse)
def save_study_endpoint(study_id: str, payload: StudyUpdateRequest, request: Request) -> StudyResponse:
    try:
        return save_study(study_id, payload, _owner_key(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Study not found") from exc


@app.get("/api/studies/{study_id}/export.md")
def export_study_markdown_endpoint(study_id: str, request: Request) -> PlainTextResponse:
    try:
        content = export_study_markdown(study_id, _owner_key(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Study not found") from exc

    return PlainTextResponse(
        content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{study_id}.md"'},
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


def _current_user(request: Request) -> AuthUserResponse | None:
    return get_user_for_session(request.cookies.get(SESSION_COOKIE_NAME))


def _owner_key(request: Request) -> str:
    return owner_key_for_user(_current_user(request))


def _set_session_cookie(response: Response, session_token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
