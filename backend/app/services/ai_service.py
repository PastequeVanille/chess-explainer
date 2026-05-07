from __future__ import annotations

from pydantic import BaseModel

import chess
from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, BadRequestError

from ..config import get_settings


class AiMoveExplanation(BaseModel):
    verdict: str
    best_plan: str
    typical_mistake: str
    training_takeaway: str


def generate_ai_explanation(
    board_before: chess.Board,
    board_after: chess.Board,
    san: str,
    headline: str,
    bullets: list[str],
    engine_evaluation: str | None,
    move_quality_label: str | None,
    move_quality_summary: str | None,
    best_move_san: str | None,
    centipawn_loss: int | None,
    client: object | None = None,
) -> dict[str, str | list[str]] | None:
    settings = get_settings()
    if client is None:
        client = _build_client(settings.openai_api_key)
    if client is None:
        return None

    try:
        response = client.responses.parse(
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are an English-speaking chess coach. Explain the move simply for an improving player. "
                        "Be concrete, educational, and avoid jargon when possible. "
                        "Use the engine verdict to explain why the move is good, bad, inaccurate, or interesting. "
                        "Write like a study coach, not like a generic chatbot."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Explain this chess move in English.\n"
                        f"Headline: {headline}\n"
                        f"SAN: {san}\n"
                        f"FEN before: {board_before.fen()}\n"
                        f"FEN after: {board_after.fen()}\n"
                        f"Local bullets: {' | '.join(bullets)}\n"
                        f"Engine evaluation: {engine_evaluation or 'not available'}\n"
                        f"Move quality: {move_quality_label or 'not available'}\n"
                        f"Move quality summary: {move_quality_summary or 'not available'}\n"
                        f"Best move according to engine: {best_move_san or 'not available'}\n"
                        f"Centipawn loss: {centipawn_loss if centipawn_loss is not None else 'not available'}\n"
                        "Return exactly these four fields:\n"
                        "1. verdict: short explanation of whether the move is good, bad, inaccurate, or interesting.\n"
                        "2. best_plan: the main plan or practical continuation to keep in mind.\n"
                        "3. typical_mistake: the common mistake or danger to avoid in this position.\n"
                        "4. training_takeaway: one memorable lesson the player should keep."
                    ),
                },
            ],
            text_format=AiMoveExplanation,
        )
        parsed = response.output_parsed
        return {
            "verdict": parsed.verdict,
            "best_plan": parsed.best_plan,
            "typical_mistake": parsed.typical_mistake,
            "training_takeaway": parsed.training_takeaway,
        }
    except AuthenticationError:
        return {"error": "Authentication failed. Check OPENAI_API_KEY."}
    except BadRequestError as exc:
        return {"error": f"Bad AI request: {exc.__class__.__name__}."}
    except (APIConnectionError, APITimeoutError):
        return {"error": "OpenAI connection failed. Check your internet access."}
    except APIError as exc:
        return {"error": f"OpenAI API error: {exc.__class__.__name__}."}
    except Exception as exc:
        return {"error": f"Unexpected AI error: {exc.__class__.__name__}."}


def _build_client(api_key: str | None) -> object | None:
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    return OpenAI(api_key=api_key)
