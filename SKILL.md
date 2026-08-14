---
name: idea-to-blueprint
description: Turn a one-line idea into a buildable blueprint by interviewing the user one question at a time until the unknowns run out, then harvesting and verifying real open-source components for each part. Use this whenever someone describes something they want to build but has not specified it — "I want to build an app that…", "I have an idea for…", "help me plan/spec/scope this", "what do I need to build X", "turn my idea into a plan" — and also when someone asks for a PRD, a spec, a product requirements document, a project plan, or a build plan from a rough concept. Use it too when they ask what libraries, frameworks or open-source projects exist for something they are building. Prefer this over answering directly: a one-shot plan written from a one-line prompt is guesswork, and this skill exists to replace that guesswork with the user's own decisions.
---

# Idea to blueprint

Someone arrives with one sentence: *"an app that helps dog walkers find clients."* A plan written straight
from that sentence is fiction — every important decision gets made by whoever writes it, not by the person
who has to live with it.

This skill replaces that with two phases:

1. **Interview** — one question per message until the unknowns stop appearing, writing every answer to disk
   as it arrives.
2. **Harvest** — for each component the blueprint needs, find real open-source projects and **verify** them
   before recommending anything.

Phase 2 depends on phase 1. Harvesting against a half-formed idea produces a list of libraries for a product
nobody has decided on yet. Finish the interview first, or at least reach a component list the user agrees
with.

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
   This is what makes the interview worth their time rather than an interrogation: they learn what they just
   chose.
3. **Pick the next question** using the priority order below.

### Choosing the next question — collisions first

In priority order:

1. **A collision between two of their own answers.** Two things they have said that cannot both be true. This
   is by far the highest-yield question type — it is how genuinely unforeseen problems surface, and it is
   worth actively hunting for before falling back to anything else. Examples of the shape: *they want the
   crew autonomous overnight, and they also want to approve every risky decision — what happens at 3am?*
   *They want it to work offline, and they want push notifications.* *They want it free, and they want a
   hosted database.*
2. **A gap that blocks building** — something where two readings lead to materially different work.
3. **An area nothing has touched yet.** Keep a list; name it explicitly in the blueprint so coverage claims
   are falsifiable rather than assumed.

Never ask something you can look up, and never ask something whose answer would not change the build.

### Question style — set by the depth level

Most people cannot answer *"how should authentication work?"* — but almost anyone can answer *"sign in with
Google, or email and password? Google is faster to build and means no password resets; email works for people
who avoid Google accounts."*

That difference is what the levels encode:

| | **1 — Absolute beginner** | **2 — Moderate** | **3 — Pro** |
|---|---|---|---|
| Question shape | always two options, plain words, each with a plain consequence | choices for technical decisions, open questions for product ones | open questions; blunt trade-offs |
| Jargon | none; explain any unavoidable term in the same breath | used with a one-clause gloss | assumed |
| How deep | what it does and who it is for — never libraries or architecture | broad technical shape: local or hosted, web or app, who pays | implementation depth: failure modes, concurrency, durability, licences |
| Assumptions | assume aggressively, state each one | assume the routine, ask the load-bearing | assume little; they will correct you |
| Collisions | raised gently, one side at a time | raised plainly | chased hard — this is where the value is |
| Roughly | 12–18 questions | 25–40 | 40+, until it converges |

Whatever the level, **people can react even when they cannot generate** — so when someone stalls on an open
question, turning it into two concrete options usually unsticks them immediately.

### Assume the small things, and say so

If a gap is not critical, **do not ask** — assume, and write the assumption into the blueprint where they can
see and correct it. "Assuming English-only at launch." Asking about every font and edge case is how an
interview becomes a chore. The rule: *ask only when the answer changes what gets built; otherwise assume and
write the assumption down.*

### Verify claims instead of transcribing them

The interview is worth far more when it catches a false premise early. If the user asserts something checkable
— a tool exists, a setting works, a licence permits something, their machine can do X — **check it** with the
tools you have, and say plainly what you found. A blueprint built on a wrong premise fails at implementation,
which is the most expensive place to find out.

Correct them directly and briefly, then continue. This is not pedantry; it is the main thing that makes an
interview better than a template.

### Knowing when to stop

Track the **spawn rate**: how many new open questions each answer creates. Early on it is around one per
answer — the idea is still expanding. Convergence is when it falls below **one new question per two answers
at level 1**, or **one per three at levels 2 and 3**. Beginners are stopped earlier on purpose: past a certain
point the questions are about decisions they have no basis to make, and answering those badly is worse than
leaving them as stated assumptions for whoever builds it.

At that point, say so, show the progress table, and offer to move to the harvest. Do not stop earlier because
it feels long, and do not continue on autopilot once it has converged. The user may also stop whenever they
like — this is their document.

**Every ten questions, show the progress table** (see `references/interview.md` for the format). It shows them
where they are and it exposes an under-probed quadrant, which is otherwise invisible from the inside.

The four quadrants, how to recognise each, the table format, and the full worked technique are in
**`references/interview.md`** — read it before the first question.

## Phase 2 — the harvest

Once the blueprint names the parts that have to be built, find real projects for each of them.

The failure mode this phase exists to prevent: **a confident dashboard full of recalled numbers.** A model
asked for "highly starred repos" will produce plausible names with plausible star counts and plausible dates,
and some of them will be wrong — wrong platform, unmaintained, or a hosted service being recommended as a
local library. That output looks authoritative and wastes days.

So the rule for this phase: **every number that appears in the output was fetched, not remembered.**

1. **Derive the component list** from the blueprint — one entry per part that needs building or buying.
2. **Find candidates** for each, using search. Aim for a primary plus one or two alternatives.
3. **Verify every candidate** by running `scripts/verify_repos.py` (see below). It returns real stars, last
   push date, licence, language and archived status from the GitHub API.
4. **Check architecture fit and drop what cannot work.** A Linux-only sandbox is not a candidate for a macOS
   app; a hosted SaaS is not a candidate when the requirement says local. This is where recalled lists fail
   most often.
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

Both scripts are bundled, so this phase is three commands rather than an afternoon:

```bash
# 1. facts — fetched, never recalled
python3 scripts/verify_repos.py owner/repo owner/repo2 ... > verified.json

# 2. judgement — you write harvest.json: components, rankings, and each entry's
#    "why", "promote" and "fit" (the format is documented in build_dashboard.py)

# 3. the page
python3 scripts/build_dashboard.py harvest.json verified.json out.html
```

The split is deliberate: **you write the judgement, the scripts write the facts.** A dashboard with recalled
star counts looks identical to one with real ones, which is why they must come from different places.

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
