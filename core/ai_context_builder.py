"""
AI-ready context generation.

The builder converts raw test results into a compact, structured summary
that can be safely sent to an AI reporting layer later.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from core.result import CheckStatus, Severity, TestRunResult


class AIContextBuilder:
    """
    Build report context from structured automation results.
    """

    def build(self, run_result: TestRunResult) -> dict[str, Any]:
        """
        Return a compact context payload for AI-assisted reporting.
        """

        findings = [
            self._finding_context(check)
            for check in run_result.checks
            if check.status in {
                CheckStatus.FAILED,
                CheckStatus.ERROR,
                CheckStatus.WARNING,
            }
        ]

        severity_counts = Counter(
            finding["severity"]
            for finding in findings
        )
        suite_counts = Counter(
            check.metadata.get("suite", "unknown")
            for check in run_result.checks
        )
        status_by_suite = self._status_by_suite(run_result)

        return {
            "run_id": run_result.run_id,
            "target": run_result.to_dict()["target"],
            "summary": {
                **run_result.summary(),
                "risk_level": self._risk_level(findings),
                "severity_counts": dict(severity_counts),
                "suite_counts": dict(suite_counts),
            },
            "coverage": {
                "executed_suites": sorted(suite_counts),
                "status_by_suite": status_by_suite,
                "tags": self._tag_counts(run_result),
            },
            "findings": findings,
            "recommended_focus": self._recommended_focus(findings),
            "suggested_test_cases": self._suggested_test_cases(
                run_result,
                findings,
            ),
            "reporting_notes": self._reporting_notes(run_result, findings),
            "prompt_guidance": self._prompt_guidance(),
        }

    def _finding_context(self, check: Any) -> dict[str, Any]:
        """
        Convert a check result into a concise finding.
        """

        return {
            "check": check.name,
            "status": check.status.value,
            "severity": check.severity.value,
            "message": check.message,
            "expected": check.expected,
            "actual": check.actual,
            "tags": check.tags,
            "evidence": [
                {
                    "kind": item.kind,
                    "label": item.label,
                    "path": item.path,
                    "value": item.value,
                }
                for item in check.evidence
            ],
            "error": check.error,
            "metadata": check.metadata,
        }

    def _status_by_suite(self, run_result: TestRunResult) -> dict[str, dict[str, int]]:
        """
        Count check statuses grouped by suite.
        """

        grouped: dict[str, Counter[str]] = {}

        for check in run_result.checks:
            suite = check.metadata.get("suite", "unknown")
            grouped.setdefault(
                suite,
                Counter(),
            )[check.status.value] += 1

        return {
            suite: dict(counts)
            for suite, counts in sorted(grouped.items())
        }

    def _tag_counts(self, run_result: TestRunResult) -> dict[str, int]:
        """
        Count tags from all executed checks.
        """

        tags = Counter(
            tag
            for check in run_result.checks
            for tag in check.tags
        )

        return dict(
            tags.most_common()
        )

    def _risk_level(self, findings: list[dict[str, Any]]) -> str:
        """
        Estimate run risk from failing and warning findings.
        """

        severities = {
            finding["severity"]
            for finding in findings
        }

        if Severity.CRITICAL.value in severities:
            return "critical"

        if Severity.HIGH.value in severities:
            return "high"

        if Severity.MEDIUM.value in severities:
            return "medium"

        if findings:
            return "low"

        return "none"

    def _recommended_focus(self, findings: list[dict[str, Any]]) -> list[str]:
        """
        Suggest quality areas that deserve attention.
        """

        if not findings:
            return [
                "No blocking issues detected in the executed checks."
            ]

        tags = Counter(
            tag
            for finding in findings
            for tag in finding.get("tags", [])
        )

        if tags:
            return [
                tag
                for tag, _ in tags.most_common(5)
            ]

        return [
            finding["check"]
            for finding in findings[:5]
        ]

    def _suggested_test_cases(
        self,
        run_result: TestRunResult,
        findings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Suggest follow-up test case candidates from results.
        """

        suggestions = []

        for finding in findings:
            suggestions.append(
                {
                    "title": f"Validate {finding['check']} behavior",
                    "priority": self._priority_from_severity(
                        finding["severity"]
                    ),
                    "source_check": finding["check"],
                    "objective": finding["message"],
                    "expected_result": finding["expected"],
                }
            )

        if suggestions:
            return suggestions

        executed_tags = self._tag_counts(run_result)

        for tag in list(executed_tags)[:5]:
            suggestions.append(
                {
                    "title": f"Expand coverage for {tag}",
                    "priority": "medium",
                    "source_check": None,
                    "objective": (
                        "Add deeper positive and negative scenarios "
                        f"for the {tag} area."
                    ),
                    "expected_result": (
                        "Critical user-facing behavior is covered with "
                        "clear assertions and evidence."
                    ),
                }
            )

        return suggestions

    def _priority_from_severity(self, severity: str) -> str:
        """
        Map check severity into a test-case priority.
        """

        if severity in {
            Severity.CRITICAL.value,
            Severity.HIGH.value,
        }:
            return "high"

        if severity == Severity.MEDIUM.value:
            return "medium"

        return "low"

    def _reporting_notes(
        self,
        run_result: TestRunResult,
        findings: list[dict[str, Any]],
    ) -> list[str]:
        """
        Produce deterministic notes for later narrative reports.
        """

        notes = []

        if not run_result.checks:
            notes.append("The run did not execute any checks.")

        if not findings and run_result.checks:
            notes.append("All executed checks completed without findings.")

        if run_result.has_failures:
            notes.append("Blocking findings should be reviewed before release.")

        evidence_count = sum(
            len(check.evidence)
            for check in run_result.checks
        )

        notes.append(
            f"{evidence_count} evidence item(s) were collected."
        )

        return notes

    def _prompt_guidance(self) -> dict[str, Any]:
        """
        Describe safe ways to use this context with an AI layer.
        """

        return {
            "intended_use": [
                "Summarize automation results for QA stakeholders.",
                "Draft bug report descriptions from findings.",
                "Suggest follow-up manual or automated test cases.",
            ],
            "constraints": [
                "Do not invent failures that are not present in findings.",
                "Treat skipped checks as coverage gaps, not product defects.",
                "Use evidence paths as references, not as proof of visual correctness.",
            ],
        }
