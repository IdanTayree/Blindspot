#!/usr/bin/env python3
"""Fetch real metadata for GitHub repositories, so a recommendation can cite facts rather than memory.

A model asked for "highly starred repos" will produce plausible names with plausible star counts. The names
are usually real; the numbers are recalled and often wrong or years stale. This script exists so the harvest
phase never has to guess: everything it prints came from the API just now, and anything it could not fetch is
marked `verified: false` rather than quietly filled in.

Usage:
    python3 verify_repos.py --strict owner/repo [owner/repo ...] > verified.json
    python3 verify_repos.py --file repos.txt          # one owner/repo per line, # comments allowed

Auth: uses the `gh` CLI when it is installed and logged in, which raises the rate limit from 60 requests an
hour to 5000 and works with private repos the user can see. Falls back to the unauthenticated public API,
which is fine for a few dozen lookups.

Only the standard library is used, and Python 3.10+ is recommended.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

API = "https://api.github.com/repos/"

#: owner/repo, tolerating a full URL, a trailing .git, or surrounding whitespace.
_SLUG = re.compile(r"(?:https://github\.com/|github\.com/|git@github\.com:)?([A-Za-z0-9][A-Za-z0-9_.-]*)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$")


def slug(raw: str) -> str | None:
    """Accept only a GitHub URL or a complete owner/repo, never an arbitrary URL suffix."""
    if not isinstance(raw, str):
        return None
    match = _SLUG.fullmatch(raw.strip())
    if not match or match[2] in (".", ".."):
        return None
    return f"{match[1]}/{match[2]}"


def _via_gh(path: str) -> dict | None:
    """The `gh` CLI, when present — it carries the user's auth and the higher rate limit."""
    if not shutil.which("gh"):
        return None
    try:
        out = subprocess.run(["gh", "api", "--hostname", "github.com", path], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except ValueError:
        return None


def _via_http(path: str) -> tuple[dict | None, str]:
    """The public API. Returns (payload, note) so a rate limit is reported rather than looking like a 404."""
    request = urllib.request.Request(
        API.rstrip("/").replace("/repos", "") + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "blindspot"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8")), ""
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return None, "rate limited (install and log in to `gh` for a higher limit)"
        if e.code == 404:
            return None, "not found — renamed, deleted, or private"
        return None, f"HTTP {e.code}"
    except (urllib.error.URLError, ValueError, OSError) as e:
        return None, f"unreachable: {e}"


def _age_days(pushed_at: str | None) -> int | None:
    if not isinstance(pushed_at, str) or not pushed_at:
        return None
    try:
        when = datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - when).days


def freshness(days: int | None) -> str:
    """A badge derived from a real date, so the dashboard never has to characterise activity by feel."""
    if days is None:
        return "unknown"
    if days <= 90:
        return "active"
    if days <= 365:
        return "maintained"
    return "stale"


def verify(name: str) -> dict:
    repo = slug(name)
    if not repo:
        return {"input": name, "verified": False, "note": "not an owner/repo reference"}

    path = f"/repos/{repo}"
    data = _via_gh(path)
    note = ""
    if data is None:
        data, note = _via_http(path)
    if not isinstance(data, dict) or not isinstance(data.get("full_name"), str) or not slug(data["full_name"]) or any(
            type(data.get(key)) is not int or data[key] < 0
            for key in ("stargazers_count", "forks_count", "open_issues_count")) or not isinstance(data.get("archived"), bool):
        return {"input": name, "repo": repo, "verified": False,
                "note": note or "lookup failed or malformed repository metadata"}

    days = _age_days(data.get("pushed_at"))
    licence_data = data.get("license")
    licence = licence_data.get("spdx_id") if isinstance(licence_data, dict) else None
    return {
        "input": name,
        "repo": data.get("full_name", repo),
        "verified": True,
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "open_issues": data.get("open_issues_count"),
        "pushed_at": data.get("pushed_at") if isinstance(data.get("pushed_at"), str) else None,
        "days_since_push": days,
        "freshness": freshness(days),
        # NOASSERTION means a licence file exists that GitHub could not identify — not the same as none,
        # and worth surfacing differently because it needs a human to read it.
        "license": None if licence in (None, "NOASSERTION") else licence,
        "license_note": "present but unrecognised — read it" if licence == "NOASSERTION" else None,
        "language": data.get("language"),
        "archived": bool(data.get("archived")),
        "description": data.get("description"),
        "html_url": "https://github.com/" + data["full_name"],
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Fetch GitHub metadata, not a security assessment.")
    parser.add_argument("repos", nargs="*")
    parser.add_argument("--file", "-f", help="one repository per line")
    parser.add_argument("--strict", action="store_true", help="exit 1 if any lookup is unverified")
    args = parser.parse_args(argv[1:])
    if args.file and args.repos:
        parser.error("use repository arguments OR --file")
    try:
        if args.file:
            with open(args.file, encoding="utf-8") as source:
                names = [ln.split("#", 1)[0].strip() for ln in source]
        else:
            names = args.repos
    except OSError as exc:
        parser.error(str(exc))
    names = [n for n in names if n]
    if not names:
        parser.error("provide at least one repository")

    results = [verify(n) for n in names]
    json.dump(results, sys.stdout, indent=2)
    sys.stdout.write("\n")

    failed = [r for r in results if not r.get("verified")]
    if failed:
        print(f"\n{len(failed)} of {len(results)} could not be verified — report these as unverified, "
              f"do not fill them in from memory:", file=sys.stderr)
        for r in failed:
            print(f"  {r.get('input')}: {r.get('note')}", file=sys.stderr)
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
