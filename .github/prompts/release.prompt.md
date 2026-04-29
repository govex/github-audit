---
description: "Prepare a release — AI picks the next version number, updates CHANGELOG.md and CITATION.cff, and tells you how to finish."
argument-hint: "Optional: override version (e.g. 2.0.0) or leave blank for auto"
agent: agent
---

Prepare a new release for this project. The user said: $input

## Instructions

### 1. Determine the next version

Read [CHANGELOG.md](../../CHANGELOG.md) to find:
- The **current latest version** (the highest `## [x.y.z]` heading that is NOT `[Unreleased]`).
- The **[Unreleased]** section — the list of changes since the last release.

If the user provided a version number, validate it is higher than the current version and use it.

Otherwise, **auto-select** the next version using semantic versioning:

| If `[Unreleased]` contains… | Bump |
|---|---|
| A `### Removed` or `### Changed` section describing breaking/incompatible changes | **MAJOR** (e.g. 1.2.3 → 2.0.0) |
| A `### Added` section (new features, no breaking changes) | **MINOR** (e.g. 1.2.3 → 1.3.0) |
| Only `### Fixed`, `### Security`, or `### Deprecated` | **PATCH** (e.g. 1.2.3 → 1.2.4) |

Present your reasoning: list which sub-headings exist under `[Unreleased]` and explain why you chose MAJOR, MINOR, or PATCH.

### 2. Edit CHANGELOG.md

- Rename `## [Unreleased]` to `## [Unreleased]` (keep it) and insert a new version section **below** it:
  ```
  ## [Unreleased]

  ## [x.y.z] — YYYY-MM-DD
  ```
- Move all content from under `[Unreleased]` into the new version section (leave `[Unreleased]` empty).
- Update the link references at the bottom of the file:
  - Add `[x.y.z]` comparing the previous tag to the new tag.
  - Update `[Unreleased]` to compare the new tag to `HEAD`.
  - If the links are inside an HTML comment (`<!-- -->`), uncomment them.
- Use today's date for `YYYY-MM-DD`.

### 3. Edit CITATION.cff

Read [CITATION.cff](../../CITATION.cff) and update:
- `version:` → the new version string (without `v` prefix)
- `date-released:` → today's date (`YYYY-MM-DD`)

### 4. Draft release title and notes

Compose a short **release title** (one line, human-friendly) summarizing the release theme.

Compose **release notes** by summarizing the CHANGELOG entries in a user-friendly way — group related items, add context where helpful, keep it concise.

### 5. Present the result

Show the user:

1. **Version selected:** `vX.Y.Z` with reasoning
2. **Files edited:** list of changes made to CHANGELOG.md and CITATION.cff
3. **Suggested release title:** the one-liner
4. **Release notes preview:** the formatted notes

Then tell the user:

> **Next steps (you do these manually):**
> 1. Review the changes above
> 2. Commit: `git commit -am "chore: release vX.Y.Z"`
> 3. Push: `git push`
> 4. Go to **Actions → Release → Run workflow** → enter `X.Y.Z` → click **Run**
>
> The workflow will create the git tag, extract notes from CHANGELOG.md, and publish the GitHub Release automatically.

### Rules

- **Never** run git commands, push to remote, or trigger workflows. Only edit local files.
- **Never** modify files other than CHANGELOG.md and CITATION.cff.
- If `[Unreleased]` is empty, tell the user there's nothing to release and stop.
- If the CHANGELOG format doesn't match Keep a Changelog, warn the user and do your best.
