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

`checks/registry.py` is the central source used by the runner.

### pages

Page Objects encapsulate Selenium interactions with specific pages.

Current Page Objects target the public demo site:

- home page,
- redirect page,
- status codes page.

The next migration step is to remove remaining legacy assumptions and make Page Objects fully settings-driven.

### reports

Reports are generated artifacts and are ignored by Git.

The runner writes:

- technical run JSON,
- AI-ready context JSON,
- screenshots,
- optional DOM evidence.

## Design Principles

- Keep checks independent from CLI concerns.
- Keep runner logic independent from page-specific behavior.
- Prefer structured results over prints and raw assertions.
- Capture evidence close to failures.
- Keep public code free from API keys, private prompts, and client-specific templates.
- Add abstractions only when they reduce real repetition or clarify ownership.

## Known Migration Notes

`utils/driver.py` currently delegates to `core.driver_factory` for compatibility with older tests. It should be removed once script-style tests are migrated.

The `tests/` folder still contains older examples. Future work should either convert them to `pytest` tests for framework internals or replace them with runner-based examples.
