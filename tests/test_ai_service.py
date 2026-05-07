from backend.app.services.ai_service import generate_ai_explanation

import chess


class _FakeParsed:
    verdict = "This is a strong central move that fits the position well."
    best_plan = "Continue with Nf3 and rapid kingside development."
    typical_mistake = "Do not waste time with an early queen move."
    training_takeaway = "Central space matters most when the position is still undeveloped."


class _FakeResponse:
    output_parsed = _FakeParsed()


class _FakeResponses:
    def parse(self, **kwargs):
        return _FakeResponse()


class _FakeClient:
    responses = _FakeResponses()


class _FailingResponses:
    def parse(self, **kwargs):
        raise RuntimeError("boom")


class _FailingClient:
    responses = _FailingResponses()


def test_generate_ai_explanation_returns_none_without_client_or_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    before = chess.Board()
    after = chess.Board()
    after.push_san("e4")
    result = generate_ai_explanation(
        board_before=before,
        board_after=after,
        san="e4",
        headline="Pion joue e4",
        bullets=["Le pion se deplace de e2 vers e4."],
        engine_evaluation=None,
        move_quality_label=None,
        move_quality_summary=None,
        best_move_san=None,
        centipawn_loss=None,
    )
    assert result is None


def test_generate_ai_explanation_parses_structured_result(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    before = chess.Board()
    after = chess.Board()
    after.push_san("e4")
    result = generate_ai_explanation(
        board_before=before,
        board_after=after,
        san="e4",
        headline="Pion joue e4",
        bullets=["Le pion se deplace de e2 vers e4."],
        engine_evaluation="0.30",
        move_quality_label="Good move",
        move_quality_summary="Good move. The move stays close to the engine choice.",
        best_move_san="e4",
        centipawn_loss=8,
        client=_FakeClient(),
    )
    assert result is not None
    assert result["verdict"] == "This is a strong central move that fits the position well."
    assert result["best_plan"] == "Continue with Nf3 and rapid kingside development."


def test_generate_ai_explanation_returns_error_payload_on_failure(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    before = chess.Board()
    after = chess.Board()
    after.push_san("e4")
    result = generate_ai_explanation(
        board_before=before,
        board_after=after,
        san="e4",
        headline="Pawn played e4",
        bullets=["The pawn moves from e2 to e4."],
        engine_evaluation="0.30",
        move_quality_label="Good move",
        move_quality_summary="Good move.",
        best_move_san="e4",
        centipawn_loss=8,
        client=_FailingClient(),
    )
    assert result is not None
    assert "error" in result
