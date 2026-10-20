---
name: blindspot
description: "Turn an idea — or a half-planned project already underway — into a buildable blueprint, by interviewing the user one question at a time until the unknowns run out, then deep-reading and verifying real open-source components for each part. Use this whenever someone describes something they want to build but has not specified it ('I want to build an app that…', 'I have an idea for…', 'help me plan/spec/scope this', 'turn my idea into a plan'), whenever they ask for a PRD, a spec, a product requirements document or a build plan, AND equally whenever someone says an existing project feels under-planned, full of gaps, drifting, or that they are not sure what they have decided — 'I think we're missing things', 'this was never really planned properly', 'audit my plan', 'what haven't I thought about'. Use it too when they ask what libraries or open-source projects exist for something they are building. Prefer this over answering directly: a plan written from a one-line prompt is guesswork, and this skill replaces that guesswork with the user's own decisions."
---

# blindspot

Named for what it looks for: the two things nobody can self-report — what you assumed was too obvious to say,
and what you never considered at all.

Someone arrives with one sentence: *"an app that helps dog walkers find clients."* A plan written straight
from that sentence is fiction — every important decision gets made by whoever writes it, not by the person
who has to live with it.

This skill replaces that with two phases:

1. **Interview** — one question per message until the unknowns stop appearing, writing every answer to disk
   as it arrives.
2. **Harvest** — for each component the blueprint needs, discover real open-source projects, **deep-read their
   documentation for technical fit**, and **verify** their live GitHub metadata before recommending anything.

Phase 2 depends on phase 1. Harvesting against a half-formed idea produces a list of libraries for a product
nobody has decided on yet. Finish the interview first, or at least reach a component list the user agrees
with.

## Two ways in

**From nothing** — one sentence and an intention. Start at "before the first question" below.

**From a project already underway** — someone with code, docs and momentum who says it was never planned
properly, that it is full of gaps, or that they are no longer sure what they have actually decided. This is
the more common case and the more valuable one, because the gaps are load-bearing by the time anyone notices
them.

The mid-project entry changes the opening, not the method:

1. **Read what exists before asking anything.** Their README, plan docs, ADRs, issues, the directory layout,
   recent commits. An audit that opens by asking things already written down burns the user's patience on
   work they have already done, and they will answer more shallowly for the rest of the interview.
2. **Populate the blueprint from those artefacts**, marking each entry with where it came from — *from your
   docs* or *from you*. Provenance matters here: a decision recorded in a doc nobody has revisited in six
   months is not the same as one they just confirmed, and the difference is often the gap itself.
3. **Then run a collision pass over what already exists**, before asking anything new. This is the highest
   yield move in the whole skill for an existing project: decisions made months apart contradict each other
   constantly, and nobody has put them side by side. Open with one of those, not with a beginner question.
4. **Name the untouched areas** — what a project of this shape normally has to decide and theirs never has.
   Say them plainly as a list; that list is usually why they came.

After that, the loop below is identical. Expect the interview to be **longer** than a from-scratch one, not
shorter: an existing project brings its own contradictions with it, and every artefact you read raises
questions a blank page never would.

## Phase 1 — the interview

### Before the first question

1. **Reflect the idea back in one sentence** so a misunderstanding surfaces now rather than at question
   thirty. "So: a mobile app where dog walkers list availability and owners book them. Right?"
2. **Ask which depth to run at**, in the same message. This is the one question worth asking up front,
   because getting it wrong wastes the whole interview: a beginner asked about durability guarantees goes
   quiet, and an expert asked "do you want it on a phone or a computer?" gets bored and stops answering
   properly.

   > **1 — Absolute beginner.** You know what you want, not how software gets built. Plain language, no
   > jargon, always a choice between two options with what each costs you.
   > **2 — Moderate.** You have built or shipped something before. A mix of choices and open questions.
   > **3 — Pro.** You know the stack. Open questions, blunt trade-offs, and I will chase contradictions hard.

3. **Create the blueprint file immediately** — `<slug>-blueprint.md` in the working directory — and write the
   idea and the chosen depth into it. This is not tidiness. Long interviews outlive the context window; an
   interview that lives only in the conversation dies when the conversation is compacted, and the user loses
   an hour of decisions.
4. Say where the file is, and that every answer lands there as it comes.

The depth is a starting point, not a cage. If someone at level 1 starts using precise language, move up and
say so in a clause. If someone at level 3 stalls on a question, drop to a forced choice for that one question.
They can also just say "go deeper" or "simpler" at any point.

