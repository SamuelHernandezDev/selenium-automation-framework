"""
Reusable authentication checks.
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


LOGIN_PATH = "/login"
DASHBOARD_PATH = "/dashboard"
VALID_EMAIL = "qa@example.com"
VALID_PASSWORD = "Password123"


def check_login_form_renders(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify the login form renders with expected controls.
    """

    check_name = "auth.login_form_renders"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        _open_login_page(driver, base_url)
        expected_ids = [
            "login-email",
            "login-password",
            "submit-login",
        ]
        missing = [
            element_id
            for element_id in expected_ids
            if not driver.find_elements(By.ID, element_id)
        ]
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if missing:
            result = CheckResult.failed(
                check_name,
                "Login form is missing expected controls.",
                severity=Severity.HIGH,
                expected=", ".join(expected_ids),
                actual=", ".join(missing),
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["auth", "login", "smoke"],
            )
        else:
            result = CheckResult.passed(
                check_name,
                "Login form renders expected controls.",
                expected=", ".join(expected_ids),
                actual="All controls found",
                evidence=evidence,
                tags=["auth", "login", "smoke"],
            )

        result.duration_ms = _duration_ms(start)
        return result

    except Exception as exc:
        return _unexpected_error(driver, collector, check_name, exc, start)


def check_invalid_login_shows_error(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify invalid credentials show an authentication error.
    """

    check_name = "auth.invalid_login_shows_error"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        _open_login_page(driver, base_url)
        _submit_login(driver, VALID_EMAIL, "wrong-password")
        _wait_for_element(driver, "login-error")

        error_text = driver.find_element(By.ID, "login-error").text.strip()
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if error_text == "Invalid email or password.":
            result = CheckResult.passed(
                check_name,
                "Invalid login shows the expected error.",
                expected="Invalid email or password.",
                actual=error_text,
                evidence=evidence,
                tags=["auth", "login", "negative"],
            )
        else:
            result = CheckResult.failed(
                check_name,
                "Invalid login error did not match expectations.",
                severity=Severity.HIGH,
                expected="Invalid email or password.",
                actual=error_text,
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["auth", "login", "negative"],
            )

        result.duration_ms = _duration_ms(start)
        return result

    except Exception as exc:
        return _unexpected_error(driver, collector, check_name, exc, start)


def check_valid_login_reaches_dashboard(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify valid credentials reach the dashboard.
    """

    check_name = "auth.valid_login_reaches_dashboard"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        _open_login_page(driver, base_url)
        _submit_login(driver, VALID_EMAIL, VALID_PASSWORD)
        _wait_for_element(driver, "dashboard-welcome")

        heading = driver.find_element(By.TAG_NAME, "h1").text.strip()
        welcome = driver.find_element(By.ID, "dashboard-welcome").text.strip()
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if heading == "Dashboard" and VALID_EMAIL in welcome:
            result = CheckResult.passed(
                check_name,
                "Valid login reaches the dashboard.",
                expected=f"Dashboard for {VALID_EMAIL}",
                actual=welcome,
                evidence=evidence,
                tags=["auth", "login", "positive"],
            )
        else:
            result = CheckResult.failed(
                check_name,
                "Valid login did not reach the expected dashboard state.",
                severity=Severity.HIGH,
                expected=f"Dashboard for {VALID_EMAIL}",
                actual=f"{heading}: {welcome}",
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["auth", "login", "positive"],
            )

        result.duration_ms = _duration_ms(start)
        return result

    except Exception as exc:
        return _unexpected_error(driver, collector, check_name, exc, start)


def check_logout_returns_to_login(
    driver,
    base_url: str,
    *,
    evidence_collector: EvidenceCollector | None = None,
) -> CheckResult:
    """
    Verify logout clears the session and returns to login.
    """

    check_name = "auth.logout_returns_to_login"
    collector = evidence_collector or EvidenceCollector()
    start = perf_counter()

    try:
        _open_login_page(driver, base_url)
        _submit_login(driver, VALID_EMAIL, VALID_PASSWORD)
        _wait_for_element(driver, "logout-link")
        driver.get(_logout_url(base_url))
        _wait_for_login_state(driver)

        driver.get(_dashboard_url(base_url))
        _wait_for_login_state(driver)

        heading = driver.find_element(By.TAG_NAME, "h1").text.strip()
        current_url = driver.current_url
        evidence = [
            collector.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        if heading == "Login" and "/login" in current_url:
            result = CheckResult.passed(
                check_name,
                "Logout returns the user to the login page.",
                expected="Login page after logout",
                actual=current_url,
                evidence=evidence,
                tags=["auth", "logout", "session"],
            )
        else:
            result = CheckResult.failed(
                check_name,
                "Logout did not return to the expected login state.",
                severity=Severity.HIGH,
                expected="Login page after logout",
                actual=f"{heading}: {current_url}",
                evidence=evidence
                + collector.failure_bundle(driver, check_name),
                tags=["auth", "logout", "session"],
            )

        result.duration_ms = _duration_ms(start)
        return result

    except Exception as exc:
        return _unexpected_error(driver, collector, check_name, exc, start)


def _submit_login(driver, email: str, password: str) -> None:
    """
    Fill and submit the login form.
    """

    _wait_for_element(driver, "login-email")
    _wait_for_element(driver, "login-password")
    driver.execute_script(
        """
        const emailInput = document.getElementById("login-email");
        const passwordInput = document.getElementById("login-password");
        const submitButton = document.getElementById("submit-login");
        emailInput.value = arguments[0];
        passwordInput.value = arguments[1];
        emailInput.dispatchEvent(new Event("input", { bubbles: true }));
        passwordInput.dispatchEvent(new Event("input", { bubbles: true }));
        submitButton.click();
        """,
        email,
        password,
    )


def _open_login_page(driver, base_url: str) -> None:
    """
    Open the login page from a clean browser session.
    """

    driver.get(base_url)
    driver.delete_all_cookies()
    driver.get(_login_url(base_url))
    _wait_for_element(driver, "login-form")


def _login_url(base_url: str) -> str:
    """
    Return the login page URL for a base URL.
    """

    return urljoin(base_url, LOGIN_PATH)


def _dashboard_url(base_url: str) -> str:
    """
    Return the dashboard page URL for a base URL.
    """

    return urljoin(base_url, DASHBOARD_PATH)


def _logout_url(base_url: str) -> str:
    """
    Return the logout URL for a base URL.
    """

    return urljoin(base_url, "/logout")


def _wait_for_element(driver, element_id: str):
    """
    Wait until an element exists.
    """

    return WebDriverWait(
        driver,
        10,
    ).until(
        EC.presence_of_element_located(
            (By.ID, element_id)
        )
    )


def _wait_for_url_contains(driver, path: str):
    """
    Wait until the browser reaches a URL containing the expected path.
    """

    return WebDriverWait(
        driver,
        10,
    ).until(
        EC.url_contains(path)
    )


def _wait_for_login_state(driver):
    """
    Wait until the login page is visible and ready for input.
    """

    return WebDriverWait(
        driver,
        10,
    ).until(
        lambda current_driver: (
            current_driver.find_elements(By.ID, "login-email")
            and current_driver.find_element(By.TAG_NAME, "h1").text.strip() == "Login"
        )
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
        "Unexpected error while executing authentication check.",
        evidence=collector.failure_bundle(
            driver,
            check_name,
            exc,
        ),
        tags=["auth", "runner"],
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


AUTH_CHECKS: dict[str, Callable[..., CheckResult]] = {
    "login_form_renders": check_login_form_renders,
    "invalid_login_shows_error": check_invalid_login_shows_error,
    "valid_login_reaches_dashboard": check_valid_login_reaches_dashboard,
    "logout_returns_to_login": check_logout_returns_to_login,
}
