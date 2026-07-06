# AI Reporting Strategy

The public version of this project does not call an AI API. It produces structured, AI-ready context that can be consumed later by a private reporting layer.

This keeps the repository safe to publish while still demonstrating how automation output can be prepared for intelligent analysis.

## Goals

- Summarize technical automation results for QA and engineering readers.
- Provide consistent findings with evidence references.
- Suggest follow-up test cases from executed checks.
- Support future report generation without exposing private prompts or credentials.

## Generated Files

Each run can generate:

```text
reports/json/latest_run.json
reports/json/<run_id>.json
reports/json/latest_ai_context.json
reports/json/<run_id>_ai_context.json
reports/html/latest_report.html
reports/html/<run_id>.html
```

The technical run JSON is the source of truth. The AI context is a derived, compact reporting payload.
The HTML report is a readable static view over the same structured data.

## AI Context Contents

The context currently includes:

- `run_id`
- target URL, profile, browser, suite metadata
- status summary
- risk level
- severity counts
- suite coverage
- tag counts
- findings
- evidence references
- recommended focus
- suggested future test cases
- reporting notes
- prompt guidance

## Finding Rules

Only these statuses are treated as findings:

- `failed`
- `error`
- `warning`

Skipped checks are treated as coverage gaps, not product defects.

Passed checks contribute to coverage and reporting confidence, but they should not be inflated into claims beyond what the checks verified.

## Safe Public Boundary

The public repository should include:

- result schemas,
- AI-ready context builder,
- example generated structure,
- deterministic report signals,
- public demo target configuration.

The public repository should not include:

- API keys,
- private prompts,
- client-specific templates,
- internal QA formats,
- private application URLs,
- automatic ticket creation credentials.

## Future Private Layer

A private extension can consume `latest_ai_context.json` to:

- draft QA summaries,
- generate bug report descriptions,
- fill test-case templates,
- produce release notes for test coverage,
- prioritize findings by risk,
- create stakeholder-friendly reports.

That layer should treat the JSON as evidence-informed input, not as absolute truth.

## Prompt Guidance

An AI report should:

- state what was tested,
- state what passed,
- call out warnings, failures, and errors,
- reference evidence paths,
- distinguish skipped checks from defects,
- avoid inventing issues not present in findings,
- suggest next tests based on actual coverage gaps.
