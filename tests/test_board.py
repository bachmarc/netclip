"""Story 01-01: Unit-Tests für src/core/board.py (PostBoard).

Nur Core + FakeClock — kein FastAPI, kein Server, kein Netz (REQ-002, REQ-004,
REQ-005, REQ-006, REQ-007, REQ-010, REQ-011).
"""

from datetime import UTC, datetime

from src.core.board import PostBoard
from tests.fakes.fake_clock import DEFAULT_START, FakeClock


def _clock() -> FakeClock:
    return FakeClock()


def _ts(clock: FakeClock) -> datetime:
    return clock.now()


# --- Add ---------------------------------------------------------------------


def test_add_post_erhält_id_1_und_feld_werte() -> None:
    board = PostBoard()
    clock = _clock()
    clock.tick(seconds=5)

    post = board.add_post("hallo welt", "192.168.1.7", _ts(clock))

    assert post["id"] == 1
    assert post["text"] == "hallo welt"
    assert post["sender"] == "192.168.1.7"
    # ISO-8601-UTC-String, korrekt übernommen aus der übergebenen Zeit
    assert post["timestamp"] == clock.now().isoformat()
    assert isinstance(post["timestamp"], str)


def test_add_post_aufsteigende_ids() -> None:
    board = PostBoard()
    clock = _clock()

    ids = [board.add_post(f"post {i}", "test-ip", _ts(clock))["id"] for i in range(5)]

    assert ids == [1, 2, 3, 4, 5]


def test_add_post_timestamp_wird_iso_utc_string() -> None:
    board = PostBoard()
    clock = _clock()

    post = board.add_post("x", "test-ip", _ts(clock))

    parsed = datetime.fromisoformat(post["timestamp"])
    assert parsed == clock.now()
    assert parsed.tzinfo is not None
    assert parsed.utcoffset() is not None
    assert parsed.utcoffset().total_seconds() == 0


# --- Add-Validierung ----------------------------------------------------------


def test_add_post_leerer_text_value_error() -> None:
    board = PostBoard()
    clock = _clock()

    try:
        board.add_post("", "test-ip", _ts(clock))
    except ValueError as exc:
        assert str(exc) != ""
    else:
        raise AssertionError("ValueError erwartet")


def test_add_post_nur_whitespace_value_error() -> None:
    board = PostBoard()
    clock = _clock()

    for text in ("   ", "\t", "\n  \t "):
        try:
            board.add_post(text, "test-ip", _ts(clock))
        except ValueError:
            pass
        else:
            raise AssertionError(f"ValueError erwartet bei {text!r}")


def test_add_post_zu_langer_text_value_error_meldung_enthaelt_grenzwert() -> None:
    board = PostBoard(max_text_length=10)
    clock = _clock()

    try:
        board.add_post("a" * 11, "test-ip", _ts(clock))
    except ValueError as exc:
        meldung = str(exc)
        assert "10" in meldung  # Grenzwert in der Meldung
    else:
        raise AssertionError("ValueError erwartet")


def test_add_post_default_grenzwert_100000_steht_in_meldung() -> None:
    board = PostBoard()
    clock = _clock()

    try:
        board.add_post("a" * 100_001, "test-ip", _ts(clock))
    except ValueError as exc:
        assert "100000" in str(exc)
    else:
        raise AssertionError("ValueError erwartet")


def test_add_post_text_exakt_grenzwert_erlaubt() -> None:
    board = PostBoard(max_text_length=10)
    clock = _clock()

    post = board.add_post("a" * 10, "test-ip", _ts(clock))

    assert post["text"] == "a" * 10


# --- get_posts ----------------------------------------------------------------


def test_get_posts_komplett_aufsteigend() -> None:
    board = PostBoard()
    clock = _clock()

    for i in range(4):
        board.add_post(f"post {i}", "test-ip", _ts(clock))
        clock.tick()

    posts = board.get_posts()

    assert [p["id"] for p in posts] == [1, 2, 3, 4]
    assert [p["text"] for p in posts] == ["post 0", "post 1", "post 2", "post 3"]


def test_get_posts_since_id_1_nur_posts_ab_2() -> None:
    board = PostBoard()
    clock = _clock()

    for i in range(4):
        board.add_post(f"post {i}", "test-ip", _ts(clock))
        clock.tick()

    posts = board.get_posts(since_id=1)

    assert [p["id"] for p in posts] == [2, 3, 4]


