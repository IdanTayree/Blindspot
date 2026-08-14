#!/usr/bin/env python3
"""Render a component-harvest dashboard from a ranking spec plus verified GitHub metadata.

The split matters: **you write the judgement, this writes the facts.** The spec file holds the rankings and
the reasoning — which candidate sits where, why, and what would promote it — while every number on the page
comes from `verify_repos.py`, which fetched it. A dashboard whose star counts were recalled looks identical to
one whose star counts are real, which is exactly why the two have to come from different places.

Usage:
    python3 verify_repos.py owner/a owner/b ... > verified.json
    python3 build_dashboard.py harvest.json verified.json out.html [template.html]

The page's look lives in `assets/dashboard_template.html`, not in this file, so a dashboard comes out
consistent every run instead of being reinvented — and so it can be reskinned by editing HTML rather than
Python. Placeholders in it are $-style: $title $subtitle $target $components $ranked $excluded $checked
$chips $sections.

Spec format (`harvest.json`):

    {
      "title": "Project component harvest",
      "subtitle": "Ranked open-source candidates for each part.",
      "target_stack": "Rust · Tauri · Apple Silicon, local-first",
      "components": [
        {
          "id": "queue",
          "title": "Durable task queue",
          "job": "One queue across projects that survives a reboot.",
          "ranked": [
            {"repo": "owner/name",
             "why":     "the trade-off that puts it at this position",
             "promote": "the condition under which the user should switch to it",
             "fit":     "how it sits in the target stack"}
          ],
          "excluded": [{"name": "owner/name or a non-repo option", "why": "reason"}]
        }
      ]
    }

Rank at least three deep. A component with one survivor is a component with no fallback, and the whole point
of the list is that when the first choice hits a wall the second is already evaluated.

A `repo` the verifier could not confirm still renders — labelled `unverified`, with no invented numbers. A
repo that has been renamed shows the slug it moved from, because a stale slug in someone's notes is how a
dead reference survives for years.

Standard library only.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from string import Template


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def index(verified: list) -> dict:
    """Look-up by canonical name *and* by the slug asked for, so renames resolve either way."""
    out = {}
    for row in verified:
        if row.get("verified"):
            out.setdefault(row["repo"].lower(), row)
            out.setdefault(row["input"].lower(), row)
    return out


def candidate_html(rank: int, entry: dict, repos: dict) -> str:
    slug = entry.get("repo", "")
    row = repos.get(slug.lower())
    why = esc(entry.get("why", ""))
    promote = esc(entry.get("promote", ""))
    fit = esc(entry.get("fit", ""))

    if not row:
        return f"""<li class="cand"><div class="rank">{rank}</div><div class="body">
        <div class="name">{esc(slug)} <span class="badge warn">unverified</span></div>
        <p class="why"><b>Why {rank}:</b> {why}</p>
        {f'<p class="promote"><b>Promote when:</b> {promote}</p>' if promote else ''}
        {f'<p class="fit"><b>Fit:</b> {fit}</p>' if fit else ''}
        </div></li>"""

    renamed = row["repo"].lower() != slug.lower()
    licence = row.get("license") or "no licence detected"
    badges = [
        f'<span class="badge {row["freshness"]}">{row["freshness"]} · {esc((row.get("pushed_at") or "")[:10])}</span>',
        f'<span class="badge {"warn" if not row.get("license") else ""}">{esc(licence)}</span>',
    ]
    if row.get("archived"):
        badges.insert(0, '<span class="badge bad">archived</span>')
    moved = f'<span class="badge warn">moved from {esc(slug)}</span>' if renamed else ""

    return f"""<li class="cand"><div class="rank">{rank}</div><div class="body">
      <div class="name"><a href="{esc(row['html_url'])}" target="_blank" rel="noopener">{esc(row['repo'])}</a>{moved}</div>
      <div class="facts"><span class="stat"><b>{row['stars']:,}</b> stars</span>
        {''.join(badges)}<span class="lang">{esc(row.get('language') or '—')}</span></div>
      <p class="desc">{esc(row.get('description') or '')}</p>
      <p class="why"><b>Why {rank}:</b> {why}</p>
      {f'<p class="promote"><b>Promote when:</b> {promote}</p>' if promote else ''}
      {f'<p class="fit"><b>Fit:</b> {fit}</p>' if fit else ''}
    </div></li>"""


#: The page's look lives here rather than in this file, so it can be reskinned without touching Python — and
#: so every project's dashboard comes out looking the same instead of being reinvented per run.
DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "dashboard_template.html"


def load_template(path: Path | None = None) -> str:
    chosen = Path(path) if path else DEFAULT_TEMPLATE
    if not chosen.is_file():
        raise SystemExit(f"template not found: {chosen}")
    return chosen.read_text(encoding="utf-8")


def build(spec: dict, verified: list, template_path: Path | None = None) -> str:
    repos = index(verified)
    checked = next((r.get("checked_at", "") for r in verified if r.get("verified")), "")

    sections, ranked_total, excluded_total = [], 0, 0
    for comp in spec.get("components", []):
        ranked = comp.get("ranked", [])
        excluded = comp.get("excluded", [])
        ranked_total += len(ranked)
        excluded_total += len(excluded)

        items = "\n".join(candidate_html(i + 1, e, repos) for i, e in enumerate(ranked))
        block = ""
        if excluded:
            rows = "\n".join(
                f"<li><b>{esc(e.get('name',''))}</b> — {esc(e.get('why',''))}</li>" for e in excluded)
            block = (f'<details class="excluded"><summary>Excluded — {len(excluded)}</summary>'
                     f"<ul>{rows}</ul></details>")

        sections.append(f"""<section class="component" data-id="{esc(comp.get('id',''))}">
          <header><h2>{esc(comp.get('title',''))}</h2>
          <p class="job">{esc(comp.get('job',''))}</p>
          <span class="depth">{len(ranked)} ranked</span></header>
          <ol class="cands">{items}</ol>{block}</section>""")

    chips = "\n".join(
        f'<button class="chip" data-filter="{esc(c.get("id",""))}">{esc(c.get("title",""))}</button>'
        for c in spec.get("components", []))

    return Template(load_template(template_path)).safe_substitute(
        title=esc(spec.get("title", "Component harvest")),
        subtitle=esc(spec.get("subtitle", "")),
        target=esc(spec.get("target_stack", "")),
        components=len(spec.get("components", [])),
        ranked=ranked_total, excluded=excluded_total,
        checked=esc(checked), chips=chips, sections="\n".join(sections))


def main(argv: list[str]) -> int:
    if len(argv) < 4:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    spec = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    verified = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    out = Path(argv[3])
    template = Path(argv[4]) if len(argv) > 4 else None
    out.write_text(build(spec, verified, template), encoding="utf-8")

    thin = [c.get("title") for c in spec.get("components", []) if len(c.get("ranked", [])) < 3]
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
    if thin:
        print(f"\n{len(thin)} component(s) ranked fewer than three deep — these have no real fallback, "
              f"say so in the summary:", file=sys.stderr)
        for name in thin:
            print(f"  {name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
