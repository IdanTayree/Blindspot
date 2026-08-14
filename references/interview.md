# The interview technique

Read this before asking the first question.

The method is Thariq's four-quadrant framing of unknowns, adapted into a live interview. The quadrants are
not a taxonomy to file things under afterwards — each one is found by a *different* move, and knowing which
move produces which quadrant is the whole technique.

## The four quadrants and how each is actually found

| | They can state it | They cannot state it |
|---|---|---|
| **They know it** | **known known** — direct questions | **unknown known** — they explain something they assumed was obvious |
| **They don't** | **known unknown** — their own deferrals | **unknown unknown** — collisions between their answers |

### Known knowns — direct questions

The cheapest quadrant. Ask, and write it down. It fills fastest and it is the least valuable per question,
which is worth remembering when the count looks impressive.

### Known unknowns — listen for deferrals

They arrive in phrases like *"we'll have to figure out the threshold"*, *"and etc"*, *"I'm not sure yet"*.
Record them as open rather than pressing — an unknown the user knows they have is not a risk, it is a
scheduled decision. Pressing for an answer they do not have produces a guess that then gets built.

### Unknown knowns — listen for "obviously" and "of course"

This is the quadrant people underestimate. It contains everything so obvious to them that they never thought
to say it — and it is often load-bearing.

**The tell is in the language.** When someone says *"of course"*, *"obviously"*, *"as I said"*, *"I mean"*,
or explains something as if you should already have known it, they are handing you an unknown known. Capture
it verbatim and mark it, because it usually reframes something already written down.

The other reliable source: ask them to explain a term they have used casually. "You said abilities and skills
in the same sentence — what's the difference in your head?" The answer is almost always a design principle
they have never written anywhere.

### Unknown unknowns — collisions, and nothing else

**Open questions do not produce this quadrant.** You cannot ask "what haven't you thought of?" and get an
answer. It appears when two things they have already said are put side by side and cannot both be true.

So after each answer, spend a moment scanning the decisions already recorded for a pair that conflicts. Then
ask about the conflict, plainly, naming both sides:

> "Two of your answers pull against each other. You want it to work with no internet, and you want it to send
> reminders to your phone. Push notifications need a network. Which gives?"

Common collision seams, useful to check against:

- **Autonomy vs. approval** — they want it to work unattended *and* to approve important decisions.
- **Privacy vs. reach** — local-only *and* accessible from their phone.
- **Free vs. capable** — no running costs *and* a feature that needs a server.
- **Speed vs. quality** — a small fast model *and* work they will not accept if it is mediocre.
- **Capacity vs. ambition** — many things at once *and* one machine.
- **Reversibility vs. simplicity** — undo everything *and* no version control.
- **Openness vs. control** — anyone can contribute *and* nothing untrusted runs.

A collision is not a gotcha. Present it as a design fork with real consequences on both sides, and the user
usually produces a third option better than either — that is the point of the exercise.

## Entering a project that already exists

The more common case, and the more valuable one: someone with code, docs and momentum who says the project
was never planned properly, is full of gaps, or that they can no longer tell what has actually been decided.
By the time anyone notices, the gaps are load-bearing.

The method does not change. The opening does.

### Read before asking

Their README, plan documents, ADRs, issue tracker, directory layout, recent commits. Whatever exists.

This is not optional politeness. An audit that opens by asking things already written in their repo spends
the user's patience on work they have already done, and they answer more shallowly for the rest of the
interview — which costs exactly the depth the audit was for.

### Populate the blueprint from the artefacts, with provenance

Fill the known-knowns from what you read, and mark each entry **from your docs** or **from you**. The
distinction earns its keep quickly: a decision written in a document nobody has revisited in six months is
not the same as one they confirmed a minute ago, and the gap between those two is frequently the thing they
came to find.

Where an artefact and the person contradict each other, that is not an error to resolve quietly — it is a
finding. Show both and ask which is true now.

### Open with a collision, not with a question

The single highest-yield move available on an existing project. Decisions made months apart contradict each
other constantly, because nobody has ever put them side by side — and the person is far too close to the
project to see it. Run the collision pass over what already exists *before* asking anything new, and open
with the sharpest one you find.

It also establishes immediately that this is not a form to fill in.

### Name the untouched areas out loud

What does a project of this shape normally have to decide that theirs never has? List them plainly. That list
is usually the reason they came, and seeing it written down is often the most valuable single message in the
interview.

### Expect it to run longer

Longer than from-scratch, not shorter. An existing project brings its own contradictions with it, and every
document you read raises questions a blank page never would. Say so early, so the length reads as thoroughness
rather than drift.

## The progress table, every ten questions

Show this **unprompted, every ten answers**, and again at the end. Two reasons: a long interview with no
visible horizon feels endless even when it is going well, and a quadrant that has quietly stopped producing
looks exactly like a finished one from the inside.

```markdown
| Quadrant | Entries | How they were found | Still producing? |
|---|---:|---|---|
| Known knowns | 21 | direct questions | yes — fastest, and cheapest |
| Known unknowns | 7 | their own deferrals | shrinking |
| Unknown knowns | 8 | "obviously" moments | slowing |
| Unknown unknowns | 6 | collisions between their answers | yes, rate halved |
```

Alongside it, always give:

- **The spawn rate** — new open questions per answer over the last ten. Early on, roughly one. Converged is
  below one per three (below one per two at level 1).
- **Areas nothing has touched yet**, named explicitly. A coverage claim nobody can check is worth nothing,
  and this list is how the user spots the gap that matters to them.
