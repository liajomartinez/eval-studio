"""
Golden examples for the pilot readiness tool.

A "golden example" is a worked example where a human (us) decided the right
answer by hand, ahead of time, from real public evidence. Later, when the
actual tool runs on the same input, we compare its answer to ours. If they
disagree, that's a bug (or a spec gap) to investigate -- not something to
paper over.

Two Python concepts do all the work in this file:

- a dictionary (the `{key: value}` blocks below) groups related facts under
  named labels -- e.g. one pilot's `criteria` dictionary holds five text
  fields, one per criterion, so the tool can look up "performance" instead of
  guessing which paragraph is about what.
- a list (the `EXAMPLES = [ ... ]` at the bottom) is just an ordered
  collection -- here, a collection of examples the tool will be checked
  against one by one.

Both cases below are grounded in real public findings (court rulings,
independent commissioned evaluations, academic audits) rather than invented
numbers. Where the public record is genuinely silent on a criterion, that is
recorded as UNKNOWN rather than filled in -- see SPEC.md for why guessing
isn't acceptable here. Only aggregate, system-level findings are used; no
individual case data appears anywhere in this file.
"""

syri = {
    "name": "syri_netherlands",
    "pilot": {
        "pilot_name": "SyRI (Systeem Risico Indicatie / System Risk Indication)",
        "agency": "Dutch Ministry of Social Affairs and Employment, deployed via participating municipalities",
        "summary": (
            "SyRI cross-referenced government data on individuals (tax, benefits, "
            "employment, and other records) to flag people as 'high risk' for social "
            "welfare, benefits, or tax fraud. Flagged profiles were referred for "
            "further investigation in the municipality that had requested the analysis."
        ),
        "criteria": {
            # UNKNOWN: only 2 of 5 requested analyses were ever completed; zero
            # detections at n=2 is statistical insufficiency, not a general
            # "small samples don't count" rule -- see scale_readiness below,
            # which shares this same n=2 limitation.
            "performance": (
                "Between 2014 and 2019, five Dutch municipalities requested a SyRI "
                "risk analysis of a neighborhood, but only two of those five projects "
                "were actually carried out. Dutch investigative reporting in 2019 found "
                "that none of the completed SyRI analyses had led to a newly detected "
                "fraud case being identified through the system."
            ),
            # FAIL: court flagged a specific disparate-impact risk,
            # unconfirmable only because the government withheld disclosure --
            # burden defaults against the pilot on hard-required criteria,
            # per SPEC.md's UNKNOWN-vs-flagged-FAIL rule.
            "bias_fairness": (
                "The government never disclosed the specific risk indicators or "
                "scoring logic SyRI used. The District Court of The Hague noted a risk "
                "that the system could disproportionately flag people in "
                "lower-income neighborhoods, but the court stated that because the "
                "model's inner workings were never revealed, it could not be verified "
                "whether SyRI actually used a discriminatory model."
            ),
            # UNKNOWN: genuine silence, not a flagged-and-blocked risk like
            # bias_fairness above -- no source raises an oversight concern
            # either way, so this stays UNKNOWN under SPEC.md's rule.
            "human_oversight": (
                "Public reporting describes SyRI as producing a risk flag that would "
                "trigger further investigation by a municipality, but no source found "
                "documents a specific review process, appeal mechanism, or human "
                "sign-off procedure that applied to a flagged individual before "
                "consequences followed."
            ),
            # FAIL: a direct court ruling on this exact question, not an
            # inference from indirect evidence.
            "transparency": (
                "In February 2020, the District Court of The Hague ruled that SyRI "
                "violated the right to privacy under Article 8 of the European "
                "Convention on Human Rights. The court specifically found that the "
                "transparency principle was not met, because there was no public "
                "insight into the risk indicators or how the risk model worked."
            ),
            # FAIL: direct factual count of rollout against the legislature's
            # own anticipated scope (5 requested), not a statistical inference
            # about effectiveness -- contrast with performance above, where
            # the same n=2 fact instead raises statistical-insufficiency doubt.
            "scale_readiness": (
                "Only two of the five municipality-level analyses ever requested "
                "under the SyRI legislation were actually completed before the "
                "system was struck down by the court in 2020."
            ),
        },
        "sources": [
            "https://www.loc.gov/item/global-legal-monitor/2020-03-13/netherlands-court-prohibits-governments-use-of-ai-software-to-detect-welfare-fraud/",
            "https://algorithmwatch.org/en/syri-netherlands-algorithm/",
            "https://digitalfreedomfund.org/case-studies/the-syri-welfare-fraud-risk-scoring-algorithm/",
            "https://iapp.org/news/a/digital-welfare-fraud-detection-and-the-dutch-syri-judgment",
        ],
    },
    "expected": {
        "verdict": "NOT READY",
        "criteria": {
            "performance": {
                "status": "UNKNOWN",
                "explanation": (
                    "Only 2 of 5 requested analyses were ever completed. Zero "
                    "detections at that sample size (n=2) is statistical "
                    "insufficiency, not proof the system doesn't work -- this "
                    "is a specific n=2 judgment, not a blanket claim that "
                    "small samples never count. Note the same n=2 limitation "
                    "also caps confidence in scale_readiness below."
                ),
                "evidence": None,
            },
            "bias_fairness": {
                "status": "FAIL",
                "explanation": (
                    "A court identified a specific, real risk of disparate "
                    "impact on lower-income neighborhoods, and could not "
                    "confirm it only because the government withheld how the "
                    "model worked. On a hard-required criterion the burden "
                    "sits on the pilot to demonstrate fairness -- a flagged "
                    "risk the pilot itself made unverifiable is a failure to "
                    "meet that burden, not a neutral absence of evidence "
                    "(contrast with human_oversight below, where nothing was "
                    "raised at all)."
                ),
                "evidence": (
                    "The District Court of The Hague noted a risk that the "
                    "system could disproportionately flag people in "
                    "lower-income neighborhoods"
                ),
            },
            "human_oversight": {
                "status": "UNKNOWN",
                "explanation": (
                    "The record describes what SyRI's output was used for in "
                    "general terms, but documents no specific human review or "
                    "appeal procedure that applied to a flagged individual."
                ),
                "evidence": None,
            },
            "transparency": {
                "status": "FAIL",
                "explanation": (
                    "A court explicitly ruled the transparency requirement was "
                    "not met, finding no public insight into the model's "
                    "indicators or logic."
                ),
                "evidence": (
                    "the transparency principle was not met, because there was "
                    "no public insight into the risk indicators or how the risk "
                    "model worked"
                ),
            },
            "scale_readiness": {
                "status": "FAIL",
                "explanation": (
                    "Fewer than half of the municipalities that requested a "
                    "SyRI analysis ever had one completed, indicating the "
                    "system did not demonstrate reliable operation at the "
                    "scale its legislative mandate anticipated."
                ),
                "evidence": (
                    "Only two of the five municipality-level analyses ever "
                    "requested under the SyRI legislation were actually "
                    "completed"
                ),
            },
        },
        "verdict_reason": (
            "bias_fairness is a hard-required criterion and it FAILed (per "
            "SPEC.md's flagged-but-unconfirmable rule), so the verdict is "
            "NOT READY regardless of the two UNKNOWNs elsewhere -- a "
            "documented failure is checked first and is never overridden by "
            "missing information on other criteria."
        ),
    },
}

