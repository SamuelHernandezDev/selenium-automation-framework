# Public Roadmap

This roadmap separates what belongs in the public showcase from private future work.

## Completed

- Page Object Model foundation.
- Configurable profiles through YAML.
- Selenium Chrome driver factory.
- Structured result models.
- Evidence collection helpers.
- Reusable check suites:
  - navigation,
  - error states,
  - accessibility signals,
  - visual smoke checks.
- Central check registry.
- Custom test runner.
- Professional CLI for run, list, and report commands.
- JSON technical reports.
- AI-ready context reports.
- Internal pytest suite for framework contracts.
- Removal of the legacy driver wrapper.
- Generated reports kept out of source control.
- Page Objects refined to avoid direct runtime configuration ownership.
- Local Flask demo app for deterministic browser automation.
- Input and form validation checks for the local contact flow.
- Authentication demo flow and Selenium checks.
- Data table demo flow with search, filtering, sorting, and Selenium checks.
- Static HTML report generation from structured run data.
- GitHub Actions CI for unit tests, dependency checks, and local Selenium demo execution.

## Next Public Improvements

- Add README examples with sample output snippets.

## Future Public Enhancements

- Additional pytest coverage for runner edge cases.
- More flexible check parameters from YAML.
- Browser selection beyond Chrome.
- Better report artifact organization by run ID.
- Optional DOM evidence on failures.
- Lightweight accessibility expansion.
- Visual baseline strategy without exposing private assets.

## Private Future Work

- Real AI API integration.
- Private prompt library.
- Automatic test case document generation.
- Client-specific report templates.
- Private application profiles.
- Ticket or issue tracker integration.
- Sensitive QA metrics and dashboards.

## Guiding Rule

The public repository should demonstrate architecture, automation skill, and reporting strategy. Private extensions should contain credentials, proprietary workflows, and client-specific intelligence.
