#!/usr/bin/env python3
"""
GitHub Organization Repository Audit
Audits repositories in a GitHub org for best practices and metadata.

Usage:
    python audit/audit.py                                # all repos in default org
    python audit/audit.py govex                          # all repos in govex
    python audit/audit.py govex --repos gepi-ui          # one repo
    python audit/audit.py govex --repos gepi-ui gepi-api # two repos
"""

import argparse
import os
import sys
import base64
import time
import datetime
import hashlib
import re
import requests
from tabulate import tabulate
from dotenv import load_dotenv
from to_excel import write_xlsx

# Load .env from repo root (one level above audit/)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

# ── CLI args ──────────────────────────────────────────────────────────────────────────────
_parser = argparse.ArgumentParser(description="Audit GitHub org repositories.")
_parser.add_argument("org", nargs="?", default=None, help="GitHub org to audit (default: GITHUB_ORG env var)")
_parser.add_argument("--repos", nargs="+", metavar="REPO",
                     help="Audit only these repo names (case-insensitive). Omit to audit all repos.")
_args = _parser.parse_args()

# ── Config ──────────────────────────────────────────────────────────────────────────────
ORG = _args.org or os.environ.get("GITHUB_ORG", "govex")
REPO_FILTER = {r.lower() for r in _args.repos} if _args.repos else None
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

BASE = "https://api.github.com"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# ── Helpers ───────────────────────────────────────────────────────────────────


def gh(path, params=None, _full_url=None):
    url = _full_url or f"{BASE}{path}"
    for attempt in range(5):
        r = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if r.status_code in (401, 403, 404, 409, 204):
            return None
        if not r.content:
            return None
        if r.status_code == 429:
            retry_after = int(r.headers.get("Retry-After", 10))
            print(f"  [rate-limited] sleeping {retry_after}s ...", file=sys.stderr)
            time.sleep(retry_after)
            continue
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return None
    return None


def gh_paginated(path, retry_202=False):
    url = f"{BASE}{path}"
    results = []
    while url:
        for attempt in range(5):
            r = requests.get(url, headers=HEADERS, params={"per_page": 100}, timeout=30)
            if r.status_code in (401, 403, 404):
                return results
            if r.status_code == 204 or not r.content:
                return results
            if r.status_code == 202 and retry_202:
                time.sleep(3)
                continue
            if r.status_code == 202:
                return results
            if r.status_code == 429:
                retry_after = int(r.headers.get("Retry-After", 10))
                print(f"  [rate-limited] sleeping {retry_after}s ...", file=sys.stderr)
                time.sleep(retry_after)
                continue
            r.raise_for_status()
            try:
                data = r.json()
            except Exception:
                return results
            if not isinstance(data, list):
                return results
            results.extend(data)
            url = r.links.get("next", {}).get("url")
            break
        else:
            break
    return results


def file_content(owner, repo, path):
    """Return (exists: bool, content: str|None, size: int)"""
    data = gh(f"/repos/{owner}/{repo}/contents/{path}")
    if not data:
        return False, None, 0
    if isinstance(data, list):          # it's a directory listing
        return True, None, 0
    raw = data.get("content", "")
    size = data.get("size", 0)
    try:
        decoded = base64.b64decode(raw).decode("utf-8", errors="replace")
    except Exception:
        decoded = ""
    return True, decoded, size


def file_exists(owner, repo, path):
    exists, _, _ = file_content(owner, repo, path)
    return exists


def count_lines(text):
    if not text:
        return 0
    return len(text.splitlines())


def meaningful_readme(content, char_count):
    """
    Heuristic: placeholder if very short OR mostly boilerplate.
    Returns (is_placeholder: bool, reason: str)
    """
    if char_count < 200:
        return True, "very short (<200 chars)"
    if content:
        lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
        non_heading = [ln for ln in lines if not ln.startswith("#")]
        if len(non_heading) < 3:
            return True, "headings-only content"
    return False, "ok"


