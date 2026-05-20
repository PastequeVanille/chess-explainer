from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import chess

from ..schemas import StudyResponse, StudySummaryResponse, StudyUpdateRequest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STUDY_DIR = PROJECT_ROOT / "data" / "studies"


def list_studies(owner_key: str = "guest") -> list[StudySummaryResponse]:
    # `Path` from pathlib gives a cleaner file API than manual string path
    # concatenation.
    study_dir = _study_dir(owner_key)
    study_dir.mkdir(parents=True, exist_ok=True)
    studies: list[StudySummaryResponse] = []
    for path in sorted(study_dir.glob("*.json")):
        payload = json.loads(path.read_text())
        studies.append(
            StudySummaryResponse(
                id=payload["id"],
                title=payload["title"],
                updated_at=payload["updated_at"],
                move_count=len(payload.get("move_history_uci", [])),
            )
        )
    studies.sort(key=lambda item: item.updated_at, reverse=True)
    return studies


def create_study(title: str, owner_key: str = "guest") -> StudyResponse:
    # UUIDs are convenient identifiers when you want unique IDs without a
    # central counter.
    now = _now_iso()
    study = StudyResponse(
        id=str(uuid4()),
        title=title,
        move_history_uci=[],
        current_ply=0,
        flipped=False,
        notes_by_ply={},
        annotations_by_ply={},
        analysis_cache_by_ply={},
        created_at=now,
        updated_at=now,
    )
    _write_study(study, owner_key)
    return study


def get_study(study_id: str, owner_key: str = "guest") -> StudyResponse:
    path = _study_path(study_id, owner_key)
    payload = json.loads(path.read_text())
    return StudyResponse(**payload)


def save_study(study_id: str, payload: StudyUpdateRequest, owner_key: str = "guest") -> StudyResponse:
    # Read-modify-write is a simple persistence pattern when JSON files are good
    # enough for the project scale.
    current = get_study(study_id, owner_key)
    updated = StudyResponse(
        id=current.id,
        title=payload.title,
        move_history_uci=payload.move_history_uci,
        current_ply=payload.current_ply,
        flipped=payload.flipped,
        notes_by_ply=payload.notes_by_ply,
        annotations_by_ply=payload.annotations_by_ply,
        analysis_cache_by_ply=payload.analysis_cache_by_ply,
        created_at=current.created_at,
        updated_at=_now_iso(),
    )
    _write_study(updated, owner_key)
    return updated


def export_study_markdown(study_id: str, owner_key: str = "guest") -> str:
    # This function is a good example of transforming structured data into a
    # human-readable export format.
    study = get_study(study_id, owner_key)
    san_moves = _uci_to_san_moves(study.move_history_uci)

    lines = [
        f"# {study.title}",
        "",
        f"- Study ID: `{study.id}`",
        f"- Created: {study.created_at}",
        f"- Updated: {study.updated_at}",
        f"- Move count: {len(study.move_history_uci)}",
        "",
        "## Move list",
        "",
        _format_move_list(san_moves),
        "",
        "## Position notes",
        "",
    ]

    if not study.move_history_uci:
        lines.append("No moves recorded yet.")
        return "\n".join(lines)

    for ply in range(1, len(study.move_history_uci) + 1):
        cache = study.analysis_cache_by_ply.get(str(ply), {})
        note = study.notes_by_ply.get(str(ply))
        san = san_moves[ply - 1] if ply - 1 < len(san_moves) else study.move_history_uci[ply - 1]
        lines.extend(
            [
                f"### Ply {ply}: {san}",
                "",
                f"Headline: {cache.get('headline') or 'No generated headline.'}",
                "",
            ]
        )

        opening = cache.get("opening") or {}
        if opening.get("name"):
            lines.extend(
                [
                    f"- Opening: {opening['name']}",
                    f"- Opening summary: {opening.get('summary') or 'No summary.'}",
                ]
            )

        for label, key in (
            ("What happened", "what_happened"),
            ("Key ideas", "key_ideas"),
            ("Watch out", "watch_out"),
            ("Full notes", "bullets"),
        ):
            values = cache.get(key) or []
            if not values:
                continue
            lines.append(f"- {label}:")
            lines.extend([f"  - {value}" for value in values])

        if cache.get("ai_verdict"):
            lines.append(f"- Coach verdict: {cache['ai_verdict']}")
        if cache.get("ai_best_plan"):
            lines.append(f"- Best plan: {cache['ai_best_plan']}")
        if cache.get("ai_typical_mistake"):
            lines.append(f"- Typical mistake: {cache['ai_typical_mistake']}")
        if cache.get("ai_training_takeaway"):
            lines.append(f"- Training takeaway: {cache['ai_training_takeaway']}")

        if note and note.comment:
            lines.append(f"- Your comment: {note.comment}")
        if note and note.custom_explanation:
            lines.append(f"- Your edited explanation: {note.custom_explanation}")
        lines.append("")

    return "\n".join(lines)


def _write_study(study: StudyResponse, owner_key: str) -> None:
    study_dir = _study_dir(owner_key)
    study_dir.mkdir(parents=True, exist_ok=True)
    # Pydantic can serialize the whole model directly to JSON, which keeps the
    # persistence code compact.
    _study_path(study.id, owner_key).write_text(study.model_dump_json(indent=2))


def _study_path(study_id: str, owner_key: str) -> Path:
    return _study_dir(owner_key) / f"{study_id}.json"


def _study_dir(owner_key: str) -> Path:
    if owner_key == "guest":
        return STUDY_DIR
    return STUDY_DIR / "users" / owner_key


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _uci_to_san_moves(move_history_uci: list[str]) -> list[str]:
    board = chess.Board()
    san_moves: list[str] = []
    for uci in move_history_uci:
        move = chess.Move.from_uci(uci)
        if move not in board.legal_moves:
            san_moves.append(uci)
            break
        san_moves.append(board.san(move))
        board.push(move)
    return san_moves


def _format_move_list(san_moves: list[str]) -> str:
    if not san_moves:
        return "No moves recorded."

    chunks: list[str] = []
    for index in range(0, len(san_moves), 2):
        move_number = (index // 2) + 1
        white = san_moves[index]
        black = san_moves[index + 1] if index + 1 < len(san_moves) else ""
        chunk = f"{move_number}. {white}"
        if black:
            chunk += f" {black}"
        chunks.append(chunk)
    return " ".join(chunks)
