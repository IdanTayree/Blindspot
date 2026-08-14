#!/usr/bin/env python3
"""Render a component-harvest dashboard from a ranking spec plus verified GitHub metadata.

The split matters: **you write the judgement, this writes the facts.** The spec file holds the rankings and
the reasoning — which candidate sits where, why, and what would promote it — while every number on the page
comes from `verify_repos.py`, which fetched it. A dashboard whose star counts were recalled looks identical to
one whose star counts are real, which is exactly why the two have to come from different places.

Usage:
    python3 verify_repos.py owner/a owner/b ... > verified.json
    python3 build_dashboard.py harvest.json verified.json out.html

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


def build(spec: dict, verified: list) -> str:
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

    return TEMPLATE.format(
        title=esc(spec.get("title", "Component harvest")),
        subtitle=esc(spec.get("subtitle", "")),
        target=esc(spec.get("target_stack", "")),
        components=len(spec.get("components", [])),
        ranked=ranked_total, excluded=excluded_total,
        checked=esc(checked), chips=chips, sections="\n".join(sections))


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root {{
  --bg:#faf9f7; --panel:#ffffff; --ink:#1a1917; --dim:#6b6862; --line:#e4e1db;
  --accent:#a4501e; --accent-soft:#f3e6dc;
  --good:#2f6b46; --good-bg:#e6f0e9; --warnc:#8a6212; --warn-bg:#f7eed8;
  --badc:#96291f; --bad-bg:#f7e0dd; --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
}}
@media (prefers-color-scheme:dark) {{
  :root:not([data-theme="light"]) {{
    --bg:#141311; --panel:#1c1b18; --ink:#eceae5; --dim:#9b968d; --line:#2e2c28;
    --accent:#e08a4c; --accent-soft:#33241a;
    --good:#7fc79b; --good-bg:#1c2c22; --warnc:#dcb45f; --warn-bg:#2e2617;
    --badc:#e88a7d; --bad-bg:#2e1c19;
  }}
}}
:root[data-theme="dark"] {{
  --bg:#141311; --panel:#1c1b18; --ink:#eceae5; --dim:#9b968d; --line:#2e2c28;
  --accent:#e08a4c; --accent-soft:#33241a;
  --good:#7fc79b; --good-bg:#1c2c22; --warnc:#dcb45f; --warn-bg:#2e2617;
  --badc:#e88a7d; --bad-bg:#2e1c19;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
.wrap {{ max-width:1120px; margin:0 auto; padding:40px 22px 80px; }}
header.top {{ border-bottom:2px solid var(--ink); padding-bottom:18px; margin-bottom:26px; }}
h1 {{ font-size:30px; margin:0 0 6px; letter-spacing:-.02em; text-wrap:balance; }}
.sub {{ color:var(--dim); margin:0; font-size:14px; }}
.meta {{ display:flex; flex-wrap:wrap; gap:10px 26px; margin-top:16px; font-size:13px; color:var(--dim); }}
.meta b {{ color:var(--ink); font-variant-numeric:tabular-nums; }}
.note {{ background:var(--accent-soft); border-left:3px solid var(--accent); padding:12px 16px;
  margin:22px 0 26px; font-size:13.5px; border-radius:0 6px 6px 0; }}
.chips {{ display:flex; flex-wrap:wrap; gap:7px; margin-bottom:26px; }}
.chip {{ font:inherit; font-size:12.5px; padding:5px 11px; border:1px solid var(--line);
  background:var(--panel); color:var(--dim); border-radius:999px; cursor:pointer; }}
.chip:hover {{ border-color:var(--accent); color:var(--ink); }}
.chip:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
.chip.on {{ background:var(--ink); color:var(--bg); border-color:var(--ink); }}
.component {{ background:var(--panel); border:1px solid var(--line); border-radius:10px;
  padding:20px 22px; margin-bottom:18px; }}
.component header {{ display:flex; flex-wrap:wrap; align-items:baseline; gap:8px 14px; margin-bottom:14px; }}
.component h2 {{ font-size:18px; margin:0; letter-spacing:-.01em; }}
.job {{ margin:0; color:var(--dim); font-size:13.5px; flex:1 1 260px; }}
.depth {{ font-size:11.5px; color:var(--dim); border:1px solid var(--line); padding:2px 8px;
  border-radius:999px; white-space:nowrap; }}
ol.cands {{ list-style:none; margin:0; padding:0; }}
.cand {{ display:flex; gap:14px; padding:14px 0; border-top:1px solid var(--line); }}
.cand:first-child {{ border-top:none; }}
.rank {{ flex:0 0 30px; height:30px; border-radius:50%; display:grid; place-items:center;
  font-size:13px; font-weight:600; background:var(--line); color:var(--dim); font-variant-numeric:tabular-nums; }}
.cand:first-child .rank {{ background:var(--accent); color:#fff; }}
.body {{ flex:1; min-width:0; }}
.name {{ font-family:var(--mono); font-size:14px; display:flex; flex-wrap:wrap; gap:8px; align-items:center; }}
.name a {{ color:var(--ink); text-decoration:none; border-bottom:1px solid var(--accent); }}
.name a:hover {{ color:var(--accent); }}
.facts {{ display:flex; flex-wrap:wrap; gap:6px 12px; align-items:center; margin:7px 0;
  font-size:12px; color:var(--dim); }}
.stat b {{ color:var(--ink); font-variant-numeric:tabular-nums; }}
.badge {{ font-size:11px; padding:2px 8px; border-radius:999px; background:var(--line); color:var(--dim); }}
.badge.active {{ background:var(--good-bg); color:var(--good); }}
.badge.maintained {{ background:var(--warn-bg); color:var(--warnc); }}
.badge.stale, .badge.bad {{ background:var(--bad-bg); color:var(--badc); }}
.badge.warn {{ background:var(--warn-bg); color:var(--warnc); }}
.lang {{ font-family:var(--mono); font-size:11.5px; }}
.desc {{ margin:6px 0; font-size:13px; color:var(--dim); }}
.why, .promote, .fit {{ margin:5px 0; font-size:13px; }}
.promote {{ color:var(--dim); }}
.fit {{ color:var(--dim); font-size:12.5px; }}
.why b, .promote b, .fit b {{ color:var(--ink); font-weight:600; }}
.excluded {{ margin-top:14px; border-top:1px dashed var(--line); padding-top:12px; }}
.excluded summary {{ cursor:pointer; font-size:12.5px; color:var(--dim); }}
.excluded ul {{ margin:10px 0 0; padding-left:20px; font-size:12.5px; color:var(--dim); }}
.excluded li {{ margin-bottom:6px; }}
.excluded b {{ font-family:var(--mono); color:var(--ink); }}
footer {{ margin-top:36px; padding-top:18px; border-top:1px solid var(--line);
  font-size:12.5px; color:var(--dim); }}
</style></head><body><div class="wrap">
<header class="top">
  <h1>{title}</h1>
  <p class="sub">{subtitle}</p>
  <div class="meta">
    <span><b>{components}</b> components</span>
    <span><b>{ranked}</b> ranked candidates</span>
    <span><b>{excluded}</b> excluded, with reasons</span>
    <span>verified <b>{checked}</b></span>
  </div>
</header>
<p class="note"><b>Every number on this page was fetched from the GitHub API</b> on {checked} — stars, last
push, licence and archived status. Nothing is recalled. Where GitHub reports no licence, this page says so
rather than guessing, and a repository that has been renamed shows the slug it moved from. Target stack:
{target}.</p>
<div class="chips"><button class="chip on" data-filter="all">All</button>
{chips}</div>
{sections}
<footer>Ranked lists go at least three deep by design: whatever gets chosen will eventually hit a wall, and
the next option needs to be already evaluated rather than researched again months later. Each entry carries
why it sits where it does and the condition that would promote it.</footer>
</div>
<script>
const chips=[...document.querySelectorAll('.chip')],secs=[...document.querySelectorAll('.component')];
chips.forEach(c=>c.addEventListener('click',()=>{{
  chips.forEach(x=>x.classList.toggle('on',x===c));
  const f=c.dataset.filter;
  secs.forEach(s=>s.style.display=(f==='all'||s.dataset.id===f)?'':'none');
}}));
</script></body></html>"""


def main(argv: list[str]) -> int:
    if len(argv) < 4:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    spec = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    verified = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    out = Path(argv[3])
    out.write_text(build(spec, verified), encoding="utf-8")

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
