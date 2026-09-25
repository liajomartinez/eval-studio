# Eval Studio — Pilot Readiness Tool: Spec (v1)

## What it does

Takes a structured description of one government AI pilot and returns a
readiness verdict — `READY`, `CONDITIONAL`, `NOT READY`, or `ABSTAIN` — along
with per-criterion reasoning that points back to the specific part of the
input it's grounded in.

## Input format (v1: structured, not free text)

A dictionary with one text field per criterion. Free text *within* each field
is fine (that's what the model reasons over) — what's structured is which
field a given piece of evidence belongs to. Free-text-only input (where the
tool has to figure out which sentence is about what) is a stretch goal for
later, not v1.

```python
pilot = {
    "pilot_name": "...",
    "agency": "...",
    "summary": "...",  # what the AI does, who it affects
    "criteria": {
        "performance": "...",       # eval methodology + results, or "" if not addressed
        "bias_fairness": "...",
        "human_oversight": "...",
        "transparency": "...",
        "scale_readiness": "...",
    },
}
```

An empty string (or missing key) for a criterion means "not addressed" —
that's what drives `UNKNOWN` below, not the tool guessing from silence.

## The five criteria

1. **performance** — did the eval show the system meets an accuracy/error-rate
   bar appropriate to its use case?
2. **bias_fairness** — was the system tested across affected subgroups, and
   did it pass?
3. **human_oversight** — is there a human-in-the-loop or appeal process for
   people affected by a decision?
4. **transparency** — can affected people learn an AI was involved and how to
   contest it?
5. **scale_readiness** — was the pilot tested at a scale relevant to full
   rollout, or only a small sample?

**performance** and **bias_fairness** are *hard-required*: safety-critical,
no exceptions. **human_oversight**, **transparency**, and **scale_readiness**
are *soft-required*: process gaps that are reasonable to flag as "fix before
scaling" rather than an automatic disqualifier.

## Per-criterion output

For each of the 5 criteria, the tool returns:

- `status`: `PASS`, `FAIL`, or `UNKNOWN`
- `explanation`: a short, reasoned sentence for why
- `evidence`: a verbatim quote from that criterion's input field the verdict
  is grounded in — `None` if `status` is `UNKNOWN` (there's nothing to quote)

This makes the reasoning checkable against the source, not just asserted —
which matters later when we run independent grading passes and need to
diagnose disagreements.

## Overall verdict logic

Evaluated in this priority order (highest first):

1. **NOT READY** if `performance` or `bias_fairness` is `FAIL` — hard fail,
   no exceptions. Checked first: a documented failure must never be
   overridden by missing documentation elsewhere. If thin evidence on other
   criteria could turn a known failure into an abstain, that's a bad
   incentive — it would reward incomplete pilot writeups.
2. **ABSTAIN** if 3 or more of the 5 criteria are `UNKNOWN` (and rule 1
   didn't already fire) — at that point there isn't enough input to judge
   fairly at all.
3. **ABSTAIN** if `performance` or `bias_fairness` is `UNKNOWN` (and neither
   rule above fired) — can't judge a hard-required criterion without
   evidence.
4. **CONDITIONAL** if any of `human_oversight`, `transparency`, or
   `scale_readiness` is `FAIL` or `UNKNOWN`.
5. **READY** — everything else (all criteria `PASS`).

### Decided: performance is judged, not thresholded

**Decision:** `performance` is a model judgment call, like the other four
criteria — not a hardcoded numeric threshold. The model must state, as part
of its `explanation`, what bar it judged the evidence against and why.

**Why:**

- **Consistency.** The other four criteria (`bias_fairness`,
  `human_oversight`, `transparency`, `scale_readiness`) have no numeric
  threshold to check against — they're already reasoned judgment calls.
  Making `performance` uniquely deterministic while everything else is
  judgment-based is an inconsistent design with no real justification.
- **A hardcoded number has nothing to compare against for some real pilots.**
  The SyRI golden example (`golden_examples.py`) is the concrete case that
  ruled this out: its performance evidence is Dutch investigative reporting
  that zero fraud cases were detected across the completed analyses — not a
  percentage, an AUC, or any other clean metric a threshold check could read.
  Pilots also report wildly different metrics (accuracy, AUC, F1, false
  positive rate, or plain prose) — one fixed number can't be compared
  meaningfully across all of them, and reliably extracting "the number" from
  free text is itself a hard, error-prone problem, not an easier one.
- **The right bar plausibly varies by use case anyway** (a fraud detector and
  a diagnostic tool don't need the same accuracy floor), which argues for
  judgment over a single fixed number regardless of the extraction problem.

**Trade-off accepted:** this is less mechanically reproducible than a
threshold check — the same input isn't guaranteed byte-identical output
across runs. What keeps it from being an unaccountable black box is the same
rule applied everywhere else in this spec: the model must ground its call in
`evidence` and explain its reasoning, including the bar it applied, so the
verdict is checkable and arguable rather than just asserted.

## Output shape (draft)

```python
result = {
    "verdict": "CONDITIONAL",
    "criteria": {
        "performance": {"status": "PASS", "explanation": "...", "evidence": "..."},
        "bias_fairness": {"status": "PASS", "explanation": "...", "evidence": "..."},
        "human_oversight": {"status": "UNKNOWN", "explanation": "...", "evidence": None},
        "transparency": {"status": "PASS", "explanation": "...", "evidence": "..."},
        "scale_readiness": {"status": "PASS", "explanation": "...", "evidence": "..."},
    },
}
```

## Golden examples (next step)

Test cases sourced from real, public AI pilots, each with a hand-written
expected verdict + per-criterion breakdown. These are what we check the
tool's actual output against — see `golden_examples.py`.
