---
name: cultivate-taste-bud
description: Interview a person into their own taste profile — the standards behind how they judge creative work, products, code, and decisions — and keep it evolving as new evidence arrives. Produces a TASTE.md plus an append-only history. Use when someone wants to cultivate or articulate their taste, build a taste profile, work out what they actually value, or make their standards legible to an agent. Not for applying an existing profile, and not a visual style guide.
---

# Cultivate a taste bud

Elicit a person's own standards of judgment and record them so they keep
improving. Their conclusions, never yours.

## Neutrality rules

Content neutrality is the product. These bind every state below.

1. Never state a principle the person's evidence does not support.
2. Build tensions only from material already in their profile.
3. Never rank their principles. Priority between principles is theirs alone.
4. Ask for the choice before the reason. Never the reverse.
5. If your own preference shapes a question, append a `leak` entry to the
   history.
6. Change nothing without being asked or without consent. Noticing a
   contradiction, a gap, or a better wording earns you the right to surface
   it, never to write it. Volunteering an unrequested opinion about their
   taste is itself a violation, not only editing the file.

## Evidence tiers

Every recorded claim carries the tier of evidence behind it.

| Tier | Source |
|---|---|
| 1 | Artifacts they made, kept, shipped, killed |
| 2 | Real past decisions that carried a price |
| 3 | Forced choice between two concrete options, made now |
| 4 | Stated admiration, stated belief |

Tier 4 may propose a principle. It may never confirm one.

## Loop

Enter anywhere, stop anywhere. Read `TASTE.md` first; `Open Tensions` says
where to resume.

1. **seed** — Collect rejections and costly past decisions. Question bank in
   [references/elicitation.md](references/elicitation.md). Distil straight
   into the profile; discard verbatim material unless retention was opted
   into.
2. **tension** — Build a concrete dilemma where two of their own values
   collide, with a stated price. Never generic.
3. **choice** — They choose. Record the choice, the price, what won, what
   lost, and the tier.
4. **boundary** — Only now ask for reasoning: where does this stop, and what
   would make you abandon it?
5. **gate** — Apply [references/promotion.md](references/promotion.md).
6. **record** — Update the principle and append the history entry in one
   pass. Formats in [references/format.md](references/format.md).
7. **predict** — Once a core principle exists, predict their judgment on a
   held-out item. A miss opens a tension and re-enters the loop.

## Verify before finishing

Run the validator rather than trusting your own bookkeeping:

```bash
python3 scripts/taste_profile.py <profile-dir>/TASTE.md <profile-dir>/log.md
```

It fails when a principle claims a status its evidence does not support, or
when a paid-by reference resolves to nothing. Fix what it reports.

## Offer, do not assume

At the end, offer to package the profile as a portable skill so any agent
applies it. Do not install anything without being asked.
