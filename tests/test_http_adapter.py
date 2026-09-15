"""Story 02-01: Adapter-Tests für src/adapters/http.py — FastAPI TestClient, kein Socket.

Fake = TestClient-Transport (kein lauschender Server, kein Netz, kein externes System).
Board und ``now_fn`` werden injiziert (deterministisch). Deckt Design §4 (API-Skizze)
und §5 (Fehlerbehandlung) ab (REQ-001, REQ-003, REQ-009, REQ-012).
"""

from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.http import create_app
from src.core.board import PostBoard

FIXED_TIME = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
WEB_INDEX = Path(__file__).resolve().parents[1] / "src" / "web" / "index.html"


def _client(
    board: PostBoard | None = None,
    now_fn: "object | None" = None,
) -> tuple[TestClient, FastAPI, PostBoard]:
    """Hilfs-Factory: TestClient + App + (injiziertes oder frisches) Board."""
    board = board if board is not None else PostBoard()
    app = create_app(board=board, now_fn=now_fn)
    return TestClient(app), app, board


# --- POST /api/posts ---------------------------------------------------------


def test_post_api_posts_liefert_post_danach_in_liste_sichtbar() -> None:
    client, _, _ = _client()

    response = client.post("/api/posts", json={"text": "hallo welt"})

    assert response.status_code == 200
    post = response.json()["post"]
    assert post["id"] == 1
    assert post["text"] == "hallo welt"
    assert post["sender"] == "testclient"  # TestClient-Standard-Client-IP
    assert isinstance(post["timestamp"], str)

    listing = client.get("/api/posts").json()
    assert [p["id"] for p in listing["posts"]] == [1]
    assert listing["posts"][0]["text"] == "hallo welt"
    assert listing["posts"][0]["sender"] == "testclient"


def test_post_api_posts_leerer_text_liefert_400_mit_deutscher_meldung() -> None:
    client, _, _ = _client()

    response = client.post("/api/posts", json={"text": ""})

    assert response.status_code == 400
    assert response.json() == {"error": "Text darf nicht leer sein."}
    assert client.get("/api/posts").json()["posts"] == []


def test_post_api_posts_zu_langer_text_liefert_400_mit_fehlermeldung() -> None:
    client, _, _ = _client(board=PostBoard(max_text_length=5))

    response = client.post("/api/posts", json={"text": "viel zu langer text"})

    assert response.status_code == 400
    assert "zu lang" in response.json()["error"]
    assert "5" in response.json()["error"]
    assert client.get("/api/posts").json()["posts"] == []


# --- GET /api/posts ----------------------------------------------------------


def test_get_api_posts_mit_since_id_liefert_nur_neuere_posts() -> None:
    client, _, _ = _client()
    for i in range(3):
        client.post("/api/posts", json={"text": f"post {i + 1}"})

    response = client.get("/api/posts", params={"since_id": 1})

    assert response.status_code == 200
    posts = response.json()["posts"]
    assert [p["id"] for p in posts] == [2, 3]
    assert [p["text"] for p in posts] == ["post 2", "post 3"]


# --- POST /api/clear ---------------------------------------------------------


def test_clear_all_liefert_cleared_flag_genau_einmal() -> None:
    client, _, _ = _client()
    client.post("/api/posts", json={"text": "eins"})
    client.post("/api/posts", json={"text": "zwei"})

    cleared = client.post("/api/clear", json={"mode": "all"})
    assert cleared.status_code == 200
    assert cleared.json() == {"cleared": True}

    first = client.get("/api/posts").json()
    assert first == {"posts": [], "cleared": True}  # genau EINMAL true, Liste leer

    second = client.get("/api/posts").json()
    assert second == {"posts": [], "cleared": False}  # zweiter Abruf: false


def test_clear_last_entfernt_nur_letzten_post() -> None:
    client, _, _ = _client()
    client.post("/api/posts", json={"text": "eins"})
    client.post("/api/posts", json={"text": "zwei"})

    response = client.post("/api/clear", json={"mode": "last"})
    assert response.status_code == 200
    assert response.json() == {"cleared": True}

    listing = client.get("/api/posts").json()
    assert [p["text"] for p in listing["posts"]] == ["eins"]
    assert listing["cleared"] is True


def test_clear_mit_ungültigem_mode_liefert_400() -> None:
    client, _, _ = _client()

    response = client.post("/api/clear", json={"mode": "bogus"})

    assert response.status_code == 400
    error = response.json()["error"]
    assert "all" in error and "last" in error


