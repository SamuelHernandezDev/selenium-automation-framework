"""
Unit tests for check registry behavior.
"""

import pytest

from checks.registry import (
    available_checks,
    available_suites,
    get_check,
    resolve_checks,
)


def test_registry_exposes_expected_suites():
    assert available_suites() == [
        "accessibility",
        "auth",
        "error_states",
        "forms",
        "inputs",
        "navigation",
        "visual",
    ]


def test_registry_resolves_suite_checks():
    resolved = resolve_checks(
        [
            "navigation",
            "error_states",
        ]
    )

    assert len(resolved) == 5
    assert resolved[0][0] == "navigation"
    assert resolved[0][1] == "page_title"


def test_registry_lists_fully_qualified_checks():
    checks = available_checks()

    assert "navigation.page_title" in checks
    assert "auth.valid_login_reaches_dashboard" in checks
    assert "inputs.invalid_email_feedback" in checks
    assert "forms.valid_contact_submit_success" in checks
    assert "visual.viewport_screenshot" in checks


def test_registry_raises_clear_error_for_unknown_check():
    with pytest.raises(ValueError, match="was not found"):
        get_check(
            "navigation",
            "missing_check",
        )
