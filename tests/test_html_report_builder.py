"""
Unit tests for static HTML report generation.
"""

from core.ai_context_builder import AIContextBuilder
from core.html_report_builder import HTMLReportBuilder
from core.result import CheckResult, Severity, TestRunResult as RunResult


def test_html_report_includes_summary_and_check_details():
    run = RunResult(
        target_url="https://example.com",
        suite="navigation",
        profile="demo",
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
    run.finish()
    context = AIContextBuilder().build(run)

    html = HTMLReportBuilder().build(
        run,
        context,
    )

    assert "<!doctype html>" in html
    assert "Automation Report" in html
    assert "navigation.page_title" in html
    assert "Title captured." in html
    assert "risk-none" in html


def test_html_report_escapes_check_content():
    run = RunResult(
        target_url="https://example.com",
        suite="navigation",
    )
    run.add_check(
        CheckResult.failed(
            "navigation.<script>",
            "Unexpected <strong>markup</strong>.",
            severity=Severity.HIGH,
            tags=["navigation"],
            metadata={
                "suite": "navigation",
            },
        )
    )
    context = AIContextBuilder().build(run)

    html = HTMLReportBuilder().build(
        run,
        context,
    )

    assert "navigation.&lt;script&gt;" in html
    assert "Unexpected &lt;strong&gt;markup&lt;/strong&gt;." in html
    assert "Unexpected <strong>markup</strong>." not in html


def test_html_report_save_writes_file(tmp_path):
    run = RunResult(
        target_url="https://example.com",
        suite="navigation",
    )
    run.add_check(
        CheckResult.passed(
            "navigation.page_title",
            "Title captured.",
            metadata={
                "suite": "navigation",
            },
        )
    )
    context = AIContextBuilder().build(run)

    output_path = HTMLReportBuilder().save(
        run,
        context,
        tmp_path / "report.html",
    )

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").startswith("<!doctype html>")
