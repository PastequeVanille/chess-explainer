from backend.app.logic.wikibooks_openings import (
    _debug_build_title_from_san,
    _debug_extract_summary_from_html,
    fetch_opening_explanation,
)
import httpx


class _FakeResponse:
    def __init__(self, text=None, payload=None):
        self.text = text
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        if self._payload is None:
            raise AttributeError("No JSON payload configured")
        return self._payload


class _FakeClient:
    def __init__(self, text):
        self.text = text

    def get(self, *args, **kwargs):
        url = args[0]
        if "api.php" in url:
            return _FakeResponse(
                payload={
                    "parse": {
                        "text": self.text,
                    }
                }
            )
        return _FakeResponse(text=self.text)

    def close(self):
        return None


class _FailingClient:
    def get(self, *args, **kwargs):
        raise httpx.ConnectError("network down")

    def close(self):
        return None


def test_build_wikibooks_title() -> None:
    title = _debug_build_title_from_san(["e4", "e5", "Nf3"])
    assert title == "Chess Opening Theory/1. e4/1...e5/2. Nf3"


def test_extract_summary_from_html() -> None:
    html = """
    <div class="mw-parser-output">
      <p>1...e5 is the Open game.</p>
      <p>Black mirrors White and fights for the centre.</p>
      <h2>Attack the pawn</h2>
      <p>Later section.</p>
    </div>
    """
    summary = _debug_extract_summary_from_html(html)
    assert summary == "1...e5 is the Open game.\n\nBlack mirrors White and fights for the centre."


def test_fetch_opening_explanation_uses_move_history() -> None:
    client = _FakeClient(
        """
        <div class="mw-parser-output">
          <table class="infobox">
            <tr><th colspan="2">Open Game</th></tr>
            <tr><th>ECO code:</th><td>C20-C99</td></tr>
            <tr><th>Parent:</th><td>King's pawn game</td></tr>
            <tr><th>Responses:</th><td><a>2. Nf3</a><a>2. Bc4</a></td></tr>
          </table>
          <p>1...e5 is the Open game.</p>
          <p>Black mirrors White and fights for the centre.</p>
        </div>
        """
    )
    result = fetch_opening_explanation(["e2e4"], "e7e5", client=client)
    assert result is not None
    assert result.title == "Chess Opening Theory/1. e4/1...e5"
    assert result.url.endswith("Chess_Opening_Theory/1._e4/1...e5")
    assert result.opening_name == "Open Game"
    assert result.eco == "C20-C99"
    assert result.responses == ["2. Nf3", "2. Bc4"]


def test_fetch_opening_explanation_falls_back_to_local_opening_when_wikibooks_fails() -> None:
    result = fetch_opening_explanation(["e2e4"], "e7e5", client=_FailingClient())
    assert result is not None
    assert result.opening_name == "Open Game"
    assert result.eco == "C20-C99"
    assert "open positions" in result.summary.lower()


def test_fetch_opening_explanation_can_use_wikibooks_without_local_opening_book_match() -> None:
    client = _FakeClient(
        """
        <div class="mw-parser-output">
          <table class="infobox">
            <tr><th colspan="2">Vienna Game</th></tr>
            <tr><th>ECO code:</th><td>C25-C29</td></tr>
            <tr><th>Parent:</th><td>Open Game</td></tr>
            <tr><th>Responses:</th><td><a>2...Nf6</a><a>2...Bc5</a></td></tr>
          </table>
          <p>The Vienna Game starts with 2.Nc3 and keeps central options flexible.</p>
          <p>White may aim for f4, rapid development, or quieter positional play.</p>
        </div>
        """
    )
    result = fetch_opening_explanation(["e2e4", "e7e5"], "b1c3", client=client)
    assert result is not None
    assert result.title == "Chess Opening Theory/1. e4/1...e5/2. Nc3"
    assert result.opening_name == "Vienna Game"
    assert result.eco == "C25-C29"


def test_fetch_opening_explanation_keeps_ponziani_in_opening_phase() -> None:
    result = fetch_opening_explanation(
        ["e2e4", "e7e5", "g1f3", "b8c6"],
        "c2c3",
        client=_FailingClient(),
    )
    assert result is not None
    assert result.opening_name == "Ponziani Opening"
    assert result.eco == "C44"
    assert result.parent == "Open Game"


def test_fetch_opening_explanation_returns_none_once_out_of_opening_phase() -> None:
    client = _FailingClient()
    result = fetch_opening_explanation(
        [
            "e2e4",
            "e7e5",
            "g1f3",
            "b8c6",
            "f1c4",
            "f8c5",
            "c2c3",
            "g8f6",
            "d2d4",
            "e5d4",
        ],
        "c3d4",
        client=client,
    )
    assert result is None
