# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main`  | ✅ Current |

## Reporting a Vulnerability

**Please do not open a public GitHub Issue for security vulnerabilities.**

If you discover a security issue, email the maintainers directly or use [GitHub's private vulnerability reporting](../../security/advisories/new) feature.

Include as much detail as possible:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We aim to respond within **5 business days** and to publish a fix within **30 days** of confirmation.

## Credential & Token Safety

This tool reads a `GITHUB_TOKEN` from environment variables only. It **never** logs, stores, or transmits tokens.

- Never commit your `.env` file — it is git-ignored by default.
- Use a minimal-scope PAT (`read:org` + `repo` read-only).
- Rotate your token immediately if you believe it was exposed.

## Dependency Security

Dependencies are tracked via `requirements.txt` and monitored by Dependabot. Keep dependencies up to date by running:

```bash
pip install --upgrade -r requirements.txt
```
