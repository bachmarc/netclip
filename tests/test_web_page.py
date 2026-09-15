"""Story 02-02 + 04-01: Web-Frontend-Tests — TestClient + Datei-Lesen, kein Browser,
kein Netz.

Red-Phase: Tests VOR Implementierung von ``src/web/index.html`` geschrieben und gegen
den HTML-Platzhalter aus ``src/adapters/http.py`` gelaufen (fehlgeschlagen, da der
Platzhalter die charakteristischen UI-Strings nicht enthält und die Datei fehlte).
Deckt Story-Testkriterien + Design §4a (Polling-Contract) ab (REQ-002, REQ-006).

Story 04-01 (REQ-013, Design §4a revised): Chat-Layout-Contract-Tests — chronologische
Liste (neue Posts unten via append), fixierter Eingabebereich unten, Auto-Scroll mit
„am unteren Ende"-Erkennung.
"""

from pathlib import Path
import re

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


# ---------------------------------------------------------------------------
# Story 04-01: Chat-Layout-Contract (REQ-013, Design §4a revised)
# ---------------------------------------------------------------------------


def test_web_index_html_haengt_neue_posts_unten_an() -> None:
    # Chat-Semantik: neue Posts werden unten angehängt (chronologisch, API liefert
    # aufsteigend). prepend/insertBefore/insertAdjacentHTML(afterbegin) dürfen für
    # die Post-Liste nicht mehr verwendet werden.
    content = WEB_INDEX.read_text(encoding="utf-8")

    assert "liste.append(" in content or "liste.appendChild(" in content, (
        "Post-Liste muss neue Posts unten anhängen (append/appendChild)"
    )
    assert "liste.prepend(" not in content, "prepend widerspricht Chat-Semantik"
    assert "insertBefore" not in content, "insertBefore widerspricht Chat-Semantik"
    assert "insertAdjacentHTML" not in content, (
        "insertAdjacentHTML widerspricht Chat-Semantik"
    )


def test_web_index_html_automatisch_scrollen_am_unteren_ende() -> None:
    # Auto-Scroll: scrollTop/scrollHeight-Logik vorhanden + „am unteren Ende"-Erkennung
    # (Distanz-Toleranz), geprüft VOR dem Anhängen neuer Posts (Design §4a).
    content = WEB_INDEX.read_text(encoding="utf-8")

    assert "scrollTop" in content, "scrollTop-Logik für Auto-Scroll fehlt"
    assert "scrollHeight" in content, "scrollHeight-Logik für Auto-Scroll fehlt"
    assert "ScrollTo" in content or "scrollTo" in content, (
        "Scroll-Aufruf für Auto-Scroll fehlt"
    )
    # Toleranz-Distanz (~30px) für „am unteren Ende"-Erkennung:
    for needle in (30, "clientHeight"):
        assert str(needle) in content, (
            f"'{needle}' fehlt — Erkennung am unteren Ende (Toleranz/Distanz)"
        )
    # Erkennung muss VOR dem Anhängen passieren („am unteren Ende" vor append prüfen):
    vorbereitung = content.index("warAmEnde")
    anhaengen = content.index("liste.append(") if "liste.append(" in content else (
        content.index("liste.appendChild(")
    )
    assert vorbereitung < anhaengen, (
        "Erkennung am unteren Ende muss VOR dem Anhängen geprüft werden"
    )


def test_web_index_html_layout_eingabebereich_unten_fixiert() -> None:
    # Layout: Scroll-Container (Post-Liste) + fixierter Eingabebereich unten
    # (flex column mit order oder position: sticky/fixed — Design §4a).
    content = WEB_INDEX.read_text(encoding="utf-8")

    assert "flex-direction: column" in content, "flex column Layout für Chat fehlt"
    assert "order:" in content, "order-Regel für Eingabebereich unten fehlt"
    layout_matcher = (
        "position: sticky" in content
        or "position: fixed" in content
        or "position:sticky" in content
        or "position:fixed" in content
    )
    assert layout_matcher, "fixierter Eingabebereich (sticky/fixed) fehlt"
    # Scrollbarer Post-Listen-Container:
    assert "overflow-y" in content, "scrollbare Post-Liste (overflow-y) fehlt"


# ---------------------------------------------------------------------------
# Story 05-01: Copy-freundliche Text-Markierung (REQ-014, Design §4a)
# ---------------------------------------------------------------------------


def test_web_index_html_kopfzeile_nicht_markierbar_text_markierbar() -> None:
    # Statischer Contract-Check: `user-select: none` (o. ohne Leerzeichen) kommt im
    # CSS vor UND ist dem Kopfzeilen-Selektor (`.kopf`, Zeit + IP) zugeordnet —
    # NICHT global, NICHT auf dem Post-Text (`.text`), der markierbar bleiben muss.
    content = WEB_INDEX.read_text(encoding="utf-8")

    treffer = re.findall(r"user-select\s*:\s*none", content)
    assert treffer, "user-select: none fehlt (Kopfzeile nicht markierbar)"
    assert len(treffer) == 1, (
        "user-select: none genau 1× (nur Kopfzeilen-Regel, nicht global/Text)"
    )

    # Zuordnung: Regel-Block mit user-select enthält den Kopfzeilen-Selektor.
    regel = re.search(r"([.#][\w#>\s.,:+-]*?)\{[^}]*user-select\s*:\s*none[^}]*\}", content)
    assert regel is not None, (
        "user-select: none muss in einem CSS-Regelblock stehen"
    )
    assert ".kopf" in regel.group(1), (
        "user-select: none muss der Post-Kopfzeile (.kopf) zugeordnet sein"
    )

    # Negativ-Check: Post-Text (.text) bleibt markierbar — seine Regel darf kein
    # user-select: none enthalten.
    text_regel = re.search(r"\.text\s*\{([^}]*)\}", content)
    assert text_regel is not None, "Post-Text-Regel (.text) fehlt"
    assert "user-select" not in text_regel.group(1), (
        "Post-Text (.text) darf nicht user-select: none haben — Text bleibt markierbar"
    )