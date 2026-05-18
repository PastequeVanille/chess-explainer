from __future__ import annotations

from pydantic import BaseModel, Field


# Pydantic models define the API contract: what the backend accepts and what it
# returns. FastAPI uses them both for validation and for API documentation.
class HealthResponse(BaseModel):
    status: str = "ok"


class EngineStatusResponse(BaseModel):
    enabled: bool
    path: str | None = None


class AiStatusResponse(BaseModel):
    enabled: bool
    model: str


class AuthUserResponse(BaseModel):
    id: str
    email: str
    display_name: str


class AuthStatusResponse(BaseModel):
    authenticated: bool
    user: AuthUserResponse | None = None


class GameStateResponse(BaseModel):
    fen: str
    turn: str
    move_number: int


class LegalMovesResponse(BaseModel):
    from_square: str
    legal_targets: list[str]


class CandidateMoveResponse(BaseModel):
    san: str
    uci: str
    score: str


class OpeningInfoResponse(BaseModel):
    name: str | None = None
    eco: str | None = None
    parent: str | None = None
    summary: str | None = None
    wikibooks_url: str | None = None
    common_responses: list[str] = Field(default_factory=list)


class StudyPhaseResponse(BaseModel):
    key: str = "opening"
    label: str = "Opening"
    title: str = "Opening study"
    meta: str = ""
    summary: str = ""
    ideas: list[str] = Field(default_factory=list)
    continuations_label: str = "Typical replies"
    source_label: str | None = None


class PositionStatusResponse(BaseModel):
    key: str = "in_progress"
    label: str = "In progress"
    summary: str = "The game is still in progress."
    is_check: bool = False
    is_checkmate: bool = False
    is_game_over: bool = False
    result: str | None = None
    winner: str | None = None


class MoveExplanationRequest(BaseModel):
    # Regex validation is useful at the API boundary: it rejects obviously
    # malformed inputs before the service layer starts real chess work.
    fen: str
    from_square: str = Field(pattern=r"^[a-h][1-8]$")
    to_square: str = Field(pattern=r"^[a-h][1-8]$")
    promotion: str | None = Field(default=None, pattern=r"^[qrbn]$")
    move_history_uci: list[str] = Field(default_factory=list)


class EngineMoveRequest(BaseModel):
    fen: str
    move_history_uci: list[str] = Field(default_factory=list)


class MoveExplanationResponse(BaseModel):
    # This response is intentionally rich: the frontend receives one structured
    # payload instead of having to reconstruct the study view from many smaller
    # calls.
    san: str
    uci: str
    fen_after: str
    turn: str
    move_number: int
    headline: str
    bullets: list[str]
    what_happened: list[str] = Field(default_factory=list)
    key_ideas: list[str] = Field(default_factory=list)
    watch_out: list[str] = Field(default_factory=list)
    opening: OpeningInfoResponse = Field(default_factory=OpeningInfoResponse)
    study_phase: StudyPhaseResponse = Field(default_factory=StudyPhaseResponse)
    game_status: PositionStatusResponse = Field(default_factory=PositionStatusResponse)
    engine_evaluation: str | None = None
    ai_summary: str | None = None
    ai_coaching_points: list[str] = Field(default_factory=list)
    ai_verdict: str | None = None
    ai_best_plan: str | None = None
    ai_typical_mistake: str | None = None
    ai_training_takeaway: str | None = None
    ai_error: str | None = None
    best_move_san: str | None = None
    best_move_uci: str | None = None
    best_move_score: str | None = None
    played_move_score: str | None = None
    centipawn_loss: int | None = None
    move_quality: str | None = None
    move_quality_label: str | None = None
    move_quality_summary: str | None = None
    evaluation_bar_white_pct: int | None = None
    candidate_moves: list[CandidateMoveResponse] = Field(default_factory=list)


class EngineMoveResponse(BaseModel):
    uci: str
    san: str
    fen_after: str
    turn: str
    move_number: int
    game_status: PositionStatusResponse = Field(default_factory=PositionStatusResponse)


class ArrowAnnotation(BaseModel):
    from_square: str = Field(pattern=r"^[a-h][1-8]$")
    to_square: str = Field(pattern=r"^[a-h][1-8]$")
    color: str


class HighlightAnnotation(BaseModel):
    square: str = Field(pattern=r"^[a-h][1-8]$")
    color: str


class BoardAnnotations(BaseModel):
    arrows: list[ArrowAnnotation] = Field(default_factory=list)
    highlights: list[HighlightAnnotation] = Field(default_factory=list)


class PositionStudyNote(BaseModel):
    comment: str = ""
    custom_explanation: str = ""


class StudyState(BaseModel):
    # This model is the persistent "study document" stored on disk as JSON.
    title: str
    move_history_uci: list[str] = Field(default_factory=list)
    current_ply: int = 0
    flipped: bool = False
    notes_by_ply: dict[str, PositionStudyNote] = Field(default_factory=dict)
    annotations_by_ply: dict[str, BoardAnnotations] = Field(default_factory=dict)
    analysis_cache_by_ply: dict[str, dict] = Field(default_factory=dict)


class StudyCreateRequest(BaseModel):
    title: str = "Untitled Study"


class StudyUpdateRequest(StudyState):
    pass


class AuthRegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=40)


class AuthLoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)


class StudySummaryResponse(BaseModel):
    id: str
    title: str
    updated_at: str
    move_count: int


class StudyResponse(StudyState):
    id: str
    created_at: str
    updated_at: str
