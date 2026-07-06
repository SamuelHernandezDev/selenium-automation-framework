"""
HTML report generation for automation runs.

The builder turns structured run results and AI-ready context into a small
static report that can be opened locally or uploaded as a CI artifact.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from core.result import CheckResult, TestRunResult


class HTMLReportBuilder:
    """
    Build a stakeholder-friendly HTML report from structured run data.
    """

    def build(
        self,
        run_result: TestRunResult,
        ai_context: dict[str, Any],
    ) -> str:
        """
        Return a complete HTML document for a run.
        """

        summary = run_result.summary()
        target = run_result.to_dict()["target"]
        risk_level = ai_context.get("summary", {}).get("risk_level", "unknown")

        return "\n".join(
            [
                "<!doctype html>",
                '<html lang="en">',
                "<head>",
                '<meta charset="utf-8">',
                '<meta name="viewport" content="width=device-width, initial-scale=1">',
                f"<title>Automation Report - {escape(run_result.run_id)}</title>",
                f"<style>{self._styles()}</style>",
                "</head>",
                "<body>",
                '<main class="report-shell">',
                self._header(run_result, target, risk_level),
                self._summary_cards(summary),
                self._suite_coverage(ai_context),
                self._findings(ai_context),
                self._checks_table(run_result.checks),
                self._notes(ai_context),
                "</main>",
                "</body>",
                "</html>",
            ]
        )

    def save(
        self,
        run_result: TestRunResult,
        ai_context: dict[str, Any],
        path: str | Path,
    ) -> Path:
        """
        Save a generated HTML report.
        """

        output_path = Path(path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        output_path.write_text(
            self.build(run_result, ai_context),
            encoding="utf-8",
        )

        return output_path

    def _header(
        self,
        run_result: TestRunResult,
        target: dict[str, Any],
        risk_level: str,
    ) -> str:
        """
        Build the report header.
        """

        return f"""
<section class="hero">
  <p class="eyebrow">Automation Report</p>
  <h1>{escape(run_result.profile)} / {escape(target.get("suite", ""))}</h1>
  <dl class="meta-grid">
    <div><dt>Run ID</dt><dd>{escape(run_result.run_id)}</dd></div>
    <div><dt>Target</dt><dd>{escape(target.get("url", ""))}</dd></div>
    <div><dt>Browser</dt><dd>{escape(target.get("browser", ""))}</dd></div>
    <div><dt>Risk</dt><dd><span class="pill risk-{escape(risk_level)}">{escape(risk_level)}</span></dd></div>
  </dl>
</section>
"""

    def _summary_cards(self, summary: dict[str, Any]) -> str:
        """
        Build status summary cards.
        """

        cards = [
            ("Total", summary.get("total_checks", 0), "neutral"),
            ("Passed", summary.get("passed", 0), "passed"),
            ("Failed", summary.get("failed", 0), "failed"),
            ("Warnings", summary.get("warning", 0), "warning"),
            ("Skipped", summary.get("skipped", 0), "skipped"),
            ("Errors", summary.get("error", 0), "error"),
        ]

        items = "\n".join(
            f"""
  <article class="metric metric-{escape(kind)}">
    <span>{escape(label)}</span>
    <strong>{escape(str(value))}</strong>
  </article>
"""
            for label, value, kind in cards
        )

        return f"""
<section class="metric-grid" aria-label="Run summary">
{items}
</section>
"""

    def _suite_coverage(self, ai_context: dict[str, Any]) -> str:
        """
        Build a suite coverage table.
        """

        status_by_suite = ai_context.get("coverage", {}).get("status_by_suite", {})

        if not status_by_suite:
            return self._empty_section(
                "Suite Coverage",
                "No suite coverage was recorded.",
            )

        rows = "\n".join(
            f"""
  <tr>
    <td>{escape(suite)}</td>
    <td>{escape(str(counts.get("passed", 0)))}</td>
    <td>{escape(str(counts.get("failed", 0)))}</td>
    <td>{escape(str(counts.get("warning", 0)))}</td>
    <td>{escape(str(counts.get("skipped", 0)))}</td>
    <td>{escape(str(counts.get("error", 0)))}</td>
  </tr>
"""
            for suite, counts in status_by_suite.items()
        )

        return f"""
<section class="panel">
  <h2>Suite Coverage</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Suite</th>
          <th>Passed</th>
          <th>Failed</th>
          <th>Warnings</th>
          <th>Skipped</th>
          <th>Errors</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</section>
