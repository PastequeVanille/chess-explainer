from fastapi.testclient import TestClient
from uuid import uuid4

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


def test_fen_history_endpoint_accepts_query_params() -> None:
    response = client.get("/api/fen-history", params=[("move_history_uci", "e2e4")])
    assert response.status_code == 200
    history = response.json()["history"]
    assert history[0].startswith("rnbqkbnr/pppppppp/")
    assert len(history) == 2


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
