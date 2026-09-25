# Eval Studio

Government agencies pilot AI tools before rolling them out at full scale.
Fraud-detection systems, benefits-eligibility screening, and child-welfare
risk-scoring tools are common examples. Deciding whether one of these pilots
is actually ready to expand from a small test into everyday, widespread use
is a real judgment call, and there's rarely a consistent, documented way
agencies make it.

Eval Studio takes a pilot's setup and its evaluation results and returns one
of three calls:

- **Ready to scale** — move forward to full deployment
- **Not ready** — stay in pilot; core problems need fixing first
- **Conditionally ready** — move forward, but only after specific gaps are
  addressed

It names which specific criteria passed or failed, and abstains rather than
guesses when there isn't enough information to judge.

This is a work in progress. See [SPEC.md](SPEC.md) for the tool's design.

## Why

Most federal AI pilots never make it to full deployment. Brookings estimates
that roughly 60% stay stuck in pilot or pre-deployment status. There's rarely
a clear, defensible way to decide when one's actually ready to scale. Eval
Studio tries to make that call reasoned and checkable instead of ad hoc. It
weighs a pilot's evaluation results against a fixed set of criteria, shows
its work criterion by criterion, and abstains rather than guesses when the
evidence isn't there.

<!-- Once a fuller write-up exists, link it here, e.g.:
See WRITEUP.md for the full reasoning behind the design. -->

## Status

Early development. Not yet functional end to end.

## License

MIT — see [LICENSE](LICENSE).
