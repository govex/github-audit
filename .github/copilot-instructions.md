# GitHub Audit — Copilot Instructions

This repo has two purposes: (1) a **starter template** for any GovEx repo, and (2) an **audit tool** in the `audit/` subdirectory. To use just the template, delete `audit/`. All governance files (LICENSE, CONTRIBUTING.md, .github/, etc.) are independent of the audit scripts.

## 🚫 HARD STOP: Never push or open PRs without explicit instruction

**Do NOT do any of the following unless the user explicitly asks:**
- `git push` / `git push --force` / `git push -u origin <branch>`
- Create a pull request (via CLI, API, or any tool)
- Merge a pull request
- Create or push a git tag

**Allowed without asking:** `git add`, `git commit`, `git status`, `git log`, `git diff`, `git fetch`, `git checkout`, `git merge` (local only), `git branch`.

When implementation is complete, stop at a local commit and say: *"Ready to push — run `git push` when you're ready, or tell me to push."*

## ⚠️ MANDATORY: Keep documentation in sync

**After EVERY change you make — no matter how small — you MUST review and update all three of these files before finishing:**

1. **`KNOWLEDGE_BASE.md`** — Update the structure, function tables, field lists, or conventions if anything changed. This is the single source of truth about how the repo works.
2. **`CHANGELOG.md`** — Add a bullet under `[Unreleased]` in the correct sub-heading (Added / Changed / Fixed / Removed). Never skip this.
3. **`README.md`** — Update the project layout tree, best-practice guide, or any section affected by the change.

**This is not optional.** Stale docs are worse than no docs. If you add a file, it goes in the layout tree and KNOWLEDGE_BASE. If you change behavior, it goes in the CHANGELOG. If you rename something, update all three. Do this as part of every task, not as a separate step.

## Audit tool architecture

- **`audit/audit.py`** — Fetches data for every repo in a GitHub org using the GitHub REST API and writes a timestamped Excel file to `audit/output/` directly. CLI is `argparse`-based: positional `org` (optional if `GITHUB_ORG` is in `.env`) and optional `--repos <name> [name …]` to scope to specific repos. All API calls go through the `gh()` (single request) and `gh_paginated()` (auto-paging) helpers. Each repo is audited by `audit_repo()` which returns a flat dict of fields including both classic branch protection and Rulesets API results. `main()` collects results, prints markdown tables to stdout, and calls `write_xlsx()`.
- **`audit/to_excel.py`** — Exposes `write_xlsx(repos, org_owners, audited_at, out_path)` which builds and saves a timestamped Excel workbook in `audit/output/` with 6 tabs using `openpyxl`. Called automatically by `audit.py`. A standalone `__main__` path exists for backward compatibility with an existing `audit_results.json`, but `audit.py` no longer produces that JSON by default.
- **`audit/output/`** — Git-ignored. Never commit files here.
- **`audit/requirements.txt`** — Python dependencies for the audit scripts only.
- **`.github/prompts/audit.prompt.md`** — `/audit` Copilot slash command; parses natural-language input to build and run the correct `python audit/audit.py` command.

## Key conventions

- All GitHub API requests must use the shared `HEADERS` dict (includes auth + API version). Never construct headers inline.
- Rate-limit handling lives in `gh()` and `gh_paginated()` — don't add retry logic elsewhere.
- New audit checks belong in `audit_repo()` as a key in the returned dict, then surfaced in a `print_section()` call in `main()`, and finally added as a column in the relevant `to_excel.py` tab.
- Excel formatting helpers (`hfill`, `header_style`, `apply_zebra`, `highlight_bool_col`) are already defined in `audit/to_excel.py` — use them, don't add new color/style code inline.
- Boolean audit fields (e.g. `readme_exists`, `dependabot`) should be `True/False` in the JSON dict, converted to `"Yes"/"No"` strings only at the Excel-writing stage via `bool_str()`.
- Max line length: 120 characters. Use `flake8 --max-line-length=120`.

## Environment

- `GITHUB_TOKEN` — loaded from `.env` at repo root (git-ignored). Never hardcode or log tokens.
- `GITHUB_ORG` — optional default org; can be overridden via CLI arg.
- See `.env.example` for the full variable list.

## Adding a new audit check — checklist

1. Add a helper function (or inline logic in `audit_repo()`) in `audit/audit.py` that calls `gh()` or `file_exists()`
2. Add the result key(s) to the `return` dict in `audit_repo()`
3. Add the column to the relevant `print_section()` table in `main()`
4. Add the column to the correct tab in `audit/to_excel.py` with appropriate `highlight_bool_col()` formatting
5. Update `audit/README.md` → "What it checks" table if the check is user-visible
6. Update top-level `README.md` → "What it checks" table too

## References

- [KNOWLEDGE_BASE.md](../KNOWLEDGE_BASE.md) — **read this first** — full repo structure, function tables, field lists, conventions
- [CONTRIBUTING.md](../CONTRIBUTING.md) — branch/commit conventions, PR process
- [README.md](../README.md) — full project docs and best-practice guide
- [audit/README.md](../audit/README.md) — audit tool usage
