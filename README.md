# github-audit

[![CI](https://github.com/govex/github-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/govex/github-audit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

This repository serves two independent purposes:

| Purpose | What it is |
|---|---|
| **[Audit tool](audit/)** | Python scripts that audit every repo in a GitHub org against best practices and produce a color-coded Excel scorecard |
| **Starter template** | A reference implementation of every file a well-governed GitHub repo should have — LICENSE, CONTRIBUTING, SECURITY, CODEOWNERS, CI workflows, Copilot setup, and more |

> **Using this as a template?** Clone the repo, delete the `audit/` folder, and update the files below for your project. Everything else stays intact and independent.

---

## Table of Contents

- [Audit tool](#audit-tool)
- [Using as a starter template](#using-as-a-starter-template)
- [Project layout](#project-layout)
- [Repository best-practice guide](#repository-best-practice-guide)
- [Support](#support)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)
- [Citation](#citation)

---

## Audit tool

The `audit/` directory contains the GitHub org audit scripts. See **[audit/README.md](audit/README.md)** for full setup, configuration, and usage instructions.

**Quick start:**
```bash
pip install -r audit/requirements.txt
cp .env.example .env   # add your GITHUB_TOKEN

python audit/audit.py <org_name>                         # all repos → audit_org_<org>_<timestamp>.xlsx
python audit/audit.py <org_name> --repos <repo>          # single repo → audit_repo_<repo>_<timestamp>.xlsx
python audit/audit.py <org_name> --repos <r1> <r2> ...   # several repos → audit_repos_<r1>_<r2>_<timestamp>.xlsx
```

Output files are **never overwritten** — each run produces a unique timestamped file.

A `/audit` Copilot slash command is also available — see `.github/prompts/audit.prompt.md`.

> To use only the template and not the audit tool, simply delete the `audit/` folder — nothing else in the repo depends on it.

---

## Using as a starter template

1. Clone or fork this repo and rename it for your project
2. Delete the `audit/` folder if you don't need the audit scripts
3. Update each file below — expand any section in the [best-practice guide](#repository-best-practice-guide) for details
4. Set your repo's **description** and **topics** in the GitHub UI (Settings → About)
5. Enable **branch protection** on `main` (Settings → Branches)
6. Enable **Dependabot** and **secret scanning** (Settings → Security)

---

## Project layout

```
github-audit/
│
│  ── Audit tool (delete this folder if using as template only) ──
├── audit/
│   ├── audit.py                     # Calls GitHub API, audits each repo
│   ├── to_excel.py                  # Excel generation (called automatically by audit.py)
│   ├── requirements.txt             # Python dependencies
│   ├── README.md                    # Audit tool usage docs
│   └── output/                      # Git-ignored; created on first run
│
│  ── Template files (keep these for any repo) ──
├── .env.example                     # Env variable template (copy → .env)
├── .editorconfig                    # Editor formatting rules
├── LICENSE                          # MIT license
├── CHANGELOG.md                     # Version history
├── CONTRIBUTING.md                  # How to contribute
├── SECURITY.md                      # How to report vulnerabilities
├── SUPPORT.md                       # How to get help
├── CITATION.cff                     # How to cite this project
├── KNOWLEDGE_BASE.md                # Running reference for repo structure & conventions
└── .github/
    ├── CODEOWNERS                   # Who reviews which files
    ├── dependabot.yml               # Automated dependency updates
    ├── copilot-instructions.md      # Copilot knowledge base (auto-loaded)
    ├── PULL_REQUEST_TEMPLATE.md     # PR checklist shown on every PR
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md            # Template for bug reports
    │   └── feature_request.md       # Template for feature requests
    ├── prompts/
    │   ├── release.prompt.md        # /release slash-command — AI-assisted version prep
    │   └── audit.prompt.md          # /audit slash-command — run targeted org/repo audit
    └── workflows/
        ├── ci.yml                   # GitHub Actions: lint + smoke test
        ├── codeql.yml               # GitHub CodeQL security scanning
        └── release.yml              # One-click tag + GitHub Release
```

---

## Repository best-practice guide

Each section below explains a file in this repo, why it matters, and what to change for your own projects. Click any heading to expand.

---

### Documentation & governance files

<details>
<summary><strong>README</strong> — the repo homepage</summary>

The first thing anyone sees when they visit your repository. GitHub renders it automatically.

**What to include (minimum):**
- One-sentence project description
- How to install / set up
- How to use it
- How to contribute
- License

**What to change:** Replace the title, description, badges, and setup steps with your project's info. Remove sections that don't apply.
</details>

<details>
<summary><strong>LICENSE</strong> — choosing the right one</summary>

A legal file that tells others what they can and cannot do with your code. Without one, the code is legally "all rights reserved" even if it's public.

| License | Best for | Key rule |
|---|---|---|
| **MIT** | Most projects, tools, utilities | Anyone can use/modify — just keep the copyright notice |
| **Apache 2.0** | Projects needing patent protection | Same as MIT, plus explicit patent grant |
| **GPL v3** | Code that must stay open-source | Modifications must also be released as GPL |
| **CC BY 4.0** | Data, reports, non-code works | Attribution required; not recommended for code |
| **Unlicense / CC0** | Public domain | No restrictions whatsoever |

**For most GovEx repos: MIT is the right choice.**

**What to change:** Update the copyright year and organization name on the first line of `LICENSE`:
```
Copyright (c) 2026 Your Organization Name
```
</details>

<details>
<summary><strong>CONTRIBUTING.md</strong> — how to contribute</summary>

Instructions for contributors — setup, branching workflow, submission guidelines.

**When does GitHub use it?** GitHub auto-links to `CONTRIBUTING.md` whenever someone opens a new issue or PR.

**What to change:**
- Update the `git clone` URL
- Update language-specific setup steps (e.g. `npm install` vs `pip install`)
- Update maintainer/reviewer names
</details>

<details>
<summary><strong>SECURITY.md</strong> — vulnerability reporting</summary>

Tells people how to report a security vulnerability *privately* instead of opening a public issue.

**When does GitHub use it?** It's linked from the repo's **Security** tab and shown on security-related issues.

**What to change:**
- Update the contact method (email or GitHub private advisory link)
- Adjust response-time commitments to match your team's capacity
</details>

<details>
<summary><strong>CITATION.cff</strong> — how to cite this project</summary>

Machine-readable citation metadata. GitHub shows a **"Cite this repository"** button automatically when this file exists.

**What to change:**
- `title`, `abstract` — your project name and description
- `authors` — for a person use `given-names` + `family-names`; for an organization use `name`
- `repository-code` — your GitHub URL
- `version` and `date-released` — current release info

**Example author entries:**
```yaml
authors:
  # Organization / team:
  - name: "GovEx (Bloomberg Center for Government Excellence)"
  # Individual person:
  - given-names: "Jane"
    family-names: "Smith"
    affiliation: "GovEx, Johns Hopkins University"
```
</details>

<details>
<summary><strong>CHANGELOG.md</strong> — version history</summary>

A human-readable log of changes between versions, using the [Keep a Changelog](https://keepachangelog.com) format.

**Sections per version:** Added, Changed, Deprecated, Removed, Fixed, Security

**What to do:** Every time you merge a behavior-changing PR, add a bullet under `[Unreleased]`. When you cut a release, rename it to the version number and date.
</details>

<details>
<summary><strong>SUPPORT.md</strong> — where to get help</summary>

Tells users how to get support. For public open-source repos, this typically means pointing to GitHub Issues.

GitHub displays a link to `SUPPORT.md` in the new-issue flow.

**What to change:** Update or remove the issue tracker link if hosting outside GitHub.
</details>

---

### GitHub settings & automation

<details>
<summary><strong>CODEOWNERS</strong> — auto-assign PR reviewers</summary>

Lives in `.github/CODEOWNERS`. Maps file patterns to GitHub usernames. When a PR touches matching files, those users are automatically requested as reviewers.

```
# Pattern          Owner(s)
*                  @alice              # fallback: Alice reviews everything
*.py               @alice @bob         # Python: both must review
docs/              @carol              # docs changes: Carol reviews
```

**What to change:** Replace `@katigregg` with your team's GitHub usernames.

> CODEOWNERS only enforces reviews if **branch protection** is also enabled (see below).
</details>

<details>
<summary><strong>dependabot.yml</strong> — automated dependency updates</summary>

Tells GitHub's Dependabot bot to open PRs when your dependencies have new versions or security patches.

**What to change:**
- `package-ecosystem` — `"pip"`, `"npm"`, `"maven"`, etc.
- `interval` — `"daily"`, `"weekly"`, or `"monthly"`
- `open-pull-requests-limit` — how many Dependabot PRs can be open at once

**To enable vulnerability alerts separately:** Repo → Settings → Security → Enable "Dependabot alerts" and "Dependabot security updates".
</details>

<details>
<summary><strong>Branch protection</strong> — prevent direct pushes to main</summary>

Rules that require PRs and reviews before anything reaches `main`.

**How to set it up:**
1. Repo → **Settings** → **Branches**
2. Click **Add branch ruleset** (or "Add rule")
3. Set **Branch name pattern** to `main`
4. Enable:

| Setting | What it does | Recommended? |
|---|---|---|
| Require a pull request before merging | No direct pushes to `main` | ✅ Yes |
| Require approvals (1+) | Someone else must review | ✅ Yes |
| Dismiss stale reviews | Re-review if new commits pushed | ✅ Yes |
| Require review from Code Owners | CODEOWNERS enforced | ✅ If using CODEOWNERS |
| Require status checks to pass | CI must be green | ✅ Yes |
| Include administrators | Rules apply to admins too | Recommended |

5. Click **Save changes**
</details>

<details>
<summary><strong>Merge strategy</strong> — squash vs rebase vs merge commit</summary>

When a PR is merged, GitHub offers three options:

| Strategy | What it does | Best for |
|---|---|---|
| **Squash and merge** ✅ | All branch commits become one commit on `main` | Most teams — clean history |
| **Rebase and merge** | Replays commits on top of `main`, no merge bubble | Full history, linear |
| **Merge commit** | Preserves full branch history with a merge commit | Large projects |

**This repo uses: Squash and merge.**

**To enforce:** Settings → General → Pull Requests → check only "Allow squash merging".
</details>

<details>
<summary><strong>Repo description and topics</strong> — discoverability</summary>

Two metadata fields visible on the repo homepage.

**How to set them:**
1. On the repo main page, click the ⚙️ gear icon next to **"About"**
2. Fill in **Description** (1–2 sentences)
3. Add **Topics** — lowercase, hyphen-separated keywords
4. Click **Save changes**

**Good topic examples:** `govex`, `open-data`, `civic-tech`, `python`, `data-analysis`, `public-health`
</details>

---

### Issue and PR templates

<details>
<summary><strong>Issue templates</strong> — how to use them</summary>

Pre-filled forms that appear when someone clicks **New issue**. They prevent vague reports and speed up triage.

**How GitHub uses them:** When `.github/ISSUE_TEMPLATE/` has multiple files, GitHub shows a menu:
> **Choose an issue type:** 🐛 Bug Report · 💡 Feature Request

**How to open an issue:**
1. Go to the repo → **Issues** tab → **New issue**
2. Select the template that fits
3. Fill in every section
4. Click **Submit new issue**

**What to change:**
- `name` / `about` — the label and description in the menu
- `assignees` — who gets auto-assigned
- `labels` — auto-applied label (`bug`, `enhancement`, etc.)
- The body — add/remove sections for your project's needs
</details>

<details>
<summary><strong>Pull Request template</strong> — how to use it</summary>

A pre-filled description that appears every time someone opens a PR.

**How to use it:**
1. Push your branch to GitHub
2. Go to **Pull requests** → **New pull request**
3. Select your branch in the "compare" dropdown
4. The template pre-fills the description — **complete every section**
5. Check off each item in the checklist
6. Click **Create pull request**

**What to change:** Add/remove checklist items to match your team's "definition of done".
</details>

---

### Branching & versioning

<details>
<summary><strong>Branch naming conventions</strong></summary>

**Format: `type/short-description`**

| Type | Use for | Example |
|---|---|---|
| `feature/` | New functionality | `feature/add-csv-export` |
| `fix/` | Bug fixes | `fix/pagination-off-by-one` |
| `docs/` | Documentation only | `docs/update-contributing` |
| `chore/` | Maintenance, deps, CI | `chore/bump-requests-2.32` |
| `refactor/` | Code restructuring | `refactor/extract-helpers` |

**Rules:** lowercase + hyphens only, 3–5 words, branch from `main`, delete after merge.

**Commit message format:**
```
type(scope): short imperative description

Optional body explaining WHY, not what.
```
Example: `fix(auth): handle expired token gracefully`
</details>

<details>
<summary><strong>GitHub Releases and semantic versioning</strong></summary>

**Semantic versioning:** `MAJOR.MINOR.PATCH`

| Part | When to increment | Example |
|---|---|---|
| `MAJOR` | Breaking change | `1.x.x` → `2.0.0` |
| `MINOR` | New feature, backward-compatible | `1.0.x` → `1.1.0` |
| `PATCH` | Bug fix, backward-compatible | `1.0.0` → `1.0.1` |

**How to publish a release (automated):**
1. Update `CHANGELOG.md` — move `[Unreleased]` items to a new `## [x.y.z] — YYYY-MM-DD` section
2. Commit & push: `git commit -m "chore: release v1.1.0" && git push`
3. GitHub → **Actions** → **Release** → **Run workflow** → enter `1.1.0` → click **Run**

The workflow validates the version, creates a git tag, extracts notes from CHANGELOG.md, and publishes a GitHub Release — all automatically.
</details>

---

### CI/CD & security

<details>
<summary><strong>GitHub Actions / CI workflow</strong></summary>

An automated script (`.github/workflows/ci.yml`) that runs on every push and PR to catch errors before they reach `main`.

**How it works:**
1. You push or open a PR
2. GitHub spins up a runner and executes the steps in `ci.yml`
3. A green ✅ or red ❌ appears on the PR

**Viewing results:** Go to the **Actions** tab, or check the status at the bottom of any PR.

**What to change:**
- `python-version` — match your project
- Add test steps (e.g. `run: pytest`)
- Swap for your stack if not Python (e.g. `npm test`)
</details>

<details>
<summary><strong>CodeQL / secret scanning</strong></summary>

**CodeQL** (`.github/workflows/codeql.yml`) scans code for security vulnerabilities on every push/PR and weekly. Results appear in **Security → Code scanning**.

**Secret scanning** (no file needed) detects accidentally committed tokens/passwords. For private repos, enable it manually:
1. **Settings → Security → Secret scanning**
2. Enable **"Secret scanning"** and **"Push protection"**

Push protection blocks the push before a credential reaches GitHub.

**What to change in `codeql.yml`:** Update `languages` from `python` to your language(s): `javascript`, `java`, `go`, `ruby`, `csharp`.
</details>

---

### Editor & environment

<details>
<summary><strong>.editorconfig</strong> — consistent formatting</summary>

Tells code editors to use the same indentation, line endings, and whitespace rules regardless of personal settings.

**Most people never need to touch this file.** VS Code users may need the [EditorConfig extension](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig).
</details>

<details>
<summary><strong>.gitignore and .env</strong> — secrets and ignored files</summary>

**`.gitignore`** tells git which files to never commit — build outputs, `node_modules/`, `venv/`, credentials, OS noise.

**`.env`** stores secrets (tokens, API keys) as environment variables. **`.env.example`** is the committed template showing what's needed without real values.

**Golden rules:**
- `.env` is in `.gitignore` — **never committed**
- `.env.example` is committed — shows teammates what variables to set
- If you accidentally commit a secret: rotate the credential immediately, then remove from git history
</details>

---

### AI tooling

<details>
<summary><strong>GitHub Copilot — knowledge base and prompts</strong></summary>

#### copilot-instructions.md (knowledge base)

A file at `.github/copilot-instructions.md` that Copilot reads automatically on every request. Think of it as a **briefing document for your AI assistant** — repo architecture, naming conventions, key patterns.

**What to put in yours (keep it short):**
- Main entry points and what they do
- Patterns that differ from common defaults
- How to run/build/test
- Links to docs (don't copy content inline)

**What NOT to include:** things enforced by your linter, obvious conventions, full file contents.

#### Custom prompts (slash commands)

Reusable task templates in `.github/prompts/*.prompt.md` that appear as **slash commands** in VS Code Copilot Chat. Each prompt is a markdown file with YAML frontmatter and step-by-step instructions that Copilot follows.

**Example in this repo: `/release`**

Type `/release` in Copilot Chat and it will:
1. Read CHANGELOG.md to find the current version and unreleased changes
2. Auto-select the next version (major/minor/patch) based on what changed
3. Edit CHANGELOG.md — move `[Unreleased]` items into a dated version section
4. Edit CITATION.cff — update `version` and `date-released`
5. Show you a release-notes preview and the exact commands to commit + trigger the release workflow

You can override the version: `/release` → `2.0.0`

#### How to create your own prompt

1. Create `.github/prompts/my-task.prompt.md`
2. Add frontmatter:
   ```yaml
   ---
   description: "Brief description — shown in the slash-command menu"
   argument-hint: "What to type after the command"
   agent: agent
   ---
   ```
3. Write step-by-step instructions in markdown below the frontmatter. Be specific — tell Copilot which files to read, what logic to apply, and what output to produce.
4. Save — `/my-task` is immediately available in Copilot Chat.

**Tips for good prompts:**
- Reference files with relative paths from the prompt (e.g. `[CHANGELOG.md](../../CHANGELOG.md)`)
- Use `$input` to capture what the user types after the command
- Add a "Rules" section at the end with guardrails (e.g. "never push to remote")
- Keep instructions deterministic — avoid vague language like "improve" or "clean up"

**More prompt ideas:** `/write-tests`, `/review-pr`, `/draft-readme`, `/update-changelog`
</details>

---

## Support

To report a bug or request a feature, [open a GitHub Issue](../../issues). See [SUPPORT.md](SUPPORT.md) for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Security

To report a vulnerability, see [SECURITY.md](SECURITY.md). Never commit your `.env` file or token.

## License

[MIT License](LICENSE) © 2026 GovEx.

## Citation

Cite this project using [CITATION.cff](CITATION.cff) or click **"Cite this repository"** on the GitHub page.
