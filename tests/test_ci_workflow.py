"""Statische Workflow-Verifikation für Story 08-01 (REQ-017, Design §6).

Liest ``.github/workflows/ci.yml`` und ``docker-compose.yml`` als Text und parsed
das YAML — kein Docker, kein Netz, kein echter Registry-Push. Der echte Push-SMOKE
ist der CI-Lauf selbst auf GitHub (laut Story nicht lokal simulierbar).

Rot-Phase (vor Implementierung): Guards, Login, permissions und compose-``image``
fehlen — alle Assertions hier schlagen fehl. Grün: Workflow pusht bei main-push
nach ghcr.io, PRs pushen nie, compose bleibt build-fähig.
"""

from __future__ import annotations

import pathlib
import unittest

import yaml

WORKFLOW_PATH = pathlib.Path(".github/workflows/ci.yml")
COMPOSE_PATH = pathlib.Path("docker-compose.yml")

IMAGE_LATEST = "ghcr.io/bachmarc/netclip:latest"
IMAGE_SHA = "ghcr.io/bachmarc/netclip:${{ github.sha }}"
PUSH_GUARD = "github.event_name == 'push' && github.ref == 'refs/heads/main'"
LOGIN_ACTION = "docker/login-action@v3"
BUILD_PUSH_ACTION = "docker/build-push-action@v6"


def _load_workflow() -> dict:
    raw = WORKFLOW_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    assert isinstance(data, dict), "ci.yml muss ein YAML-Mapping sein"
    return data


def _docker_build_job(data: dict) -> dict:
    jobs = data.get("jobs", {})
    assert "docker-build" in jobs, "ci.yml muss den Job 'docker-build' enthalten"
    return jobs["docker-build"]


def _steps(job: dict) -> list[dict]:
    steps = job.get("steps", [])
    assert isinstance(steps, list), "docker-build braucht eine steps-Liste"
    return steps


def _steps_using(steps: list[dict], action: str) -> list[dict]:
    return [s for s in steps if s.get("uses") == action]


def _step_names(steps: list[dict]) -> list[str]:
    return [str(s.get("name", "")) for s in steps]


class TestWorkflowYamlValide:
    """Testkriterium 1: YAML parst valide (vor/nach — Guards/Login fehlen zunächst)."""

    def test_workflow_yaml_parst_valide(self) -> None:
        data = _load_workflow()
        assert "jobs" in data

    def test_docker_build_job_existiert(self) -> None:
        job = _docker_build_job(_load_workflow())
        assert isinstance(job, dict)

    def test_lint_test_job_untouched(self) -> None:
        """lint-test-Job bleibt unverändert (Checkout, Python, pip, ruff, pytest)."""
        data = _load_workflow()
        lint = data["jobs"]["lint-test"]
        assert lint["runs-on"] == "ubuntu-latest"
        names = _step_names(lint["steps"])
        assert any("ruff" in n for n in names)
        assert any("pytest" in n for n in names)
        assert not any("ghcr" in n.lower() for n in names)
        assert not any(
            s.get("uses") in {LOGIN_ACTION, BUILD_PUSH_ACTION} for s in lint["steps"]
        )


class TestDockerBuildJobGuard:
    """Testkriterium 2: needs-Kette + permissions (nur grüner Lint+Test pusht)."""

    def test_docker_build_needs_lint_test(self) -> None:
        job = _docker_build_job(_load_workflow())
        assert job.get("needs") == "lint-test"

    def test_permissions_enthaelt_packages_write(self) -> None:
        job = _docker_build_job(_load_workflow())
        perms = job.get("permissions")
        assert isinstance(perms, dict), "docker-build braucht Job-Level permissions"
        assert perms.get("packages") == "write"
        assert perms.get("contents") == "read"


class TestRegistryLogin:
    """Testkriterium 3: Login-Step vor jedem Push (GITHUB_TOKEN, ghcr.io)."""

    def test_login_step_vor_push_steps(self) -> None:
        job = _docker_build_job(_load_workflow())
        steps = _steps(job)
        logins = _steps_using(steps, LOGIN_ACTION)
        assert logins, f"Workflow muss {LOGIN_ACTION} verwenden"

        login_idx = steps.index(logins[0])
        pushes = [s for s in steps if _is_build_push(s)]
        assert pushes, f"Workflow muss {BUILD_PUSH_ACTION} verwenden"
        push_idx = min(steps.index(s) for s in pushes)
        assert login_idx < push_idx, "Login muss VOR Build+Push kommen"

        login = logins[0]["with"]
        assert login.get("registry") == "ghcr.io"
        assert login.get("username") == "${{ github.actor }}"
        assert login.get("password") == "${{ secrets.GITHUB_TOKEN }}"

    def test_login_verwendet_github_token_secret(self) -> None:
        raw = WORKFLOW_PATH.read_text(encoding="utf-8")
        login_block = raw.split(LOGIN_ACTION, 1)[1].split("- ", 1)[0]
        assert "secrets.GITHUB_TOKEN" in login_block
        assert "ghcr.io" in login_block


