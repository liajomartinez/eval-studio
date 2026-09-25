"""
Turns a pilot dict (see golden_examples.py / SPEC.md for the shape) into a
readiness verdict.

The work splits into two very different kinds of logic, on purpose:

- Judging each of the 5 criteria (is the evidence a PASS, FAIL, or UNKNOWN?)
  requires understanding messy, real-world English -- that's a job for
  Claude, not for Python's if-statements. See `judge_criteria`.
- Turning those 5 judgments into one overall verdict is a fixed rule we
  already wrote down in SPEC.md ("hard FAIL beats everything," etc.) -- that
  part should be plain, deterministic Python, not another model call, so the
  same 5 judgments always produce the same verdict. See `determine_verdict`.

Keeping those two apart matters: if the tool's answer on a case is ever
wrong, this split tells you where to look -- was a criterion mis-judged
(look at `judge_criteria`'s prompt/output), or was a correctly-judged set of
criteria turned into the wrong verdict (look at `determine_verdict`, which
you can test with plain dictionaries and no API calls at all)?
"""

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-5"

# A list of the five criterion names. Several functions below loop over this
# list instead of repeating "performance", "bias_fairness", ... five times.
CRITERIA = [
    "performance",
    "bias_fairness",
    "human_oversight",
    "transparency",
    "scale_readiness",
]

# A set works like a list for membership checks (`x in HARD_REQUIRED`), but
# it's the more honest tool here: order doesn't matter and there are no
# duplicates, which is exactly true of "which criteria are hard-required."
HARD_REQUIRED = {"performance", "bias_fairness"}


def build_tool_schema():
    """The JSON shape Claude must fill in -- one PASS/FAIL/UNKNOWN judgment
    per criterion, each with an explanation and a verbatim evidence quote."""
    criterion_schema = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["PASS", "FAIL", "UNKNOWN"],
            },
            "explanation": {
                "type": "string",
                "description": (
                    "A short, reasoned sentence for why. For 'performance' "
                    "specifically, state what bar you judged the evidence "
                    "against and why that bar fits this use case."
                ),
            },
            "evidence": {
                "type": ["string", "null"],
                "description": (
                    "A verbatim quote copied exactly from that criterion's "
                    "input text, grounding the status. Must be null if "
                    "status is UNKNOWN -- there is nothing to quote."
                ),
            },
        },
        "required": ["status", "explanation", "evidence"],
    }
    return {
        "name": "submit_pilot_assessment",
        "description": "Submit a PASS/FAIL/UNKNOWN judgment for each of the 5 readiness criteria.",
        "input_schema": {
            "type": "object",
            "properties": {name: criterion_schema for name in CRITERIA},
            "required": CRITERIA,
        },
    }


def build_prompt(pilot):
    """Builds the text Claude reads before judging a pilot. A function, not
    a hardcoded string, because we call this once per pilot with different
    pilot data plugged in."""
    lines = [
        "You are assessing a government AI pilot for scale-readiness.",
        "Judge each of the 5 criteria below using ONLY the evidence given "
        "for that criterion. Do not assume anything not stated.",
        "",
        f"Pilot: {pilot['pilot_name']}",
        f"Agency: {pilot['agency']}",
        f"Summary: {pilot['summary']}",
        "",
    ]
    for name in CRITERIA:
        lines.append(f"## {name}")
        lines.append(pilot["criteria"][name])
        lines.append("")
    lines.append(
        "For each criterion, decide PASS, FAIL, or UNKNOWN. UNKNOWN means "
        "the text genuinely does not address this criterion either way -- "
        "it is not a hedge, and it is not a substitute for FAIL when the "
        "evidence actually describes a problem.\n"
        "\n"
        "Two specific rules that override your first instinct:\n"
        "\n"
        "1. On 'performance' specifically: if the judgment would rest on an "
        "observed result (e.g. zero detections, a reported rate) from a "
        "sample too small to distinguish a real effect from noise, label it "
        "UNKNOWN even if the observed result itself is negative. Reserve "
        "FAIL for either a large-enough sample showing a consistent result, "
        "or a clearly missed explicit benchmark. Example: 2 completed trials "
        "out of 5 planned, both showing zero successes, is too small a "
        "sample to certify FAIL -- that's UNKNOWN.\n"
        "\n"
        "2. On 'performance' or 'bias_fairness' specifically (the two "
        "hard-required criteria): if a real, specific risk or problem is "
        "flagged in the evidence, and it could not be confirmed only "
        "because the pilot itself withheld the information needed to "
        "verify it, label that FAIL, not UNKNOWN. On these two criteria the "
        "burden is on the pilot to demonstrate it's safe and fair -- a "
        "flagged concern the pilot made unverifiable is a failure to meet "
        "that burden, not a neutral absence of evidence. This is different "
        "from genuine silence (nothing raised at all either way), which "
        "stays UNKNOWN."
    )
    return "\n".join(lines)