def extract_license_spdx(owner, repo):
    data = gh(f"/repos/{owner}/{repo}/license")
    if not data:
        return None, None
    lic = data.get("license") or {}
    return lic.get("spdx_id"), lic.get("name")


def get_branch_protection(owner, repo, branch):
    data = gh(f"/repos/{owner}/{repo}/branches/{branch}/protection")
    if not data:
        return {}
    return data


def get_topics(owner, repo):
    data = gh(f"/repos/{owner}/{repo}/topics",
              params={"per_page": 100})
    if not data:
        return []
    return data.get("names", [])


def get_last_contributor(owner, repo):
    """Last person to push a commit."""
    commits = gh(f"/repos/{owner}/{repo}/commits", params={"per_page": 1})
    if not commits:
        return None, None
    c = commits[0]
    author = c.get("author") or {}
    login = author.get("login", "")
    commit_meta = c.get("commit") or {}
    committer_meta = commit_meta.get("committer") or {}
    date = committer_meta.get("date", "")
    return login or commit_meta.get("author", {}).get("name", "?"), date


def get_contributors(owner, repo):
    data = gh_paginated(f"/repos/{owner}/{repo}/contributors", retry_202=True)
    return [(c.get("login"), c.get("contributions")) for c in (data or []) if isinstance(c, dict)]


def get_codeowners(owner, repo):
    """Check for CODEOWNERS in root, docs/, or .github/"""
    for path in ["CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"]:
        exists, content, _ = file_content(owner, repo, path)
        if exists:
            return True, path, content
    return False, None, None


def get_citation(owner, repo):
    exists, content, size = file_content(owner, repo, "CITATION.cff")
    if exists:
        return True, "CITATION.cff", size
    # also check citation.bib
    exists2, content2, size2 = file_content(owner, repo, "CITATION.bib")
    if exists2:
        return True, "CITATION.bib", size2
    return False, None, 0


def get_contributing(owner, repo):
    for path in ["CONTRIBUTING.md", "CONTRIBUTING.rst", "CONTRIBUTING.txt",
                 ".github/CONTRIBUTING.md"]:
        exists, content, size = file_content(owner, repo, path)
        if exists:
            return True, path, size
    return False, None, 0


def get_security_policy(owner, repo):
    for path in ["SECURITY.md", ".github/SECURITY.md"]:
        exists, _, size = file_content(owner, repo, path)
        if exists:
            return True, path, size
    return False, None, 0


def get_issue_templates(owner, repo):
    # GitHub issue templates can live in .github/ISSUE_TEMPLATE/
    data = gh(f"/repos/{owner}/{repo}/contents/.github/ISSUE_TEMPLATE")
    if data and isinstance(data, list):
        return [f["name"] for f in data]
    # single file
    if file_exists(owner, repo, ".github/ISSUE_TEMPLATE.md"):
        return [".github/ISSUE_TEMPLATE.md"]
    return []


def get_pr_template(owner, repo):
    for path in [".github/PULL_REQUEST_TEMPLATE.md",
                 "PULL_REQUEST_TEMPLATE.md",
                 "docs/PULL_REQUEST_TEMPLATE.md"]:
        if file_exists(owner, repo, path):
            return True, path
    return False, None


def get_workflows(owner, repo):
    data = gh(f"/repos/{owner}/{repo}/contents/.github/workflows")
    if data and isinstance(data, list):
        return [f["name"] for f in data if f.get("type") == "file"]
    return []


