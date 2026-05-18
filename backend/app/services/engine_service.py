from __future__ import annotations

from dataclasses import dataclass

import chess
import chess.engine


MATE_SCORE = 100000

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}


@dataclass(frozen=True)
class EngineCandidateMove:
    # Dataclasses are useful for structured internal results that are not API
    # models. They are lightweight and readable.
    san: str
    uci: str
    score_display: str


@dataclass(frozen=True)
class EngineMoveAnalysis:
    best_move_uci: str
    best_move_san: str
    best_score_cp: int
    played_score_cp: int
    after_score_cp: int
    best_score_display: str
    played_score_display: str
    after_score_display: str
    centipawn_loss: int
    move_quality: str
    move_quality_label: str
    move_quality_summary: str
    evaluation_bar_white_pct: int
    is_interesting: bool
    candidate_moves: list[EngineCandidateMove]


@dataclass(frozen=True)
class EngineReply:
    uci: str
    san: str
    fen_after: str


def analyse_move_with_engine(
    engine: chess.engine.SimpleEngine,
    board_before: chess.Board,
    move: chess.Move,
) -> EngineMoveAnalysis:
    # Engine integration is split out into its own service so the main chess
    # service stays focused on orchestration.
    info_before = engine.analyse(board_before, chess.engine.Limit(time=0.15), multipv=3)
    # Some libraries can return one dict or a list depending on options. This is
    # a common Python normalization step when working with external APIs.
    if isinstance(info_before, dict):
        info_before = [info_before]

    best_info = info_before[0]
    best_move = best_info["pv"][0]
    best_move_san = board_before.san(best_move)
    best_score_cp = _score_to_white_cp(best_info["score"].white())
    best_score_display = _score_to_display(best_info["score"].white())

    board_after = board_before.copy(stack=True)
    board_after.push(move)
    info_after = engine.analyse(board_after, chess.engine.Limit(time=0.10))
    after_score = info_after["score"].white()
    after_score_cp = _score_to_white_cp(after_score)
    after_score_display = _score_to_display(after_score)
    next_moves = engine.analyse(board_after, chess.engine.Limit(time=0.12), multipv=3)
    if isinstance(next_moves, dict):
        next_moves = [next_moves]

    played_score_cp = after_score_cp
    played_score_display = after_score_display
    centipawn_loss = _centipawn_loss(board_before.turn, best_score_cp, played_score_cp)
    is_interesting = _is_interesting_move(board_before, move, best_move, centipawn_loss)
    move_quality, move_quality_label = _classify_move(centipawn_loss, best_move == move, is_interesting)
    move_quality_summary = _build_quality_summary(
        move_quality=move_quality,
        move_quality_label=move_quality_label,
        centipawn_loss=centipawn_loss,
        best_move_san=best_move_san,
        best_move=best_move,
        move=move,
    )

    return EngineMoveAnalysis(
        best_move_uci=best_move.uci(),
        best_move_san=best_move_san,
        best_score_cp=best_score_cp,
        played_score_cp=played_score_cp,
        after_score_cp=after_score_cp,
        best_score_display=best_score_display,
        played_score_display=played_score_display,
        after_score_display=after_score_display,
        centipawn_loss=centipawn_loss,
        move_quality=move_quality,
        move_quality_label=move_quality_label,
        move_quality_summary=move_quality_summary,
        evaluation_bar_white_pct=_white_bar_percentage(after_score_cp),
        is_interesting=is_interesting,
        candidate_moves=_extract_candidate_moves(board_after, next_moves),
    )


def choose_engine_reply(
    engine: chess.engine.SimpleEngine,
    board: chess.Board,
) -> EngineReply:
    result = engine.play(board, chess.engine.Limit(time=0.18))
    move = result.move
    if move is None:
        raise chess.engine.EngineError("Engine did not return a move")

    san = board.san(move)
    board_after = board.copy(stack=True)
    board_after.push(move)
    return EngineReply(
        uci=move.uci(),
        san=san,
        fen_after=board_after.fen(),
    )


def _score_to_white_cp(score: chess.engine.PovScore) -> int:
    return score.score(mate_score=MATE_SCORE)


def _score_to_display(score: chess.engine.PovScore) -> str:
    mate = score.mate()
    if mate is not None:
        return f"#{mate}"

    cp = score.score()
    if cp is None:
        return "0.00"
    return f"{cp / 100:.2f}"


def _centipawn_loss(turn: bool, best_score_cp: int, played_score_cp: int) -> int:
    if turn == chess.WHITE:
        return max(0, best_score_cp - played_score_cp)
    return max(0, played_score_cp - best_score_cp)


def _classify_move(centipawn_loss: int, is_best_move: bool, is_interesting: bool) -> tuple[str, str]:
    # Domain logic often becomes cleaner when converted into small helper
    # functions with explicit inputs and outputs.
    if is_best_move:
        return "best", "Best move"
    if is_interesting and centipawn_loss <= 80:
        return "interesting", "Interesting"
    if centipawn_loss <= 30:
        return "good", "Good move"
    if centipawn_loss <= 90:
        return "inaccuracy", "Inaccuracy"
    if centipawn_loss <= 220:
        return "mistake", "Mistake"
    return "blunder", "Blunder"


def _build_quality_summary(
    move_quality: str,
    move_quality_label: str,
    centipawn_loss: int,
    best_move_san: str,
    best_move: chess.Move,
    move: chess.Move,
) -> str:
    if move_quality == "best":
        return "Stockfish considers this the best move in the position."
    if move_quality == "interesting":
        return (
            "Stockfish does not prefer this first, but it sees the move as a playable and interesting idea "
            f"with limited cost ({centipawn_loss} cp)."
        )
    return (
        f"{move_quality_label}. The move loses about {centipawn_loss} centipawns compared with "
        f"the engine choice {best_move_san}."
    )


def _white_bar_percentage(score_cp: int) -> int:
    # Convert an engine score into a UI-friendly 0-100 scale for the evaluation
    # bar. This is a pure transformation function.
    clipped = max(-1200, min(1200, score_cp))
    return int(round(((clipped + 1200) / 2400) * 100))


def _is_interesting_move(
    board_before: chess.Board,
    move: chess.Move,
    best_move: chess.Move,
    centipawn_loss: int,
) -> bool:
    if move == best_move or centipawn_loss > 80:
        return False

    if board_before.gives_check(move):
        return True

    if board_before.is_capture(move):
        return True

    moving_piece = board_before.piece_at(move.from_square)
    captured_piece = board_before.piece_at(move.to_square)
    if moving_piece and moving_piece.piece_type != chess.PAWN:
        if move.to_square in {chess.C4, chess.D4, chess.E4, chess.F4, chess.C5, chess.D5, chess.E5, chess.F5}:
            return True

    if moving_piece and captured_piece:
        return PIECE_VALUES[moving_piece.piece_type] < PIECE_VALUES[captured_piece.piece_type]

    return False


def _extract_candidate_moves(
    board: chess.Board,
    infos: list[dict],
) -> list[EngineCandidateMove]:
    candidates: list[EngineCandidateMove] = []
    for info in infos[:3]:
        pv = info.get("pv") or []
        if not pv:
            continue
        move = pv[0]
        candidates.append(
            EngineCandidateMove(
                san=board.san(move),
                uci=move.uci(),
                score_display=_score_to_display(info["score"].white()),
            )
        )
    return candidates
