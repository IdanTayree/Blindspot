# The harvest — finding and verifying components

Read this before recommending any project.

## Why verification is the whole job

A model asked for "the best highly-starred repos for X" will answer fluently from memory. The names are
usually real. The **numbers are not** — star counts, last-updated dates and licences recalled from training
data are stale at best and invented at worst. The output looks authoritative, and someone then spends days
adopting an archived project or a Linux-only tool for a Mac app.

Three failure modes seen in practice, all of which verification catches:

1. **Recalled star counts** presented as facts, including placeholders like "★ Active Standard" sitting in a
   column labelled stars.
2. **Self-contradiction** — a summary claiming 23 components surveyed above a page containing 10.
3. **Architecture mismatch** — recommending a Linux-namespaces sandbox for macOS, or a hosted cloud service
   for a requirement that says local-only. This is the most damaging one, because the reasoning around it
   often sounds excellent.

So: **every number in the output was fetched. Anything unfetched is labelled unverified.**

## The protocol

### 1. Derive the component list from the blueprint

One entry per part that has to be built or bought. Name each in terms of the job it does — "durable task
queue", "wake-word detection", "screen capture and understanding" — not in terms of a library you already
have in mind. Naming it after a library narrows the search to that library's competitors.

For each component, write down the **constraints that disqualify** before searching: platform, language,
runs-locally, licence compatibility, whether a service dependency is acceptable. These do the filtering
later.

### 2. Search

Search the web for current candidates. Useful queries combine the job with the constraint — "durable task
queue rust embedded", "on-device wake word detection macOS". Look for:

- projects with real adoption, not just a good README
- recent commits, not merely a recent release
- a licence compatible with what the user is building

Aim for a primary and one or two alternatives per component. More than three is noise.

### 3. Verify — always, with the script

```bash
python3 scripts/verify_repos.py owner/repo another/repo > verified.json
```

Returns per repo: `stars`, `pushed_at`, `days_since_push`, `license`, `language`, `archived`, `open_issues`,
`description`, `html_url`, and `verified`. It uses the `gh` CLI when present and falls back to the public
API.

Rules that follow from the output:

- `verified: false` → say "unverified" in the dashboard. Never substitute a remembered number.
- `archived: true` → not a candidate, however good it looks. Say why it was excluded.
- `days_since_push > 365` → only a candidate if it is genuinely the standard with no modern alternative, and
  the dashboard must say that explicitly.
- No licence → treat as a blocker for anything the user intends to ship, and flag it.

### 4. Check fit, and reject on it

For each surviving candidate, answer in one line: **can this actually run in the user's stack?** Platform,
language, runtime dependency, and whether it is a library or a service. A candidate that fails fit is
excluded with the reason stated — the exclusion is useful information, not clutter.

### 5. Rank, and keep what you demote

When a better candidate appears, the previous one becomes a **ranked alternative** with a note explaining the
change. Never silently drop it. The user is choosing, and the reason one option lost is often more useful
than the winner's description.

## The dashboard

A single self-contained HTML file — no external scripts, stylesheets, fonts or images, since it must open
from disk and survive being emailed. Requirements:

- **One card per component**, showing the primary candidate and its ranked alternatives.
- **Verified numbers only**, each with the date verified. Unverified fields say so in words.
- **A freshness badge** computed from the real `pushed_at`, not a vibe: e.g. active (<90 days), maintained
  (<1 year), stale (>1 year).
- **Licence** shown per candidate, since it decides adoption.
- **A fit line** per candidate against the user's actual stack.
- **A demotion note** wherever an alternative was ranked below a newer primary.
- **Category filtering**, so a long list stays usable.
- **An excluded section** per component — what was rejected and why. This is what stops the same dead end
  being investigated twice.

Read the `artifact-design` skill's guidance if it is available; otherwise keep the design restrained —
readable type, a real hierarchy, and a palette that works in both light and dark. The content is the product
here, not the chrome.

## The executive summary

Alongside the dashboard, give a short summary in the conversation:

- what to adopt first, and why that one
- anything with no good candidate — this is the most valuable line in the summary, because it is where the
  user will actually have to build
- anything excluded for a reason they might disagree with, so they can overrule it

Keep it to a screen. The dashboard holds the detail.
