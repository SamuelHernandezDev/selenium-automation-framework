"""
Reusable form validation checks.
"""

from __future__ import annotations

from time import perf_counter
from typing import Callable
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.evidence_collector import EvidenceCollector
from core.result import CheckResult, Severity


CONTACT_PATH = "/contact"


def check_empty_contact_submit_shows_errors(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify empty contact form submission shows required field errors.
    """

    check_name = "forms.empty_contact_submit_errors"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()
    expected_errors = {
        "name-error": "Name is required.",
        "email-error": "Email is required.",
        "message-error": "Message is required.",
    }

    try:
        driver.get(_contact_url(base_url))
        driver.find_element(By.ID, "submit-contact").click()
        _wait_for_element(driver, "name-error")

        actual_errors = {
            error_id: driver.find_element(By.ID, error_id).text.strip()
            for error_id in expected_errors
        }
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if actual_errors == expected_errors:
            result = CheckResult.passed(
                check_name,
                "Empty contact submit shows expected required field errors.",
                expected=str(expected_errors),
                actual=str(actual_errors),
                evidence=evidence,
                tags=["forms", "validation", "negative"],
            )
        else:
            result = CheckResult.failed(
                check_name,
                "Required field errors do not match expectations.",
                severity=Severity.HIGH,
                expected=str(expected_errors),
                actual=str(actual_errors),
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["forms", "validation", "negative"],
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
        )


def check_valid_contact_submit_reaches_success(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify valid contact form submission reaches the success state.
    """

    check_name = "forms.valid_contact_submit_success"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(_contact_url(base_url))
        driver.find_element(By.ID, "name").send_keys("Grace Hopper")
        driver.find_element(By.ID, "email").send_keys("grace@example.com")
        driver.find_element(By.ID, "message").send_keys(
            "This is a valid form submission message."
        )
        driver.find_element(By.ID, "submit-contact").click()

        heading = driver.find_element(By.TAG_NAME, "h1").text.strip()
        success_message = driver.find_element(By.ID, "success-message").text.strip()
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if heading == "Contact Submitted" and "Grace Hopper" in success_message:
            result = CheckResult.passed(
                check_name,
                "Valid contact form submission reaches the success state.",
                expected="Contact Submitted",
                actual=success_message,
                evidence=evidence,
                tags=["forms", "validation", "positive"],
            )
        else:
            result = CheckResult.failed(
                check_name,
                "Valid contact form submission did not reach success state.",
                severity=Severity.HIGH,
                expected="Contact Submitted with submitted name",
                actual=f"{heading}: {success_message}",
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["forms", "validation", "positive"],
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
        )


def check_contact_error_messages_are_accessible(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify invalid fields reference visible error messages.
    """

    check_name = "forms.accessible_contact_errors"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(_contact_url(base_url))
        driver.find_element(By.ID, "submit-contact").click()
        _wait_for_element(driver, "name-error")

        field_ids = [
            "name",
            "email",
            "message",
        ]
        inaccessible = []

        for field_id in field_ids:
            field = driver.find_element(By.ID, field_id)
            error_id = field.get_attribute("aria-describedby")
            invalid_state = field.get_attribute("aria-invalid")
            error_text = driver.find_element(By.ID, error_id).text.strip()

            if invalid_state != "true" or not error_text:
                inaccessible.append(field_id)

        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if inaccessible:
            result = CheckResult.failed(
                check_name,
                "One or more invalid fields do not expose accessible errors.",
                severity=Severity.HIGH,
                expected="Invalid fields reference visible errors",
                actual=", ".join(inaccessible),
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["forms", "accessibility", "validation"],
                metadata={
                    "inaccessible_fields": inaccessible,
                },
            )
        else:
            result = CheckResult.passed(
                check_name,
                "Invalid fields expose accessible error messages.",
                expected="Invalid fields reference visible errors",
                actual="All invalid fields expose errors",
                evidence=evidence,
                tags=["forms", "accessibility", "validation"],
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
        )


def _contact_url(base_url: str) -> str:
    """
    Return the contact page URL for a base URL.
    """

    return urljoin(
        base_url,
        CONTACT_PATH,
    )


def _unexpected_error(
    driver,
    collector: EvidenceCollector,
    check_name: str,
    exc: Exception,
    start: float,
) -> CheckResult:
    """
    Build a consistent unexpected-error result.
    """

    result = CheckResult.errored(
        check_name,
        "Unexpected error while executing form validation check.",
        evidence=collector.failure_bundle(
            driver,
            check_name,
            exc,
        ),
        tags=["forms", "runner"],
        error=repr(exc),
    )
    result.duration_ms = _duration_ms(start)

    return result


def _wait_for_element(driver, element_id: str):
    """
    Wait until an element exists after form submission.
    """

    return WebDriverWait(
        driver,
        10,
    ).until(
        EC.presence_of_element_located(
            (By.ID, element_id)
        )
    )


def _duration_ms(start: float) -> int:
    """
    Return elapsed milliseconds from a perf_counter start value.
    """

    return int(
        (perf_counter() - start) * 1000
    )


FORM_VALIDATION_CHECKS: dict[str, Callable[..., CheckResult]] = {
    "empty_contact_submit_errors": check_empty_contact_submit_shows_errors,
    "valid_contact_submit_success": check_valid_contact_submit_reaches_success,
    "accessible_contact_errors": check_contact_error_messages_are_accessible,
}