def test_get_posts_since_id_0_alle_posts() -> None:
    board = PostBoard()
    clock = _clock()

    for i in range(3):
        board.add_post(f"post {i}", "test-ip", _ts(clock))
        clock.tick()

    assert [p["id"] for p in board.get_posts(since_id=0)] == [1, 2, 3]


def test_get_posts_seit_letztem_post_leer() -> None:
    board = PostBoard()
    clock = _clock()

    board.add_post("nur einer", "test-ip", _ts(clock))

    assert board.get_posts(since_id=1) == []


# --- Clear all ----------------------------------------------------------------


def test_clear_all_leert_liste_und_consume_cleared_true_dann_false() -> None:
    board = PostBoard()
    clock = _clock()

    board.add_post("a", "test-ip", _ts(clock))
    board.add_post("b", "test-ip", _ts(clock))

    assert board.get_posts() != []
    assert board.consume_cleared() is False  # vor Clear kein Signal

    board.clear_all()

    assert board.get_posts() == []
    assert board.consume_cleared() is True  # True genau einmal
    assert board.consume_cleared() is False  # danach wieder False


# --- Clear last ---------------------------------------------------------------


def test_clear_last_entfernt_nur_letzten_post_und_setzt_signal() -> None:
    board = PostBoard()
    clock = _clock()

    board.add_post("a", "test-ip", _ts(clock))
    board.add_post("b", "test-ip", _ts(clock))
    board.add_post("c", "test-ip", _ts(clock))

    board.clear_last()

    assert [p["id"] for p in board.get_posts()] == [1, 2]
    assert board.consume_cleared() is True
    assert board.consume_cleared() is False


def test_clear_last_auf_leerem_board_setzt_signal() -> None:
    board = PostBoard()

    board.clear_last()

    assert board.get_posts() == []
    assert board.consume_cleared() is True
    assert board.consume_cleared() is False


def test_get_posts_nach_clear_all_und_neuem_add_id_monoton() -> None:
    board = PostBoard()
    clock = _clock()

    board.add_post("a", "test-ip", _ts(clock))
    board.clear_all()
    post = board.add_post("b", "test-ip", _ts(clock))

    # ID-Counter bleibt monoton, startet nicht neu
    assert post["id"] == 2
    assert [p["id"] for p in board.get_posts()] == [2]


# --- FIFO-Limit ---------------------------------------------------------------


def test_fifo_max_posts_3_mit_5_adds_nur_ids_3_4_5() -> None:
    board = PostBoard(max_posts=3)
    clock = _clock()

    for i in range(5):
        board.add_post(f"post {i}", "test-ip", _ts(clock))
        clock.tick()

    posts = board.get_posts()

    assert [p["id"] for p in posts] == [3, 4, 5]
    assert [p["text"] for p in posts] == ["post 2", "post 3", "post 4"]


# --- simuliere_post (Simulation-Helper) ---------------------------------------


def test_simuliere_post_ohne_argumente_deterministisch() -> None:
    board = PostBoard()

    post = board.simuliere_post()

    assert post == {
        "id": 1,
        "text": "test",
        "sender": "test-ip",
        "timestamp": DEFAULT_START.isoformat(),
    }
    assert DEFAULT_START == datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    assert [p["id"] for p in board.get_posts()] == [1]


def test_simuliere_post_mit_argumenten_und_now() -> None:
    board = PostBoard()
    clock = FakeClock()
    clock.tick(seconds=42)

    post = board.simuliere_post(text="eigener text", sender="10.0.0.2", now=clock.now())

    assert post["text"] == "eigener text"
    assert post["sender"] == "10.0.0.2"
    assert post["timestamp"] == clock.now().isoformat()


# --- RAM-only / Restart-Semantik (REQ-007) ------------------------------------


def test_neues_board_ist_leer_ram_only() -> None:
    board = PostBoard()
    clock = _clock()

    board.add_post("a", "test-ip", _ts(clock))
    board.add_post("b", "test-ip", _ts(clock))

    frisches_board = PostBoard()

    assert frisches_board.get_posts() == []
    assert frisches_board.consume_cleared() is False