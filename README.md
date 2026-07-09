# Selenium Automation Framework

[![CI](https://github.com/SamuelHernandezDev/selenium-automation-framework/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/SamuelHernandezDev/selenium-automation-framework/actions/workflows/ci.yml)

A modular UI automation framework built with Python, Selenium WebDriver, configurable check suites, a deterministic Flask demo app, CI validation, JSON reports, static HTML reports, and AI-ready execution context.

This repository is a public portfolio project. It demonstrates how I structure browser automation, test execution, evidence collection, reporting, and future AI-assisted QA workflows without exposing private prompts, credentials, or client-specific templates.

## What This Demonstrates

- Selenium WebDriver automation with reusable Page Object patterns.
- Configurable execution through YAML profiles.
- A central browser driver factory.
- Modular check suites for navigation, error states, accessibility signals, visual smoke checks, inputs, forms, authentication, and data tables.
- A deterministic local Flask app used as a stable automation target.
- Structured result models for checks, evidence, and full test runs.
- JSON reports and static HTML reports generated from each run.
- AI-ready context generated from real automation results.
- GitHub Actions validation with downloadable generated reports.
- A custom runner that can execute by profile, suite, check, or target URL.

## Quick Start

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the framework unit tests:

```bash
venv\Scripts\python.exe -m pytest
```

Start the local deterministic demo app:

```bash
venv\Scripts\python.exe -m demo_app.app
```

In another terminal, run the full local automation profile:

```bash
venv\Scripts\python.exe -m core.test_runner --profile local_demo
```

Example output:

```text
Automation run completed
Profile: local_demo
Suites: navigation,error_states,accessibility,visual,inputs,forms,auth,data
Checks: 24 total, 22 passed, 0 failed, 0 warning, 2 skipped, 0 error
Latest JSON: reports\json\latest_run.json
Latest AI Context: reports\json\latest_ai_context.json
Latest HTML Report: reports\html\latest_report.html
```

## Demo App Coverage

The included Flask app exposes predictable pages for browser automation:

| Area | Route | What gets validated |
| --- | --- | --- |
| Home and navigation | `/` | Page title, current URL, expected links |
| Redirect flow | `/redirect` | Link-driven navigation and redirect behavior |
| Status pages | `/status-codes` | Expected status-code messaging and error-state pages |
| Contact form | `/contact` | Required fields, invalid input, accessible errors, successful submit |
| Authentication | `/login`, `/dashboard`, `/logout` | Login form, invalid credentials, valid login, protected page, logout |
| Ticket table | `/tickets` | Table rendering, search, status filtering, priority sorting |

## Available Suites

| Suite | Purpose |
| --- | --- |
| `navigation` | Basic page identity, URL, and redirect flow checks |
| `error_states` | Predictable status-code and error page checks |
| `accessibility` | Lightweight accessibility signals such as headings, alt text, and form names |
| `visual` | Smoke-level rendering, viewport, overflow, and screenshot evidence checks |
| `inputs` | Input presence, labels, constraints, and invalid input feedback |
| `forms` | Contact form validation, success paths, and accessible error references |
| `auth` | Login, invalid credential handling, protected route behavior, and logout |
| `data` | Searchable, filterable, sortable ticket table behavior |

List all registered suites and checks:

```bash
venv\Scripts\python.exe -m core.test_runner --list
```

Run one suite:

```bash
venv\Scripts\python.exe -m core.test_runner --profile local_demo --suite auth
```

Run one check:

```bash
venv\Scripts\python.exe -m core.test_runner --profile local_demo --suite data --check ticket_priority_sort
```

Override the target URL:

```bash
venv\Scripts\python.exe -m core.test_runner --profile default --base-url https://the-internet.herokuapp.com/
```

## Reports

Each run writes technical JSON artifacts under `reports/json/`:

```text
latest_run.json
<run_id>.json
latest_ai_context.json
<run_id>_ai_context.json
```

Each run also writes a static HTML summary under `reports/html/`:

```text
latest_report.html
<run_id>.html
```

Visual and failure evidence is stored under:

```text
reports/screenshots/
reports/dom/
```

Generated reports are ignored by Git and created at runtime.

## AI-Ready Context

The public version does not call an AI API. Instead, it produces a safe structured payload that can be consumed later by a private AI reporting layer.

Small example:

```json
{
  "summary": {
    "total_checks": 24,
    "passed": 22,
    "failed": 0,
    "error": 0,
    "risk_level": "none"
  },
  "coverage": {
    "executed_suites": [
      "accessibility",
      "auth",
      "data",
      "error_states",
      "forms",
      "inputs",
      "navigation",
      "visual"
    ]
  },
  "recommended_focus": [
    "No blocking issues detected in the executed checks."
  ]
}
```

The AI context is designed to support future private workflows such as QA summaries, bug report drafts, test case generation, and stakeholder-friendly release notes.

See [docs/ai-reporting-strategy.md](docs/ai-reporting-strategy.md).

## CI Validation

GitHub Actions runs on every push and pull request to `main`.

The workflow validates:

- dependency installation,
- unit tests with `pytest`,
- dependency health with `pip check`,
- local Flask demo startup,
- grouped Selenium suites from the `local_demo` profile,
- generated JSON, AI context, HTML reports, and demo logs as short-lived workflow artifacts.

The CI uses grouped Selenium steps instead of one opaque browser run so failures are easier to diagnose by quality area.

## Project Structure

```text
selenium-automation-framework/
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- checks/
|   |-- accessibility_checks.py
|   |-- auth_checks.py
|   |-- data_table_checks.py
|   |-- error_state_checks.py
|   |-- form_validation_checks.py
|   |-- input_checks.py
|   |-- navigation_checks.py
|   |-- registry.py
|   `-- visual_checks.py
|-- config/
|   |-- settings.py
|   `-- test_profiles.yaml
|-- core/
|   |-- ai_context_builder.py
|   |-- driver_factory.py
|   |-- evidence_collector.py
|   |-- html_report_builder.py
|   |-- result.py
|   `-- test_runner.py
|-- demo_app/
|   |-- app.py
|   |-- static/
|   `-- templates/
|-- docs/
|   |-- ai-reporting-strategy.md
|   |-- architecture.md
|   `-- public-roadmap.md
|-- pages/
|   |-- base_page.py
|   |-- home_page.py
|   |-- redirect_page.py
|   `-- status_codes_page.py
|-- tests/
|   |-- test_ai_context_builder.py
|   |-- test_demo_app.py
|   |-- test_html_report_builder.py
|   |-- test_pages.py
|   |-- test_registry.py
|   |-- test_result_models.py
|   `-- test_settings.py
|-- requirements.txt
`-- README.md
```

## Technical Highlights

- Checks follow a common contract and return structured `CheckResult` objects.
- The runner owns browser lifecycle and report generation.
- The registry decouples CLI selection from check implementation.
- The demo app keeps CI deterministic and avoids relying only on third-party websites.
- HTML and AI context are derived from the same run data, keeping reporting consistent.
- Public code intentionally avoids API keys, private prompts, client workflows, and proprietary report templates.

## Future Improvements

- More flexible check parameters from YAML.
- Browser selection beyond Chrome.
- Better report artifact organization by run ID.
- Optional DOM evidence on failures.
- Lightweight accessibility expansion.
- Visual baseline strategy without exposing private assets.
- Private AI integration for test case documents and stakeholder reports.

## Documentation

- [Architecture](docs/architecture.md)
- [AI Reporting Strategy](docs/ai-reporting-strategy.md)
- [Public Roadmap](docs/public-roadmap.md)

## License

MIT License.
