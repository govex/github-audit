---
description: "Run the GitHub org audit — optionally scope to specific repos by name."
argument-hint: "Optional: org name and/or repo names, e.g. 'govex' or 'govex gepi-ui gepi-api'"
agent: agent
---

Run the GitHub org audit for the user. The user said: $input

## Instructions

### 1. Determine the target org and repos

Parse the user's input to extract:
- **Org name** — any word that looks like a GitHub organization slug (e.g. `govex`). If not provided, omit from the command and let the script use `GITHUB_ORG` from `.env`.
- **Repo names** — any remaining words that look like repo names (kebab-case or otherwise). These go after `--repos`.

If you cannot determine which words are the org vs. repo names, ask the user to clarify before running.

### 2. Build the command

Construct the `python audit/audit.py` command from the parsed values:

| Scenario | Command |
|---|---|
| No input — use default org, all repos | `python audit/audit.py` |
| Org only | `python audit/audit.py <org>` |
| Org + one repo | `python audit/audit.py <org> --repos <repo>` |
| Org + multiple repos | `python audit/audit.py <org> --repos <repo1> <repo2> ...` |

> All commands must be run from the **repo root**.

### 3. Run the audit

Run the constructed command in the terminal. The script will:
- Print markdown summary tables to stdout for each category of checks
- Write a timestamped, scope-scoped Excel report to `audit/output/` using one of these filename patterns:
  - Full org: `audit_org_<org>_<YYYYMMDD_HHMMSS>.xlsx`
  - Single repo: `audit_repo_<repo>_<YYYYMMDD_HHMMSS>.xlsx`
  - Multiple repos: `audit_repos_<repo1>_<repo2>_<YYYYMMDD_HHMMSS>.xlsx` (SHA-1 hash suffix used for very long slugs)
- Each run produces a unique file — existing reports are never overwritten

Report any errors (e.g. missing `GITHUB_TOKEN`, unknown org, no matching repos) to the user with suggested fixes.

### 4. Report results

After the command completes successfully, summarize:
- How many repositories were audited
- The full path to the Excel output file (printed by the script at the end of its run)
- Any warnings printed (e.g. repo names that were not found in the org)
