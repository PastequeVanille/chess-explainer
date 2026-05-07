from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ..models import StudyResponse, StudySummaryResponse, StudyUpdateRequest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STUDY_DIR = PROJECT_ROOT / "data" / "studies"


def list_studies(owner_key: str = "guest") -> list[StudySummaryResponse]:
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


def _write_study(study: StudyResponse, owner_key: str) -> None:
    study_dir = _study_dir(owner_key)
    study_dir.mkdir(parents=True, exist_ok=True)
    _study_path(study.id, owner_key).write_text(study.model_dump_json(indent=2))


def _study_path(study_id: str, owner_key: str) -> Path:
    return _study_dir(owner_key) / f"{study_id}.json"


def _study_dir(owner_key: str) -> Path:
    if owner_key == "guest":
        return STUDY_DIR
    return STUDY_DIR / "users" / owner_key


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()
