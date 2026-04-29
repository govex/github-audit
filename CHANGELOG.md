# Changelog

All notable changes to this project will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project uses [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Changed
- `SUPPORT.md` rewritten for public audience — removed internal Asana service-request link, 2-business-day SLA, and internal routing copy; now directs users to GitHub Issues (#12)
- `audit/README.md`: corrected stale `repo_audit.xlsx` filename references to timestamped pattern
- `CONTRIBUTING.md`: corrected stale `repo_audit.xlsx` filename reference
- `README.md`: fixed missing `Citation` ToC entry; updated SUPPORT.md accordion description

## [1.1.0] — 2026-04-29

### Added
- `--repos` flag for `audit/audit.py` — scope the audit to one or more specific repositories by name (`python audit/audit.py <org> --repos <repo1> <repo2>`)
- `argparse`-based CLI for `audit/audit.py` — positional `org` arg (optional when `GITHUB_ORG` is set in `.env`) replaces previous `sys.argv` parsing
- `REPO_FILTER` global — case-insensitive set built from `--repos` values; `None` when flag is omitted (audits all repos)
- Warning output when a `--repos` name is not found in the org; exits non-zero if no matching repos remain
- `.github/prompts/audit.prompt.md` — `/audit` Copilot slash command that parses natural-language input and runs the correct `audit.py` command
- Rulesets API check (`get_rulesets`, `get_rulesets_summary`) — detects active GitHub Rulesets targeting the default branch
- `has_any_protection` field — `True` if either classic branch protection OR a Ruleset is active; drives scorecard and Excel Governance tab
- Timestamped, scope-scoped Excel output filenames — `audit_org_<org>_<timestamp>.xlsx`, `audit_repo_<repo>_<timestamp>.xlsx`, `audit_repos_<r1>_<r2>_<timestamp>.xlsx`; files are never overwritten
- New Excel columns in Governance & CI tab: "Rulesets Summary", "Has Rulesets?", "Any Protection?"
- Hard-stop guardrail in `copilot-instructions.md` — agents must never push or open PRs without explicit user instruction

### Changed
- Excel output filename changed from hardcoded `repo_audit.xlsx` to timestamped, scope-scoped names (see Added above)
- Branch Protection section in stdout and Excel now shows both classic protection and Rulesets separately, with a combined "Any Protection?" column

### Fixed
- Upgraded `codeql.yml` from `github/codeql-action` v3 → v4 (v3 deprecated December 2026)
- Added `actions: read` permission to `codeql.yml` to resolve "Resource not accessible by integration" failures on Dependabot PRs
- `audit/audit.py` now exits with code 1 (not 0) when `--repos` filter matches no repositories

---

## [1.0.0] — 2026-04-28

### Added
- `audit/audit.py` — audits every repo in a GitHub org for best practices via the GitHub REST API
- `audit/to_excel.py` — converts audit data to a formatted 6-tab Excel workbook with color-coded Summary Scorecard
- 7 audit categories: overview, documentation, license, contributors, governance, CI/CD, security tooling
- Dual-purpose repo structure: template files at root, audit scripts in `audit/`
- `KNOWLEDGE_BASE.md` — running reference for repo structure, function tables, field lists, and conventions
- `audit/README.md` — audit-specific setup and usage docs
- `.github/workflows/release.yml` — one-click manual-dispatch workflow that tags, extracts CHANGELOG notes, and creates a GitHub Release
- `.github/prompts/release.prompt.md` — `/release` Copilot slash command for AI-assisted version preparation
- Mandatory doc-sync directive in `copilot-instructions.md` — agents must update KNOWLEDGE_BASE.md, CHANGELOG.md, and README.md after every change
- Full starter-template file set: LICENSE (MIT), CONTRIBUTING.md, SECURITY.md, SUPPORT.md, CITATION.cff, CHANGELOG.md, .editorconfig, .env.example
- `.github/` governance files: CODEOWNERS, dependabot.yml, copilot-instructions.md, PR template, issue templates (bug report + feature request)
- CI/CD workflows: `ci.yml` (flake8 lint + syntax check + smoke test), `codeql.yml` (CodeQL security scanning)
- `python-dotenv` integration — `.env` is loaded automatically, no manual `export` needed
- `audit/audit.py` calls `write_xlsx()` directly — produces `repo_audit.xlsx` in one step
- `PULL_REQUEST_TEMPLATE.md` checklist includes `CHANGELOG.md` and `KNOWLEDGE_BASE.md` doc-sync items

[Unreleased]: https://github.com/govex/github-audit/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/govex/github-audit/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/govex/github-audit/releases/tag/v1.0.0
