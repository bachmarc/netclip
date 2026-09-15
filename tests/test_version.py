"""Story 00-01: Version-Modul muss APP_VERSION = "0.1.0" liefern.

Reine Import-Assertion — keine externen Systeme, kein Netzwerk, kein Server.
Schützt gegen versehentliche Versions-Bumps.
"""

from src.version import APP_VERSION


def test_app_version_is_0_1_0() -> None:
    assert APP_VERSION == "0.1.0"
