"""
Central check registry.

The runner can use this module to resolve suites and individual checks
without knowing where each check is implemented.
"""

from __future__ import annotations

from collections.abc import Callable

from core.result import CheckResult

from checks.accessibility_checks import ACCESSIBILITY_CHECKS
from checks.auth_checks import AUTH_CHECKS
from checks.data_table_checks import DATA_TABLE_CHECKS
from checks.error_state_checks import ERROR_STATE_CHECKS
from checks.form_validation_checks import FORM_VALIDATION_CHECKS
from checks.input_checks import INPUT_CHECKS
from checks.navigation_checks import NAVIGATION_CHECKS
from checks.visual_checks import VISUAL_CHECKS


CheckCallable = Callable[..., CheckResult]


SUITE_REGISTRY: dict[str, dict[str, CheckCallable]] = {
    "navigation": NAVIGATION_CHECKS,
    "error_states": ERROR_STATE_CHECKS,
    "auth": AUTH_CHECKS,
    "data": DATA_TABLE_CHECKS,
    "accessibility": ACCESSIBILITY_CHECKS,
    "visual": VISUAL_CHECKS,
    "inputs": INPUT_CHECKS,
    "forms": FORM_VALIDATION_CHECKS,
}


def available_suites() -> list[str]:
    """
    Return every registered suite name.
    """

    return sorted(SUITE_REGISTRY)


def available_checks(suite: str | None = None) -> list[str]:
    """
    Return registered check names.
    """

    if suite is not None:
        return sorted(
            _get_suite(suite)
        )

    return sorted(
        f"{suite_name}.{check_name}"
        for suite_name, checks in SUITE_REGISTRY.items()
        for check_name in checks
    )


def get_suite_checks(suite: str) -> dict[str, CheckCallable]:
    """
    Return all checks registered for a suite.
    """

    return dict(
        _get_suite(suite)
    )


def get_check(suite: str, check_name: str) -> CheckCallable:
    """
    Return a single check callable by suite and name.
    """

    checks = _get_suite(suite)

    try:
        return checks[check_name]
    except KeyError as exc:
        available = ", ".join(sorted(checks)) or "none"
        raise ValueError(
            f"Check '{check_name}' was not found in suite '{suite}'. "
            f"Available checks: {available}."
        ) from exc


def resolve_checks(suites: list[str]) -> list[tuple[str, str, CheckCallable]]:
    """
    Resolve suite names into ordered check callables.
    """

    resolved = []

    for suite in suites:
        for check_name, check in get_suite_checks(suite).items():
            resolved.append(
                (
                    suite,
                    check_name,
                    check,
                )
            )

    return resolved


def _get_suite(suite: str) -> dict[str, CheckCallable]:
    """
    Return a registered suite or raise a clear configuration error.
    """

    try:
        return SUITE_REGISTRY[suite]
    except KeyError as exc:
        available = ", ".join(available_suites()) or "none"
        raise ValueError(
            f"Suite '{suite}' is not registered. Available suites: {available}."
        ) from exc
