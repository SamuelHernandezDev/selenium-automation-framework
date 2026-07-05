"""
Result models used by the automation framework.

This module defines the shared contract between checks, runners,
reporters, and future AI-assisted report generation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    """
    Return a timezone-aware UTC timestamp in ISO 8601 format.
    """

    return datetime.now(timezone.utc).isoformat()


class CheckStatus(str, Enum):
    """
    Supported execution states for a single check.
    """

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    ERROR = "error"


class Severity(str, Enum):
    """
    Business or quality impact assigned to a finding.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class Evidence:
    """
    A single evidence item produced during a check.
    """

    kind: str
    label: str
    value: Any | None = None
    path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert evidence to a JSON-friendly dictionary.
        """

        return asdict(self)


@dataclass(slots=True)
class CheckResult:
    """
    Result produced by one reusable check.
    """

    name: str
    status: CheckStatus
    severity: Severity
    message: str
    expected: str | None = None
    actual: str | None = None
    duration_ms: int | None = None
    evidence: list[Evidence] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    started_at: str = field(default_factory=utc_now)
    finished_at: str | None = None

    @classmethod
    def passed(
        cls,
        name: str,
        message: str,
        *,
        severity: Severity = Severity.LOW,
        expected: str | None = None,
        actual: str | None = None,
        evidence: list[Evidence] | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "CheckResult":
        """
        Build a successful check result.
        """

        now = utc_now()

        return cls(
            name=name,
            status=CheckStatus.PASSED,
            severity=severity,
            message=message,
            expected=expected,
            actual=actual,
            evidence=evidence or [],
            tags=tags or [],
            metadata=metadata or {},
            started_at=now,
            finished_at=now,
        )

    @classmethod
    def failed(
        cls,
        name: str,
        message: str,
        *,
        severity: Severity = Severity.MEDIUM,
        expected: str | None = None,
        actual: str | None = None,
        evidence: list[Evidence] | None = None,
        tags: list[str] | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "CheckResult":
        """
        Build a failed check result.
        """

        now = utc_now()

        return cls(
            name=name,
            status=CheckStatus.FAILED,
            severity=severity,
            message=message,
            expected=expected,
            actual=actual,
            evidence=evidence or [],
            tags=tags or [],
            error=error,
            metadata=metadata or {},
            started_at=now,
            finished_at=now,
        )

    @classmethod
    def warning(
        cls,
        name: str,
        message: str,
        *,
        severity: Severity = Severity.LOW,
        expected: str | None = None,
        actual: str | None = None,
        evidence: list[Evidence] | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "CheckResult":
        """
        Build a non-blocking warning result.
        """

        now = utc_now()

        return cls(
            name=name,
            status=CheckStatus.WARNING,
            severity=severity,
            message=message,
            expected=expected,
            actual=actual,
            evidence=evidence or [],
            tags=tags or [],
            metadata=metadata or {},
            started_at=now,
            finished_at=now,
        )

    @classmethod
    def skipped(
        cls,
        name: str,
        message: str,
        *,
        severity: Severity = Severity.LOW,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "CheckResult":
        """
        Build a skipped check result.
        """

        now = utc_now()

        return cls(
            name=name,
            status=CheckStatus.SKIPPED,
            severity=severity,
            message=message,
            tags=tags or [],
            metadata=metadata or {},
            started_at=now,
            finished_at=now,
        )

    @classmethod
    def errored(
        cls,
        name: str,
        message: str,
        *,
        severity: Severity = Severity.HIGH,
        expected: str | None = None,
        actual: str | None = None,
        evidence: list[Evidence] | None = None,
        tags: list[str] | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "CheckResult":
        """
        Build a check result for unexpected execution errors.
        """

        now = utc_now()

        return cls(
            name=name,
            status=CheckStatus.ERROR,
            severity=severity,
            message=message,
            expected=expected,
            actual=actual,
            evidence=evidence or [],
            tags=tags or [],
            error=error,
            metadata=metadata or {},
            started_at=now,
            finished_at=now,
        )

    def add_evidence(self, evidence: Evidence) -> None:
        """
        Attach evidence to this result.
        """

        self.evidence.append(evidence)

    @property
    def is_blocking(self) -> bool:
        """
        Return whether the check should fail the run quality gate.
        """

        return self.status in {CheckStatus.FAILED, CheckStatus.ERROR}

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the check result to a JSON-friendly dictionary.
        """

        data = asdict(self)
        data["status"] = self.status.value
        data["severity"] = self.severity.value
        return data


@dataclass(slots=True)
class TestRunResult:
    """
    Aggregated result for a complete automation run.
    """

    target_url: str
    suite: str
    profile: str = "default"
    browser: str = "chrome"
    headless: bool = True
    run_id: str = field(default_factory=lambda: uuid4().hex)
    started_at: str = field(default_factory=utc_now)
    finished_at: str | None = None
    checks: list[CheckResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_check(self, result: CheckResult) -> None:
        """
        Add a check result to the run.
        """

        self.checks.append(result)

    def finish(self) -> None:
        """
        Mark the run as finished.
        """

        self.finished_at = utc_now()

    @property
    def has_failures(self) -> bool:
        """
        Return whether the run contains blocking findings.
        """

        return any(check.is_blocking for check in self.checks)

    def summary(self) -> dict[str, Any]:
        """
        Return execution counters grouped by check status.
        """

        counters = {
            status.value: 0
            for status in CheckStatus
        }

        for check in self.checks:
            counters[check.status.value] += 1

        return {
            "total_checks": len(self.checks),
            "has_failures": self.has_failures,
            **counters,
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the run result to a JSON-friendly dictionary.
        """

        return {
            "run_id": self.run_id,
            "target": {
                "url": self.target_url,
                "suite": self.suite,
                "profile": self.profile,
                "browser": self.browser,
                "headless": self.headless,
            },
            "summary": self.summary(),
            "checks": [
                check.to_dict()
                for check in self.checks
            ],
            "metadata": self.metadata,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }

    def save_json(self, path: str | Path) -> Path:
        """
        Persist the run result as formatted JSON.
        """

        output_path = Path(path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        output_path.write_text(
            json.dumps(
                self.to_dict(),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return output_path
