"""
Unit tests for AI-ready context generation.
"""

from core.ai_context_builder import AIContextBuilder
from core.result import CheckResult, Severity, TestRunResult as RunResult


def test_ai_context_reports_no_risk_when_all_checks_pass():
    run = RunResult(
        target_url="https://example.com",
        suite="navigation",
    )
    run.add_check(
        CheckResult.passed(
            "navigation.page_title",
            "Title captured.",
            tags=["navigation"],
            metadata={
                "suite": "navigation",
            },
        )
    )

    context = AIContextBuilder().build(run)

    assert context["summary"]["risk_level"] == "none"
    assert context["findings"] == []
    assert context["coverage"]["executed_suites"] == ["navigation"]
    assert context["suggested_test_cases"]


def test_ai_context_builds_findings_and_priorities():
    run = RunResult(
        target_url="https://example.com",
        suite="accessibility",
    )
    run.add_check(
        CheckResult.failed(
            "accessibility.form_control_names",
            "Controls are missing accessible names.",
            severity=Severity.HIGH,
            expected="Every control has a label.",
            actual="2 unnamed controls.",
            tags=["accessibility", "forms"],
            metadata={
                "suite": "accessibility",
            },
        )
    )

    context = AIContextBuilder().build(run)

    assert context["summary"]["risk_level"] == "high"
    assert context["summary"]["severity_counts"] == {
        "high": 1,
    }
    assert context["findings"][0]["check"] == "accessibility.form_control_names"
    assert context["suggested_test_cases"][0]["priority"] == "high"
