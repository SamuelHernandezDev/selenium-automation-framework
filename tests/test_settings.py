"""
Unit tests for settings and profile loading.
"""

from pathlib import Path

import pytest

from config.settings import load_settings


def test_load_settings_reads_profile_from_yaml(tmp_path):
    profile_path = tmp_path / "profiles.yaml"
    profile_path.write_text(
        """
demo:
  base_url: "https://example.com"
  suites:
    - navigation
  browser:
    name: "chrome"
    headless: false
    timeout: 15
    window_width: 1200
    window_height: 800
    arguments:
      - "--disable-gpu"
  reports_dir: "custom-reports"
  metadata:
    environment: "test"
""",
        encoding="utf-8",
    )

    settings = load_settings(
        "demo",
        profile_path=profile_path,
    )

    assert settings.base_url == "https://example.com"
    assert settings.suites == ["navigation"]
    assert settings.browser.headless is False
    assert settings.browser.timeout == 15
    assert settings.browser.arguments == ["--disable-gpu"]
    assert settings.reports_dir == Path("custom-reports")
    assert settings.metadata["environment"] == "test"


def test_load_settings_raises_for_missing_profile(tmp_path):
    profile_path = tmp_path / "profiles.yaml"
    profile_path.write_text(
        "default: {}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="was not found"):
        load_settings(
            "missing",
            profile_path=profile_path,
        )


def test_local_demo_profile_includes_form_suites():
    settings = load_settings("local_demo")

    assert "inputs" in settings.suites
    assert "forms" in settings.suites
    assert "data" in settings.suites
    assert settings.base_url == "http://127.0.0.1:5000/"