allegheny = {
    "name": "allegheny_family_screening_tool",
    "pilot": {
        "pilot_name": "Allegheny Family Screening Tool (AFST)",
        "agency": "Allegheny County Department of Human Services (Pennsylvania, USA)",
        "summary": (
            "AFST generates a numeric risk score from administrative data (such as "
            "public benefits, criminal justice, and behavioral health records) for "
            "children referred to Allegheny County's child welfare hotline. The "
            "score is shown to call screeners alongside other information to help "
            "decide whether to open a formal investigation."
        ),
        "criteria": {
            # PASS: real quantitative result from an independent evaluation,
            # with an explicit stated conclusion of improvement over the prior
            # (non-algorithmic) process -- a materially stronger basis than
            # SyRI's performance evidence.
            "performance": (
                "Allegheny County commissioned an independent evaluation, "
                "published in 2019, that measured the tool's predictive accuracy "
                "using the AUC statistic. The published results reported an AUC of "
                "about 74.4% for Black children and about 77.4% for non-Black "
                "children, and the evaluators concluded the tool improved the "
                "accuracy of screening decisions compared to the prior, "
                "non-algorithmic process."
            ),
            # FAIL: multiple independent, affirmative findings of disparity
            # (not a flagged-but-unconfirmed risk like SyRI's), plus an active
            # federal investigation -- documented, not merely suspected.
            "bias_fairness": (
                "The same independent evaluation reported a lower AUC for Black "
                "children (about 74.4%) than for non-Black children (about "
                "77.4%). Separately, researchers found that AFST-generated risk "
                "scores carried forward racial disparities present in the input "
                "data (for example, by using juvenile-probation history and "
                "public-benefits eligibility as risk factors), and a later "
                "academic audit found that children and parents with "
                "disabilities were significantly more likely to receive higher "
                "risk scores across multiple scoring elements. The tool's use of "
                "disability-related indicators is reportedly under review by the "
                "U.S. Department of Justice."
            ),
            # PASS: not just design-on-paper -- there's evidence the human
            # step functions substantively, measurably reducing bias, a
            # stronger bar than a nominal "human in the loop" claim.
            "human_oversight": (
                "AFST is designed as a decision-support input rather than an "
                "automated decision: the risk score is shown to call screeners as "
                "one factor among others, and the screener makes the final call "
                "on whether to open an investigation. Research on the tool's use "
                "found that screeners overriding the tool's score reduced some of "
                "the racial disparities present in the raw algorithmic output."
            ),
            # PASS: concrete, verifiable actions (public methodology doc,
            # published external evaluation), not just a general claim of
            # openness.
            "transparency": (
                "Allegheny County has published a detailed public methodology "
                "document describing how AFST's score is built, and it committed "
                "to and published an independent, external evaluation of the "
                "tool's impact and validity rather than keeping the evaluation "
                "internal."
            ),
            # PASS: full production volume, county-wide, for years -- about
            # as strong a case for this criterion as the evidence gets.
            "scale_readiness": (
                "AFST has been used for every incoming child-maltreatment "
                "referral call screened by Allegheny County's Department of "
                "Human Services since it went live in August 2016, rather than "
                "being limited to a small sample or a single office."
            ),
        },
        "sources": [
            "https://csda.aut.ac.nz/news-and-events/2019/allegheny-family-screening-tool-evaluation-improved-decision-accuracy,-reduced-disparities",
            "https://www.aclu.org/the-devil-is-in-the-details-interrogating-values-embedded-in-the-allegheny-family-screening-tool",
            "https://www.tandfonline.com/doi/full/10.1080/15548732.2026.2689958",
            "https://www.alleghenycountyanalytics.us/wp-content/uploads/2019/05/Methodology-V2-from-16-ACDHS-26_PredictiveRisk_Package_050119_FINAL-7.pdf",
            "https://www.pbs.org/newshour/nation/ap-report-doj-examining-ai-screening-tool-used-by-pa-child-welfare-agency",
        ],
    },
    "expected": {
        "verdict": "NOT READY",
        "criteria": {
            "performance": {
                "status": "PASS",
                "explanation": (
                    "An independent evaluation was commissioned and published, "
                    "reporting quantitative accuracy figures (AUC in the mid-70s "
                    "for both groups) and concluding the tool improved accuracy "
                    "over the prior, non-algorithmic process."
                ),
                "evidence": (
                    "the evaluators concluded the tool improved the accuracy of "
                    "screening decisions compared to the prior, non-algorithmic "
                    "process"
                ),
            },
            "bias_fairness": {
                "status": "FAIL",
                "explanation": (
                    "Multiple independent analyses found the tool scored Black "
                    "families and families with disabilities less accurately or "
                    "more harshly than the general population -- the disability "
                    "disparity is significant enough to have drawn a federal "
                    "investigation."
                ),
                "evidence": (
                    "children and parents with disabilities were significantly "
                    "more likely to receive higher risk scores across multiple "
                    "scoring elements"
                ),
            },
            "human_oversight": {
                "status": "PASS",
                "explanation": (
                    "The tool is structured so a human screener retains the "
                    "final decision, and research specifically found human "
                    "overrides reduced bias present in the raw score -- evidence "
                    "the oversight step is more than a formality."
                ),
                "evidence": (
                    "screeners overriding the tool's score reduced some of the "
                    "racial disparities present in the raw algorithmic output"
                ),
            },
            "transparency": {
                "status": "PASS",
                "explanation": (
                    "The county published its own methodology documentation and "
                    "commissioned an external, publicly released evaluation, a "
                    "substantially more transparent posture than an undisclosed "
                    "model."
                ),
                "evidence": (
                    "it committed to and published an independent, external "
                    "evaluation of the tool's impact and validity rather than "
                    "keeping the evaluation internal"
                ),
            },
            "scale_readiness": {
                "status": "PASS",
                "explanation": (
                    "The tool has operated at full county-wide referral volume "
                    "for multiple years, direct evidence it functions at real "
                    "deployment scale rather than a small trial."
                ),
                "evidence": (
                    "AFST has been used for every incoming child-maltreatment "
                    "referral call screened by Allegheny County's Department of "
                    "Human Services since it went live in August 2016"
                ),
            },
        },
        "verdict_reason": (
            "bias_fairness is a hard-required criterion and it FAILed, so the "
            "verdict is NOT READY even though every other criterion PASSed -- "
            "good process elsewhere does not offset a documented fairness "
            "failure."
        ),
    },
}