def get_default_branch_protection_summary(protection):
    if not protection:
        return "none"
    parts = []
    rr = protection.get("required_pull_request_reviews") or {}
    if rr:
        approvals = rr.get("required_approving_review_count", 0)
        parts.append(f"PR-reviews({approvals})")
        if rr.get("dismiss_stale_reviews"):
            parts.append("dismiss-stale")
        if rr.get("require_code_owner_reviews"):
            parts.append("codeowner-review")
    rsc = protection.get("required_status_checks") or {}
    if rsc:
        checks = rsc.get("contexts") or []
        parts.append(f"status-checks({len(checks)})")
    if protection.get("enforce_admins", {}).get("enabled"):
        parts.append("enforce-admins")
    if protection.get("restrictions"):
        parts.append("push-restrictions")
    require_linear = protection.get("required_linear_history", {})
    if isinstance(require_linear, dict) and require_linear.get("enabled"):
        parts.append("linear-history")
    return ", ".join(parts) if parts else "enabled(no details)"


def get_rulesets(owner, repo, default_branch):
    """Return list of active rulesets targeting the default branch."""
    data = gh(f"/repos/{owner}/{repo}/rulesets", params={"per_page": 100})
    if not data or not isinstance(data, list):
        return []
    active = []
    for rs in data:
        if rs.get("enforcement") != "active":
            continue
        conditions = rs.get("conditions") or {}
        ref_cond = conditions.get("ref_name") or {}
        include_patterns = ref_cond.get("include", [])
        # No include patterns means applies to all refs; ~DEFAULT_BRANCH and explicit ref also match
        targets_default = (
            not include_patterns
            or "~ALL" in include_patterns
            or "~DEFAULT_BRANCH" in include_patterns
            or f"refs/heads/{default_branch}" in include_patterns
        )
        if targets_default:
            active.append(rs)
    return active


def get_rulesets_summary(rulesets):
    """Convert a list of active rulesets into a human-readable summary string."""
    if not rulesets:
        return "none"
    summaries = []
    for rs in rulesets:
        name = rs.get("name", "unnamed")
        rules = rs.get("rules") or []
        rule_types = {r.get("type") for r in rules if r.get("type")}
        parts = []
        if "pull_request" in rule_types:
            for r in rules:
                if r.get("type") == "pull_request":
                    cnt = (r.get("parameters") or {}).get("required_approving_review_count", 1)
                    parts.append(f"require-PR({cnt})")
                    break
        if "required_status_checks" in rule_types:
            parts.append("status-checks")
        if "deletion" in rule_types:
            parts.append("restrict-deletions")
        if "non_fast_forward" in rule_types:
            parts.append("block-force-push")
        if "required_linear_history" in rule_types:
            parts.append("linear-history")
        if "required_signatures" in rule_types:
            parts.append("signed-commits")
        known = {"pull_request", "required_status_checks", "deletion",
                 "non_fast_forward", "required_linear_history", "required_signatures"}
        parts.extend(sorted(rule_types - known))
        desc = ", ".join(parts) if parts else "active"
        summaries.append(f"{name}: {desc}")
    return "; ".join(summaries)


def get_dependabot(owner, repo):
    data = gh(f"/repos/{owner}/{repo}/contents/.github/dependabot.yml")
    if data:
        return True
    return False


def get_vulnerability_alerts(owner, repo):
    r = requests.get(
        f"{BASE}/repos/{owner}/{repo}/vulnerability-alerts",
        headers={**HEADERS, "Accept": "application/vnd.github+json"},
        timeout=30,
    )
    return r.status_code == 204  # 204 = enabled, 404 = disabled


def get_org_owners(org):
    members = gh_paginated(f"/orgs/{org}/members?role=owner")
    return [m.get("login") for m in members]


def bool_icon(v):
    return "✓" if v else "✗"


# ── Main audit ────────────────────────────────────────────────────────────────

