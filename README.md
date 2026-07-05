# Selenium Automation Framework

A modular UI automation framework built with Python, Selenium WebDriver, Page Object Model patterns, configurable check suites, JSON reporting, and AI-ready execution context.

The goal is to show a clean automation architecture that can grow from public demo checks into private reporting, test-case generation, and AI-assisted QA workflows.

## What This Project Demonstrates

- Selenium WebDriver automation with reusable Page Objects.
- Configurable execution through YAML profiles.
- A central driver factory.
- Reusable check suites for navigation, error states, accessibility signals, and visual smoke checks.
- Structured result models for checks, evidence, and full test runs.
- JSON reports generated per execution.
- AI-ready context generated from real automation results.
- A custom runner that can execute suites by profile, suite, or check.

## Project Structure

```text
selenium-automation-framework/
|-- checks/
|   |-- accessibility_checks.py
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
|   |-- result.py
|   `-- test_runner.py
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
|-- utils/
|-- requirements.txt
`-- README.md
```

Generated reports and screenshots are ignored by Git and created at runtime.

## Available Suites

```text
navigation
error_states
accessibility
visual
```

Current checks can be listed with:

```bash
venv\Scripts\python.exe -m core.test_runner --list
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run The Framework

Run the default profile:

```bash
venv\Scripts\python.exe -m core.test_runner --profile default
```

Run the full public demo profile:

```bash
venv\Scripts\python.exe -m core.test_runner --profile full_demo
```

Run a specific suite:

```bash
venv\Scripts\python.exe -m core.test_runner --profile default --suite navigation
```

Run a specific check:

```bash
venv\Scripts\python.exe -m core.test_runner --profile default --suite navigation --check page_title
```

Override the target URL:

```bash
venv\Scripts\python.exe -m core.test_runner --profile default --base-url https://the-internet.herokuapp.com/
```

## Output

Each run writes structured artifacts under `reports/json/`:

```text
latest_run.json
<run_id>.json
latest_ai_context.json
<run_id>_ai_context.json
```

Visual and failure evidence is stored under:

```text
reports/screenshots/
reports/dom/
```

The repository does not track generated report folders. The runner creates them when needed.

## AI-Ready Context

This project does not call an AI API in the public version. Instead, it produces a safe structured payload that can be used later by a private AI reporting layer.

The AI context includes:

- run summary and risk level,
- executed suite coverage,
- findings and evidence references,
- recommended focus areas,
- suggested future test cases,
- reporting guidance.

See [docs/ai-reporting-strategy.md](docs/ai-reporting-strategy.md).

## Documentation

- [Architecture](docs/architecture.md)
- [AI Reporting Strategy](docs/ai-reporting-strategy.md)
- [Public Roadmap](docs/public-roadmap.md)

## Current Status

The framework can execute real Selenium checks against a public demo site and produce JSON reports plus AI-ready context.

Some areas are intentionally reserved for future expansion:

- `tests/` contains internal unit tests for the framework.
- `input_checks.py` and `form_validation_checks.py` are reserved for future flows with real forms.

## License

MIT License.
