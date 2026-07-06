"""
Automation test runner.

This module turns framework configuration and registered checks into an
executable run that produces structured JSON results.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from checks.registry import available_checks, available_suites, resolve_checks
from config.settings import FrameworkSettings, load_settings
from core.ai_context_builder import AIContextBuilder
from core.driver_factory import create_driver
from core.evidence_collector import EvidenceCollector
from core.html_report_builder import HTMLReportBuilder
from core.result import CheckResult, Severity, TestRunResult


class TestRunner:
    """
    Execute registered checks using framework settings.
    """

    def __init__(
        self,
        settings: FrameworkSettings,
        *,
        suites: list[str] | None = None,
        checks: list[str] | None = None,
    ) -> None:
        self.settings = settings
        self.suites = suites or settings.suites
        self.checks = checks
        self.evidence_collector = EvidenceCollector(
            settings.reports_dir
        )

    def run(self) -> TestRunResult:
        """
        Execute the configured suites/checks and return a run result.
        """

        run_result = TestRunResult(
            target_url=self.settings.base_url,
            suite=",".join(self.suites),
            profile=self.settings.profile,
            browser=self.settings.browser.name,
            headless=self.settings.browser.headless,
            metadata={
                **self.settings.metadata,
                "selected_suites": self.suites,
                "selected_checks": self.checks or ["*"],
            },
        )

        driver = None

        try:
            driver = create_driver(self.settings)

            for suite, check_name, check in self._selected_checks():
                result = self._execute_check(
                    check,
                    suite=suite,
                    check_name=check_name,
                    driver=driver,
                )
                run_result.add_check(result)

        finally:
            if driver is not None:
                driver.quit()

            run_result.finish()

        return run_result

    def save(self, run_result: TestRunResult) -> dict[str, Path]:
        """
        Save run artifacts and return their paths.
        """

        json_dir = self.settings.reports_dir / "json"
        html_dir = self.settings.reports_dir / "html"
        latest_path = json_dir / "latest_run.json"
        run_path = json_dir / f"{run_result.run_id}.json"
        latest_ai_context_path = json_dir / "latest_ai_context.json"
        ai_context_path = json_dir / f"{run_result.run_id}_ai_context.json"
        latest_html_path = html_dir / "latest_report.html"
        html_path = html_dir / f"{run_result.run_id}.html"
        ai_context = AIContextBuilder().build(run_result)
        html_builder = HTMLReportBuilder()

        run_result.save_json(run_path)
        run_result.save_json(latest_path)
        self._save_json(
            ai_context,
            ai_context_path,
        )
        self._save_json(
            ai_context,
            latest_ai_context_path,
        )
        html_builder.save(
            run_result,
            ai_context,
            html_path,
        )
        html_builder.save(
            run_result,
            ai_context,
            latest_html_path,
        )

        return {
            "run": run_path,
            "latest": latest_path,
            "ai_context": ai_context_path,
            "latest_ai_context": latest_ai_context_path,
            "html_report": html_path,
            "latest_html_report": latest_html_path,
        }

    def _save_json(
        self,
        payload: dict,
        path: Path,
    ) -> Path:
        """
        Save an arbitrary JSON payload.
        """

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return path

    def _selected_checks(self):
        """
        Resolve selected suites and optional check filters.
        """

        resolved = resolve_checks(self.suites)

        if not self.checks:
            return resolved

        selected = set(self.checks)

        return [
            (suite, check_name, check)
            for suite, check_name, check in resolved
            if check_name in selected
            or f"{suite}.{check_name}" in selected
        ]

    def _execute_check(
        self,
        check,
        *,
        suite: str,
        check_name: str,
        driver,
    ) -> CheckResult:
        """
        Execute a check and guard against unexpected runner-level errors.
        """

        try:
            result = check(
                driver,
                self.settings.base_url,
                evidence_collector=self.evidence_collector,
            )
            result.metadata.setdefault("suite", suite)
            result.metadata.setdefault("check_key", check_name)

            return result

        except TypeError as exc:
            return CheckResult.errored(
                f"{suite}.{check_name}",
                "Check could not be executed with the runner contract.",
                severity=Severity.HIGH,
                tags=[suite, "runner"],
                error=repr(exc),
                metadata={
                    "suite": suite,
                    "check_key": check_name,
                },
            )

        except Exception as exc:
            return CheckResult.errored(
                f"{suite}.{check_name}",
                "Unexpected runner-level error while executing check.",
                severity=Severity.HIGH,
                tags=[suite, "runner"],
                error=repr(exc),
                metadata={
                    "suite": suite,
                    "check_key": check_name,
                },
            )


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line parser.
    """

    parser = argparse.ArgumentParser(
        description="Run Selenium automation checks and write JSON reports."
    )
    parser.add_argument(
        "--profile",
        default="default",
        help="Profile name from config/test_profiles.yaml.",
    )
    parser.add_argument(
        "--suite",
        action="append",
        dest="suites",
        choices=available_suites(),
        help="Suite to run. Can be passed multiple times.",
    )
    parser.add_argument(
        "--check",
        action="append",
        dest="checks",
        help=(
            "Check to run by name or suite.name. "
            "Can be passed multiple times."
        ),
    )
    parser.add_argument(
        "--base-url",
        help="Override the profile base URL for this run.",
    )
    parser.add_argument(
        "--headless",
        choices=["true", "false"],
        help="Override browser headless mode.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available suites/checks and exit.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    CLI entry point.
    """

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        print(
            json.dumps(
                {
                    "suites": available_suites(),
                    "checks": available_checks(),
                },
                indent=2,
            )
        )
        return 0

    try:
        settings = load_settings(args.profile)

        if args.base_url:
            settings.base_url = args.base_url

        if args.headless:
            settings.browser.headless = args.headless == "true"

        runner = TestRunner(
            settings,
            suites=args.suites,
            checks=args.checks,
        )
        run_result = runner.run()
        output_paths = runner.save(run_result)

        _print_summary(
            run_result,
            output_paths,
        )

        return 1 if run_result.has_failures else 0

    except Exception as exc:
        print(
            f"Runner error: {exc}",
            file=sys.stderr,
        )
        return 2


def _print_summary(
    run_result: TestRunResult,
    output_paths: dict[str, Path],
) -> None:
    """
    Print a compact run summary for CLI users.
    """

    summary = run_result.summary()

    print("Automation run completed")
    print(f"Run ID: {run_result.run_id}")
    print(f"Target: {run_result.target_url}")
    print(f"Profile: {run_result.profile}")
    print(f"Suites: {run_result.suite}")
    print(
        "Checks: "
        f"{summary['total_checks']} total, "
        f"{summary['passed']} passed, "
        f"{summary['failed']} failed, "
        f"{summary['warning']} warning, "
        f"{summary['skipped']} skipped, "
        f"{summary['error']} error"
    )
    print(f"Latest JSON: {output_paths['latest']}")
    print(f"Run JSON: {output_paths['run']}")
    print(f"Latest AI Context: {output_paths['latest_ai_context']}")
    print(f"AI Context: {output_paths['ai_context']}")
    print(f"Latest HTML Report: {output_paths['latest_html_report']}")
    print(f"HTML Report: {output_paths['html_report']}")


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
