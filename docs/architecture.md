# Architecture

This project is organized around a small set of contracts:

- configuration decides what to run,
- the driver factory creates the browser,
- checks execute reusable validations,
- results capture structured outcomes,
- evidence collectors capture artifacts,
- the runner coordinates execution,
- the AI context builder transforms results into reporting input.

## Runtime Flow

```text
config/test_profiles.yaml
        |
        v
config/settings.py
        |
        v
core/test_runner.py
        |
        |-- core/driver_factory.py
        |-- checks/registry.py
        |-- core/evidence_collector.py
        |
        v
core/result.py
        |
        v
reports/json/*.json
        |
        v
core/ai_context_builder.py
```

The optional local demo target lives in `demo_app/` and can be used through the `local_demo` profile.

## Layers

### config

`config/settings.py` defines typed runtime settings and loads named profiles from `config/test_profiles.yaml`.

Profiles control:

- base URL,
- selected suites,
- browser,
- headless mode,
- timeout,
- viewport size,
- report directory,
- public/private metadata.

### core

`core/result.py` contains the shared result model:

- `Evidence`
- `CheckResult`
- `TestRunResult`
- `CheckStatus`
- `Severity`

`core/evidence_collector.py` captures browser state, screenshots, DOM snapshots, and failure bundles.

`core/driver_factory.py` creates Selenium WebDriver instances from settings.

`core/test_runner.py` executes registered checks and writes JSON artifacts.

`core/ai_context_builder.py` converts technical results into AI-ready reporting context.

### checks

Checks are reusable functions that follow this contract:

```python
def check_name(driver, base_url, *, evidence_collector=None) -> CheckResult:
    ...
```

Checks should not print, exit, or own the browser lifecycle. They return `CheckResult`.

Current suites:

- `navigation`
- `error_states`
- `accessibility`
- `visual`
- `inputs`
- `forms`

`checks/registry.py` is the central source used by the runner.

### pages

Page Objects encapsulate Selenium interactions with specific pages.

Current Page Objects target stable demo flows:

- home page,
- redirect page,
- status codes page.

Page Objects stay focused on browser interaction. Runtime configuration such as base URL, browser, and timeout is owned by config, checks, and the runner.

### reports

Reports are generated artifacts and are ignored by Git. The repository does not track empty report folders because the runner creates them when needed.

The runner writes:

- technical run JSON,
- AI-ready context JSON,
- screenshots,
- optional DOM evidence.

### demo_app

`demo_app/` is a small Flask application included in the monorepo. It provides deterministic routes for automation:

- `/`
- `/redirect`
- `/status-codes`
- `/status-codes/<code>`
- `/contact`
- `/health`

The app exists so browser automation can run against a controlled target during local development and future CI.

The input and form validation suites use the `/contact` flow to exercise required fields, invalid input feedback, accessible errors, and successful submission.

## Design Principles

- Keep checks independent from CLI concerns.
- Keep runner logic independent from page-specific behavior.
- Prefer structured results over prints and raw assertions.
- Capture evidence close to failures.
- Keep public code free from API keys, private prompts, and client-specific templates.
- Add abstractions only when they reduce real repetition or clarify ownership.

## Tests

The `tests/` folder contains fast unit tests for framework internals. Selenium browser execution is handled by the runner and is validated separately with profile-based commands.

Unit tests are deterministic and do not depend on external websites. Runner executions use the configured target URL, so public demo runs may be affected by third-party availability.

Current unit test coverage focuses on:

- result serialization,
- settings loading,
- registry resolution,
- AI context generation,
- Page Object basics,
- local demo app behavior.