def judge_criteria(pilot, client=None, model=MODEL):
    """Calls Claude once and returns a dict of the 5 criterion judgments.

    This is the only function in this file that talks to the network -- the
    rest of the logic (determine_verdict) is plain Python you can test
    without an API key at all.
    """
    if client is None:
        client = Anthropic()

    tool = build_tool_schema()
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        tools=[tool],
        tool_choice={"type": "tool", "name": tool["name"]},
        messages=[{"role": "user", "content": build_prompt(pilot)}],
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input

    raise RuntimeError("Claude did not return a tool_use block")


def determine_verdict(criteria_results):
    """Pure Python: applies the SPEC.md priority order to 5 already-judged
    criteria. No model call happens in here.

    criteria_results looks like:
        {"performance": {"status": "FAIL", ...}, "bias_fairness": {...}, ...}
    """
    statuses = {name: criteria_results[name]["status"] for name in CRITERIA}

    # Rule 1: a hard-required criterion that FAILed always wins, checked
    # first, no matter what the other 4 criteria say.
    for name in HARD_REQUIRED:
        if statuses[name] == "FAIL":
            return "NOT READY", (
                f"{name} is a hard-required criterion and it FAILed, so the "
                "verdict is NOT READY regardless of any other criterion -- "
                "a documented failure is never overridden by missing "
                "information elsewhere."
            )

    # Rule 2: too little information anywhere to judge fairly at all.
    unknown_count = sum(1 for status in statuses.values() if status == "UNKNOWN")
    if unknown_count >= 3:
        return "ABSTAIN", (
            f"{unknown_count} of the 5 criteria are UNKNOWN, which is too "
            "little information to judge this pilot fairly either way."
        )

    # Rule 3: a hard-required criterion with no evidence at all.
    for name in HARD_REQUIRED:
        if statuses[name] == "UNKNOWN":
            return "ABSTAIN", (
                f"{name} is hard-required and UNKNOWN -- there is no "
                "evidence to judge a safety-critical criterion by, so the "
                "tool abstains rather than guess."
            )

    # Rule 4: a soft-required criterion that failed or is undocumented is a
    # process gap worth flagging, but not a hard blocker.
    soft_criteria = [name for name in CRITERIA if name not in HARD_REQUIRED]
    problem_soft = [
        name for name in soft_criteria if statuses[name] in ("FAIL", "UNKNOWN")
    ]
    if problem_soft:
        return "CONDITIONAL", (
            f"{', '.join(problem_soft)} FAILed or is UNKNOWN -- a process "
            "gap to fix before scaling, but not a hard-required failure."
        )

    # Rule 5: nothing left to disqualify it.
    return "READY", "All 5 criteria PASSed."


def evaluate_pilot(pilot, client=None, model=MODEL):
    """The function the rest of the project calls: judge every criterion,
    then apply the fixed rule to get one verdict."""
    criteria_results = judge_criteria(pilot, client=client, model=model)
    verdict, verdict_reason = determine_verdict(criteria_results)
    return {
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "criteria": criteria_results,
    }


if __name__ == "__main__":
    from golden_examples import EXAMPLES

    client = Anthropic()
    for example in EXAMPLES:
        result = evaluate_pilot(example["pilot"], client=client)
        print(f"{example['name']}: {result['verdict']}")
        print(json.dumps(result, indent=2))
        print()
