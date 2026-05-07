from __future__ import annotations

from contextlib import suppress

import chess
import chess.engine

from ..config import get_settings
from .ai_service import generate_ai_explanation
from .engine_service import EngineMoveAnalysis, analyse_move_with_engine
from .wikibooks_service import fetch_opening_explanation


PIECE_NAMES = {
    chess.PAWN: "pawn",
    chess.KNIGHT: "knight",
    chess.BISHOP: "bishop",
    chess.ROOK: "rook",
    chess.QUEEN: "queen",
    chess.KING: "king",
}

CENTER_SQUARES = {chess.D4, chess.E4, chess.D5, chess.E5}


def initial_game_state() -> dict[str, str | int]:
    board = chess.Board()
    return {
        "fen": board.fen(),
        "turn": turn_name(board.turn),
        "move_number": board.fullmove_number,
    }


def legal_targets(fen: str, from_square_name: str) -> list[str]:
    board = chess.Board(fen)
    from_square = chess.parse_square(from_square_name)
    piece = board.piece_at(from_square)
    if piece is None or piece.color != board.turn:
        return []

    return [
        chess.square_name(move.to_square)
        for move in board.legal_moves
        if move.from_square == from_square
    ]


def build_fen_history(move_history_uci: list[str]) -> list[str]:
    board = chess.Board()
    history = [board.fen()]
    for uci in move_history_uci:
        move = chess.Move.from_uci(uci)
        if move not in board.legal_moves:
            raise ValueError(f"Illegal move in history: {uci}")
        board.push(move)
        history.append(board.fen())
    return history


def explain_move(
    fen: str,
    from_square_name: str,
    to_square_name: str,
    promotion: str | None = None,
    move_history_uci: list[str] | None = None,
) -> dict[str, str | int | list | dict | None]:
    board_before = chess.Board(fen)
    move = chess.Move.from_uci(f"{from_square_name}{to_square_name}{promotion or ''}")

    if move not in board_before.legal_moves:
        raise ValueError(f"Illegal move: {move.uci()}")

    moving_piece = board_before.piece_at(move.from_square)
    captured_piece = _captured_piece(board_before, move)
    san = board_before.san(move)
    bullets = _build_bullets(board_before, move, moving_piece, captured_piece)

    board_after = board_before.copy(stack=True)
    board_after.push(move)
    if board_after.is_check():
        bullets.append("The move gives check.")
    if board_after.is_checkmate():
        bullets.append("The move ends the game by checkmate.")

    engine_analysis = _analyse_move(board_before, move)
    engine_evaluation = None if engine_analysis is None else engine_analysis.after_score_display
    opening = fetch_opening_explanation(move_history_uci or [], move.uci())
    ai_explanation = generate_ai_explanation(
        board_before=board_before,
        board_after=board_after,
        san=san,
        headline=_headline(moving_piece, san),
        bullets=bullets,
        engine_evaluation=engine_evaluation,
        move_quality_label=None if engine_analysis is None else engine_analysis.move_quality_label,
        move_quality_summary=None if engine_analysis is None else engine_analysis.move_quality_summary,
        best_move_san=None if engine_analysis is None else engine_analysis.best_move_san,
        centipawn_loss=None if engine_analysis is None else engine_analysis.centipawn_loss,
    )

    if engine_analysis is not None:
        bullets.append(engine_analysis.move_quality_summary)
        bullets.append(
            f"Stockfish preferred {engine_analysis.best_move_san} "
            f"with an evaluation of {engine_analysis.best_score_display}."
        )

    sections = _build_learning_sections(
        board_before=board_before,
        move=move,
        moving_piece=moving_piece,
        bullets=bullets,
        engine_analysis=engine_analysis,
    )
    coach = _build_study_coach(
        san=san,
        sections=sections,
        opening_name=None if opening is None else opening.opening_name,
        engine_analysis=engine_analysis,
        ai_explanation=ai_explanation,
    )

    return {
        "san": san,
        "uci": move.uci(),
        "fen_after": board_after.fen(),
        "turn": turn_name(board_after.turn),
        "move_number": board_after.fullmove_number,
        "headline": _headline(moving_piece, san),
        "bullets": bullets,
        "what_happened": sections["what_happened"],
        "key_ideas": sections["key_ideas"],
        "watch_out": sections["watch_out"],
        "opening": {
            "name": None if opening is None else opening.opening_name,
            "eco": None if opening is None else opening.eco,
            "parent": None if opening is None else opening.parent,
            "summary": None if opening is None else opening.summary,
            "wikibooks_url": None if opening is None else opening.url,
            "common_responses": [] if opening is None or opening.responses is None else opening.responses,
        },
        "engine_evaluation": engine_evaluation,
        "ai_summary": coach["verdict"],
        "ai_coaching_points": [
            coach["best_plan"],
            coach["typical_mistake"],
            coach["training_takeaway"],
        ],
        "ai_verdict": coach["verdict"],
        "ai_best_plan": coach["best_plan"],
        "ai_typical_mistake": coach["typical_mistake"],
        "ai_training_takeaway": coach["training_takeaway"],
        "ai_error": None if ai_explanation is None or "error" not in ai_explanation else ai_explanation["error"],
        "best_move_san": None if engine_analysis is None else engine_analysis.best_move_san,
        "best_move_uci": None if engine_analysis is None else engine_analysis.best_move_uci,
        "best_move_score": None if engine_analysis is None else engine_analysis.best_score_display,
        "played_move_score": None if engine_analysis is None else engine_analysis.played_score_display,
        "centipawn_loss": None if engine_analysis is None else engine_analysis.centipawn_loss,
        "move_quality": None if engine_analysis is None else engine_analysis.move_quality,
        "move_quality_label": None if engine_analysis is None else engine_analysis.move_quality_label,
        "move_quality_summary": None if engine_analysis is None else engine_analysis.move_quality_summary,
        "evaluation_bar_white_pct": None if engine_analysis is None else engine_analysis.evaluation_bar_white_pct,
        "candidate_moves": []
        if engine_analysis is None
        else [
            {
                "san": candidate.san,
                "uci": candidate.uci,
                "score": candidate.score_display,
            }
            for candidate in engine_analysis.candidate_moves
        ],
    }


