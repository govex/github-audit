# Knowledge Base

A running reference for how this repository is structured, what each piece does, and how it all fits together. Updated continuously as the project evolves.

> **For Copilot agents:** This file is your primary source of truth about the repo. Read it before making assumptions. Update it whenever you change the structure, add files, or modify behavior.

---

## Purpose

This repo serves two independent purposes:

1. **Starter template** — A reference implementation of every file a well-governed GitHub repo should have. Fork/clone it for any new project and delete what you don't need.
2. **Audit tool** — Python scripts in `audit/` that audit every repository in a GitHub organization against best practices and produce a color-coded Excel scorecard.

To use only the template, delete `audit/`. Everything else is self-contained.

---

## Repository structure

```
github-audit/
│
│  ── Audit tool (deletable) ──
├── audit/
│   ├── audit.py                     # Main audit script — calls GitHub REST API
│   ├── to_excel.py                  # Excel generation module (called by audit.py; also runnable standalone)
│   ├── requirements.txt             # Python deps: requests, tabulate, openpyxl, python-dotenv
│   ├── README.md                    # Audit-specific setup and usage docs
│   └── output/                      # Git-ignored; timestamped xlsx files written here
│
│  ── Template / governance files ──
├── .env.example                     # Shows which env vars are needed (committed)
├── .editorconfig                    # Editor formatting rules (indent, EOL, etc.)
├── LICENSE                          # MIT License © 2026 GovEx
├── CHANGELOG.md                     # Keep a Changelog format, semver
├── CONTRIBUTING.md                  # Setup, branching, PR process for contributors
├── SECURITY.md                      # How to report vulnerabilities privately
├── SUPPORT.md                       # How to get help — directs users to GitHub Issues
├── CITATION.cff                     # Machine-readable citation metadata
├── KNOWLEDGE_BASE.md                # ← This file
├── README.md                        # Dual-purpose landing page with accordion guide
│
│  ── GitHub config ──
└── .github/
    ├── CODEOWNERS                   # Auto-assigns PR reviewers by file path
    ├── dependabot.yml               # Weekly pip + GitHub Actions dependency PRs
    ├── copilot-instructions.md      # Copilot knowledge base — auto-loaded every request
    ├── PULL_REQUEST_TEMPLATE.md     # Pre-filled PR description checklist
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md            # Bug report form
    │   └── feature_request.md       # Feature request form
    ├── prompts/
    │   ├── release.prompt.md        # /release slash command — AI-assisted version prep
    │   └── audit.prompt.md          # /audit slash command — run targeted org/repo audit
    └── workflows/
        ├── ci.yml                   # Lint (flake8) + syntax check + smoke test
        ├── codeql.yml               # CodeQL security scanning (Python)
        └── release.yml              # Manual-dispatch: tag + GitHub Release from CHANGELOG
```

---

## Audit tool — how it works

### Data flow

1. `audit/audit.py` is invoked via `argparse`; `ORG` and optional `REPO_FILTER` (a set of lowercased names) are resolved from CLI args / `.env`
2. `audit/audit.py` fetches the org's repo list via `gh_paginated("/orgs/{org}/repos")`
3. If `REPO_FILTER` is set, the list is filtered to matching names; warnings are printed for any names not found
4. For each repo, `audit_repo()` calls 15+ API endpoints and file-existence checks
5. Results are collected into a list of flat dicts
6. Markdown summary tables are printed to stdout
7. `write_xlsx()` (from `audit/to_excel.py`) is called directly to produce a timestamped Excel file in `audit/output/`

### Key functions in audit.py

| Function | Purpose |
|---|---|
| `gh(path)` | Single GET request with rate-limit retry (5 attempts) |
| `gh_paginated(path)` | Auto-paging GET, follows `Link: next` headers |
| `file_content(owner, repo, path)` | Returns `(exists, content, size)` via Contents API |
| `file_exists(owner, repo, path)` | Boolean wrapper around `file_content` |
| `audit_repo(repo_data)` | Main per-repo audit — returns flat dict of all fields |
| `print_section(title, rows, headers)` | Prints a markdown table to stdout |
| `_build_output_path(org, repo_filter)` | Builds timestamped, scope-scoped output path — never overwrites |
| `get_rulesets(owner, repo, default_branch)` | Returns list of active rulesets targeting the default branch |
| `get_rulesets_summary(rulesets)` | Converts ruleset list to human-readable summary string |
| `main()` | Orchestrates everything: fetch repos, audit each, write output |

### Key functions in to_excel.py

