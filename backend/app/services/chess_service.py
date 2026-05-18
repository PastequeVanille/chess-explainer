from __future__ import annotations

from contextlib import suppress

import chess
import chess.engine

from ..config import get_settings
from .ai_service import generate_ai_explanation
from .engine_service import EngineMoveAnalysis, analyse_move_with_engine, choose_engine_reply
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
PIECE_VALUES = {
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
}


def initial_game_state() -> dict[str, str | int]:
    # A small pure function: same input state every time, no side effects.
    board = chess.Board()
    return {
        "fen": board.fen(),
        "turn": turn_name(board.turn),
        "move_number": board.fullmove_number,
    }


def legal_targets(fen: str, from_square_name: str) -> list[str]:
    # Rebuild board state from FEN. This is a common backend pattern: the
    # frontend sends serialized state, and the backend turns it back into a
    # domain object.
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


def build_game_timeline(move_history_uci: list[str]) -> dict[str, list]:
    # This function rebuilds history from move notation instead of storing many
    # duplicated board states by hand.
    board = chess.Board()
    history = [board.fen()]
    san_history: list[str] = []
    statuses = [describe_position(board.fen())]

    for uci in move_history_uci:
        move = chess.Move.from_uci(uci)
        if move not in board.legal_moves:
            raise ValueError(f"Illegal move in history: {uci}")
        san_history.append(board.san(move))
        board.push(move)
        history.append(board.fen())
        statuses.append(describe_position(board.fen()))

    return {
        "history": history,
        "san_history": san_history,
        "statuses": statuses,
    }


def describe_position(fen: str) -> dict[str, str | bool | None]:
    # Centralize game-status logic in one function so every caller gets the same
    # vocabulary for check, mate, stalemate, and normal play.
    board = chess.Board(fen)
    result = board.result(claim_draw=True) if board.is_game_over(claim_draw=True) else None

    if board.is_checkmate():
        winner = "black" if board.turn == chess.WHITE else "white"
        return {
            "key": "checkmate",
            "label": "Checkmate",
            "summary": f"Checkmate. {winner.capitalize()} wins.",
            "is_check": True,
            "is_checkmate": True,
            "is_game_over": True,
            "result": result,
            "winner": winner,
        }

    if board.is_stalemate():
        return {
            "key": "stalemate",
            "label": "Stalemate",
            "summary": "Stalemate. The game is drawn because the side to move has no legal move and is not in check.",
            "is_check": False,
            "is_checkmate": False,
            "is_game_over": True,
            "result": result,
            "winner": None,
        }

    outcome = board.outcome(claim_draw=True)
    if outcome is not None:
        reason = outcome.termination.name.replace("_", " ").lower()
        winner = None if outcome.winner is None else turn_name(outcome.winner)
        label = "Draw" if winner is None else f"{winner.capitalize()} wins"
        return {
            "key": "game_over",
            "label": label,
            "summary": f"Game over by {reason}. Result: {outcome.result()}.",
            "is_check": board.is_check(),
            "is_checkmate": False,
            "is_game_over": True,
            "result": outcome.result(),
            "winner": winner,
        }

    if board.is_check():
        defender = turn_name(board.turn)
        return {
            "key": "check",
            "label": "Check",
            "summary": f"{defender.capitalize()} is in check and must answer the threat to the king.",
            "is_check": True,
            "is_checkmate": False,
            "is_game_over": False,
            "result": None,
            "winner": None,
        }

    return {
        "key": "in_progress",
        "label": "In progress",
        "summary": "The game is still in progress.",
        "is_check": False,
        "is_checkmate": False,
        "is_game_over": False,
        "result": None,
        "winner": None,
    }


