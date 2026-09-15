"""Story 02-02 + 04-01: Web-Frontend-Tests — TestClient + Datei-Lesen, kein Browser,
kein Netz.

Red-Phase: Tests VOR Implementierung von ``src/web/index.html`` geschrieben und gegen
den HTML-Platzhalter aus ``src/adapters/http.py`` gelaufen (fehlgeschlagen, da der
Platzhalter die charakteristischen UI-Strings nicht enthält und die Datei fehlte).
Deckt Story-Testkriterien + Design §4a (Polling-Contract) ab (REQ-002, REQ-006).

Story 04-01 (REQ-013, Design §4a revised): Chat-Layout-Contract-Tests — chronologische
Liste (neue Posts unten via append), fixierter Eingabebereich unten, Auto-Scroll mit
„am unteren Ende"-Erkennung.

Story 06-01 (REQ-015, REQ-016, Design §4a revised): Send-Guard (Button-Disable während
des laufenden POST-Requests) + Auto-Grow-Textarea (input-Listener, scrollHeight,
max-height 40vh, Reset nach erfolgreichem Senden).
"""

import re
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


# ---------------------------------------------------------------------------
# Story 06-01: Send-Guard + Auto-Grow-Textarea (REQ-015, REQ-016, Design §4a)
# ---------------------------------------------------------------------------


def test_web_index_html_send_guard_disabled_waehrend_request() -> None:
    # Statischer Contract-Check (REQ-015): Der Senden-Button wird im senden()-Pfad
    # VOR dem `await fetch` deaktiviert und danach/im finally wieder aktiviert —
    # Doppelklicks erzeugen so keinen zweiten POST. Reihenfolge: disable < fetch <
    # enable-Block, und die Reaktivierung liegt im finally der Try-Struktur.
    content = WEB_INDEX.read_text(encoding="utf-8")

    senden_match = re.search(
        r"async function senden\(\)\s*\{(?:(?!\nasync function )[\s\S])*",
        content,
    )
    assert senden_match is not None, "senden()-Funktion fehlt"
    senden = senden_match.group(0)

    # Disable-Matcher: `disabled = true` (mit/ohne Leerzeichen um `=`).
    disable_matcher = re.search(r"\.disabled\s*=\s*true", senden)
    assert disable_matcher, (
        "senden() muss den Button deaktivieren (disabled = true) vor dem fetch"
    )
    # Reaktivierungs-Matcher: `disabled = false`.
    enable_matcher = re.search(r"\.disabled\s*=\s*false", senden)
    assert enable_matcher, (
        "senden() muss den Button nach Abschluss reaktivieren (disabled = false)"
    )
    # Reihenfolge: Disable VOR dem fetch-Aufruf, Enable NACH dem fetch.
    fetch_pos = senden.index("await fetch(")
    assert disable_matcher.start() < fetch_pos, (
        "disabled = true muss VOR dem await fetch gesetzt werden"
    )
    assert enable_matcher.start() > fetch_pos, (
        "disabled = false muss NACH dem await fetch (finally/Ende) erfolgen"
    )
    # Reaktivierung in jedem Fall: finally-Block innerhalb von senden().
    assert re.search(r"\}?\s*finally\s*\{", senden), (
        "Reaktivierung muss im finally-Block erfolgen (auch bei Fehler)"
    )
    assert enable_matcher.start() > senden.index("finally {"), (
        "disabled = false muss im finally-Block stehen"
    )


def test_web_index_html_auto_grow_textarea() -> None:
    # Statischer Contract-Check (REQ-016): input-Listener auf der Textarea passt die
    # Höhe per scrollHeight an; CSS begrenzt mit max-height (40vh) und erlaubt
    # internen Scroll; nach erfolgreichem Senden Reset auf Ausgangshöhe.
    content = WEB_INDEX.read_text(encoding="utf-8")

    # input-EventListener auf der Textarea (#eingabe).
    assert re.search(r"eingabe\.addEventListener\(\s*[\"']input[\"']", content), (
        "input-EventListener auf der Textarea (#eingabe) fehlt"
    )
    # Höhen-Anpassung: height = auto, dann height = scrollHeight + "px".
    assert re.search(r"style\.height\s*=\s*[\"']auto[\"']", content), (
        "Höhen-Anpassung (style.height = 'auto') fehlt"
    )
    assert re.search(r"style\.height\s*=\s*[^;]+\.scrollHeight\s*\+\s*[\"']px[\"']", content), (
        "Höhen-Anpassung per scrollHeight + 'px' fehlt"
    )
    # CSS-Begrenzung: max-height ~40vh (Deckelung), overflow-y: auto (interner
    # Scroll darüber) und min-height als Ausgangshöhe (~2 Zeilen).
    css_match = re.search(r"#eingabe\s*\{([^}]*)\}", content)
    assert css_match is not None, "Textarea-Regel (#eingabe) fehlt"
    css = css_match.group(1)
    assert re.search(r"max-height\s*:\s*40vh", css), (
        "max-height: 40vh als Deckelung fehlt (#eingabe)"
    )
    assert re.search(r"overflow-y\s*:\s*auto", css), (
        "overflow-y: auto für internen Scroll fehlt (#eingabe)"
    )
    assert re.search(r"min-height\s*:\s*[\d.]+rem", css), (
        "min-height (Ausgangshöhe ~2 Zeilen) fehlt (#eingabe)"
    )
    # Reset auf Ausgangshöhe NACH erfolgreichem Senden: direkt im senden()-Erfolgs-
    # Pfad (style.height) ODER via Reset-Funktion, deren Body style.height setzt.
    senden_match = re.search(
        r"async function senden\(\)\s*\{(?:(?!\nasync function )[\s\S])*",
        content,
    )
    assert senden_match is not None, "senden()-Funktion fehlt"
    senden = senden_match.group(0)
    erfolg = senden.index('eingabe.value = "";')
    erfolgspfad = senden[erfolg:]
    if "style.height" in erfolgspfad:
        pass  # direkter Reset im Erfolgs-Pfad
    else:
        aufruf = re.search(r"(\w+)\(\)", erfolgspfad)
        assert aufruf is not None, (
            "Höhen-Reset im Erfolgs-Pfad fehlt (direkt oder via Reset-Funktion)"
        )
        funktionsname = aufruf.group(1)
        definition = re.search(
            r"function\s+" + re.escape(funktionsname) + r"\s*\([^)]*\)\s*\{([^}]*)\}",
            content,
        )
        assert definition is not None, (
            f"Reset-Funktion {funktionsname}() fehlt"
        )
        assert "style.height" in definition.group(1), (
            "Reset-Funktion muss die Höhe zurücksetzen (style.height)"
        )