| Function | Purpose |
|---|---|
| `write_xlsx(repos, org_owners, audited_at, out_path)` | Build and save the full workbook; returns the saved path |
| `hfill(hex_color)` | Create a PatternFill from a hex color |
| `header_style(ws, row, cols)` | Apply dark header styling to a row |
| `apply_zebra(ws, start, end, cols)` | Alternating row shading |
| `highlight_bool_col(ws, col, start, end)` | Green "Yes" / Red "No" conditional formatting |
| `bool_str(v)` | Convert `True`/`False` → `"Yes"`/`"No"` |
| `trunc(s, n)` | Truncate a string to `n` chars with `...` suffix |
| `autofit(ws)` | Auto-size column widths to content |
| `freeze(ws, cell)` | Freeze panes at the given cell (default `B2`) |

### Audit fields returned by `audit_repo()`

The returned dict includes these key fields (non-exhaustive):

- **Metadata:** `name`, `visibility`, `archived`, `fork`, `default_branch`, `language`, `stars`, `forks`, `open_issues`
- **Staleness:** `last_push_days`, `stale` (>180 days)
- **README:** `readme_exists`, `readme_chars`, `readme_lines`, `readme_placeholder`, `readme_placeholder_reason`
- **Docs:** `contributing_exists`, `security_policy`, `citation_exists`
- **License:** `license_spdx`, `license_name`
- **Topics:** `topics`, `topic_count`
- **Contributors:** `contributor_count`, `top_contributors`, `last_contributor`, `last_commit_date`
- **Governance:** `codeowners`, `branch_protection`, `rulesets_summary`, `has_rulesets`, `has_any_protection`
- **CI/CD:** `workflow_count`, `workflows`, `pr_template`, `issue_templates`
- **Security:** `dependabot`, `vuln_alerts`
- **Naming:** `kebab_case_name`, `has_description`, `has_homepage`

---

## Template files — what to customize

When using this repo as a template for a new project, update these files:

| File | What to change |
|---|---|
| `README.md` | Title, description, badges, setup steps, usage |
| `LICENSE` | Copyright year and organization name (line 3) |
| `CONTRIBUTING.md` | Clone URL, setup commands, reviewer names |
| `SECURITY.md` | Contact method, response time commitment |
| `SUPPORT.md` | No changes needed — already public-facing; optionally update the issue tracker link if hosting elsewhere |
| `CITATION.cff` | Title, authors, repo URL, version, date |
| `CHANGELOG.md` | Clear existing entries, start fresh |
| `.github/CODEOWNERS` | Replace `@katigregg` with your team's GitHub usernames |
| `.github/dependabot.yml` | Change `package-ecosystem` if not Python |
| `.github/workflows/ci.yml` | Change language version, test commands |
| `.github/workflows/codeql.yml` | Change `languages` if not Python |
| `.github/workflows/release.yml` | Works as-is for any project with a CHANGELOG.md |
| `.github/copilot-instructions.md` | Rewrite for your project's architecture |
| `.env.example` | Update variable names/descriptions for your project |

---

## Conventions

- **Boolean fields** are `True`/`False` in JSON, converted to `"Yes"/"No"` only at the Excel stage via `bool_str()`
- **API headers** always use the shared `HEADERS` dict — never construct inline
- **Rate limiting** is handled in `gh()` and `gh_paginated()` only — no retry logic elsewhere
- **CLI args** parsed with `argparse`; `ORG` (positional, optional) and `--repos` (zero or more repo names); `REPO_FILTER` is `None` when `--repos` is omitted, otherwise a lowercased set
- **Output filenames** are timestamped and scope-scoped — never overwrite: `audit_org_<org>_<YYYYMMDD_HHMMSS>.xlsx`, `audit_repo_<repo>_<timestamp>.xlsx`, `audit_repos_<r1>_<r2>_<timestamp>.xlsx`; if slug exceeds 200 chars, a SHA-1 short hash replaces the repo list
- **Rulesets vs classic protection** — `branch_protection` reflects the classic API; `rulesets_summary` reflects the Rulesets API; `has_any_protection` is the OR of both — use this for scorecard logic
- **Line length** max 120 chars, enforced by `flake8 --max-line-length=120`
- **Branch naming** uses `type/short-description` (e.g. `feature/add-csv-export`)
- **Commit messages** follow `type(scope): description` (e.g. `fix(auth): handle expired token`)
- **Merge strategy** is squash-and-merge — each PR becomes one commit on `main`
- **Secrets** live in `.env` (git-ignored), never hardcoded or logged

---

## Recent changes

See [CHANGELOG.md](CHANGELOG.md) for the full version history.