# The list every other part of the project will loop over when checking the
# tool's answers against ours.
EXAMPLES = [syri, allegheny]

# TODO: future golden example, ABSTAIN path (no coverage yet).
#
# IRS AI-assisted National Research Program (NRP) audit-case-selection pilot
# (piloted since the 2019 filing season: 4,000 returns selected via the new
# AI-informed process alongside an equal share via traditional selection).
#
# Sourcing so far stopped after a quick performance check, per SPEC.md's
# rule that a hard-required criterion (performance/bias_fairness) landing on
# UNKNOWN triggers ABSTAIN outright -- no need to source the other 4
# criteria to know this pilot's verdict path, so they were never built out.
#
# performance -> UNKNOWN. GAO's report on this pilot (GAO-24-106449)
# recommends IRS evaluate the redesigned process using "the number of
# audits resulting in no change to taxes due and the magnitude of tax
# change" -- a recommendation to START measuring impact, meaning that
# evaluation had not been done as of the report. No source found (GAO
# report, FedScoop, Money.com coverage) contains a quantified yield/
# accuracy/no-change-rate comparison between the AI-assisted and
# traditional selection methods for this pilot.
#
# Note for whoever builds this out later: a well-documented racial-disparity
# finding exists for IRS audit selection (2023 Stanford/IRS study; a
# separate GAO report on risk scores varying by sex) -- but that evidence is
# about the OPERATIONAL DIF/EITC workload-selection systems (the Dependent
# Database), which multiple sources describe as organizationally separate
# from this NRP research-sampling pilot. Don't reuse it here without
# confirming it actually applies to the NRP AI process specifically, not
# just the same agency's other audit-selection algorithm.
#
# Sources so far:
# https://www.gao.gov/products/gao-24-106449
# https://fedscoop.com/irs-ai-audit-models-gao-report/
# https://money.com/irs-ai-audits/