def test_clear_mit_fehlendem_mode_liefert_400() -> None:
    client, _, _ = _client()

    response = client.post("/api/clear", json={})

    assert response.status_code == 400
    assert "error" in response.json()


# --- GET / -------------------------------------------------------------------


def test_get_root_liefert_200_html() -> None:
    client, _, _ = _client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "NetClip" in response.text


def test_get_root_liefert_platzhalter_solange_index_html_fehlt() -> None:
    # src/web/index.html entsteht erst in Story 02-02; bis dahin deutscher Platzhalter.
    if WEB_INDEX.is_file():
        return  # Sobald 02-02 die Datei liefert, prüft der Test darüber nichts mehr.
    client, _, _ = _client()

    response = client.get("/")

    assert response.status_code == 200
    assert "NetClip – Frontend folgt" in response.text


# --- Injektion (Design §1) ---------------------------------------------------


def test_now_fn_injektion_setzt_deterministischen_timestamp() -> None:
    client, _, _ = _client(now_fn=lambda: FIXED_TIME)

    response = client.post("/api/posts", json={"text": "pünktlich"})

    assert response.status_code == 200
    assert response.json()["post"]["timestamp"] == FIXED_TIME.isoformat()


def test_board_injektion_app_state_board_ist_dasselbe_objekt() -> None:
    board = PostBoard()
    client, app, injected = _client(board=board)

    assert injected is board
    assert app.state.board is board
    # Injiziertes Board ist live wirksam: über API gepostet, im Board-Objekt sichtbar.
    client.post("/api/posts", json={"text": "injiziert"})
    assert [p["text"] for p in board.get_posts()] == ["injiziert"]


# --- Absender-IP hinter Reverse-Proxy (Story 09-01, REQ-018, Design §1) ------
# Header-Injektion via TestClient simuliert den Proxy — kein Netz.


def test_post_mit_xff_header_nutzt_erste_ip_als_sender() -> None:
    client, _, _ = _client()

    response = client.post(
        "/api/posts",
        json={"text": "hinter proxy"},
        headers={"X-Forwarded-For": "192.168.111.42"},
    )

    assert response.status_code == 200
    assert response.json()["post"]["sender"] == "192.168.111.42"


def test_post_mit_xff_proxy_kette_nutzt_erste_ip_der_kette() -> None:
    client, _, _ = _client()

    response = client.post(
        "/api/posts",
        json={"text": "kette"},
        headers={"X-Forwarded-For": "192.168.111.42, 172.22.0.1"},
    )

    assert response.status_code == 200
    assert response.json()["post"]["sender"] == "192.168.111.42"


def test_post_ohne_xff_header_behaelt_fallback_tcp_peer_ip() -> None:
    client, _, _ = _client()

    response = client.post("/api/posts", json={"text": "direktzugriff"})

    assert response.status_code == 200
    assert response.json()["post"]["sender"] == "testclient"


def test_post_mit_whitespace_in_xff_kette_parst_erste_ip_sauber() -> None:
    client, _, _ = _client()

    response = client.post(
        "/api/posts",
        json={"text": "whitespace"},
        headers={"X-Forwarded-For": " 192.168.111.42 , 172.22.0.1 "},
    )

    assert response.status_code == 200
    assert response.json()["post"]["sender"] == "192.168.111.42"


# --- Ungültige Bodies (QA-Loop 1: Design §1 Z.45 — ungültiger Body → 400) ----


def test_post_api_posts_malformed_json_liefert_400_mit_error_key() -> None:
    client, _, _ = _client()

    response = client.post(
        "/api/posts", content=b"{invalid", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    assert "error" in response.json()


def test_post_api_posts_ohne_text_key_liefert_400_mit_error_key() -> None:
    client, _, _ = _client()

    response = client.post("/api/posts", json={})

    assert response.status_code == 400
    assert "error" in response.json()


def test_post_api_posts_mit_nicht_text_typ_liefert_400_mit_error_key() -> None:
    client, _, _ = _client()

    response = client.post("/api/posts", json={"text": 123})

    assert response.status_code == 400
    assert "error" in response.json()


def test_post_api_clear_malformed_json_liefert_400_mit_error_key() -> None:
    client, _, _ = _client()

    response = client.post(
        "/api/clear", content=b"{invalid", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    assert "error" in response.json()