- **A rough estimate of what remains**, computed as below.

### Estimating what remains

Do not guess this, and do not quote the level's rough length back at them — by question 20 you have real data
about *this* interview.

```
direct    = open questions on the list + (untouched areas × ~3 questions each)
spawn (s) = new open questions per answer, over the last ten
remaining ≈ direct ÷ (1 − s)          # when s < 1
```

The division is the part people skip. Each answer spawns roughly `s` further questions, and those spawn more
in turn, so the true remaining count is the geometric sum — not the count of questions currently on the list.
At `s = 0.5`, fifteen open questions actually mean about **thirty** more. When `s` is close to 1, the idea is
still expanding and no meaningful estimate exists; say that instead of inventing a number.

**Always express it as a range with a `+`** — "roughly 20–30+ more" — and say what would change it. The count
is a property of how much their answers spawn, not of the project, and a number stated flatly becomes a
target they start answering *towards*, which is the opposite of what this is for.

Revise it openly when it moves. An estimate that halves because the interview converged is useful
information; an estimate silently held constant is not.

## The blueprint file

Create it before the first question and append after every answer. Structure:

```markdown
# <Idea> — blueprint

- **Status:** interview in progress · started <date>
- **The idea, in one line:** <their sentence, reflected back and confirmed>

## The record

### Q1 — <what the question was about>
<Their answer, in their own words. Quote the load-bearing sentences verbatim.>

*Consequence:* <what this implies for the build — kept visibly separate from their words>

### Q2 — …

## Progress, by quadrant
<the table>

## Assumptions made without asking
- <each one, so they can be corrected>

## Areas not yet touched
- <named explicitly>

## Components to build
<the list phase 2 harvests against — one entry per part>
```

Two rules about this file:

- **Their words and your reading stay separate.** When those blur, theirs win — you are recording a decision,
  not authoring one.
- **Write after every answer, not at the end.** An interview held only in conversation dies when the context
  window fills, and forty minutes of their decisions go with it.

## The three depth levels, in practice

The level is chosen in the first message and can move at any time. What follows is the same interview run at
three different altitudes — the *technique* never changes, only the vocabulary, the depth of probing, and how
hard collisions get pushed.

### Level 1 — absolute beginner

They know exactly what they want and nothing about how software is built. The risk is not that they answer
badly; it is that they **stop answering**, because a question they cannot parse feels like a test they are
failing. Everything here protects against that.

- **Every question is two options in plain words**, each with a plain consequence. Not three, not open.
- **No jargon at all.** Not "authentication" — "how people prove it's them". Not "offline-first" — "does it
  need to work with no internet?"
- **Never ask about implementation.** Frameworks, databases, hosting, languages: assume them, state the
  assumption, and move on. They cannot choose between Postgres and SQLite, and asking teaches them nothing.
- **Collisions are raised gently**, one side at a time: *"Earlier you said nobody should need an account.
  This part needs to know who someone is to save their bookings. Which matters more?"*
- **Stop earlier** — typically 20–35+ questions, or once the spawn rate drops below one new question per two
  answers. Past that, the remaining questions are decisions they have no basis to make, and a bad answer is
  worse than a written assumption.

Example of the same question at this level:

> **Q:** Should people be able to use it without making an account?
> **Yes** — anyone can try it instantly, but nothing they do is saved if they close it.
> **No** — everything is saved and syncs to their phone, but some people leave rather than sign up.

### Level 2 — moderate

They have shipped something before. They know what a database is; they may not know what a durable execution
engine is.

- **Choices for technical decisions, open questions for product ones.** They have real opinions about what
  the thing should do, and fewer about how to build it.
- **Jargon with a one-clause gloss:** "a queue that survives a restart — so a crash doesn't lose the work".
- **Depth stops at broad shape**: local or hosted, web or native, who pays, what happens offline. Not
  library selection — that is what the harvest is for.
- **Collisions raised plainly**, both sides at once, as a fork with consequences.
- Typically 45–70+ questions.

### Level 3 — pro

They know the stack and will find hand-holding irritating.

- **Open questions.** Forced choices only when they genuinely stall, and then just for that question.
- **Assume the vocabulary.** No glosses, no explaining.
- **Go to implementation depth** — failure modes, concurrency, durability, licences, what happens at 3am when
  nobody is watching. This is where a pro-level interview earns its keep, because these are the questions
  that get skipped and then cost weeks.
- **Chase collisions hard**, and say plainly when two answers cannot both hold. A pro will usually produce a
  third option better than either side of the fork — that is the single highest-value moment in the method.
- **Correct false premises directly and briefly.** At this level they would rather be told than humoured.
- 80–120+ questions, until the spawn rate genuinely converges — and materially more when the project already exists, since every artefact read raises questions a blank page never would. A pro-level interview on a half-planned project passing 100 questions and still producing new material is normal, not a sign something has gone wrong.

## Tone

Short. Bottom line first. The user is thinking hard about their own idea; long replies interrupt that. Two or
three lines of consequence, then the next question.

Never flatter an answer ("great question!"). If an answer is genuinely good, say what makes it good in a
clause — *"that's better than what I proposed, because it delegates the judgement instead of escalating the
interruption"* — and move on. Specific beats enthusiastic.

## When they ask you a question

They will, and it is a good sign — it means the interview turned into a design conversation. Answer it
properly, with a real recommendation rather than a list of options, then return to the loop with the next
question. Do not let a question from them end the interview by accident.
