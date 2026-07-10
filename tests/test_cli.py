"""
Unit tests for the public CLI layer.
"""

from pathlib import Path
from types import SimpleNamespace

from core import cli


def test_cli_list_outputs_registered_suites(capsys):
    exit_code = cli.main(
        [
            "list",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"suites"' in captured.out
    assert '"auth"' in captured.out
    assert '"data.ticket_priority_sort"' in captured.out


def test_cli_list_can_filter_checks_by_suite(capsys):
    exit_code = cli.main(
        [
            "list",
            "--suite",
            "data",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"ticket_priority_sort"' in captured.out
    assert "navigation.page_title" not in captured.out


def test_cli_report_returns_error_when_latest_report_is_missing(tmp_path, capsys):
    exit_code = cli.main(
        [
            "report",
            "--reports-dir",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "No latest run report found" in captured.err


def test_cli_report_prints_latest_summary(tmp_path, capsys):
    report_path = tmp_path / "json" / "latest_run.json"
    report_path.parent.mkdir(
        parents=True,
    )
    report_path.write_text(
        """
{
  "run_id": "abc123",
  "target": {
    "profile": "local_demo",
    "suite": "auth,data"
  },
  "summary": {
    "total_checks": 7,
    "passed": 7,
    "failed": 0,
    "warning": 0,
    "skipped": 0,
    "error": 0
  }
}
""",
        encoding="utf-8",
    )

    exit_code = cli.main(
        [
            "report",
            "--reports-dir",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Latest automation report" in captured.out
    assert "Run ID: abc123" in captured.out
    assert "7 total, 7 passed" in captured.out


def test_cli_run_uses_runner_contract(monkeypatch, tmp_path, capsys):
    saved_args = {}

    class FakeRunner:
        def __init__(self, settings, *, suites=None, checks=None):
            saved_args["settings"] = settings
            saved_args["suites"] = suites
            saved_args["checks"] = checks

        def run(self):
            return SimpleNamespace(
                run_id="run123",
                target_url="http://example.test",
                profile="demo",
                suite="data",
                has_failures=False,
                summary=lambda: {
                    "total_checks": 1,
                    "passed": 1,
                    "failed": 0,
                    "warning": 0,
                    "skipped": 0,
                    "error": 0,
                },
            )

        def save(self, run_result):
            return {
                "latest": Path("reports/json/latest_run.json"),
                "run": Path("reports/json/run123.json"),
                "latest_ai_context": Path("reports/json/latest_ai_context.json"),
                "ai_context": Path("reports/json/run123_ai_context.json"),
                "latest_html_report": Path("reports/html/latest_report.html"),
                "html_report": Path("reports/html/run123.html"),
            }

    settings = SimpleNamespace(
        base_url="http://profile.test",
        profile="demo",
        browser=SimpleNamespace(
            headless=True,
        ),
    )

    monkeypatch.setattr(
        cli,
        "load_settings",
        lambda profile: settings,
    )
    monkeypatch.setattr(
        cli,
        "TestRunner",
        FakeRunner,
    )

    exit_code = cli.main(
        [
            "run",
            "--profile",
            "demo",
            "--base-url",
            "http://example.test",
            "--suite",
            "data",
            "--check",
            "ticket_priority_sort",
            "--headless",
            "false",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert settings.base_url == "http://example.test"
    assert settings.browser.headless is False
    assert saved_args["suites"] == ["data"]
    assert saved_args["checks"] == ["ticket_priority_sort"]
    assert "Automation run completed" in captured.out