def _is_build_push(step: dict) -> bool:
    return step.get("uses") == BUILD_PUSH_ACTION


class TestBuildPushTagsUndGuard:
    """Testkriterium 4: Push-Guard — nur bei push-Event auf main, Tags latest+SHA."""

    def test_push_guard_nur_main_push(self) -> None:
        raw = WORKFLOW_PATH.read_text(encoding="utf-8")
        assert PUSH_GUARD in raw, (
            "Push-Bedingung 'github.event_name == push && github.ref == refs/heads/main' fehlt"
        )

    def test_push_nur_nach_login_bei_main(self) -> None:
        """push:true nur innerhalb des guarded build-push-Steps (nach Login)."""
        job = _docker_build_job(_load_workflow())
        steps = _steps(job)
        logins = _steps_using(steps, LOGIN_ACTION)
        assert logins, "Login-Step muss existieren (push:true erst nach Login)"
        login_idx = steps.index(logins[0])
        guarded = [s for s in steps if _is_build_push(s) and PUSH_GUARD in str(s.get("with", {}).get("push", ""))]
        assert guarded, "Guard muss im build-push-Step stehen (push-Parameter-Expression)"
        assert steps.index(guarded[0]) > login_idx

    def test_tags_latest_und_sha(self) -> None:
        job = _docker_build_job(_load_workflow())
        pushes = [s for s in _steps(job) if _is_build_push(s)]
        assert pushes, "build-push-action Step fehlt"
        tags = str(pushes[0].get("with", {}).get("tags", ""))
        assert IMAGE_LATEST in tags, "Tag ghcr.io/bachmarc/netclip:latest fehlt"
        assert IMAGE_SHA in tags, "SHA-Tag ghcr.io/bachmarc/netclip:${{ github.sha }} fehlt"

    def test_pr_nur_build_kein_push(self) -> None:
        """Auf Pull Requests darf nicht gepusht werden — Guard muss das abdecken."""
        raw = WORKFLOW_PATH.read_text(encoding="utf-8")
        build_push_steps = raw.split(BUILD_PUSH_ACTION)[1:]
        assert build_push_steps, "build-push-action fehlt"
        block = build_push_steps[0]
        # push-Parameter ist eine Expression, die ohne Guard false ergibt:
        assert "push:" in block
        push_expr = block.split("push:", 1)[1].split("\n", 1)[0]
        assert "github.event_name" in push_expr, (
            f"push-Parameter muss Guard-Expression enthalten, gefunden: {push_expr!r}"
        )
        assert "github.ref" in push_expr, (
            f"push-Parameter muss ref-Guard enthalten, gefunden: {push_expr!r}"
        )

    def test_context_ist_repo_root(self) -> None:
        job = _docker_build_job(_load_workflow())
        pushes = [s for s in _steps(job) if _is_build_push(s)]
        assert pushes, "build-push-action Step fehlt"
        assert pushes[0].get("with", {}).get("context") == "."


class TestComposeRegistryImage:
    """Testkriterium 5: compose hält build: . und bekommt zusätzlich das ghcr-Image."""

    def test_compose_hat_registry_image_und_build(self) -> None:
        raw = COMPOSE_PATH.read_text(encoding="utf-8")
        assert f"image: {IMAGE_LATEST}" in raw, "compose braucht image: ghcr.io/bachmarc/netclip:latest"
        assert "build: ." in raw, "compose muss build: . behalten"

    def test_compose_yaml_valide_image_neben_build(self) -> None:
        data = yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))
        service = data["services"]["netclip"]
        assert service["image"] == IMAGE_LATEST
        assert service["build"] == "."
        # Bestehende Settings unverändert:
        assert service["ports"] == ["8000:8000"]
        assert service["environment"]["PORT"] == "8000"
        assert service["environment"]["MAX_POSTS"] == "3000"
        assert service["environment"]["MAX_TEXT_LENGTH"] == "100000"
        assert service["restart"] == "unless-stopped"


class TestReadmeDeploymentSektion:
    """Story-Target README: pull-Variante + Public-Sichtbarkeit-Hinweis (deutsch)."""

    def test_readme_dokumentiert_pull_variant(self) -> None:
        raw = pathlib.Path("README.md").read_text(encoding="utf-8")
        assert "docker compose pull" in raw
        assert "docker compose up" in raw

    def test_readme_dokumentiert_public_sichtbarkeit(self) -> None:
        raw = pathlib.Path("README.md").read_text(encoding="utf-8")
        lowered = raw.lower()
        assert "sichtbarkeit" in lowered, "README muss Public-Sichtbarkeit erwähnen"
        assert "public" in lowered, "README muss die Paket-Sichtbarkeit 'public' nennen"
        assert "ghcr.io/bachmarc/netclip" in raw


if __name__ == "__main__":
    unittest.main()