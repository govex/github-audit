# Contributing to github-audit

Thank you for your interest in contributing! This document covers how to set up the project locally, the branching workflow, and submission guidelines.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Running the Audit Locally](#running-the-audit-locally)
- [Branching & Commit Conventions](#branching--commit-conventions)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Code Style](#code-style)
- [Reporting Issues](#reporting-issues)

---

## Prerequisites

- Python 3.9+
- A GitHub personal access token (classic PAT) with `read:org` and `repo` (read) scopes

## Local Setup

```bash
git clone https://github.com/govex/github-audit.git
cd github-audit

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r audit/requirements.txt

cp .env.example .env
# Edit .env and add your GITHUB_TOKEN
```

## Running the Audit Locally

```bash
# Load env vars and run against any org
export $(cat .env | grep -v '#' | xargs)
python audit/audit.py <org_name>
```

Results are written to `audit/output/` as a timestamped `.xlsx` file (git-ignored).

## Branching & Commit Conventions

- Branch from `main` using `feature/<short-description>` or `fix/<short-description>`.
- Commit messages should follow the pattern:
  ```
  type(scope): short imperative description

  Optional longer body explaining why, not what.
  ```
  Common types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`.

## Submitting a Pull Request

1. Fork the repo and create your branch from `main`.
2. Ensure the script runs without errors against at least one org.
3. Update `README.md` if your change affects usage or output.
4. Open a PR using the provided template and fill in all sections.
5. A maintainer will review within a few business days.

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Keep functions small and focused; prefer returning data over side-effects.
- Avoid committing tokens, credentials, or any personal data.

## Reporting Issues

Use the [GitHub Issues](../../issues) tab and select the appropriate template (Bug Report or Feature Request).
