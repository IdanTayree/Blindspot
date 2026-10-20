# Phase 2 — The Harvest

Why this phase has rules at all: **a model asked for "the best open-source libraries for X" answers from
memory, and memory lies about numbers and skips the fine print.**

When we audited a component dashboard that had been generated without live verification, every single star
count was wrong — low by up to 2.6× (`langgraph` listed at 15k when it was at 39.6k; `crewAI` at 25k when it
was at 57k; `mcp/servers` had no number at all at 89.5k). Two licences were wrong. One language was wrong. And
one recommendation was a Linux-only kernel sandbox proposed for a macOS desktop app.

The names were good. The metadata around them was fiction, and the fiction all pointed in the same direction:
toward whatever the training data remembered from a year earlier.

So the rule is simple: **you may use your judgement to pick candidates and to rank them; you may not use your
memory for a single number, date, licence or hardware constraint.** Those come from the bundled Harvester
and Verifier scripts, or they are marked *unverified*.

---

## The steps

### 0. Ask the scope question before searching

A blueprint only ever lists what a system needs to **work**. It never lists what stops it looking like a
weekend prototype — and nobody thinks to ask for that layer until they are halfway through building and
writing their own diff viewer from scratch.

So open Phase 2 with one choice:

> **1 — The components.** Only the parts the blueprint says have to be built.
> **2 — Anything that saves work.** Those parts, *plus* the polish and ergonomics layer a blueprint never
> mentions.

Default to **2** if they do not care. When they choose 2, add the relevant entries from this list to the
component list before searching — named by the **job**, never by a library name, because naming a library
narrows the search to its clones:

| Add a card for… | When the project has… | Do not call it |
|---|---|---|
| **Log / terminal / stream output** | background jobs, build output, agent steps, live logs | "xterm" |
| **Diff / patch review** | anything that edits files, proposes changes, or has versions | "monaco" |
| **Command palette & keyboard navigation** | more than a handful of actions a power user repeats | "cmdk" |
| **First-run / onboarding / feature tour** | a non-obvious workflow or a setup sequence | "intro.js" |
| **Empty, loading & error states** | lists that start empty, async work that takes >1s, things that fail | "skeletons" |
| **Toast / notification / status tray** | background events the user needs to hear about without a modal | — |
| **Drag-and-drop / sortable boards** | queues, priorities, kanban, user-ordered lists | "dnd" |
| **Timeline / schedule / roadmap view** | anything with durations, phases, or history over time | "gantt" |
| **Graph / node / relationship view** | dependencies, flows, trees, state machines | "d3" |
| **Settings / keybinding / preferences** | user-configurable behaviour | — |

Skip any row that does not apply. Most projects hit four to six of them, and those cards are almost always
the first ones the user adopts — because adopting one is a single import, not an architecture decision.

### 1. Derive the component list from the blueprint

