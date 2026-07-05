"""
Reusable checks for application error states.
"""

from __future__ import annotations

from time import perf_counter
from typing import Callable

from core.evidence_collector import EvidenceCollector
from core.result import CheckResult, Severity
from pages.home_page import HomePage


DEFAULT_STATUS_CODES = [
    "200",
    "301",
    "404",
    "500",
]


def check_available_status_codes(
    driver,
    base_url: str,
    *,
    expected_codes: list[str] | None = None,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify that the status code page exposes expected error states.
    """

    check_name = "error_states.available_status_codes"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()
    expected = expected_codes or DEFAULT_STATUS_CODES

    try:
        status_codes_page = _open_status_codes_page(driver, base_url)
        actual_codes = status_codes_page.get_codes()
        missing_codes = [
            code
            for code in expected
            if code not in actual_codes
        ]
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if missing_codes:
            evidence.extend(
                collector.failure_bundle(
                    driver,
                    check_name,
                )
            )
            result = CheckResult.failed(
                check_name,
                "Expected status codes were not available.",
                severity=Severity.MEDIUM,
                expected=", ".join(expected),
                actual=", ".join(actual_codes),
                evidence=evidence,
                tags=["error_states", "status_codes"],
                metadata={
                    "missing_codes": missing_codes,
                },
            )
        else:
            result = CheckResult.passed(
                check_name,
                "Expected status codes are available.",
                expected=", ".join(expected),
                actual=", ".join(actual_codes),
                evidence=evidence,
                tags=["error_states", "status_codes"],
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
            tags=["error_states", "status_codes"],
        )


def check_status_code_message(
    driver,
    base_url: str,
    *,
    code: str = "500",
    expected_text: str | None = None,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify that a status code detail page shows a useful message.
    """

    check_name = f"error_states.status_{code}_message"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()
    expected = expected_text or code

    try:
        status_codes_page = _open_status_codes_page(driver, base_url)
        status_codes_page.open_code(code)

        actual_message = status_codes_page.get_message()
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if expected not in actual_message:
            evidence.extend(
                collector.failure_bundle(
                    driver,
                    check_name,
                )
            )
            result = CheckResult.failed(
                check_name,
                "Status code page message did not contain the expected text.",
                severity=Severity.MEDIUM,
                expected=expected,
                actual=actual_message,
                evidence=evidence,
                tags=["error_states", "status_code_message"],
            )
        elif not actual_message.strip():
            result = CheckResult.warning(
                check_name,
                "Status code page message is empty.",
                expected=expected,
                actual=actual_message,
                evidence=evidence,
                tags=["error_states", "status_code_message"],
            )
        else:
            result = CheckResult.passed(
                check_name,
                "Status code page message contains the expected text.",
                expected=expected,
                actual=actual_message,
                evidence=evidence,
                tags=["error_states", "status_code_message"],
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
            tags=["error_states", "status_code_message"],
        )


def _open_status_codes_page(driver, base_url: str):
    """
    Navigate from the home page to the status codes page.
    """

    home = HomePage(driver)
    home.open(base_url)

    return (
        home
        .go_to_redirect()
        .go_to_status_codes()
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
        "Unexpected error while executing error-state check.",
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


ERROR_STATE_CHECKS: dict[str, Callable[..., CheckResult]] = {
    "available_status_codes": check_available_status_codes,
    "status_code_message": check_status_code_message,
}