def audit_repo(repo_data):
    owner = repo_data["owner"]["login"]
    name = repo_data["name"]
    full = repo_data["full_name"]
    print(f"  Auditing {full} ...", file=sys.stderr)

    default_branch = repo_data.get("default_branch", "main")

    # README
    readme_exists, readme_content, readme_size = file_content(owner, name, "README.md")
    if not readme_exists:
        readme_exists, readme_content, readme_size = file_content(owner, name, "README.rst")
    readme_lines = count_lines(readme_content) if readme_content else 0
    readme_placeholder, readme_reason = meaningful_readme(readme_content, readme_size)

    # License
    license_spdx, license_name = extract_license_spdx(owner, name)

    # Citation
    citation_exists, citation_path, citation_size = get_citation(owner, name)

    # Contributing
    contributing_exists, contributing_path, contributing_size = get_contributing(owner, name)

    # Security policy
    security_exists, security_path, security_size = get_security_policy(owner, name)

    # Topics / tags
    topics = get_topics(owner, name)

    # Contributors
    contributors = get_contributors(owner, name)
    top_contributors = contributors[:5] if contributors else []

    # Last contributor
    last_login, last_date = get_last_contributor(owner, name)
    if last_date:
        try:
            dt = datetime.datetime.fromisoformat(last_date.replace("Z", "+00:00"))
            days_ago = (datetime.datetime.now(datetime.timezone.utc) - dt).days
            last_date_str = f"{dt.strftime('%Y-%m-%d')} ({days_ago}d ago)"
        except Exception:
            last_date_str = last_date
    else:
        last_date_str = "unknown"

    # CODEOWNERS
    codeowners_exists, codeowners_path, codeowners_content = get_codeowners(owner, name)

    # Branch protection (classic API)
    protection = get_branch_protection(owner, name, default_branch)
    protection_summary = get_default_branch_protection_summary(protection)

    # Rulesets (modern GitHub branch rules)
    rulesets = get_rulesets(owner, name, default_branch)
    rulesets_summary = get_rulesets_summary(rulesets)
    has_rulesets = bool(rulesets)

    # CI/CD workflows
    workflows = get_workflows(owner, name)

    # PR template
    pr_template_exists, pr_template_path = get_pr_template(owner, name)

    # Issue templates
    issue_templates = get_issue_templates(owner, name)

    # Dependabot
    dependabot = get_dependabot(owner, name)

    # Vulnerability alerts
    vuln_alerts = get_vulnerability_alerts(owner, name)

    # Stale check (no commits in 180 days)
    pushed_at = repo_data.get("pushed_at", "")
    try:
        pushed_dt = datetime.datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        days_since_push = (datetime.datetime.now(datetime.timezone.utc) - pushed_dt).days
        stale = days_since_push > 180
    except Exception:
        days_since_push = "?"
        stale = False

    # Naming convention: lowercase-kebab-case
    kebab_ok = bool(re.match(r'^[a-z0-9][a-z0-9\-\.]*$', name))

    return {
        "name": name,
        "visibility": "private" if repo_data.get("private") else "public",
        "archived": repo_data.get("archived", False),
        "fork": repo_data.get("fork", False),
        "default_branch": default_branch,
        "language": repo_data.get("language") or "—",
        "stars": repo_data.get("stargazers_count", 0),
        "forks": repo_data.get("forks_count", 0),
        "open_issues": repo_data.get("open_issues_count", 0),
        "last_push_days": days_since_push,
        "stale": stale,
        # Readme
        "readme_exists": readme_exists,
        "readme_chars": readme_size,
        "readme_lines": readme_lines,
        "readme_placeholder": readme_placeholder,
        "readme_placeholder_reason": readme_reason,
        # License
        "license_spdx": license_spdx or "NONE",
        "license_name": license_name or "—",
        # Citation
        "citation_exists": citation_exists,
        "citation_path": citation_path or "—",
        "citation_size": citation_size,
        # Contributing
        "contributing_exists": contributing_exists,
        "contributing_path": contributing_path or "—",
        # Security
        "security_policy": security_exists,
        "security_path": security_path or "—",
        # Topics
        "topics": ", ".join(topics) if topics else "—",
        "topic_count": len(topics),
        # Contributors
        "contributor_count": len(contributors),
        "top_contributors": top_contributors,
        # Last commit
        "last_contributor": last_login or "?",
        "last_commit_date": last_date_str,
        # CODEOWNERS
        "codeowners": codeowners_exists,
        "codeowners_path": codeowners_path or "—",
        # Branch protection
        "branch_protection": protection_summary,
        # Rulesets
        "rulesets_summary": rulesets_summary,
        "has_rulesets": has_rulesets,
        "has_any_protection": protection_summary not in ("none", "") or has_rulesets,
        # CI/CD
        "workflow_count": len(workflows),
        "workflows": ", ".join(workflows) if workflows else "—",
        # Templates
        "pr_template": pr_template_exists,
        "pr_template_path": pr_template_path or "—",
        "issue_templates": len(issue_templates),
        "issue_template_names": ", ".join(issue_templates) if issue_templates else "—",
        # Security tooling
        "dependabot": dependabot,
        "vuln_alerts": vuln_alerts,
        # Naming
        "kebab_case_name": kebab_ok,
        # Description
        "has_description": bool(repo_data.get("description")),
        "description": (repo_data.get("description") or "")[:80],
        # Homepage
        "has_homepage": bool(repo_data.get("homepage")),
    }