def turn_name(turn: bool) -> str:
    return "white" if turn == chess.WHITE else "black"


def _headline(piece: chess.Piece | None, san: str) -> str:
    if piece is None:
        return f"Move played: {san}"
    piece_name = PIECE_NAMES[piece.piece_type]
    return f"{piece_name.capitalize()} played {san}"


def _captured_piece(board: chess.Board, move: chess.Move) -> chess.Piece | None:
    if board.is_en_passant(move):
        offset = -8 if board.turn == chess.WHITE else 8
        return board.piece_at(move.to_square + offset)
    return board.piece_at(move.to_square)


def _build_bullets(
    board: chess.Board,
    move: chess.Move,
    moving_piece: chess.Piece | None,
    captured_piece: chess.Piece | None,
) -> list[str]:
    if moving_piece is None:
        return ["The move is legal, but the moving piece could not be identified."]

    bullets: list[str] = []
    piece_name = PIECE_NAMES[moving_piece.piece_type]
    from_name = chess.square_name(move.from_square)
    to_name = chess.square_name(move.to_square)

    bullets.append(f"The {piece_name} moves from {from_name} to {to_name}.")

    if board.is_castling(move):
        bullets.append("Castling helps king safety and activates a rook.")

    if captured_piece is not None:
        captured_name = PIECE_NAMES[captured_piece.piece_type]
        bullets.append(f"The move captures an enemy {captured_name}.")

    if move.promotion is not None:
        promoted_name = PIECE_NAMES[move.promotion]
        bullets.append(f"The pawn promotes to a {promoted_name}.")

    if moving_piece.piece_type in {chess.KNIGHT, chess.BISHOP} and chess.square_rank(move.from_square) in {0, 7}:
        bullets.append("This develops a minor piece from its starting square.")

    if moving_piece.piece_type == chess.PAWN and abs(chess.square_rank(move.to_square) - chess.square_rank(move.from_square)) == 2:
        bullets.append("The pawn gains space with a two-square advance.")

    if move.to_square in CENTER_SQUARES:
        bullets.append("The move directly increases central control.")

    if moving_piece.piece_type == chess.QUEEN and len(board.move_stack) < 6:
        bullets.append("Early queen moves can be active, but they can also become targets.")

    return bullets


