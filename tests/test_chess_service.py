from backend.app.services import chess_service
from backend.app.services.chess_service import (
    build_game_timeline,
    describe_position,
    explain_move,
    initial_game_state,
    legal_targets,
)


def test_initial_state_is_starting_position() -> None:
    state = initial_game_state()
    assert state["fen"].startswith("rnbqkbnr/pppppppp/")


def test_legal_targets_from_e2() -> None:
    fen = initial_game_state()["fen"]
    assert legal_targets(fen, "e2") == ["e3", "e4"]


def test_explain_move_updates_fen() -> None:
    fen = initial_game_state()["fen"]
    result = explain_move(fen, "e2", "e4", move_history_uci=[])
    assert result["san"] == "e4"
    assert "4P3" in result["fen_after"]
    assert len(result["what_happened"]) >= 1
    assert len(result["key_ideas"]) >= 1
    assert len(result["watch_out"]) >= 1
    assert result["study_phase"]["key"] == "opening"
    assert result["study_phase"]["title"] == "King's Pawn Opening"


def test_illegal_move_raises_value_error() -> None:
    fen = initial_game_state()["fen"]
    try:
        explain_move(fen, "e2", "e5", move_history_uci=[])
    except ValueError as exc:
        assert "Illegal move" in str(exc)
    else:
        raise AssertionError("Expected ValueError for illegal move")


def test_explain_move_keeps_local_coach_when_ai_fails(monkeypatch) -> None:
    fen = initial_game_state()["fen"]

    def _fake_ai(**kwargs):
        return {"error": "OpenAI connection failed. Check your internet access."}

    monkeypatch.setattr(chess_service, "generate_ai_explanation", _fake_ai)
    result = explain_move(fen, "e2", "e4", move_history_uci=[])

    assert result["ai_error"] == "OpenAI connection failed. Check your internet access."
    assert result["ai_verdict"] is not None
    assert result["ai_best_plan"] is not None


def test_explain_move_marks_endgame_positions() -> None:
    fen = "8/8/4k3/3p4/3P4/4K3/8/8 w - - 0 1"
    result = explain_move(fen, "e3", "d3", move_history_uci=[])

    assert result["study_phase"]["key"] == "endgame"
    assert result["study_phase"]["title"] == "Endgame study"


def test_explain_move_supports_promotion() -> None:
    fen = "7k/4P3/8/8/8/8/8/4K3 w - - 0 1"
    result = explain_move(fen, "e7", "e8", promotion="q", move_history_uci=[])

    assert result["uci"] == "e7e8q"
    assert result["san"].startswith("e8")


def test_describe_position_detects_checkmate() -> None:
    status = describe_position("r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4")

    assert status["key"] == "checkmate"
    assert status["is_checkmate"] is True
    assert status["result"] == "1-0"
    assert status["winner"] == "white"


def test_game_timeline_returns_san_with_checkmate_marker() -> None:
    timeline = build_game_timeline(["e2e4", "e7e5", "d1h5", "b8c6", "f1c4", "g8f6", "h5f7"])

    assert timeline["san_history"][-1].endswith("#")
    assert timeline["statuses"][-1]["key"] == "checkmate"