"""

    def _findings(self, ai_context: dict[str, Any]) -> str:
        """
        Build finding cards from AI context.
        """

        findings = ai_context.get("findings", [])

        if not findings:
            return self._empty_section(
                "Findings",
                "No findings were reported in this run.",
            )

        cards = "\n".join(
            f"""
  <article class="finding">
    <div>
      <h3>{escape(finding.get("check", "unknown"))}</h3>
      <p>{escape(finding.get("message", ""))}</p>
    </div>
    <span class="pill status-{escape(finding.get("status", "unknown"))}">
      {escape(finding.get("status", "unknown"))}
    </span>
  </article>
"""
            for finding in findings
        )

        return f"""
<section class="panel">
  <h2>Findings</h2>
{cards}
</section>
"""

    def _checks_table(self, checks: list[CheckResult]) -> str:
        """
        Build a detailed checks table.
        """

        rows = "\n".join(
            f"""
  <tr>
    <td>{escape(check.name)}</td>
    <td><span class="pill status-{escape(check.status.value)}">{escape(check.status.value)}</span></td>
    <td>{escape(check.severity.value)}</td>
    <td>{escape(check.message)}</td>
    <td>{escape(str(check.duration_ms or 0))}</td>
  </tr>
"""
            for check in checks
        )

        return f"""
<section class="panel">
  <h2>Executed Checks</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Check</th>
          <th>Status</th>
          <th>Severity</th>
          <th>Message</th>
          <th>Duration ms</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</section>
"""

    def _notes(self, ai_context: dict[str, Any]) -> str:
        """
        Build reporting notes and recommended focus.
        """

        notes = ai_context.get("reporting_notes", [])
        focus = ai_context.get("recommended_focus", [])
        notes_html = self._list_items(notes)
        focus_html = self._list_items(focus)

        return f"""
<section class="panel split">
  <div>
    <h2>Recommended Focus</h2>
    <ul>{focus_html}</ul>
  </div>
  <div>
    <h2>Reporting Notes</h2>
    <ul>{notes_html}</ul>
  </div>
</section>
"""

    def _empty_section(self, title: str, message: str) -> str:
        """
        Build a panel with an empty-state message.
        """

        return f"""
<section class="panel">
  <h2>{escape(title)}</h2>
  <p class="empty">{escape(message)}</p>
</section>
"""

    def _list_items(self, values: list[Any]) -> str:
        """
        Render values as escaped list items.
        """

        if not values:
            return "<li>No items recorded.</li>"

        return "\n".join(
            f"<li>{escape(str(value))}</li>"
            for value in values
        )

    def _styles(self) -> str:
        """
        Return inline CSS for the static report.
        """

        return """
:root {
  color-scheme: light;
  font-family: Arial, Helvetica, sans-serif;
  color: #1f2933;
  background: #f4f7fb;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
}

.report-shell {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 32px 0;
}

.hero,
.panel,
.metric {
  background: #ffffff;
  border: 1px solid #d8e0ea;
  border-radius: 8px;
  box-shadow: 0 8px 20px rgba(16, 42, 67, 0.08);
}

.hero,
.panel {
  padding: 24px;
  margin-bottom: 20px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #52606d;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1,
h2,
h3 {
  margin-top: 0;
  color: #102a43;
}

.meta-grid,
.metric-grid,
.split {
  display: grid;
  gap: 16px;
}

.meta-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.meta-grid div {
  min-width: 0;
}

dt {
  color: #52606d;
  font-weight: 700;
}

dd {
  margin: 4px 0 0;
  overflow-wrap: anywhere;
}

.metric-grid {
  grid-template-columns: repeat(6, minmax(0, 1fr));
  margin-bottom: 20px;
}

.metric {
  padding: 16px;
}

.metric span {
  color: #52606d;
  font-weight: 700;
}

.metric strong {
  display: block;
  margin-top: 8px;
  font-size: 28px;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid #d8e0ea;
  border-radius: 8px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px 14px;
  border-top: 1px solid #d8e0ea;
  text-align: left;
  vertical-align: top;
}

th {
  background: #f0f4f8;
}

.pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #e6f6ff;
  color: #0b5c8e;
  font-weight: 700;
}

.status-passed,
.risk-none {
  background: #e3f9e5;
  color: #1b5e20;
}

.status-failed,
.status-error,
.risk-high,
.risk-critical {
  background: #ffebe6;
  color: #9b1c1c;
}

.status-warning,
.risk-medium,
.risk-low {
  background: #fff7cc;
  color: #7c5e10;
}

.status-skipped {
  background: #edf2f7;
  color: #52606d;
}

.finding {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 0;
  border-top: 1px solid #d8e0ea;
}

.finding p {
  margin-bottom: 0;
}

.split {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.empty {
  color: #52606d;
  font-weight: 700;
}

@media (max-width: 900px) {
  .meta-grid,
  .metric-grid,
  .split {
    grid-template-columns: 1fr;
  }
}
"""
