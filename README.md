# Taste Bud

A method for cultivating your own taste profile — the standards behind how you
judge creative work, products, code, and decisions — and keeping it evolving as
new evidence arrives.

It is content-neutral. It elicits what *you* value and records it. It does not
install anyone else's aesthetic.

## Install

```bash
claude plugins install taste-bud          # Claude Code
npx skills@latest add <owner>/taste-bud   # every other agent
```

## Use

Run `/cultivate-taste-bud`. It asks you to pick between options, one question
at a time. There is no setup, no configuration, and nothing to fill in — the
method asks you to type exactly once, and even that is optional.

Stop whenever you like. The profile is usable at any point, and the next
session resumes from its **Open Tensions** section.

## How it works

**It asks for choices, not descriptions.** People reliably invent plausible
reasons for their own judgments, so being asked *why you like something*
returns a story rather than a principle. Every question here offers options
that all cost something. What you protect when something has to give is the
evidence.

**Evidence is graded.** What you made and killed, decisions that cost you,
choices made under a stated price, and — weakest — what you say you admire.
Stated belief may *propose* a principle. It may never *confirm* one.

**A principle becomes core only when** it has an explicit boundary, a test
question you wrote yourself, and at least one decision where holding it cost
you something. No thresholds, no magic numbers, and the rule is enforced by a
script rather than by good intentions.

**It can be wrong, and finds out.** The profile predicts your judgment on
things it was not built from. A miss is the best evidence it can get about
itself, and it revises.

**It never changes anything without asking.** Noticing a contradiction earns
it the right to raise the subject, never to edit your profile. Volunteering an
unrequested opinion about your taste counts as the same violation.

## Honest limits

- It depends on your having had costly choices to draw on. Early in a career,
  that layer is thin.
- People invent reasons for their own judgments. Asking for the choice before
  the reason works around this; it does not eliminate it.
- The prediction gate measures agreement between the profile and what you
  *say*, not what you *do*. It catches drift, not self-deception.
- The profile is only as honest as your willingness to record choices that
  embarrass you.

## Verify a profile

```bash
python3 skills/cultivate-taste-bud/scripts/taste_profile.py TASTE.md log.md
```

Reports any principle claiming a status its evidence does not support, and any
reference that resolves to nothing. Python 3, standard library only.

## Privacy

Raw transcripts are discarded by default. An installed profile is symlinked
into every agent directory you select, so anything kept inside it sits in that
many file-discovery paths. Opt-in retention is stored outside the skill
directory.

## This repo

- [`skills/cultivate-taste-bud/`](skills/cultivate-taste-bud/) — the skill
- [`TASTE.md`](TASTE.md) — the author's own profile, as a worked example of the
  output. Not a target for yours.
- [`docs/specs/`](docs/specs/) and [`docs/plans/`](docs/plans/) — how it was
  designed and built, including the parts that were wrong first.
