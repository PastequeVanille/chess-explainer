from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalOpeningInfo:
    moves: tuple[str, ...]
    name: str
    summary: str
    eco: str | None = None
    parent: str | None = None
    common_responses: tuple[str, ...] = ()


OPENING_BOOK: tuple[LocalOpeningInfo, ...] = (
    LocalOpeningInfo(
        moves=("e2e4",),
        name="King's Pawn Opening",
        eco="B00-C99",
        summary=(
            "1.e4 claims central space immediately and opens lines for the queen and bishop. "
            "It often leads to open positions where development and initiative matter a lot."
        ),
        common_responses=("...e5", "...c5", "...e6", "...c6", "...d5"),
    ),
    LocalOpeningInfo(
        moves=("d2d4",),
        name="Queen's Pawn Opening",
        eco="A40-D99",
        summary=(
            "1.d4 fights for the centre while usually keeping the structure more closed than 1.e4. "
            "It often leads to plans based on pawn structure, piece coordination, and long-term pressure."
        ),
        common_responses=("...d5", "...Nf6", "...e6", "...g6"),
    ),
    LocalOpeningInfo(
        moves=("c2c4",),
        name="English Opening",
        eco="A10-A39",
        summary=(
            "1.c4 fights for d5 from the side and often leads to flexible positions. "
            "White keeps several setup options while asking Black to define the centre first."
        ),
        common_responses=("...e5", "...c5", "...Nf6", "...e6"),
    ),
    LocalOpeningInfo(
        moves=("g1f3",),
        name="Zukertort Opening",
        eco="A04-A09",
        summary=(
            "1.Nf3 is a flexible developing move that keeps many openings available. "
            "It helps control the centre without committing the central pawns too early."
        ),
        common_responses=("...d5", "...Nf6", "...g6", "...c5"),
    ),
    LocalOpeningInfo(
        moves=("e2e4", "e7e5"),
        name="Open Game",
        eco="C20-C99",
        parent="King's Pawn Opening",
        summary=(
            "1.e4 e5 usually leads to open positions where rapid development, central control, "
            "and king safety are the main themes."
        ),
        common_responses=("2.Nf3", "2.Bc4", "2.Nc3", "2.f4"),
    ),
    LocalOpeningInfo(
        moves=("e2e4", "c7c5"),
        name="Sicilian Defense",
        eco="B20-B99",
        parent="King's Pawn Opening",
        summary=(
            "The Sicilian challenges 1.e4 asymmetrically. Black accepts an imbalanced structure "
            "to fight actively for the centre and counterplay."
        ),
        common_responses=("2.Nf3", "2.Nc3", "2.c3", "2.b4"),
    ),
    LocalOpeningInfo(
        moves=("e2e4", "e7e6"),
        name="French Defense",
        eco="C00-C19",
        parent="King's Pawn Opening",
        summary=(
            "The French Defense supports ...d5 and invites a central pawn chain. "
            "Plans often revolve around pawn breaks, light-square strategy, and space management."
        ),
        common_responses=("2.d4", "2.Nf3", "2.Qe2"),
    ),
    LocalOpeningInfo(
        moves=("e2e4", "c7c6"),
        name="Caro-Kann Defense",
        eco="B10-B19",
        parent="King's Pawn Opening",
        summary=(
            "The Caro-Kann prepares ...d5 while keeping Black's structure solid. "
            "Black aims for reliable development and a sound pawn skeleton."
        ),
        common_responses=("2.d4", "2.Nc3", "2.Nf3"),
    ),
    LocalOpeningInfo(
        moves=("e2e4", "d7d5"),
        name="Scandinavian Defense",
        eco="B01",
        parent="King's Pawn Opening",
        summary=(
            "The Scandinavian strikes the e4-pawn at once. Black accepts early queen activity "
            "in exchange for direct central counterplay."
        ),
        common_responses=("2.exd5", "2.Nc3", "2.e5"),
    ),
    LocalOpeningInfo(
        moves=("d2d4", "d7d5", "c2c4"),
        name="Queen's Gambit",
        eco="D06-D69",
        parent="Queen's Pawn Opening",
        summary=(
            "The Queen's Gambit offers the c-pawn to distract Black's d-pawn and gain central influence. "
            "The main themes are central tension, development, and pawn-structure understanding."
        ),
        common_responses=("...e6", "...c6", "...dxc4"),
    ),
    LocalOpeningInfo(
        moves=("d2d4", "d7d5", "c2c4", "e7e6"),
        name="Queen's Gambit Declined",
        eco="D30-D69",
        parent="Queen's Gambit",
        summary=(
            "Black keeps the centre solid and declines the gambit. "
            "This often leads to classical development and strategic battles around the pawn structure."
        ),
        common_responses=("3.Nc3", "3.Nf3", "3.g3"),
    ),
    LocalOpeningInfo(
        moves=("d2d4", "d7d5", "c2c4", "c7c6"),
        name="Slav Defense",
        eco="D10-D19",
        parent="Queen's Gambit",
        summary=(
            "The Slav supports the d5-pawn with ...c6 while keeping the light-squared bishop flexible. "
            "It is one of Black's most reliable answers to 1.d4."
        ),
        common_responses=("3.Nc3", "3.Nf3", "3.cxd5"),
    ),
    LocalOpeningInfo(
        moves=("d2d4", "g8f6"),
        name="Indian Defense",
        eco="A45-E99",
        parent="Queen's Pawn Opening",
        summary=(
            "Black develops naturally and keeps the centre flexible. "
            "Many major openings branch from this move depending on how both sides continue."
        ),
        common_responses=("2.c4", "2.Nf3", "2.Bg5"),
    ),
    LocalOpeningInfo(
        moves=("e2e4", "e7e5", "g1f3", "b8c6", "f1b5"),
        name="Ruy Lopez",
        eco="C60-C99",
        parent="Open Game",
        summary=(
            "The Ruy Lopez increases pressure on e5 and often leads to rich strategic play. "
            "Development, central timing, and long-term queenside structure are recurring themes."
        ),
        common_responses=("...a6", "...Nf6", "...Bc5"),
    ),
    LocalOpeningInfo(
        moves=("e2e4", "e7e5", "g1f3", "b8c6", "f1c4"),
        name="Italian Game",
        eco="C50-C54",
        parent="Open Game",
        summary=(
            "The Italian develops quickly and targets f7. "
            "Typical themes include fast development, central pawn breaks, and attacking chances."
        ),
        common_responses=("...Bc5", "...Nf6", "...Be7"),
    ),
)


def lookup_opening(move_history_uci: list[str], current_move_uci: str) -> LocalOpeningInfo | None:
    sequence = tuple([*move_history_uci, current_move_uci])
    best_match: LocalOpeningInfo | None = None
    for opening in OPENING_BOOK:
        if len(opening.moves) > len(sequence):
            continue
        if sequence[: len(opening.moves)] != opening.moves:
            continue
        if best_match is None or len(opening.moves) > len(best_match.moves):
            best_match = opening
    return best_match
