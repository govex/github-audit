# Audit Tool

Scripts to audit every repository in a GitHub organization against a comprehensive set of best practices and produce a color-coded Excel scorecard.

## What it checks

| Category | Checks |
|---|---|
| **Overview** | Visibility, archived/fork status, description, language, staleness, kebab-case naming |
| **Documentation** | README (exists, length, placeholder detection), CONTRIBUTING, SECURITY policy, CITATION |
| **License & Topics** | SPDX license identifier, repository topics/tags |
| **Contributors** | Total contributor count, last committer + date, top 5 by commits |
| **Governance** | CODEOWNERS file, classic branch protection rules, GitHub Rulesets (modern branch rules), default branch name |
| **CI/CD** | GitHub Actions workflows, PR templates, issue templates |
| **Security tooling** | Dependabot config, vulnerability alerts enabled |

## Requirements

- Python 3.9+
- A GitHub [personal access token (classic)](https://github.com/settings/tokens) with scopes:
  - `read:org`
  - `repo` (read-only is sufficient)
  - `security_events` (for vulnerability alert status)

## Setup

```bash
# From the repo root:
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r audit/requirements.txt

cp .env.example .env
# Open .env and paste your GITHUB_TOKEN
```

## Configuration

Copy `.env.example` → `.env` at the repo root and fill in your values. The `.env` file is git-ignored so your token is never committed.

| Variable | Required | Description |
|---|---|---|
| `GITHUB_TOKEN` | Recommended | Classic PAT — enables 5 000 req/hr and unlocks branch-protection data. Without it the script falls back to 60 req/hr and some fields are masked. |
| `GITHUB_ORG` | Optional | Default org to audit. Can also be passed as a CLI argument. |

## Running the audit

Run all commands from the **repo root**:

```bash
# Audit all repos in an org — output: audit_org_<org>_<timestamp>.xlsx
python audit/audit.py <org_name>

# Audit a single repo — output: audit_repo_<repo>_<timestamp>.xlsx
python audit/audit.py <org_name> --repos <repo_name>

# Audit several specific repos — output: audit_repos_<r1>_<r2>_<timestamp>.xlsx
python audit/audit.py <org_name> --repos <repo1> <repo2> <repo3>
```

If `GITHUB_ORG` is set in `.env`, you can omit the org argument entirely:

```bash
python audit/audit.py
python audit/audit.py --repos <repo_name>
```

The Excel report is written to `audit/output/` with a timestamped filename — **existing files are never overwritten**.

```
audit/output/
└── audit_org_<org>_<timestamp>.xlsx    # All repos in an org
└── audit_repo_<repo>_<timestamp>.xlsx  # Single repo
└── audit_repos_<...>_<timestamp>.xlsx  # Multiple repos
```

## Output — Excel tabs

| Tab | Contents |
|---|---|
| **Overview** | Repo metadata, staleness, kebab-case naming |
| **Documentation** | README quality, CONTRIBUTING, SECURITY, CITATION |
| **License & Topics** | SPDX license identifier, topics/tags |
| **Contributors** | Last committer, commit date, top 5 contributors |
| **Governance & CI** | CODEOWNERS, branch protection, workflows, templates, Dependabot |
| **Summary Scorecard** | Pass/fail counts across all checks with color-coded ratings |

## Adding a new check

See the [copilot-instructions.md](../.github/copilot-instructions.md) for the step-by-step checklist.

## Copilot slash command

A `/audit` slash command is available via `.github/prompts/audit.prompt.md`. It parses natural-language input (org name, optional repo names) and runs the appropriate `python audit/audit.py` command for you.

## Files in this directory

| File | Purpose |
|---|---|
| `audit.py` | Calls the GitHub API, audits each repo, writes a timestamped `.xlsx` to `output/` directly |
| `to_excel.py` | Excel generation module — called by `audit.py`; can also be run standalone if you have an existing `audit_results.json` |
| `requirements.txt` | Python dependencies (`requests`, `tabulate`, `openpyxl`) |
| `output/` | Git-ignored output directory created automatically on first run |
