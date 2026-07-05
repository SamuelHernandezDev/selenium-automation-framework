"""
Lightweight accessibility checks.

These checks are intentionally small and dependency-free. They do not
replace a full accessibility audit, but they expose useful signals for
automation reports and AI-assisted feedback.
"""

from __future__ import annotations

from time import perf_counter
from typing import Callable

from selenium.webdriver.common.by import By

from core.evidence_collector import EvidenceCollector
from core.result import CheckResult, Severity


def check_page_has_main_heading(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify the page exposes at least one h1 heading.
    """

    check_name = "accessibility.main_heading"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(base_url)
        headings = [
            heading.text.strip()
            for heading in driver.find_elements(By.TAG_NAME, "h1")
            if heading.text.strip()
        ]
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if headings:
            result = CheckResult.passed(
                check_name,
                "Page exposes a main heading.",
                expected="At least one non-empty h1",
                actual=", ".join(headings),
                evidence=evidence,
                tags=["accessibility", "structure"],
            )
        else:
            result = CheckResult.warning(
                check_name,
                "Page does not expose a non-empty h1 heading.",
                severity=Severity.MEDIUM,
                expected="At least one non-empty h1",
                actual="No h1 found",
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["accessibility", "structure"],
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
            tags=["accessibility", "structure"],
        )


def check_images_have_alt_text(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify images include non-empty alt text.
    """

    check_name = "accessibility.image_alt_text"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(base_url)
        images = driver.find_elements(By.TAG_NAME, "img")
        missing_alt = [
            image.get_attribute("src") or "<inline image>"
            for image in images
            if not (image.get_attribute("alt") or "").strip()
        ]
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if not images:
            result = CheckResult.skipped(
                check_name,
                "Page does not contain images to evaluate.",
                tags=["accessibility", "images"],
            )
            result.evidence.extend(evidence)
        elif missing_alt:
            result = CheckResult.failed(
                check_name,
                "One or more images are missing alt text.",
                severity=Severity.MEDIUM,
                expected="All images include non-empty alt text",
                actual=f"{len(missing_alt)} image(s) missing alt text",
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["accessibility", "images"],
                metadata={
                    "missing_alt_sources": missing_alt,
                },
            )
        else:
            result = CheckResult.passed(
                check_name,
                "All detected images include alt text.",
                expected="All images include non-empty alt text",
                actual=f"{len(images)} image(s) checked",
                evidence=evidence,
                tags=["accessibility", "images"],
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
            tags=["accessibility", "images"],
        )


def check_form_controls_have_accessible_names(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify form controls expose labels or accessible names.
    """

    check_name = "accessibility.form_control_names"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        driver.get(base_url)
        controls = driver.find_elements(
            By.CSS_SELECTOR,
            "input:not([type='hidden']), textarea, select",
        )
        unnamed_controls = driver.execute_script(
            """
            const controls = [...document.querySelectorAll(
              "input:not([type='hidden']), textarea, select"
            )];

            return controls
              .filter((control) => {
                const id = control.id;
                const hasLabel = id && document.querySelector(
                  `label[for="${CSS.escape(id)}"]`
                );
                const wrappedByLabel = control.closest("label");
                const ariaLabel = control.getAttribute("aria-label");
                const ariaLabelledBy = control.getAttribute("aria-labelledby");
                const title = control.getAttribute("title");
                const placeholder = control.getAttribute("placeholder");

                return !(
                  hasLabel ||
                  wrappedByLabel ||
                  ariaLabel ||
                  ariaLabelledBy ||
                  title ||
                  placeholder
                );
              })
              .map((control) => ({
                tag: control.tagName.toLowerCase(),
                type: control.getAttribute("type"),
                id: control.id || null,
                name: control.getAttribute("name"),
              }));
            """
        )
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if not controls:
            result = CheckResult.skipped(
                check_name,
                "Page does not contain form controls to evaluate.",
                tags=["accessibility", "forms"],
            )
            result.evidence.extend(evidence)
        elif unnamed_controls:
            result = CheckResult.failed(
                check_name,
                "One or more form controls are missing accessible names.",
                severity=Severity.HIGH,
                expected="Every form control has a label or accessible name",
                actual=f"{len(unnamed_controls)} unnamed control(s)",
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["accessibility", "forms"],
                metadata={
                    "unnamed_controls": unnamed_controls,
                },
            )
        else:
            result = CheckResult.passed(
                check_name,
                "All detected form controls expose accessible names.",
                expected="Every form control has a label or accessible name",
                actual=f"{len(controls)} control(s) checked",
                evidence=evidence,
                tags=["accessibility", "forms"],
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
            tags=["accessibility", "forms"],
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
        "Unexpected error while executing accessibility check.",
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


ACCESSIBILITY_CHECKS: dict[str, Callable[..., CheckResult]] = {
    "main_heading": check_page_has_main_heading,
    "image_alt_text": check_images_have_alt_text,
    "form_control_names": check_form_controls_have_accessible_names,
}