# WIP: sourced, not yet hand-labeled (evidence only -- no "expected" block
# yet). Pre-RV-2.0 model only: the 2017-deployed model, bounded strictly to
# evidence describing that version, not the later RV 2.0 update or its 2025
# national rollout.
reach_vet_wip = {
    "name": "va_reach_vet_original_model",
    "pilot": {
        "pilot_name": "REACH VET (original model, deployed 2017)",
        "agency": "Veterans Health Administration (VA)",
        "summary": (
            "REACH VET runs a predictive model monthly on VHA patients seen "
            "in the past 24 months, scoring suicide risk. Patients in the "
            "top 0.1% at each facility are flagged on a clinical dashboard "
            "for a mandated care-coordinator and provider review."
        ),
        "criteria": {
            "performance": (
                "The model-development paper (McCarthy et al. 2015, "
                "American Journal of Public Health 105(9):1935-1942, "
                "published before the 2017 national rollout) reported: "
                "'suicide rates were 82 and 60 times greater than the rate "
                "in the overall sample in the highest 0.01% stratum for "
                "calculated risk for the development and validation "
                "samples, respectively.' A separate 2025 study evaluating "
                "the same original (pre-RV-2.0) model's real-world accuracy, "
                "using 2018 VHA patient data and 'the current REACH VET "
                "methodology... determined in 2017,' found: 'The PPV was "
                "0.00054 (95% CI: 0.00034 to 0.00087), indicating that very "
                "few (0.054%) of the patients in the high-risk group died "
                "by suicide.'"
            ),
            "bias_fairness": (
                "No source found -- the 2015 development paper, a 2022 GAO "
                "report on the program (GAO-22-105165), and subsequent "
                "program-evaluation literature -- describes any subgroup "
                "(race, sex, age) fairness or disparity testing for this "
                "original model. Subgroup-consistency testing only appears "
                "in the literature once the later RV 2.0 model is "
                "introduced, which is out of bounds for this evidence set."
            ),
            "human_oversight": (
                "'REACH VET coordinators... are responsible for reviewing "
                "the dashboard and notifying the VHA provider who has "
                "worked most closely with the patient,' and 'providers are "
                "responsible for reviewing each patient's care plan, "
                "contacting the patient by phone, and when appropriate, "
                "making changes in care collaboratively with the patient.' "
                "GAO-22-105165 confirms: 'clinicians are expected to "
                "evaluate each identified veteran's risk for suicide, "
                "determine appropriate treatment approaches, and contact "
                "the veteran to discuss options for care.'"
            ),
            "transparency": (
                "The model's methodology and validation results were "
                "published in a peer-reviewed journal (McCarthy et al. "
                "2015, American Journal of Public Health) prior to the "
                "2017 national rollout. GAO-22-105165 (2022) separately "
                "describes the deployed program only in generic terms: "
                "'The REACH VET program model uses 61 variables included "
                "in each veteran's VHA electronic health record.'"
            ),
            "scale_readiness": (
                "'Rapid phased national implementation of REACH VET "
                "started in November 2016, when the predictive model "
                "identified eight veterans with the highest risk scores at "
                "each facility. By February 2017, facilities received the "
                "names of all veterans in the top 0.1% risk tier at their "
                "facility,' with full national implementation in March "
                "2017."
            ),
        },
        "sources": [
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC4539821/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC12535588/",
            "https://www.gao.gov/assets/gao-22-105165.pdf",
            "https://psychiatryonline.org/doi/full/10.1176/appi.ps.202100629",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC11809762/",
        ],
    },
}