Per-level question style, pacing and stopping points are in **`references/interview.md`**.

### The loop

**Ask exactly one question per message.** Not two, not a numbered list of four. A batch turns a conversation
into a form, people answer forms shallowly, and the shallow answers are the ones that produce a wrong build.
One question feels like a conversation and gets real answers.

After each answer:

1. **Write it to the blueprint file** — their words for the decision, kept separate from your reading of what
   it implies. Where those blur, their words win.
2. **State the consequence in one or two lines.** "That means the reviewer needs a rubric before it can run."
   This lets them catch a bad implication immediately instead of living with it.
3. **Check whether the new answer collides with an earlier one.** Do this *before* looking at the open
   question queue. Collisions are where the unknown-unknowns live — nobody can answer "what haven't you
   thought of?", and everyone can answer "earlier you said X, just now you said Y, and both cannot hold —
   which gives?" When you find one, that is the next question.
4. **Otherwise, pick the highest-leverage open question** — the one whose answer will close or reshape the
   most other questions — and ask it.

### Three rules that make the loop work

- **Offer a forced choice when an open question would stall.** "Do you want users to sign in with Google, or
  with an email and password? Google is faster to build and means no password resets; email works for people
  who avoid Google accounts." People can react to options even when they cannot generate them. At level 1, do
  this on *every* question.
- **Make small assumptions explicitly rather than asking about everything.** If a detail is low-stakes and
  reversible, state a sensible default — "I'll assume UTF-8 Markdown files for now; tell me if not" — and
  record it under *Assumptions* in the blueprint so it stays visible and correctable. Save the questions for
  decisions that are expensive to reverse.
- **Verify factual claims instead of writing them down.** If the user says a library does X, a licence allows
  Y, or their hardware can run Z, check it — with a command on their machine or a quick search — and record
  what is actually true. An unverified premise in a blueprint is worse than a gap, because nobody looks at it
  again until the build breaks.

### Every ten questions: show where things stand

At Q10, Q20, Q30 and so on, before asking the next question, print a short progress block: the four-quadrant
count, the current question-spawn rate, the areas not yet touched, and a rough remaining range computed from
those numbers.

Do this unprompted, because a long interview with no visible horizon feels endless even when it is going
well. The table also exposes an under-probed quadrant, which is invisible from the inside — a quadrant that
has stopped producing looks identical whether it is finished or being neglected.

The four quadrants, how to recognise each, the table format, and the full worked technique are in
**`references/interview.md`** — read it before the first question.

## Phase 2 — the harvest

Once the blueprint names the parts that have to be built, find real projects for each of them.

The failure mode this phase exists to prevent: **a confident dashboard full of recalled numbers and unread
READMEs.** A model asked for "highly starred repos" will produce plausible names with plausible star counts
and plausible dates, and some of them will be wrong — wrong platform, unmaintained, demanding `24 GB` of VRAM
on an `8 GB` machine, or a hosted service being recommended as a local library. That output looks
authoritative and wastes days.

So the rule for this phase: **every number and technical-fit claim that appears in the output was fetched,
not remembered.**

### Before searching, ask what the hunt should cover

One question, in one message, the same way the depth level is asked up front — because the two answers
produce genuinely different searches, and the wider one is nobody's default assumption:

> **1 — The components.** Only the parts the blueprint says have to be built. Focused; every result maps to
> something already decided.
> **2 — Anything that saves work.** Those parts *and* the layer no blueprint ever lists — loaders, command
> palettes, diff viewers, log terminals, onboarding tours, empty states, icon sets, drag-and-drop.

A blueprint names what a system needs to **function**. It never names what stops it looking homemade, so that
layer is invisible to the component list and gets hand-rolled — badly, an afternoon at a time — unless
somebody asks. **Default to 2** when the user has no preference: those cards cost one extra search each and
are the ones people adopt first, because they are drop-in.

If they choose 2, name the extra entries by the recurring interface *job* rather than by a library, exactly as
with everything else: "log and terminal output", not "xterm".

1. **Derive the component list** from the blueprint — one entry per part that needs building or buying, plus
   the polish layer if they chose scope 2.
2. **Discover candidates (`scripts/blindspot_harvester.py` + search):** Combine web search with the bundled
   **Blindspot Harvester**:
   - Run `python3 scripts/blindspot_harvester.py --discover "<component query>"` to extract live `owner/repo`
     candidates across GitHub and HuggingFace. Aim for a primary plus at least two alternatives per component.