def print_section(title, rows, headers):
    print(f"\n{'═'*100}")
    print(f"  {title}")
    print('═'*100)
    print(tabulate(rows, headers=headers, tablefmt="github"))


def _build_output_path(org, repo_filter):
    """Build a timestamped, scope-scoped output path. Always unique — never overwrites."""
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    safe_org = re.sub(r"[^a-z0-9-]", "-", org.lower())
    if not repo_filter:
        base = f"audit_org_{safe_org}_{ts}"
    elif len(repo_filter) == 1:
        safe_repo = re.sub(r"[^a-z0-9-]", "-", next(iter(repo_filter)).lower())
        base = f"audit_repo_{safe_repo}_{ts}"
    else:
        slug = "_".join(re.sub(r"[^a-z0-9-]", "-", n.lower()) for n in sorted(repo_filter))
        candidate = f"audit_repos_{slug}_{ts}"
        if len(candidate) > 200:
            h = hashlib.sha1("_".join(sorted(repo_filter)).encode()).hexdigest()[:8]
            base = f"audit_repos_{h}_{ts}"
        else:
            base = candidate
    path = os.path.join(OUTPUT_DIR, f"{base}.xlsx")
    counter = 1
    while os.path.exists(path):
        path = os.path.join(OUTPUT_DIR, f"{base}_{counter}.xlsx")
        counter += 1
    return path


