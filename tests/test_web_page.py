"""Story 02-02: Web-Frontend-Tests — TestClient + Datei-Lesen, kein Browser, kein Netz.

Red-Phase: Tests VOR Implementierung von ``src/web/index.html`` geschrieben und gegen
den HTML-Platzhalter aus ``src/adapters/http.py`` gelaufen (fehlgeschlagen, da der
Platzhalter die charakteristischen UI-Strings nicht enthält und die Datei fehlte).
Deckt Story-Testkriterien + Design §4a (Polling-Contract) ab (REQ-002, REQ-006).
"""

from pathlib import Path

from fastapi.testclient import TestClient

from src.adapters.http import create_app

WEB_INDEX = Path(__file__).resolve().parents[1] / "src" / "web" / "index.html"


def test_web_index_html_existiert() -> None:
    assert WEB_INDEX.is_file()


def test_get_root_liefert_200_und_text_html() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_get_root_liefert_charakteristische_ui_strings() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    for needle in ("NetClip", "Senden", "Clear all", "Clear last"):
        assert needle in response.text, f"'{needle}' fehlt in GET /"


def test_web_index_html_enthaelt_polling_contract_strings() -> None:
    # Statischer SMOKE-Check: Verifikation der Polling-/Contract-Anbindung (Design §4a).
    content = WEB_INDEX.read_text(encoding="utf-8")

    for needle in ("since_id", "setInterval", "/api/posts", "/api/clear"):
        assert needle in content, f"'{needle}' fehlt in index.html"