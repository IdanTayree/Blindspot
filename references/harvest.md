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

**And ask the scope question first — components only, or anything that saves work?** (SKILL.md carries the
wording.) If they chose the wider scope, the list gains entries the blueprint never produced, because a
blueprint describes what a system must do and not what stops it looking homemade. The recurring ones, named
by job:

| Job | Not | Because |
|---|---|---|
| log and terminal output | "xterm" | terminal emulators are a field, not one library |
| reviewing a diff | "monaco" | diff review has lighter options than a whole editor |
| command palette / keyboard entry | "cmdk" | two different interaction models compete here |
| first-run guidance | "a tour library" | wizards and tours are separate shapes |
| loading, empty and error states | "spinners" | the most hand-rolled layer of any app |
| drag-and-drop and boards | "dnd" | the framework already in use usually decides this |
| timelines and roadmaps | "gantt" | ranges from a component to a framework |
| graph and relationship views | "d3" | rendering and layout are separable choices |

These are the cards users adopt fastest, because adoption is a single import rather than an architecture
decision — which is exactly why leaving them out feels like a thorough hunt right up until someone spends a
day rebuilding a spinner.

### 2. Search

Search the web for current candidates. Useful queries combine the job with the constraint — "durable task
queue rust embedded", "on-device wake word detection macOS". Look for:

- projects with real adoption, not just a good README
- recent commits, not merely a recent release
- a licence compatible with what the user is building

**Aim for at least four candidates per component so that three or more survive verification.** Some will turn
out to be archived, on the wrong platform, or unlicensed, and a component that ends up with a single survivor
is a component with no fallback.

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

### 4. Check fit — and before rejecting anything, ask what you actually need from it

For each surviving candidate, answer in one line: **can this run in the user's stack?** Platform, language,
runtime dependency, library or service.

Then, before writing anything off, stop and ask the question that recovers most of this phase's value:
**what do we actually need from this project?**

A candidate can fail as a *dependency* and still be the most useful thing in the list. An AGPL product cannot
be embedded — but its architecture, its state machine, the edge cases in its issue tracker and the mistakes
in its changelog are not encumbered by anything. An archived project cannot be relied on — but it already
solved the problem once, and its README will tell you what was hard about it. A commercially licensed model
cannot ship — but the shape of its API is often the best available specification for the thing you are about
to build.

Frequently the useful part is something the user had not thought of at all: a state they had not enumerated,
a failure mode nobody planned for, a configuration knob that reveals a whole class of problem. That is the
same job the interview does, aimed at a repository.

So every candidate gets one of **three verdicts**, not two:

| Verdict | Meaning |
|---|---|
| **Adopt** | Licence, platform and maintenance all allow it. It goes in the ranked list. |
| **Consult** | Cannot be adopted, but is worth reading for something specific — named explicitly. |
| **Reject** | Nothing to take. Wrong problem, or genuinely unsafe. |

**Reject is now the small category.** Most things that used to be excluded are consults.

### 4a. What "consult" is allowed to mean

The line that matters, and it is not a technicality: **copyright protects expression, not ideas.** Reading a
public repository to understand how a problem is solved is ordinary engineering. Copying its code into a
project whose licence cannot carry it is not.

Where to take from, in order of safety:

1. **Documentation, README, architecture notes, ADRs.** Written to be read and explain the thinking directly.
2. **The issue tracker.** The single most undervalued source in open source — it is a list of everything that
   went wrong in production, written by the people it happened to. Nothing there is encumbered, and it is
   usually the fastest way to learn a problem's real edge cases.
3. **Changelogs and release notes.** What they had to fix, and in what order they discovered it.
4. **Public API shape and protocol.** Interfaces and protocols are not creative expression in the way an
   implementation is, and matching one is often the point.
5. **The source itself** — last, and with care.

What must not happen, stated plainly because the cost of getting it wrong is real:

- **Never copy code, comments or distinctive structure** from a source whose licence the project cannot
  carry. Not "adapted", not "with the variable names changed" — that is the same file wearing a hat.
- **Do not paraphrase a file line by line.** Writing the same code from memory immediately after reading it
  produces a derivative work regardless of intent.
- **Take a list, write your own implementation.** "Their retry logic handles these six failure modes" is a
  requirement. Their retry function is their code.
- **When the ideas came from reading source rather than docs, say so** in the note, so a maintainer can make
  a judgement later rather than discovering it.

For an **unlicensed** repository — GitHub reporting no licence means all rights reserved, not public domain —
read the repository anyway before concluding: a `LICENSE` file GitHub failed to classify is common, and
`verify_repos.py` flags that case separately as *present but unrecognised*. Ask the maintainer if it matters;
an issue asking "what licence is this under?" is answered often enough to be worth the minute.

### 4b. Writing a useful consult note

A consult entry is worthless unless it names the extraction. Compare:

> ~~Worth reading for inspiration.~~

against:

> **Take:** its booking state machine — six states where we had assumed three — and the twelve issues tagged
> `timezone`, which enumerate failure modes we have not planned for. Read the docs and issues, not the source;
> AGPL, so nothing may be copied.

The second is a task someone can do in twenty minutes. The first is a note nobody will ever action.

Every consult carries three things: **why it cannot be adopted**, **what specifically to take**, and **where
to take it from**.

### 5. Rank at least three deep, and keep what you demote

Every component gets a **numbered list — 1st, 2nd, 3rd, and further where the field is rich** — not a winner
and a runner-up.

The reason is practical rather than tidy. Whatever gets picked will eventually hit a wall: a platform it does
not support, a licence that turns out to be wrong for shipping, a maintainer who stops, a feature everyone
assumed was there. At that moment the user needs the next option **already evaluated**, with its trade-offs
written down — not a fresh search weeks later, when the reasoning behind the original choice has been
forgotten and the whole comparison has to be redone.

So each entry carries two things:

- **Why it is at this position** — the specific trade-off that put it below the one above. "Stronger isolation,
  but requires a Linux VM on macOS." "Simpler API, no durable retries."
- **What would promote it** — the condition under which the user should switch. "Pick this instead if the
  project ever needs to run untrusted code from strangers." This is the line that makes the list useful under
  pressure, because it tells them *when* to reach for the fallback, not merely that one exists.

When a better candidate appears later, it takes first place and the rest shift down, each keeping its note.
Nothing is ever silently dropped — the reason a candidate lost is frequently more useful than the winner's
description, and a rejected option that quietly disappears gets re-investigated six months later.

## The dashboard

**Use `scripts/build_dashboard.py` rather than hand-writing HTML.** Write the rankings and reasoning into a
`harvest.json` (its format is documented at the top of that script), then:

```bash
python3 scripts/build_dashboard.py harvest.json verified.json out.html
```

It merges the judgement with the verified facts, renders renames and archived status automatically, and warns
on stderr about any component ranked fewer than three deep — treat that warning as a finding to report, since
a component with one survivor has no fallback.

Hand-writing the page instead means re-deciding the layout every time and, more importantly, makes it easy to
type a number that was never fetched.

The generated page is a single self-contained HTML file — no external scripts, stylesheets, fonts or images,
so it opens from disk and survives being emailed. What it renders:

- **One card per component**, showing the full ranked list — 1st, 2nd, 3rd and beyond — each numbered, each
  with its position rationale and its promotion condition. The list is the product; a card showing only a
  winner has thrown away most of the work.
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
