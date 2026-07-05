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
- JSON technical reports.
- AI-ready context reports.
- Internal pytest suite for framework contracts.
- Removal of the legacy driver wrapper.
- Generated reports kept out of source control.

## Next Public Improvements

- Refine Page Objects so they remain interaction-focused.
- Add README examples with sample output snippets.
- Add GitHub Actions for static validation.
- Add simple HTML report generation from JSON.

## Future Public Enhancements

- `pytest` integration for framework internals.
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