def explain_move(
    fen: str,
    from_square_name: str,
    to_square_name: str,
    promotion: str | None = None,
    move_history_uci: list[str] | None = None,
) -> dict[str, str | int | list | dict | None]:
    # This is the main orchestration function of the project. It is a good
    # example of service-layer code: validate inputs, update domain state,
    # delegate specialized tasks, then assemble one response payload.
    board_before = chess.Board(fen)
    move = chess.Move.from_uci(f"{from_square_name}{to_square_name}{promotion or ''}")

    if move not in board_before.legal_moves:
        raise ValueError(f"Illegal move: {move.uci()}")

    moving_piece = board_before.piece_at(move.from_square)
    captured_piece = _captured_piece(board_before, move)
    san = board_before.san(move)
    bullets = _build_bullets(board_before, move, moving_piece, captured_piece)

    board_after = board_before.copy(stack=True)
    # Work on a copied board so the "before" state remains available for engine
    # comparison and explanation building.
    board_after.push(move)
    game_status = describe_position(board_after.fen())
    if game_status["is_checkmate"]:
        bullets.append(str(game_status["summary"]))
    elif game_status["is_check"]:
        bullets.append("The move gives check.")

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
    if game_status["is_checkmate"]:
        sections["what_happened"] = [str(game_status["summary"]), *sections["what_happened"]][:3]
        sections["key_ideas"] = [
            "The forcing sequence matters most here: checks, captures, and direct threats decide the game.",
            *sections["key_ideas"],
        ][:4]
        sections["watch_out"] = ["The game is over, so there is no defensive resource left.", *sections["watch_out"]][:4]
    elif game_status["is_check"]:
        sections["what_happened"] = [str(game_status["summary"]), *sections["what_happened"]][:3]
        sections["watch_out"] = [
            "The checked side must answer the king threat before doing anything else.",
            *sections["watch_out"],
        ][:4]
    study_phase = _build_study_phase(
        board_after=board_after,
        opening_name=None if opening is None else opening.opening_name,
        opening_summary=None if opening is None else opening.summary,
        sections=sections,
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
        "study_phase": study_phase,
        "game_status": game_status,
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


def compute_engine_move(
    fen: str,
    move_history_uci: list[str] | None = None,
) -> dict[str, str | int]:
    del move_history_uci
    stockfish_path = get_settings().stockfish_path
    if not stockfish_path:
        raise ValueError("Stockfish is not configured.")

    board = chess.Board(fen)
    if board.is_game_over():
        raise ValueError("The game is already over.")

    # `with ... as ...` is a context manager. It ensures the external Stockfish
    # process is closed properly even if something goes wrong.
    with suppress(FileNotFoundError, chess.engine.EngineError):
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            reply = choose_engine_reply(engine, board)
            board_after = chess.Board(reply.fen_after)
            return {
                "uci": reply.uci,
                "san": reply.san,
                "fen_after": reply.fen_after,
                "turn": turn_name(board_after.turn),
                "move_number": board_after.fullmove_number,
                "game_status": describe_position(reply.fen_after),
            }

    raise ValueError("Stockfish could not be started.")


def turn_name(turn: bool) -> str:
    # python-chess uses booleans for side-to-move; this helper turns that into
    # application-level wording.
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


def _build_study_phase(
    board_after: chess.Board,
    opening_name: str | None,
    opening_summary: str | None,
    sections: dict[str, list[str]],
    engine_analysis: EngineMoveAnalysis | None,
) -> dict[str, str | list[str] | None]:
    if opening_name:
        ideas = sections["key_ideas"][:3]
        if not ideas:
            ideas = [
                "Learn the purpose of the line before memorizing move order.",
                "Tie each move to development, central control, and king safety.",
            ]
        return {
            "key": "opening",
            "label": "Opening",
            "title": opening_name,
            "meta": "Wikibooks and opening references are available for this line.",
            "summary": opening_summary
            or "Use the opening reference to connect move order with plans, structure, and typical continuations.",
            "ideas": ideas,
            "continuations_label": "Typical replies",
            "source_label": "Wikibooks opening reference",
        }

    phase_key = _infer_phase_key(board_after)
    if phase_key == "endgame":
        summary = (
            "Opening references no longer apply here. Endgame study should focus on king activity, passed pawns, "
            "piece exchanges, and concrete calculation."
        )
        if engine_analysis is not None:
            summary = f"{engine_analysis.move_quality_summary} {summary}"
        return {
            "key": "endgame",
            "label": "Endgame",
            "title": "Endgame study",
            "meta": "Technique matters more than memorized theory in this phase.",
            "summary": summary,
            "ideas": [
                "Activate the king as soon as it is safe and useful.",
                "Track passed pawns, pawn majorities, and races before choosing exchanges.",
                "Ask which endgame improves for your side before simplifying.",
            ],
            "continuations_label": "Critical continuations",
            "source_label": None,
        }

    summary = (
        "The opening phase is over. Study plans, pawn breaks, king safety, piece activity, and tactical motifs "
        "instead of looking for a memorized line."
    )
    if engine_analysis is not None:
        summary = f"{engine_analysis.move_quality_summary} {summary}"
    return {
        "key": "middlegame",
        "label": "Middlegame",
        "title": "Middlegame study",
        "meta": "No opening reference applies here. Focus on plans and imbalances.",
        "summary": summary,
        "ideas": [
            "Identify the pawn breaks both sides are aiming for.",
            "Improve the worst-placed piece before starting a new attack.",
            "Compare king safety and piece coordination before forcing tactics.",
        ],
        "continuations_label": "Plans to compare",
        "source_label": None,
    }


def _infer_phase_key(board: chess.Board) -> str:
    non_pawn_material = _count_non_pawn_material(board)
    queen_count = len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))

    if non_pawn_material <= 14:
        return "endgame"
    if queen_count == 0 and non_pawn_material <= 20:
        return "endgame"
    return "middlegame"


def _count_non_pawn_material(board: chess.Board) -> int:
    total = 0
    for piece_type, value in PIECE_VALUES.items():
        total += value * (
            len(board.pieces(piece_type, chess.WHITE)) + len(board.pieces(piece_type, chess.BLACK))
        )
    return total
