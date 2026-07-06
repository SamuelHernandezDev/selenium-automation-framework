"""
Reusable input checks.
"""

from __future__ import annotations

from time import perf_counter
from typing import Callable
from urllib.parse import urljoin

from selenium.webdriver.common.by import By

from core.evidence_collector import EvidenceCollector
from core.result import CheckResult, Severity


CONTACT_PATH = "/contact"


def check_required_contact_inputs(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify required contact form inputs are present.
    """

    check_name = "inputs.required_contact_inputs"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()
    required_fields = {
        "name": "Name",
        "email": "Email",
        "message": "Message",
    }

    try:
        driver.get(_contact_url(base_url))
        missing = []

        for field_id, label_text in required_fields.items():
            elements = driver.find_elements(By.ID, field_id)
            labels = driver.find_elements(
                By.CSS_SELECTOR,
                f"label[for='{field_id}']",
            )

            if not elements:
                missing.append(f"#{field_id}")

            if not labels or labels[0].text.strip() != label_text:
                missing.append(f"label[{field_id}]")

        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if missing:
            result = CheckResult.failed(
                check_name,
                "Required contact inputs or labels are missing.",
                severity=Severity.HIGH,
                expected=", ".join(required_fields),
                actual=", ".join(missing),
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["inputs", "forms", "required"],
                metadata={
                    "missing": missing,
                },
            )
        else:
            result = CheckResult.passed(
                check_name,
                "Required contact inputs and labels are present.",
                expected=", ".join(required_fields),
                actual="All required fields found",
                evidence=evidence,
                tags=["inputs", "forms", "required"],
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


def check_invalid_email_input_feedback(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify invalid email input returns a field-level error.
    """

    check_name = "inputs.invalid_email_feedback"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(_contact_url(base_url))
        driver.find_element(By.ID, "name").send_keys("Ada Lovelace")
        driver.find_element(By.ID, "email").send_keys("invalid-email")
        driver.find_element(By.ID, "message").send_keys(
            "This message is long enough for validation."
        )
        driver.find_element(By.ID, "submit-contact").click()

        error_text = driver.find_element(By.ID, "email-error").text.strip()
        invalid_state = driver.find_element(By.ID, "email").get_attribute(
            "aria-invalid"
        )
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if error_text == "Enter a valid email address." and invalid_state == "true":
            result = CheckResult.passed(
                check_name,
                "Invalid email input shows the expected feedback.",
                expected="Enter a valid email address.",
                actual=error_text,
                evidence=evidence,
                tags=["inputs", "forms", "negative"],
            )
        else:
            result = CheckResult.failed(
                check_name,
                "Invalid email feedback did not match expectations.",
                severity=Severity.HIGH,
                expected="Enter a valid email address. and aria-invalid=true",
                actual=f"{error_text}; aria-invalid={invalid_state}",
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["inputs", "forms", "negative"],
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


def check_contact_input_constraints(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify contact inputs expose expected client-side constraints.
    """

    check_name = "inputs.contact_input_constraints"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(_contact_url(base_url))
        constraints = {
            "name.maxlength": driver.find_element(By.ID, "name").get_attribute(
                "maxlength"
            ),
            "email.type": driver.find_element(By.ID, "email").get_attribute("type"),
            "message.maxlength": driver.find_element(
                By.ID,
                "message",
            ).get_attribute("maxlength"),
        }
        expected = {
            "name.maxlength": "60",
            "email.type": "email",
            "message.maxlength": "500",
        }
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if constraints == expected:
            result = CheckResult.passed(
                check_name,
                "Contact inputs expose expected constraints.",
                expected=str(expected),
                actual=str(constraints),
                evidence=evidence,
                tags=["inputs", "constraints"],
            )
        else:
            result = CheckResult.failed(
                check_name,
                "Contact input constraints do not match expectations.",
                severity=Severity.MEDIUM,
                expected=str(expected),
                actual=str(constraints),
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["inputs", "constraints"],
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
        "Unexpected error while executing input check.",
        evidence=collector.failure_bundle(
            driver,
            check_name,
            exc,
        ),
        tags=["inputs", "runner"],
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


INPUT_CHECKS: dict[str, Callable[..., CheckResult]] = {
    "required_contact_inputs": check_required_contact_inputs,
    "invalid_email_feedback": check_invalid_email_input_feedback,
    "contact_input_constraints": check_contact_input_constraints,
}
