"""
Application settings and profile loading.

The framework can run with default values, environment overrides,
or named profiles defined in config/test_profiles.yaml.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT_DIR / "config"
REPORTS_DIR = ROOT_DIR / "reports"
DEFAULT_PROFILE_PATH = CONFIG_DIR / "test_profiles.yaml"


@dataclass(slots=True)
class BrowserSettings:
    """
    Browser-specific execution settings.
    """

    name: str = "chrome"
    headless: bool = True
    timeout: int = 30
    window_width: int = 1366
    window_height: int = 768
    arguments: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FrameworkSettings:
    """
    Runtime settings consumed by drivers, checks, and runners.
    """

    profile: str = "default"
    base_url: str = "https://the-internet.herokuapp.com/"
    suites: list[str] = field(default_factory=lambda: ["navigation"])
    browser: BrowserSettings = field(default_factory=BrowserSettings)
    reports_dir: Path = REPORTS_DIR
    metadata: dict[str, Any] = field(default_factory=dict)


def load_settings(
    profile: str = "default",
    profile_path: str | Path = DEFAULT_PROFILE_PATH,
) -> FrameworkSettings:
    """
    Load settings from a named YAML profile and environment overrides.
    """

    data = _load_profiles(profile_path)
    selected = data.get(profile)

    if selected is None:
        available = ", ".join(sorted(data)) or "none"
        raise ValueError(
            f"Profile '{profile}' was not found. Available profiles: {available}."
        )

    browser_data = selected.get("browser", {})

    settings = FrameworkSettings(
        profile=profile,
        base_url=selected.get(
            "base_url",
            FrameworkSettings.base_url,
        ),
        suites=list(
            selected.get(
                "suites",
                ["navigation"],
            )
        ),
        browser=BrowserSettings(
            name=browser_data.get("name", "chrome"),
            headless=browser_data.get("headless", True),
            timeout=browser_data.get("timeout", 30),
            window_width=browser_data.get("window_width", 1366),
            window_height=browser_data.get("window_height", 768),
            arguments=list(browser_data.get("arguments", [])),
        ),
        reports_dir=Path(
            selected.get(
                "reports_dir",
                REPORTS_DIR,
            )
        ),
        metadata=dict(selected.get("metadata", {})),
    )

    return apply_environment_overrides(settings)


def apply_environment_overrides(settings: FrameworkSettings) -> FrameworkSettings:
    """
    Apply supported environment variable overrides.
    """

    base_url = os.getenv("BASE_URL")
    browser_name = os.getenv("BROWSER")
    headless = os.getenv("HEADLESS")
    timeout = os.getenv("DEFAULT_TIMEOUT")

    if base_url:
        settings.base_url = base_url

    if browser_name:
        settings.browser.name = browser_name

    if headless is not None:
        settings.browser.headless = headless.lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    if timeout:
        settings.browser.timeout = int(timeout)

    return settings


def _load_profiles(path: str | Path) -> dict[str, Any]:
    """
    Load the profile dictionary from disk.
    """

    profile_path = Path(path)

    if not profile_path.exists():
        return {
            "default": {}
        }

    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError(
            "PyYAML is required to load test profiles. "
            "Install project dependencies with 'pip install -r requirements.txt'."
        ) from exc

    content = profile_path.read_text(
        encoding="utf-8",
    )
    parsed = yaml.safe_load(content) or {}

    if not isinstance(parsed, dict):
        raise ValueError("Profile file must contain a YAML mapping.")

    return parsed


try:
    DEFAULT_SETTINGS = load_settings()
except RuntimeError:
    DEFAULT_SETTINGS = apply_environment_overrides(
        FrameworkSettings()
    )

# Backwards-compatible constants used by the existing Page Objects/tests.
BASE_URL = DEFAULT_SETTINGS.base_url
DEFAULT_TIMEOUT = DEFAULT_SETTINGS.browser.timeout
HEADLESS = DEFAULT_SETTINGS.browser.headless
