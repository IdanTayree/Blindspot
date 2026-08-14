# idea-to-blueprint

A Claude skill that turns one sentence into something you can actually build.

You arrive with *"an app that helps dog walkers find clients."* A plan written straight from that sentence is
fiction — every decision that matters gets made by whoever writes it, not by the person who has to live with
it. This skill replaces that with two phases:

1. **Interview** — one question per message until the unknowns stop appearing, writing every answer to disk as
   it arrives.
2. **Harvest** — for each component the blueprint needs, find real open-source projects and **verify** them
   before recommending anything.

You end with a blueprint document containing your own decisions, and a dashboard of components with numbers
that were fetched rather than remembered.

## Why it is not just "ask me some questions"

The interview is built on Thariq's four-quadrant framing of unknowns, and the useful part is that **each
quadrant is found by a different move**:

| | You can state it | You cannot state it |
|---|---|---|
| **You know it** | known known — direct questions | **unknown known** — you explain something you assumed was obvious |
| **You don't** | known unknown — your own deferrals | **unknown unknown** — collisions between your answers |

The bottom-right box is the one that matters, and **open questions never produce it.** You cannot ask someone
"what haven't you thought of?" It appears when two things you already said are placed side by side and cannot
both be true:

> "You want it to work with no internet, and you want reminders on your phone. Push notifications need a
> network. Which gives?"

In the interview this skill was built from, *every single* unknown-unknown came from a collision like that,
and none came from an open question. So the skill hunts for collisions first and falls back to open questions
only when it cannot find one.

Three other things it does deliberately:

- **Forced choices by default.** "Sign in with Google, or email and password? Google is faster to build and
  means no password resets; email works for people who avoid Google accounts." People can react even when they
  cannot generate — which is what makes this usable by someone without a technical background. It escalates to
  open questions when you show you have opinions.
- **Assume the small things and say so.** Non-critical gaps become written assumptions you can correct, rather
  than questions that turn an interview into a chore.
- **Check claims instead of transcribing them.** If you assert something checkable — a tool exists, a licence
  permits something, your machine can do X — it verifies with the tools it has. A blueprint built on a false
  premise fails at implementation, which is the most expensive place to find out.

## Why the harvest verifies everything

Ask any model for "the best highly-starred repos for X" and it answers fluently from memory. The names are
usually real. **The numbers are not.**

This was measured while building the skill. A generated component dashboard was checked against the live
GitHub API:

| Repo | Dashboard claimed | Actual |
|---|---|---|
| langchain-ai/langgraph | ★ 15k+ | 39,660 |
| crewAIInc/crewAI | ★ 25k+ | 57,067 |
| e2b-dev/E2B | ★ 8k+ | 13,392 |
| modelcontextprotocol/servers | "★ Active Standard" | 89,556 |

Every count was wrong, low by up to 2.6×, and the largest project in the list had no number at all. Two
licences and languages were also wrong — and one recommendation was a Linux-only tool proposed for a macOS
app, which is the failure that actually costs days.

So the rule for phase 2 is simple: **every number in the output was fetched.** Anything that could not be
fetched is labelled unverified rather than filled in from memory.

## Install

Clone into your skills directory:

```bash
git clone git@github.com:IdanTayree/idea-to-blueprint.git ~/.claude/skills/idea-to-blueprint
```

Then start a Claude session and describe an idea. The skill triggers on things like *"I want to build…"*,
*"help me spec this"*, *"turn my idea into a plan"*, or a request for a PRD.

## Using the verifier on its own

The repo checker works standalone, with no dependencies beyond Python 3:

```bash
python3 scripts/verify_repos.py langchain-ai/langgraph crewAIInc/crewAI > verified.json
python3 scripts/verify_repos.py --file repos.txt        # one owner/repo per line
```

It returns stars, last push date, freshness, licence, language and archived status. It uses the `gh` CLI when
installed (5,000 requests/hour instead of 60) and falls back to the public API.

Renames are worth the run on their own. Verifying 60 candidates for one project turned up **nine slugs that
had silently moved** — `microsoft/presidio`, `Byron/gitoxide`, `argmaxinc/WhisperKit`, `block/goose` and
others all redirect now. A stale slug in someone's notes outlives the rename by years.

## Layout

```
idea-to-blueprint/
├── SKILL.md                    the two phases and the loop
├── references/
│   ├── interview.md            the quadrants, collision seams, progress table, output format
│   └── harvest.md              verification protocol and dashboard requirements
└── scripts/
    ├── verify_repos.py         GitHub metadata, fetched not recalled
    └── build_dashboard.py      renders the ranked dashboard from facts + judgement
```

## Licence

MIT. See [LICENSE](LICENSE).
