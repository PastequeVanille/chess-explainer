from fastapi.testclient import TestClient
from uuid import uuid4

from backend.app import main as main_module
from backend.app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_engine_status_endpoint() -> None:
    response = client.get("/api/engine-status")
    assert response.status_code == 200
    assert "enabled" in response.json()


def test_ai_status_endpoint() -> None:
    response = client.get("/api/ai-status")
    assert response.status_code == 200
    assert "enabled" in response.json()
    assert "model" in response.json()


def test_explain_move_endpoint() -> None:
    game = client.get("/api/game").json()
    response = client.post(
        "/api/explain-move",
        json={
            "fen": game["fen"],
            "from_square": "e2",
            "to_square": "e4",
            "move_history_uci": [],
        },
    )

    payload = response.json()
    assert response.status_code == 200
    assert payload["san"] == "e4"
    assert payload["headline"] == "Pawn played e4"
    assert "move_quality" in payload
    assert "opening" in payload
    assert "study_phase" in payload
    assert "game_status" in payload
    assert "what_happened" in payload
    assert "key_ideas" in payload
    assert "watch_out" in payload


def test_study_endpoints_round_trip() -> None:
    created = client.post("/api/studies", json={"title": "API Study"}).json()
    assert created["title"] == "API Study"

    saved = client.put(
        f"/api/studies/{created['id']}",
        json={
            "title": "API Study",
            "move_history_uci": ["e2e4", "e7e5"],
            "current_ply": 2,
            "flipped": False,
            "notes_by_ply": {
                "2": {
                    "comment": "Open game.",
                    "custom_explanation": "Mirror response in the centre.",
                }
            },
            "annotations_by_ply": {
                "2": {
                    "arrows": [{"from_square": "e2", "to_square": "e4", "color": "#4f46e5"}],
                    "highlights": [{"square": "e4", "color": "#f59e0b"}],
                }
            },
            "analysis_cache_by_ply": {
                "2": {
                    "headline": "Edited headline",
                    "opening": {
                        "name": "Open Game",
                        "summary": "Edited opening summary.",
                        "common_responses": ["2.Nf3", "2.Bc4"],
                    },
                    "what_happened": ["Edited line"],
                    "key_ideas": ["Edited idea"],
                    "watch_out": ["Edited warning"],
                    "bullets": ["Edited note"],
                    "ai_verdict": "Edited verdict",
                }
            },
        },
    ).json()

    fetched = client.get(f"/api/studies/{created['id']}").json()
    assert saved["current_ply"] == 2
    assert fetched["notes_by_ply"]["2"]["comment"] == "Open game."
    assert fetched["analysis_cache_by_ply"]["2"]["headline"] == "Edited headline"


def test_study_markdown_export_endpoint() -> None:
    created = client.post("/api/studies", json={"title": "Export Study"}).json()
    client.put(
        f"/api/studies/{created['id']}",
        json={
            "title": "Export Study",
            "move_history_uci": ["e2e4", "e7e5"],
            "current_ply": 2,
            "flipped": False,
            "notes_by_ply": {"2": {"comment": "Study note", "custom_explanation": ""}},
            "annotations_by_ply": {},
            "analysis_cache_by_ply": {"2": {"headline": "Open game position", "key_ideas": ["Fight for the centre"]}},
        },
    )

    response = client.get(f"/api/studies/{created['id']}/export.md")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert "# Export Study" in response.text
    assert "Fight for the centre" in response.text


def test_engine_move_endpoint(monkeypatch) -> None:
    monkeypatch.setattr(
        main_module,
        "compute_engine_move",
        lambda fen, move_history_uci=None: {
            "uci": "e7e5",
            "san": "e5",
            "fen_after": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
            "turn": "white",
            "move_number": 2,
            "game_status": {
                "key": "in_progress",
                "label": "In progress",
                "summary": "The game is still in progress.",
                "is_check": False,
                "is_checkmate": False,
                "is_game_over": False,
                "result": None,
                "winner": None,
            },
        },
    )

    response = client.post(
        "/api/engine-move",
        json={
            "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
            "move_history_uci": ["e2e4"],
        },
    )
    assert response.status_code == 200
    assert response.json()["uci"] == "e7e5"


def test_fen_history_endpoint_accepts_query_params() -> None:
    response = client.get("/api/fen-history", params=[("move_history_uci", "e2e4")])
    assert response.status_code == 200
    payload = response.json()
    history = payload["history"]
    assert history[0].startswith("rnbqkbnr/pppppppp/")
    assert len(history) == 2
    assert payload["san_history"] == ["e4"]
    assert payload["statuses"][-1]["key"] == "in_progress"


def test_auth_register_login_and_me() -> None:
    email = f"test-{uuid4().hex[:10]}@example.com"
    with TestClient(app) as auth_client:
        registered = auth_client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "study-pass-123",
                "display_name": "Test Player",
            },
        )
        assert registered.status_code == 200
        assert registered.json()["authenticated"] is True
        assert registered.json()["user"]["email"] == email

        me = auth_client.get("/api/auth/me")
        assert me.status_code == 200
        assert me.json()["authenticated"] is True
        assert me.json()["user"]["display_name"] == "Test Player"

        logout = auth_client.post("/api/auth/logout")
        assert logout.status_code == 200
        assert logout.json()["authenticated"] is False

        login = auth_client.post(
            "/api/auth/login",
            json={"email": email, "password": "study-pass-123"},
        )
        assert login.status_code == 200
        assert login.json()["authenticated"] is True