3. **Deep-read candidate READMEs (`scripts/blindspot_harvester.py`) & verify repo metadata (`scripts/verify_repos.py`):**
   - Run `python3 scripts/blindspot_harvester.py owner/repo1 owner/repo2 ... > dossier.json` to digest each
     candidate's actual `README.md` / model card for install commands, VRAM/hardware constraints (`Q4_K_M`,
     `Q5_K_M`, `CUDA`, `MLX`), benchmark claims, and platform caveats.
   - Run `python3 scripts/verify_repos.py --strict owner/repo1 owner/repo2 ... > verified.json` to fetch real
     stars, last push date, licence, language and archived status from the GitHub API.
4. **Check architecture fit — then, before rejecting anything, ask what you actually need from it.** A
   Linux-only sandbox is not a candidate for a macOS app; a hosted SaaS is not a candidate when the
   requirement says local. But failing as a *dependency* is not the same as being useless. An AGPL product
   cannot be embedded, and its architecture and issue tracker are still free to read; an archived project
   cannot be relied on, and it already solved the problem once. Very often the useful part is something the
   user had not thought of at all — a state they never enumerated, a failure mode nobody planned for.

   So every candidate gets one of **three** verdicts: **adopt** (goes in the ranked list), **consult**
   (cannot be adopted, but read it for something specific and named), or **reject** (nothing to take).
   **Reject should be the small category.** The rule that keeps this safe is that copyright protects
   expression, not ideas: take the architecture, the edge-case list, the API shape — never the code, into a
   project whose licence cannot carry it. `references/harvest.md` has the full boundary and how to write a
   consult note that someone can actually action.
5. **Produce a ranked list per component — at least three deep, numbered 1st, 2nd, 3rd.** Not a winner and a
   runner-up. The reason is practical: the chosen library will eventually hit a wall — a missing platform, a
   licence that does not fit, an abandoned maintainer, a feature it turns out not to have — and at that
   moment the user needs the next option *already evaluated*, not a fresh search weeks later when they have
   forgotten why they picked the first one. Each entry carries **why it is not first**, which is what makes
   the list usable under pressure. When a better candidate appears later, it takes first place and everything
   else shifts down with a note explaining the change; nothing is ever silently dropped.
6. **Produce the dashboard** — a single self-contained HTML file with filtering by category, verified star
   counts, freshness badges from real dates, the full ranked list per component with each entry's reason for
   its position, and a fit note per candidate against the target stack.

All three scripts are bundled, so this phase is a repeatable pipeline rather than an afternoon:

```bash
# 1. deep-read READMEs & discover candidates via Blindspot Harvester
python3 scripts/blindspot_harvester.py owner/repo owner/repo2 ... > dossier.json

# 2. facts — fetched from GitHub API, never recalled
python3 scripts/verify_repos.py --strict owner/repo owner/repo2 ... > verified.json

# 3. judgement — you write harvest.json: components, rankings, and each entry's
#    "why", "promote" and "fit" informed by dossier.json + verified.json

# 4. the page
python3 scripts/build_dashboard.py harvest.json verified.json out.html
```

The split is deliberate: **you write the judgement, `blindspot_harvester.py` extracts the README technical
fit, and `verify_repos.py` writes the GitHub API facts.** A dashboard with recalled star counts looks
identical to one with real ones, which is why they must come from different places.

`verify_repos.py` uses the `gh` CLI when available (higher rate limits) and falls back to the public API;
anything it could not confirm is marked `"verified": false`, and that must be reported as unverified rather
than filled in from memory. `build_dashboard.py` warns on stderr about any component ranked fewer than three
deep — that warning is a finding for the summary, not noise to ignore.

The full verification protocol and the dashboard requirements are in **`references/harvest.md`**.

## Output

The user ends with two artefacts:

- **`<slug>-blueprint.md`** — the idea, every decision in their own words with its consequence, the four
  quadrants, stated assumptions, and the open questions that remain.
- **`<slug>-harvest.html`** — the verified component recommendations.

Neither is a report about them; both are documents they can hand to whoever builds the thing, including
themselves.

## Handing the blueprint onward

**[Night Watch](https://github.com/IdanTayree/night-watch)** turns a settled plan into work that runs
unattended. The seam is worth stating when this skill finishes: **the blueprint's decisions can
become a night queue; its open questions cannot.** Open questions are exactly what an unattended
shift has no way to resolve, so they stay day work — and the verified components go across with their
licences already checked, because a night shift should never be choosing a dependency.

If the user asks what to do with the blueprint next, that is the honest answer: settle the open
questions, then decompose the decisions into phases a gate can prove.
