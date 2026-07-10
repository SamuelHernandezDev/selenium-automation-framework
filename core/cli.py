"""
Professional command-line interface for the automation framework.

This module keeps the public CLI focused on user-facing commands while
reusing the existing runner, settings, registry, and report generation logic.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from checks.registry import available_checks, available_suites
from config.settings import load_settings
from core.test_runner import TestRunner, _print_summary


def build_parser() -> argparse.ArgumentParser:
    """
    Build the top-level CLI parser.
    """

    parser = argparse.ArgumentParser(
        prog="qa-auto",
        description="Run Selenium checks and inspect generated QA reports.",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    _add_run_parser(subparsers)
    _add_list_parser(subparsers)
    _add_report_parser(subparsers)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    CLI entry point.
    """

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "run":
            return _run_command(args)

        if args.command == "list":
            return _list_command(args)

        if args.command == "report":
            return _report_command(args)

        parser.error(f"Unknown command: {args.command}")

    except Exception as exc:
        print(
            f"CLI error: {exc}",
            file=sys.stderr,
        )
        return 2

    return 2


def _add_run_parser(subparsers) -> None:
    """
    Add the run command parser.
    """

    parser = subparsers.add_parser(
        "run",
        help="Execute configured Selenium checks.",
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
        help="Check to run by name or suite.name. Can be passed multiple times.",
    )
    parser.add_argument(
        "--base-url",
        help="Override the profile base URL for this run.",
    )
    parser.add_argument(
        "--headless",
        choices=[
            "true",
            "false",
        ],
        help="Override browser headless mode.",
    )


def _add_list_parser(subparsers) -> None:
    """
    Add the list command parser.
    """

    parser = subparsers.add_parser(
        "list",
        help="List registered suites and checks.",
    )
    parser.add_argument(
        "--suite",
        choices=available_suites(),
        help="Limit listed checks to one suite.",
    )


def _add_report_parser(subparsers) -> None:
    """
    Add the report command parser.
    """

    parser = subparsers.add_parser(
        "report",
        help="Show paths and summary for the latest generated report.",
    )
    parser.add_argument(
        "--reports-dir",
        default="reports",
        help="Reports directory to inspect.",
    )


def _run_command(args: argparse.Namespace) -> int:
    """
    Execute a runner command and save reports.
    """

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


def _list_command(args: argparse.Namespace) -> int:
    """
    Print registered suites and checks.
    """

    payload = {
        "suites": available_suites(),
        "checks": (
            available_checks(args.suite)
            if args.suite
            else available_checks()
        ),
    }

    print(
        json.dumps(
            payload,
            indent=2,
        )
    )

    return 0


def _report_command(args: argparse.Namespace) -> int:
    """
    Print a compact summary for the latest generated report.
    """

    reports_dir = Path(args.reports_dir)
    latest_run = reports_dir / "json" / "latest_run.json"
    latest_ai_context = reports_dir / "json" / "latest_ai_context.json"
    latest_html_report = reports_dir / "html" / "latest_report.html"

    if not latest_run.exists():
        print(
            f"No latest run report found at {latest_run}.",
            file=sys.stderr,
        )
        return 1

    payload = json.loads(
        latest_run.read_text(
            encoding="utf-8",
        )
    )
    summary = payload.get(
        "summary",
        {},
    )
    target = payload.get(
        "target",
        {},
    )

    print("Latest automation report")
    print(f"Run ID: {payload.get('run_id', 'unknown')}")
    print(f"Profile: {target.get('profile', 'unknown')}")
    print(f"Suites: {target.get('suite', 'unknown')}")
    print(
        "Checks: "
        f"{summary.get('total_checks', 0)} total, "
        f"{summary.get('passed', 0)} passed, "
        f"{summary.get('failed', 0)} failed, "
        f"{summary.get('warning', 0)} warning, "
        f"{summary.get('skipped', 0)} skipped, "
        f"{summary.get('error', 0)} error"
    )
    print(f"Latest JSON: {latest_run}")
    print(f"Latest AI Context: {latest_ai_context}")
    print(f"Latest HTML Report: {latest_html_report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
