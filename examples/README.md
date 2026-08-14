# Examples

What the two phases actually produce.

| File | What it is |
|---|---|
| [`blueprint.md`](blueprint.md) | **Phase 1 output** — a short illustrative interview, showing how decisions, consequences, collisions, assumptions and untouched areas get recorded. Invented, and labelled as such. |
| [`harvest.json`](harvest.json) | **Phase 2 input** — the ranking spec you write: components, ranked candidates, and each entry's `why` / `promote` / `fit`. Taken from a real harvest, with the project's identity genericised. |
| [`dashboard.html`](dashboard.html) | **Phase 2 output** — the rendered page. Open it in a browser; it is self-contained. |

The split between `harvest.json` and the dashboard is the important part: **you write the judgement, the
scripts write the facts.** Nothing in the spec file contains a star count or a date — those come from
`verify_repos.py` at render time, which is what stops a recalled number reaching the page.

Rebuild the dashboard from these files:

```bash
python3 ../scripts/verify_repos.py --file repos.txt > verified.json
python3 ../scripts/build_dashboard.py harvest.json verified.json dashboard.html
```

Look at `harvest.json` before writing your own — particularly the `promote` fields. They are the line that
makes a ranked list usable months later, when the first choice has hit a wall and nobody remembers why it was
first.
