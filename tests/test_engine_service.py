import chess

from backend.app.services.engine_service import analyse_move_with_engine


class _FakeEngine:
    def analyse(self, board, limit, multipv=None):
        fen = board.board_fen()
        if multipv:
            if board.turn == chess.BLACK:
                return [
                    {
                        "pv": [chess.Move.from_uci("c7c5")],
                        "score": chess.engine.PovScore(chess.engine.Cp(45), chess.WHITE),
                    },
                    {
                        "pv": [chess.Move.from_uci("e7e5")],
                        "score": chess.engine.PovScore(chess.engine.Cp(40), chess.WHITE),
                    },
                ]
            return [
                {
                    "pv": [chess.Move.from_uci("e2e4")],
                    "score": chess.engine.PovScore(chess.engine.Cp(50), chess.WHITE),
                },
                {
                    "pv": [chess.Move.from_uci("d2d4")],
                    "score": chess.engine.PovScore(chess.engine.Cp(40), chess.WHITE),
                },
            ]
        if fen.startswith("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR"):
            return {
                "score": chess.engine.PovScore(chess.engine.Cp(45), chess.WHITE),
            }
        return {
            "score": chess.engine.PovScore(chess.engine.Cp(-180), chess.WHITE),
        }


def test_engine_marks_best_move() -> None:
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    result = analyse_move_with_engine(_FakeEngine(), board, move)
    assert result.move_quality == "best"
    assert result.best_move_san == "e4"
    assert result.centipawn_loss == 5
    assert len(result.candidate_moves) >= 2


def test_engine_marks_mistake_for_large_loss() -> None:
    board = chess.Board()
    move = chess.Move.from_uci("a2a3")
    result = analyse_move_with_engine(_FakeEngine(), board, move)
    assert result.move_quality in {"mistake", "blunder"}
    assert result.centipawn_loss > 90