def _analyse_move(board_before: chess.Board, move: chess.Move) -> EngineMoveAnalysis | None:
    stockfish_path = get_settings().stockfish_path
    if not stockfish_path:
        return None

    with suppress(FileNotFoundError, chess.engine.EngineError):
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            return analyse_move_with_engine(engine, board_before, move)

    return None


def _build_learning_sections(
    board_before: chess.Board,
    move: chess.Move,
    moving_piece: chess.Piece | None,
    bullets: list[str],
    engine_analysis: EngineMoveAnalysis | None,
) -> dict[str, list[str]]:
    what_happened = bullets[:2] if bullets else []
    key_ideas: list[str] = []
    watch_out: list[str] = []

    if moving_piece is not None and moving_piece.piece_type == chess.PAWN:
        if move.to_square in CENTER_SQUARES:
            key_ideas.append("Central pawn moves often shape the whole plan of the opening.")
        if abs(chess.square_rank(move.to_square) - chess.square_rank(move.from_square)) == 2:
            key_ideas.append("A two-square pawn push gains space, but it can also leave squares behind it weaker.")

    if moving_piece is not None and moving_piece.piece_type in {chess.KNIGHT, chess.BISHOP}:
        key_ideas.append("Develop minor pieces toward active squares before starting slow side plans.")

    if board_before.is_capture(move):
        key_ideas.append("Always ask what changed after the capture: material, structure, and piece activity.")

    if engine_analysis is not None:
        if engine_analysis.move_quality in {"best", "good", "interesting"}:
            key_ideas.append(engine_analysis.move_quality_summary)
        if engine_analysis.move_quality in {"inaccuracy", "mistake", "blunder"}:
            watch_out.append(engine_analysis.move_quality_summary)
        if engine_analysis.best_move_san and engine_analysis.best_move_san != board_before.san(move):
            watch_out.append(f"Compare this move with Stockfish's preferred move {engine_analysis.best_move_san}.")

    if moving_piece is not None and moving_piece.piece_type == chess.QUEEN and len(board_before.move_stack) < 6:
        watch_out.append("Early queen moves can lose time if the opponent develops by attacking the queen.")

    if not what_happened:
        what_happened = ["The move changed the position, but no short explanation was generated."]
    if not key_ideas:
        key_ideas = ["Ask what this move changes in space, development, king safety, and central control."]
    if not watch_out:
        watch_out = ["Check the opponent's forcing replies: checks, captures, and threats."]

    return {
        "what_happened": what_happened[:3],
        "key_ideas": key_ideas[:4],
        "watch_out": watch_out[:4],
    }


def _build_study_coach(
    san: str,
    sections: dict[str, list[str]],
    opening_name: str | None,
    engine_analysis: EngineMoveAnalysis | None,
    ai_explanation: dict[str, str | list[str]] | None,
) -> dict[str, str]:
    if ai_explanation is not None and "error" not in ai_explanation:
        return {
            "verdict": str(ai_explanation["verdict"]),
            "best_plan": str(ai_explanation["best_plan"]),
            "typical_mistake": str(ai_explanation["typical_mistake"]),
            "training_takeaway": str(ai_explanation["training_takeaway"]),
        }

    verdict_parts: list[str] = []
    if engine_analysis is not None:
        verdict_parts.append(engine_analysis.move_quality_summary)
    if opening_name:
        verdict_parts.append(f"This position belongs to the {opening_name}.")
    if not verdict_parts:
        verdict_parts.append(f"{san} changes the position in a meaningful way even without live AI commentary.")

    best_plan = sections["key_ideas"][0]
    if engine_analysis is not None and engine_analysis.candidate_moves:
        candidate_text = ", ".join(candidate.san for candidate in engine_analysis.candidate_moves[:3])
        best_plan = f"Consider the main continuations {candidate_text} and compare which plan fits the position best."

    typical_mistake = sections["watch_out"][0]
    training_takeaway = sections["key_ideas"][0]
    if opening_name and opening_name not in training_takeaway:
        training_takeaway = f"In the {opening_name}, remember: {training_takeaway.lower()}"

    return {
        "verdict": " ".join(verdict_parts),
        "best_plan": best_plan,
        "typical_mistake": typical_mistake,
        "training_takeaway": training_takeaway,
    }
