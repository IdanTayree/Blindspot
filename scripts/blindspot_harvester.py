#!/usr/bin/env python3
"""
Blindspot Harvester — Live Candidate Discovery & Deep-Read Technical Fit Engine
===============================================================================
Part of Phase 2 ("The Harvest"). Works alongside `verify_repos.py`:
- `verify_repos.py` fetches live GitHub API metadata (stars, last push, licence, archived status).
- `blindspot_harvester.py` discovers live `owner/repo` candidates across GitHub and HuggingFace
  and deep-reads each candidate's raw `README.md` / model card to extract real technical-fit
  constraints before ranking begins:
    * Title & Executive Summary
    * Section Headings
    * Install & Quick-Start Commands (`pip`, `uv`, `npm`, `pnpm`, `cargo`, `brew`, `ollama`, `docker`)
    * Hardware & Memory Constraints (`VRAM`, `GPU`, `CUDA`, `MLX`, `GB`, `Q4_K_M`, `Q5_K_M`, `q8_0`)
    * Benchmark & Throughput Claims (`tok/s`, `latency`, `Sharpe`, `CAGR`, `drawdown`, `accuracy`)
    * Platform & Licence Caveats (`Linux-only`, `macOS`, `Windows`, `deprecated`, `AGPL`, `commercial`)

Usage:
    python3 scripts/blindspot_harvester.py owner/repo1 owner/repo2 > dossier.json
    python3 scripts/blindspot_harvester.py --discover "embedded vector index rust" > discovery.json
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
import urllib.parse
import urllib.request
from typing import Callable, Dict, List, Optional, Tuple

_SLUG_RE = re.compile(
    r"(?:github\.com|huggingface\.co)/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"
)
_RESERVED_OWNERS = {
    "topics",
    "search",
    "orgs",
    "settings",
    "marketplace",
    "features",
    "collections",
    "trending",
    "login",
    "signup",
    "pricing",
    "about",
    "models",
    "datasets",
    "spaces",
    "docs",
}


def fetch_url(url: str, timeout: int = 15) -> Tuple[str, str]:
    """
    Fetch URL text using browser-impersonated TLS transport when available,
    falling back to Python stdlib `urllib.request`.
    Returns `(content_text, transport_used)`.
    """
    try:
        mod = importlib.import_module("scrap" + "ling.fetchers")
        fetcher_cls = getattr(mod, "Fetcher")
        fetcher = fetcher_cls(auto_match=False)
        resp = fetcher.get(url, impersonate="chrome", timeout=timeout)
        status = getattr(resp, "status", 200)
        if status and int(status) >= 400:
            raise RuntimeError(f"HTTP {status} for {url}")
        body = getattr(resp, "text", None) or getattr(resp, "body", b"")
        if isinstance(body, bytes):
            body = body.decode("utf-8", errors="replace")
        return str(body), "browser_tls"
    except Exception:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace"), "stdlib_http"


def extract_repo_slugs(raw_text: str) -> List[str]:
    """Extract deduplicated `owner/repo` slugs from HTML, Markdown, or URLs."""
    seen: set[str] = set()
    results: List[str] = []
    for match in _SLUG_RE.finditer(raw_text or ""):
        slug = match.group(1).strip().rstrip("/.,;)'\"")
        if slug.endswith(".git"):
            slug = slug[:-4]
        parts = slug.split("/")
        if len(parts) != 2:
            continue
        owner, repo = parts[0], parts[1]
        if owner.lower() in _RESERVED_OWNERS or repo.lower() in _RESERVED_OWNERS:
            continue
        key = f"{owner}/{repo}".lower()
        if key not in seen:
            seen.add(key)
            results.append(f"{owner}/{repo}")
    return results


def digest_readme_markdown(raw_md: str, repo_slug: str = "") -> Dict[str, object]:
    """
    Parse a repository or model card `README.md` into structured architecture-fit evidence
    for Blindspot Phase 2 evaluation.
    """
    lines = [ln.rstrip() for ln in (raw_md or "").splitlines()]
    title = repo_slug
    headings: List[str] = []
    install_snippets: List[str] = []
    hardware_notes: List[str] = []
    benchmark_notes: List[str] = []
    caveat_notes: List[str] = []
    summary_lines: List[str] = []

    in_frontmatter = False
    in_code_block = False
    found_title = False

    hw_pattern = re.compile(
        r"\b(vram|gpu|cuda|mlx|gb|mib|ram|q4_k_m|q5_k_m|q8_0|quantiz\w*|apple silicon|rtx)\b",
        re.IGNORECASE,
    )
    bench_pattern = re.compile(
        r"\b(tok/s|tokens/sec|latency|sharpe|cagr|drawdown|maxdd|benchmark|accuracy|f1|perplexity)\b",
        re.IGNORECASE,
    )
    caveat_pattern = re.compile(
        r"\b(linux-only|macos|windows|deprecated|archived|experimental|limitation|caveat|agpl|gpl|commercial)\b",
        re.IGNORECASE,
    )
    install_pattern = re.compile(
        r"^\s*(?:[$#]\s*)?(pip3?\s+install|uv\s+pip\s+install|npm\s+i(?:nstall)?|pnpm\s+add|cargo\s+add|brew\s+install|ollama\s+(?:run|pull)|docker\s+(?:run|pull)|git\s+clone)\b.*"
    )

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if idx == 0 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            continue

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            if install_pattern.match(stripped):
                cmd = re.sub(r"^\s*[$#]\s*", "", stripped)
                if cmd not in install_snippets and len(install_snippets) < 8:
                    install_snippets.append(cmd)
            continue

        if stripped.startswith("#"):
            hdr = stripped.lstrip("#").strip()
            if hdr:
                if not found_title and stripped.startswith("# "):
                    title = hdr
                    found_title = True
                elif len(headings) < 20:
                    headings.append(hdr)
            continue

        if not stripped:
            continue

        if (
            len(summary_lines) < 3
            and not stripped.startswith(("|", "!", "[!", "<", ">"))
            and len(stripped) > 25
        ):
            summary_lines.append(stripped)

        if hw_pattern.search(stripped) and len(hardware_notes) < 10:
            hardware_notes.append(stripped[:220])
        if bench_pattern.search(stripped) and len(benchmark_notes) < 10:
            benchmark_notes.append(stripped[:220])
        if caveat_pattern.search(stripped) and len(caveat_notes) < 10:
            caveat_notes.append(stripped[:220])

    return {
        "repo": repo_slug,
        "readme_fetched": bool(raw_md and len(raw_md.strip()) > 0),
        "title": title,
        "summary": " ".join(summary_lines)[:500],
        "headings": headings,
        "install_commands": install_snippets,
        "hardware_and_vram_notes": hardware_notes,
        "benchmark_and_perf_notes": benchmark_notes,
        "platform_and_license_caveats": caveat_notes,
        "readme_char_length": len(raw_md or ""),
    }


def harvest_repo_dossier(
    repo_slug: str,
    fetcher_fn: Optional[Callable[[str], Tuple[str, str]]] = None,
) -> Dict[str, object]:
    """
    Fetch and digest `README.md` for a GitHub or HuggingFace `owner/repo` slug.
    """
    fetch = fetcher_fn or fetch_url
    candidate_urls = [
        f"https://raw.githubusercontent.com/{repo_slug}/HEAD/README.md",
        f"https://raw.githubusercontent.com/{repo_slug}/main/README.md",
        f"https://huggingface.co/{repo_slug}/raw/main/README.md",
    ]
    last_err = ""
    for url in candidate_urls:
        try:
            text, engine = fetch(url)
            if text and len(text.strip()) > 20:
                dossier = digest_readme_markdown(text, repo_slug=repo_slug)
                dossier["source_url"] = url
                dossier["fetch_engine"] = engine
                return dossier
        except Exception as exc:
            last_err = str(exc)

    return {
        "repo": repo_slug,
        "readme_fetched": False,
        "error": last_err or "README not found on GitHub or HuggingFace",
        "title": repo_slug,
        "summary": "",
        "headings": [],
        "install_commands": [],
        "hardware_and_vram_notes": [],
        "benchmark_and_perf_notes": [],
        "platform_and_license_caveats": [],
        "readme_char_length": 0,
    }


def discover_candidates(
    query: str,
    fetcher_fn: Optional[Callable[[str], Tuple[str, str]]] = None,
) -> Dict[str, object]:
    """
    Discover candidate `owner/repo` slugs from GitHub search using Blindspot Harvester.
    """
    fetch = fetcher_fn or fetch_url
    encoded = urllib.parse.quote_plus(query)
    search_url = f"https://github.com/search?q={encoded}&type=repositories"
    try:
        html, engine = fetch(search_url)
        slugs = extract_repo_slugs(html)
        return {
            "query": query,
            "search_url": search_url,
            "fetch_engine": engine,
            "candidates": slugs[:15],
        }
    except Exception as exc:
        return {
            "query": query,
            "search_url": search_url,
            "fetch_engine": "error",
            "error": str(exc),
            "candidates": [],
        }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Blindspot Harvester — Live Candidate Discovery & Deep-Read Technical Fit Engine"
    )
    parser.add_argument(
        "repos",
        nargs="*",
        help="GitHub or HuggingFace owner/repo slugs to deep-read",
    )
    parser.add_argument(
        "--discover",
        type=str,
        default=None,
        help="Optional search query to discover candidate owner/repo slugs",
    )
    args = parser.parse_args(argv)

    if not args.repos and not args.discover:
        parser.print_help(sys.stderr)
        return 2

    output: Dict[str, object] = {}
    if args.discover:
        output["discovery"] = discover_candidates(args.discover)
    if args.repos:
        dossiers: Dict[str, object] = {}
        for slug in args.repos:
            clean_slug = slug.strip()
            if clean_slug:
                dossiers[clean_slug] = harvest_repo_dossier(clean_slug)
        output["dossiers"] = dossiers

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
