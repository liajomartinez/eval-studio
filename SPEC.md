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

### UNKNOWN vs. a flagged-but-unconfirmable FAIL, on hard-required criteria

Not every case where a criterion "can't be confirmed" is a genuine UNKNOWN.
Two situations look similar but aren't:

- **Genuine silence** — no concern is raised, nothing is addressed either
  way. This is UNKNOWN. Example: SyRI's `human_oversight` — no source found
  discusses any review or appeal process at all, for or against.
- **A flagged, unconfirmable risk, where the unconfirmability is caused by
  the evaluated party's own non-disclosure.** On `performance` or
  `bias_fairness` specifically (the hard-required criteria), this defaults
  to **FAIL**, not UNKNOWN. Example: SyRI's `bias_fairness` — a court
  identified a specific, real risk of disparate impact, and could not
  confirm it only because the government withheld how the model worked.

The reasoning: on a hard-required criterion, the burden sits on the pilot to
demonstrate it's fair, not on an outside evaluator to prove harm occurred
after the fact. If a flagged, specific risk that the pilot itself made
unverifiable defaulted to a neutral UNKNOWN, that would let an agency dodge
a fairness failure simply by not disclosing its methodology — rewarding
opacity instead of penalizing it. UNKNOWN is reserved for cases where
nothing was raised at all, not for cases where something was raised and the
evaluated party is the reason it couldn't be settled.

This distinction does not apply to the soft-required criteria
(`human_oversight`, `transparency`, `scale_readiness`), where UNKNOWN
already routes to CONDITIONAL rather than a full abstain — there's less at
stake in getting the FAIL/UNKNOWN line exactly right there.

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

### Sample size vs. a genuine FAIL, on performance specifically

A performance judgment resting on an observed result (e.g. zero detections,
a reported rate) from a sample too small to distinguish a real effect from
noise should be labeled **UNKNOWN**, even if the observed result itself is
negative. **FAIL** is reserved for either a large-enough sample showing a
consistent result, or a clearly missed explicit benchmark.

**Example:** SyRI's `performance` — only 2 of 5 planned analyses were ever
completed, and those 2 detected zero fraud cases. That's too small a sample
to treat "zero" as a proven failure to perform; it's UNKNOWN, not FAIL. This
was a real, live disagreement between a hand-reviewed judgment and the
model's first output on this exact case (the model initially called it
FAIL, reasoning only "it ran, and the result was zero," without weighing
sample size at all) — which is why this rule is written down here and also
built into the prompt in `verdict.py`, not left as an implicit standard the
model has no way to know to apply.

This is a distinct judgment from `scale_readiness`, even though both draw on
the same "2 of 5 completed" fact for SyRI: `performance` asks how much
confidence the observed result deserves, while `scale_readiness` asks
whether the pilot was ever tested at the scale its own mandate anticipated.
The same fact can UNKNOWN one criterion and FAIL the other — that's not a
duplication bug, it's two different questions being asked of one fact.

### Evidence timing: same system vs. a different system

A golden example's evidence can be dated later than the pilot decision it's
judging, as long as it describes **the same, unmodified system** — not a
system that was later changed. Evidence about a subsequently modified or
different version is out of scope, regardless of how directly relevant it
looks.

**In scope:** SyRI's court ruling (2020) evaluated years of the same
system's actual real-world operation, using analysis that wasn't available
in real time when SyRI first launched. REACH VET's `performance` evidence
similarly draws on a 2025 retrospective study of real-world accuracy — but
that study explicitly re-scored patients using "the current REACH VET
methodology... determined in 2017," i.e. the same original model, just
measured later. Both are fair game.

**Out of scope:** REACH VET's later "RV 2.0" update is a different,
structurally changed system (retrained model, added subgroup-consistency
testing). Using RV 2.0's evidence to judge the original 2017 rollout
decision would mean judging that decision on facts about something that
didn't exist yet — that's not "evidence surfacing later," it's evidence
about a different pilot. This is why REACH VET's golden example (see
`golden_examples.py`) is bounded strictly to pre-RV-2.0 sources, even where
RV 2.0's evidence would have been more flattering.

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
