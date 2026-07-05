"""
Lightweight visual and layout checks.

These checks provide browser-rendering signals that are useful for
smoke tests and AI-ready reports without introducing visual diffing yet.
"""

from __future__ import annotations

from time import perf_counter
from typing import Callable

from selenium.webdriver.common.by import By

from core.evidence_collector import EvidenceCollector
from core.result import CheckResult, Severity


def check_page_renders_body(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify the page body renders with visible content.
    """

    check_name = "visual.body_renders"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(base_url)
        body = driver.find_element(By.TAG_NAME, "body")
        body_text = body.text.strip()
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            ),
            collector.capture_screenshot(
                driver,
                label=f"{check_name}_screenshot",
            ),
        ]

        if body.is_displayed() and body_text:
            result = CheckResult.passed(
                check_name,
                "Page body rendered with visible text content.",
                expected="Visible body with non-empty text",
                actual=body_text[:500],
                evidence=evidence,
                tags=["visual", "smoke"],
            )
        elif body.is_displayed():
            result = CheckResult.warning(
                check_name,
                "Page body is visible but does not contain text content.",
                expected="Visible body with non-empty text",
                actual="Visible body with empty text",
                evidence=evidence,
                tags=["visual", "smoke"],
            )
        else:
            result = CheckResult.failed(
                check_name,
                "Page body is not visible.",
                severity=Severity.HIGH,
                expected="Visible body",
                actual="Body is hidden",
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["visual", "smoke"],
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
            tags=["visual", "smoke"],
        )


def check_no_horizontal_overflow(
    driver,
    base_url: str,
    *,
    tolerance_px: int = 2,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify the document does not overflow horizontally.
    """

    check_name = "visual.horizontal_overflow"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(base_url)
        metrics = driver.execute_script(
            """
            const root = document.documentElement;
            const body = document.body;
            const scrollWidth = Math.max(root.scrollWidth, body.scrollWidth);
            const clientWidth = root.clientWidth;

            return {
              scrollWidth,
              clientWidth,
              overflowPx: scrollWidth - clientWidth,
              viewportWidth: window.innerWidth,
              viewportHeight: window.innerHeight,
            };
            """
        )
        overflow_px = int(metrics.get("overflowPx", 0))
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            ),
            collector.capture_screenshot(
                driver,
                label=f"{check_name}_screenshot",
            ),
        ]

        if overflow_px <= tolerance_px:
            result = CheckResult.passed(
                check_name,
                "Page does not appear to overflow horizontally.",
                expected=f"Overflow <= {tolerance_px}px",
                actual=f"Overflow: {overflow_px}px",
                evidence=evidence,
                tags=["visual", "layout"],
                metadata=metrics,
            )
        else:
            result = CheckResult.failed(
                check_name,
                "Page appears to overflow horizontally.",
                severity=Severity.MEDIUM,
                expected=f"Overflow <= {tolerance_px}px",
                actual=f"Overflow: {overflow_px}px",
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["visual", "layout"],
                metadata=metrics,
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
            tags=["visual", "layout"],
        )


def check_viewport_screenshot(
    driver,
    base_url: str,
    *,
    label: str = "viewport",
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Capture a screenshot as baseline evidence for visual review.
    """

    check_name = "visual.viewport_screenshot"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(base_url)
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            ),
            collector.capture_screenshot(
                driver,
                label=label,
            ),
        ]

        result = CheckResult.passed(
            check_name,
            "Viewport screenshot was captured successfully.",
            expected="Screenshot artifact",
            actual=label,
            evidence=evidence,
            tags=["visual", "evidence"],
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
            tags=["visual", "evidence"],
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
        "Unexpected error while executing visual check.",
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


VISUAL_CHECKS: dict[str, Callable[..., CheckResult]] = {
    "body_renders": check_page_renders_body,
    "horizontal_overflow": check_no_horizontal_overflow,
    "viewport_screenshot": check_viewport_screenshot,
}
