"""
Evidence collection helpers.

The collector stores browser artifacts and converts them into Evidence
objects that can be attached to check results.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from core.result import Evidence


class EvidenceCollector:
    """
    Collect screenshots, DOM snapshots, and browser state.
    """

    def __init__(self, output_dir: str | Path = "reports") -> None:
        self.output_dir = Path(output_dir)
        self.screenshot_dir = self.output_dir / "screenshots"
        self.dom_dir = self.output_dir / "dom"

    def capture_screenshot(self, driver: Any, label: str) -> Evidence:
        """
        Save a browser screenshot and return it as evidence.
        """

        self.screenshot_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = self.screenshot_dir / f"{self._safe_name(label)}.png"
        driver.save_screenshot(str(path))

        return Evidence(
            kind="screenshot",
            label=label,
            path=str(path),
        )

    def capture_dom(self, driver: Any, label: str) -> Evidence:
        """
        Save the current page HTML and return it as evidence.
        """

        self.dom_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = self.dom_dir / f"{self._safe_name(label)}.html"
        path.write_text(
            driver.page_source,
            encoding="utf-8",
        )

        return Evidence(
            kind="dom",
            label=label,
            path=str(path),
        )

    def browser_state(self, driver: Any, label: str = "browser_state") -> Evidence:
        """
        Capture lightweight browser metadata.
        """

        value: dict[str, Any] = {
            "current_url": getattr(driver, "current_url", None),
            "title": getattr(driver, "title", None),
        }

        try:
            value["window_size"] = driver.get_window_size()
        except Exception as exc:
            value["window_size_error"] = str(exc)

        return Evidence(
            kind="browser_state",
            label=label,
            value=value,
        )

    def failure_bundle(
        self,
        driver: Any,
        check_name: str,
        error: Exception | str | None = None,
        *,
        include_dom: bool = False,
    ) -> list[Evidence]:
        """
        Capture the standard evidence set for a failed check.
        """

        evidence = [
            self.browser_state(
                driver,
                label=f"{check_name}_state",
            )
        ]

        try:
            evidence.append(
                self.capture_screenshot(
                    driver,
                    label=f"{check_name}_failure",
                )
            )
        except Exception as exc:
            evidence.append(
                Evidence(
                    kind="capture_error",
                    label=f"{check_name}_screenshot_error",
                    value=str(exc),
                )
            )

        if include_dom:
            try:
                evidence.append(
                    self.capture_dom(
                        driver,
                        label=f"{check_name}_failure",
                    )
                )
            except Exception as exc:
                evidence.append(
                    Evidence(
                        kind="capture_error",
                        label=f"{check_name}_dom_error",
                        value=str(exc),
                    )
                )

        if error is not None:
            evidence.append(
                Evidence(
                    kind="exception",
                    label=f"{check_name}_exception",
                    value=str(error),
                )
            )

        return evidence

    @staticmethod
    def _safe_name(value: str) -> str:
        """
        Convert a label into a stable filesystem-friendly name.
        """

        normalized = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "-",
            value.strip().lower(),
        ).strip("-")

        return normalized or "evidence"
