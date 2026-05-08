from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import quote

import chess
import httpx
from bs4 import BeautifulSoup

from ..config import get_settings
from .opening_service import is_opening_sequence, lookup_opening

WIKIBOOKS_PAGE_BASE = "https://en.wikibooks.org/wiki/"
WIKIBOOKS_API_URL = "https://en.wikibooks.org/w/api.php"


@dataclass(frozen=True)
class WikibooksExplanation:
    title: str
    url: str
    summary: str
    opening_name: str | None = None
    eco: str | None = None
    parent: str | None = None
    responses: list[str] | None = None


def fetch_opening_explanation(
    move_history_uci: list[str],
    current_move_uci: str,
    client: httpx.Client | None = None,
) -> WikibooksExplanation | None:
    if not is_opening_sequence(move_history_uci, current_move_uci):
        return None

    san_moves = _uci_history_to_san_history(move_history_uci, current_move_uci)
    if not san_moves:
        return None

    title = _build_wikibooks_title(san_moves)
    if title is None:
        return None

    local_opening = lookup_opening(move_history_uci, current_move_uci)

    settings = get_settings()
    headers = {
        "User-Agent": settings.wikibooks_user_agent,
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    should_close = client is None
    client = client or httpx.Client(timeout=8.0, follow_redirects=True, headers=headers)
    url = f"{WIKIBOOKS_PAGE_BASE}{quote(title.replace(' ', '_'), safe='/._')}"
    try:
        html = _fetch_parsed_html(client, title)
        summary = _extract_summary_from_html(html)
        if not summary:
            html = _fetch_page_html(client, url)
            summary = _extract_summary_from_html(html)
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        if local_opening is None:
            return None
        return WikibooksExplanation(
            title=title,
            url=url,
            summary=local_opening.summary,
            opening_name=local_opening.name,
            eco=local_opening.eco,
            parent=local_opening.parent,
            responses=list(local_opening.common_responses),
        )
    finally:
        if should_close:
            client.close()

    if not summary and local_opening is None:
        return None

    opening_info = _extract_opening_info_from_html(html)
    responses = opening_info["responses"] or (
        [] if local_opening is None else list(local_opening.common_responses)
    )

    return WikibooksExplanation(
        title=title,
        url=url,
        summary=summary or local_opening.summary,
        opening_name=opening_info["opening_name"] or (None if local_opening is None else local_opening.name),
        eco=opening_info["eco"] or (None if local_opening is None else local_opening.eco),
        parent=opening_info["parent"] or (None if local_opening is None else local_opening.parent),
        responses=responses,
    )


def _uci_history_to_san_history(
    move_history_uci: list[str],
    current_move_uci: str,
) -> list[str] | None:
    board = chess.Board()
    san_moves: list[str] = []

    for uci in [*move_history_uci, current_move_uci]:
        try:
            move = chess.Move.from_uci(uci)
        except ValueError:
            return None

        if move not in board.legal_moves:
            return None

        san_moves.append(board.san(move))
        board.push(move)

    return san_moves


def _build_wikibooks_title(san_moves: list[str]) -> str | None:
    if not san_moves:
        return None

    segments = ["Chess Opening Theory"]
    for index, san in enumerate(san_moves):
        move_number = (index // 2) + 1
        prefix = f"{move_number}. " if index % 2 == 0 else f"{move_number}..."
        segments.append(f"{prefix}{san}")
    return "/".join(segments)


def _fetch_page_html(client: httpx.Client, url: str) -> str:
    response = client.get(url)
    response.raise_for_status()
    return response.text


def _fetch_parsed_html(client: httpx.Client, title: str) -> str:
    response = client.get(
        WIKIBOOKS_API_URL,
        params={
            "action": "parse",
            "page": title,
            "prop": "text",
            "format": "json",
            "formatversion": "2",
            "redirects": "1",
        },
    )
    response.raise_for_status()
    payload = response.json()
    return payload["parse"]["text"]


def _extract_summary_from_html(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", class_="mw-parser-output")
    if content is None:
        return None

    paragraphs: list[str] = []
    for node in content.children:
        name = getattr(node, "name", None)
        if name in {"h2", "h3"} and paragraphs:
            break
        if name != "p":
            continue

        text = " ".join(node.get_text(" ", strip=True).split())
        if not text:
            continue
        if text.startswith("Retrieved from "):
            continue
        paragraphs.append(text)
        if len(paragraphs) == 2:
            break

    if not paragraphs:
        return None
    return "\n\n".join(paragraphs)


def _extract_opening_info_from_html(html: str) -> dict[str, str | list[str] | None]:
    soup = BeautifulSoup(html, "html.parser")
    info = {
        "opening_name": None,
        "eco": None,
        "parent": None,
        "responses": [],
    }
    infobox = soup.find("table", class_="infobox")
    if infobox is None:
        return info

    title_cell = infobox.find("th")
    if title_cell is not None:
        info["opening_name"] = " ".join(title_cell.get_text(" ", strip=True).split())

    for row in infobox.find_all("tr"):
        header = row.find("th")
        value = row.find("td")
        if header is None:
            continue

        if value is None:
            combined = " ".join(header.get_text(" ", strip=True).split())
            if ":" not in combined:
                continue
            key, raw_value = [part.strip() for part in combined.split(":", 1)]
        else:
            key = " ".join(header.get_text(" ", strip=True).split())
            raw_value = " ".join(value.get_text(" ", strip=True).split())
        key = key.lower()
        if key.startswith("eco code"):
            info["eco"] = raw_value
        elif key.startswith("parent"):
            info["parent"] = raw_value
        elif key.startswith("responses"):
            responses = []
            if value is not None:
                responses = [
                    " ".join(link.get_text(" ", strip=True).split())
                    for link in value.find_all("a")
                    if link.get_text(" ", strip=True)
                ]
            if not responses:
                responses = [chunk.strip() for chunk in re.split(r"(?=\d+\.\s)", raw_value) if chunk.strip()]
            info["responses"] = responses

    return info


def _debug_build_title_from_san(san_moves: list[str]) -> str | None:
    return _build_wikibooks_title(san_moves)


def _debug_extract_summary_from_html(html: str) -> str | None:
    return _extract_summary_from_html(html)