def main():
    print(f"\n{'═'*100}")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    scope = f"repos: {', '.join(sorted(REPO_FILTER))}" if REPO_FILTER else "all repos"
    print(f"  GitHub Org Audit: {ORG}   |   {scope}   |   {ts}")
    print('═'*100)

    if not TOKEN:
        print("\n  ⚠  GITHUB_TOKEN not set — using unauthenticated requests (60 req/hr limit, some data masked)\n",
              file=sys.stderr)

    # Org info
    org_data = gh(f"/orgs/{ORG}")
    if org_data:
        print(f"\nOrg:         {org_data.get('name') or ORG}")
        print(f"Description: {org_data.get('description') or '—'}")
        print(f"Email:       {org_data.get('email') or '—'}")
        print(f"Blog:        {org_data.get('blog') or '—'}")
        print(f"Location:    {org_data.get('location') or '—'}")
        pub = org_data.get('public_repos', '?')
        priv = org_data.get('total_private_repos', '(auth required)')
        print(f"Public repos:{pub}  | Private repos: {priv}")
        members_url = org_data.get('public_members_url', '').replace('{/member}', '')
        print(f"Members:     {members_url}")

    # Org owners (requires auth + owner membership)
    owners = get_org_owners(ORG)
    print(f"\nOrg Owners ({len(owners)}): {', '.join(owners) if owners else '(requires org-member auth)'}")

    # Fetch all repos, then optionally filter to requested names
    print("\nFetching repository list...", file=sys.stderr)
    repos = gh_paginated(f"/orgs/{ORG}/repos")
    if not repos:
        print("No repos found or insufficient permissions.")
        return

    if REPO_FILTER:
        found = {r["name"].lower() for r in repos}
        missing = REPO_FILTER - found
        for m in sorted(missing):
            print(f"  ⚠  Repo '{m}' not found in {ORG} — skipping.", file=sys.stderr)
        repos = [r for r in repos if r["name"].lower() in REPO_FILTER]
        if not repos:
            print("No matching repositories found. Check repo names and org.", file=sys.stderr)
            sys.exit(1)

    print(f"Auditing {len(repos)} repositor{'y' if len(repos) == 1 else 'ies'}...\n", file=sys.stderr)
    results = []
    for repo in sorted(repos, key=lambda r: r["name"].lower()):
        results.append(audit_repo(repo))

    # ── Table 1: Overview ───────────────────────────────────────────────────
    overview_rows = []
    for r in results:
        overview_rows.append([
            r["name"],
            r["visibility"],
            "✓" if r["archived"] else "—",
            "✓" if r["fork"] else "—",
            r["language"],
            r["description"][:60] + ("…" if len(r["description"]) > 60 else ""),
            bool_icon(r["has_description"]),
            r["stars"],
            r["open_issues"],
            r["last_push_days"],
            "STALE" if r["stale"] else "active",
            bool_icon(r["kebab_case_name"]),
        ])
    print_section("1. REPOSITORY OVERVIEW", overview_rows,
                  ["Repo", "Visibility", "Archived", "Fork", "Language", "Description (60)", "Desc?",
                   "Stars", "Issues", "Days Since Push", "Status", "Kebab-Name?"])

    # ── Table 2: Documentation ──────────────────────────────────────────────
    doc_rows = []
    for r in results:
        doc_rows.append([
            r["name"],
            bool_icon(r["readme_exists"]),
            r["readme_chars"],
            r["readme_lines"],
            "PLACEHOLDER" if r["readme_placeholder"] else "ok",
            r["readme_placeholder_reason"] if r["readme_placeholder"] else "—",
            bool_icon(r["citation_exists"]),
            r["citation_path"],
            bool_icon(r["contributing_exists"]),
            r["contributing_path"],
            bool_icon(r["security_policy"]),
            r["security_path"],
        ])
    print_section("2. DOCUMENTATION FILES (README / CITATION / CONTRIBUTING / SECURITY)", doc_rows,
                  ["Repo", "README?", "Chars", "Lines", "README Quality",
                   "README Reason", "CITATION?", "Citation File",
                   "CONTRIBUTING?", "Contrib File", "SECURITY?", "Security File"])

    # ── Table 3: License & Topics ───────────────────────────────────────────
    lic_rows = []
    for r in results:
        lic_rows.append([
            r["name"],
            r["license_spdx"],
            r["license_name"],
            r["topic_count"],
            r["topics"],
        ])
    print_section("3. LICENSE & TOPICS / TAGS", lic_rows,
                  ["Repo", "License SPDX", "License Name", "# Topics", "Topics"])

    # ── Table 4: Contributors ───────────────────────────────────────────────
    contrib_rows = []
    for r in results:
        top = "; ".join([f"{login}({cnt})" for login, cnt in r["top_contributors"]]) or "—"
        contrib_rows.append([
            r["name"],
            r["contributor_count"],
            r["last_contributor"],
            r["last_commit_date"],
            top,
        ])
    print_section("4. CONTRIBUTORS & LAST ACTIVITY", contrib_rows,
                  ["Repo", "# Contributors", "Last Committer", "Last Commit Date", "Top 5 Contributors (commits)"])

    # ── Table 5: Ownership & Governance ────────────────────────────────────
    gov_rows = []
    for r in results:
        gov_rows.append([
            r["name"],
            bool_icon(r["codeowners"]),
            r["codeowners_path"],
        ])
    print_section("5. CODE OWNERSHIP (CODEOWNERS)", gov_rows,
                  ["Repo", "CODEOWNERS?", "CODEOWNERS Path"])

    # ── Table 6: Branch Protection & Rulesets ────────────────────────────────
    bp_rows = []
    for r in results:
        bp_rows.append([
            r["name"],
            r["default_branch"],
            r["branch_protection"],
            r["rulesets_summary"],
            bool_icon(r["has_any_protection"]),
        ])
    print_section("6. BRANCH PROTECTION & RULESETS (default branch)", bp_rows,
                  ["Repo", "Default Branch", "Classic Protection", "Rulesets", "Any Protection?"])

    # ── Table 7: CI/CD & Automation ─────────────────────────────────────────
    ci_rows = []
    for r in results:
        ci_rows.append([
            r["name"],
            r["workflow_count"],
            r["workflows"][:80],
            bool_icon(r["pr_template"]),
            r["pr_template_path"],
            r["issue_templates"],
            r["issue_template_names"][:60],
            bool_icon(r["dependabot"]),
            bool_icon(r["vuln_alerts"]),
        ])
    print_section("7. CI/CD, TEMPLATES & SECURITY TOOLING", ci_rows,
                  ["Repo", "# Workflows", "Workflow Files",
                   "PR Template?", "PR Tmpl Path",
                   "# Issue Tmpls", "Issue Template Names",
                   "Dependabot?", "Vuln Alerts?"])

    # ── Summary scorecard ───────────────────────────────────────────────────
    total = len(results)
    def pct(n): return f"{n}/{total} ({100*n//total}%)" if total else "0"

    print(f"\n{'═'*100}")
    print("  SUMMARY SCORECARD")
    print('═'*100)
    checks = [
        ("Has README",            sum(1 for r in results if r["readme_exists"])),
        ("Non-placeholder README", sum(1 for r in results if r["readme_exists"] and not r["readme_placeholder"])),
        ("Has License",           sum(1 for r in results if r["license_spdx"] != "NONE")),
        ("Has CONTRIBUTING",      sum(1 for r in results if r["contributing_exists"])),
        ("Has SECURITY policy",   sum(1 for r in results if r["security_policy"])),
        ("Has CITATION",          sum(1 for r in results if r["citation_exists"])),
        ("Has Topics/Tags",       sum(1 for r in results if r["topic_count"] > 0)),
        ("Has Description",       sum(1 for r in results if r["has_description"])),
        ("Has CODEOWNERS",        sum(1 for r in results if r["codeowners"])),
        ("Branch Protection set", sum(1 for r in results if r["has_any_protection"])),
        ("Has CI Workflows",      sum(1 for r in results if r["workflow_count"] > 0)),
        ("Has PR Template",       sum(1 for r in results if r["pr_template"])),
        ("Has Issue Template(s)", sum(1 for r in results if r["issue_templates"] > 0)),
        ("Dependabot enabled",    sum(1 for r in results if r["dependabot"])),
        ("Vuln Alerts enabled",   sum(1 for r in results if r["vuln_alerts"])),
        ("Kebab-case name",       sum(1 for r in results if r["kebab_case_name"])),
        ("Is active (≤180d)",     sum(1 for r in results if not r["stale"])),
        ("Is public",             sum(1 for r in results if r["visibility"] == "public")),
        ("Is private",            sum(1 for r in results if r["visibility"] == "private")),
    ]
    for label, count in checks:
        bar_len = 30
        filled = int(bar_len * count / total) if total else 0
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  {label:<30} {bar}  {pct(count)}")

    # ── Excel output ────────────────────────────────────────────────────────
    for r in results:
        r["top_contributors"] = [list(t) for t in r["top_contributors"]]
    audited_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    xlsx_path = _build_output_path(ORG, REPO_FILTER)
    write_xlsx(results, owners, audited_at, xlsx_path)
    print(f"\n  Saved: {xlsx_path}")


if __name__ == "__main__":
    main()
