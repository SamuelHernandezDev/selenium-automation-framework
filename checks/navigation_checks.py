"""
Reusable navigation checks.

Checks in this module return CheckResult objects instead of raising
assertions directly, making them usable by pytest, a custom runner,
or an AI-ready reporting pipeline.
"""

from __future__ import annotations

from time import perf_counter
from typing import Callable

from core.evidence_collector import EvidenceCollector
from core.result import CheckResult, Evidence, Severity
from pages.home_page import HomePage


def check_page_title(
    driver,
    base_url: str,
    *,
    expected_title: str | None = None,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Open the target URL and verify the browser title.
    """

    check_name = "navigation.page_title"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        home = HomePage(driver)
        home.open(base_url)

        actual_title = home.get_title()
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        result = _evaluate_text(
            check_name=check_name,
            actual=actual_title,
            expected=expected_title,
            empty_message="Page title is empty.",
            success_message="Page title was captured successfully.",
            mismatch_message="Page title did not match the expected value.",
            tags=["navigation", "smoke"],
            evidence=evidence,
        )

        if result.is_blocking:
            result.evidence.extend(
                collector.failure_bundle(
                    driver,
                    check_name,
                )
            )

        result.duration_ms = _duration_ms(start)

        return result

    except Exception as exc:
        return _unexpected_error(
            driver,
            collector,
            check_name,
            exc,
            start,
            tags=["navigation", "smoke"],
        )


def check_redirect_link_flow(
    driver,
    base_url: str,
    *,
    expected_heading: str = "Redirection",
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify the home page redirect link opens the redirect page.
    """

    check_name = "navigation.redirect_link_flow"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        home = HomePage(driver)
        home.open(base_url)

        redirect_page = home.go_to_redirect()
        actual_heading = redirect_page.get_heading()
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        result = _evaluate_text(
            check_name=check_name,
            actual=actual_heading,
            expected=expected_heading,
            empty_message="Redirect page heading is empty.",
            success_message="Redirect flow reached the expected page.",
            mismatch_message="Redirect page heading did not match.",
            tags=["navigation", "redirect"],
            evidence=evidence,
            severity=Severity.MEDIUM,
        )

        if result.is_blocking:
            result.evidence.extend(
                collector.failure_bundle(
                    driver,
                    check_name,
                )
            )

        result.duration_ms = _duration_ms(start)

        return result

    except Exception as exc:
        return _unexpected_error(
            driver,
            collector,
            check_name,
            exc,
            start,
            tags=["navigation", "redirect"],
        )


def check_current_url_contains(
    driver,
    base_url: str,
    *,
    expected_fragment: str | None = None,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify that opening a URL leaves the browser at an expected route.
    """

    check_name = "navigation.current_url_contains"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(base_url)
        actual_url = driver.current_url
        expected = expected_fragment or base_url.rstrip("/")
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if expected in actual_url:
            result = CheckResult.passed(
                check_name,
                "Current URL contains the expected fragment.",
                expected=expected,
                actual=actual_url,
                evidence=evidence,
                tags=["navigation", "url"],
            )
        else:
            evidence.extend(
                collector.failure_bundle(
                    driver,
                    check_name,
                )
            )
            result = CheckResult.failed(
                check_name,
                "Current URL does not contain the expected fragment.",
                severity=Severity.MEDIUM,
                expected=expected,
                actual=actual_url,
                evidence=evidence,
                tags=["navigation", "url"],
            )

        result.duration_ms = _duration_ms(start)

        return result

    except Exception as exc:
        return _unexpected_error(
            driver,
            collector,
            check_name,
            exc,
            start,
            tags=["navigation", "url"],
        )


def _evaluate_text(
    *,
    check_name: str,
    actual: str,
    expected: str | None,
    empty_message: str,
    success_message: str,
    mismatch_message: str,
    tags: list[str],
    evidence: list[Evidence],
    severity: Severity = Severity.LOW,
) -> CheckResult:
    """
    Evaluate common text assertions consistently.
    """

    if expected is not None and actual != expected:
        return CheckResult.failed(
            check_name,
            mismatch_message,
            severity=severity,
            expected=expected,
            actual=actual,
            evidence=evidence,
            tags=tags,
        )

    if not actual.strip():
        return CheckResult.warning(
            check_name,
            empty_message,
            severity=Severity.LOW,
            expected=expected or "Non-empty text",
            actual=actual,
            evidence=evidence,
            tags=tags,
        )

    return CheckResult.passed(
        check_name,
        success_message,
        severity=Severity.LOW,
        expected=expected,
        actual=actual,
        evidence=evidence,
        tags=tags,
    )


def _unexpected_error(
    driver,
    collector: EvidenceCollector,
    check_name: str,
    exc: Exception,
    start: float,
    *,
    tags: list[str],
) -> CheckResult:
    """
    Build a consistent unexpected-error result with evidence.
    """

    result = CheckResult.errored(
        check_name,
        "Unexpected error while executing navigation check.",
        evidence=collector.failure_bundle(
            driver,
            check_name,
            exc,
        ),
        tags=tags,
        error=repr(exc),
    )
    result.duration_ms = _duration_ms(start)

    return result


def _duration_ms(start: float) -> int:
    """
    Return elapsed milliseconds from a perf_counter start value.
    """

    return int(
        (perf_counter() - start) * 1000
    )


NAVIGATION_CHECKS: dict[str, Callable[..., CheckResult]] = {
    "page_title": check_page_title,
    "redirect_link_flow": check_redirect_link_flow,
    "current_url_contains": check_current_url_contains,
}
