"""
Unit tests for framework result models.
"""

import json

from core.result import CheckResult, CheckStatus, Severity, TestRunResult as RunResult


def test_check_result_serializes_status_and_severity_values():
    result = CheckResult.failed(
        "navigation.page_title",
        "Title mismatch.",
        severity=Severity.HIGH,
        expected="Expected",
        actual="Actual",
        tags=["navigation"],
    )

    payload = result.to_dict()

    assert payload["status"] == "failed"
    assert payload["severity"] == "high"
    assert payload["expected"] == "Expected"
    assert payload["actual"] == "Actual"


def test_test_run_summary_counts_check_statuses():
    run = RunResult(
        target_url="https://example.com",
        suite="navigation",
    )
    run.add_check(
        CheckResult.passed(
            "navigation.page_title",
            "Title captured.",
        )
    )
    run.add_check(
        CheckResult.warning(
            "accessibility.main_heading",
            "Missing h1.",
        )
    )
    run.add_check(
        CheckResult.errored(
            "visual.body_renders",
            "Unexpected error.",
        )
    )

    summary = run.summary()

    assert summary["total_checks"] == 3
    assert summary[CheckStatus.PASSED.value] == 1
    assert summary[CheckStatus.WARNING.value] == 1
    assert summary[CheckStatus.ERROR.value] == 1
    assert summary["has_failures"] is True


def test_test_run_save_json_writes_serialized_payload(tmp_path):
    run = RunResult(
        target_url="https://example.com",
        suite="navigation",
    )
    run.add_check(
        CheckResult.passed(
            "navigation.page_title",
            "Title captured.",
        )
    )
    run.finish()

    output_path = run.save_json(
        tmp_path / "run.json"
    )
    payload = json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    )

    assert payload["run_id"] == run.run_id
    assert payload["summary"]["passed"] == 1
    assert payload["target"]["url"] == "https://example.com"