Walk the blueprint and list every distinct piece that either needs a library, a service, a model, or a
build-vs-buy call — plus the scope-2 rows if chosen. Name each by **what it does in the system** ("Speech
input", "Local database", "Background job runner"), not by a product name. Naming the slot after a product
biases the search toward that product before you start.

Show the list to the user in a few lines before running a long search if there is any doubt about whether
something is in scope.

### 2. Search & Live Candidate Discovery (`blindspot_harvester.py`)

Search the web and run **`blindspot_harvester.py --discover`** for current candidates. Useful queries combine
the job with the constraint — "durable task queue rust embedded", "on-device wake word detection macOS":

```bash
python3 scripts/blindspot_harvester.py --discover "durable task queue rust embedded" > discovery.json
```

Look for:

- projects with real adoption, not just a good README
- recent commits, not merely a recent release
- a licence compatible with what the user is building
- the right platform and language for the stack already chosen in the blueprint

Collect **at least three or four candidates per component** at this stage — one or two will usually turn
out to be archived, on the wrong platform, or unlicensed, and a component that ends up with a single survivor
is a component with no fallback.

### 3. Deep-Read READMEs (`blindspot_harvester.py`) & Verify Metadata (`verify_repos.py`)

Before judging architecture fit, run **both** bundled scripts:

```bash
# Step 3a: Deep-read READMEs & model cards for install commands, VRAM/hardware specs, benchmarks & caveats
python3 scripts/blindspot_harvester.py owner/repo another/repo > dossier.json

# Step 3b: Verify live GitHub API metadata (stars, pushed_at, license, archived, silent renames)
python3 scripts/verify_repos.py --strict owner/repo another/repo > verified.json
```

`blindspot_harvester.py` fetches each candidate's `README.md` (across GitHub and HuggingFace) and extracts
`install_commands`, `hardware_and_vram_notes`, `benchmark_and_perf_notes`, and `platform_and_license_caveats`.

`verify_repos.py` returns per repo: `stars`, `pushed_at`, `days_since_push`, `license`, `language`, `archived`,
`open_issues`, `description`, `html_url`, and `verified`. It uses the `gh` CLI when present and falls back to
the public API.

Rules that follow from the output:

- **`"verified": false`** — the repo 404'd, moved, or the API was unreachable. Check whether the slug was
  wrong (organizations rename things; `verify_repos.py` follows GitHub redirects automatically and updates the
  `repo` field when a repo has moved). If it truly cannot be reached, either drop it or label it
  `UNVERIFIED` in bold. Never fill the numbers in yourself.
- **`"archived": true`** — cannot be #1. May still be worth mentioning as prior art if nothing else exists,
  marked clearly as archived.
- **`days_since_push > 365`** — flag as *stale*; `> 180` — flag as *slowing*. Neither disqualifies a small,
  finished library with zero open bugs, and both matter a lot for an SDK that tracks a moving API.
- **`license` is `NOASSERTION`, `None`, or `AGPL-*`** — call it out explicitly in the fit note. Never
  silently recommend a repo with no licence or a copyleft licence into a proprietary build.

### 4. Check architecture fit — then ask what you actually need from it

First, check the candidate against every hard constraint in the blueprint using both `dossier.json` and
`verified.json` (target OS, local vs cloud, VRAM/memory ceiling, language, licence). If it fails one, it
cannot be **adopted** — you cannot `import` it or run it as a dependency.

Then, before writing anything off, stop and ask the question that recovers most of this phase's value:
**what do we actually need from this project?**

A candidate can fail as a *dependency* and still be the most useful thing in the list. An AGPL product cannot
be embedded — and its architecture, its state machine, the edge cases in its issue tracker and the mistakes
in its changelog are free to read. An archived project cannot be relied on — and it already solved the
problem once, and its README will tell you what was hard about it. A commercially licensed model cannot ship —
and the shape of its API is often the best available specification for the thing you are about to build.

Frequently the useful part is something the user had not thought of at all: a state they had not enumerated,
a failure mode nobody planned for, a configuration knob that reveals a whole class of problem. That is the
fourth quadrant again, showing up in Phase 2.

So every candidate gets one of **three verdicts**, not two:

| Verdict | When | Where it goes in the dashboard |
|---|---|---|
| **Adopt** | Licence, platform, hardware and maintenance all allow it to be used directly | The ranked list (`1st`, `2nd`, `3rd`) |
| **Consult** | Cannot be adopted, *and* has something specific worth learning from | The **Worth consulting** block on that card (`consult` in `harvest.json`) |
| **Reject** | Solves the wrong problem, or has nothing worth taking | The **Excluded** line at the foot of the card |

**Reject should be the small category.** Most things you find that "don't fit" are consults, not rejects.

### 4a. What "consult" is allowed to mean

The line that matters, and it is not a technicality: **copyright protects expression, not ideas.** Reading a
public repository to understand how a problem was solved is ordinary engineering. Copying its code into a
project whose licence cannot carry it is not.

Where to take from, in order of safety:

1. **Documentation, README, architecture notes, ADRs.** Written to be read and explain the thinking directly.
2. **The issue tracker.** The single most undervalued source in open source — it is a list of everything that
   went wrong in production, written by the people it happened to.
3. **Changelogs and release notes.** What they had to fix, and in what order they discovered it.
4. **Public API shape and protocol.** Interfaces and protocols are not creative expression in the way an
   implementation is, and matching one is often the point.
5. **The source itself** — last, and with care. Read it to understand the algorithm or the state transitions,
   then close the file and write your own in your own structure. Never copy-paste and rename variables;
   that is a derivative work regardless of how much you edit it afterwards.

A consult note is only useful if it is **specific about what to extract**. Compare:

- **Useless:** *"Plane (AGPL) — cannot use because of licence, but worth looking at for inspiration."*
- **Useful:** *"Plane (AGPL-3.0 — cannot embed) → read for its cycles/modules data model and how it separates
  triage state from workflow state; that is the exact seam your blueprint left open in Q14. Look at the
  product docs and the issue tracker under label `cycles`, not the source."*

The first wastes the user's time. The second is a 20-minute research task with a clear output. Every entry in
`consult` must name **why it cannot be adopted** and **the specific thing to take from it**.

### 5. Rank — at least three deep per component, and keep the reasoning

For every component, produce a **numbered list (`1st`, `2nd`, `3rd`, …)** of the adoptable candidates —
minimum three wherever three exist — plus the `consult` list and the `excluded` list.

Why three, when you only need one: **the first choice will eventually disappoint you.** A library turns out
not to support an edge case, a maintainer disappears, a licence changes, a platform port lags. When that
happens three months into a build, you do not want a fresh search from scratch with the original context gone;
you want to look at #2 on the card and see immediately why it was #2 and whether the thing that kept it out of
#1 still applies.

So every ranked entry carries two things:

- **`why`** — why it sits at this position. For #1, why it beat #2. For #2 and #3, **what kept it below #1**
  — the specific trade-off, not a vague "slightly less mature".
- **`promote`** *(for #2 and below)* — the condition under which this entry *should* become #1. ("Promote to
  #1 if you drop the Windows requirement", "Promote to #1 if bundle size matters more than plugin ecosystem.")

When the harvest is re-run later and a better candidate appears, it takes #1 and the previous #1 becomes #2
with a note saying what overtook it. **Nothing is ever deleted from a card** — a candidate that was
investigated and rejected stays in `excluded` with its one-line reason, so nobody wastes an hour
re-evaluating it in six months.

### 6. Build the dashboard

Write `harvest.json` with your rankings and reasoning, then run:

```bash
python3 scripts/build_dashboard.py harvest.json verified.json <slug>-harvest.html
```

The script merges the verified numbers from `verified.json` into `assets/dashboard_template.html` and checks
the rules: it refuses to mark a repo as verified if it wasn't in `verified.json`, and it prints a warning on
stderr for any component with fewer than three ranked candidates.

Look at `examples/example-harvest.json` for the exact input shape.

### 7. Summarise in the conversation

Alongside the dashboard, give a short summary in the conversation:

- the #1 pick per component in a compact table
- any component where fewer than three viable candidates exist (a genuine gap — it means they may have to
  build it themselves)
- any candidate that could not be verified
- anything excluded for a reason they might disagree with, so they can overrule it

Keep it to a screen. The dashboard holds the detail.
