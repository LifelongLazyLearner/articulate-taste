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

## Ask in picks, not prose

Every question is multiple choice with a skip option. Exactly one question in
this method requires typing — the test question at core promotion, which is
deferrable, so a whole session can run without composing a sentence.

Options are assembled only from what the person has already chosen, rejected,
or named. Offering a principle you invented and asking them to agree is cheap
assent wearing a multiple-choice costume. Details in
[references/elicitation.md](references/elicitation.md).

Ask nothing you can look up, and configure nothing you can default.

## Loop

Enter anywhere, stop anywhere. Read `TASTE.md` first; `Open Tensions` says
where to resume.

1. **seed** — Open with a forced choice in the present tense, price stated
   inside the question. Never open by asking someone to recall a costly
   episode: that reads as an exam and returns reconstructed evidence.
2. **tension** — Build a concrete dilemma where two of their own values
   collide, with a stated price. Never generic.
3. **choice** — They choose. Then anchor it with a pick: has this come up for
   real, and did they choose the same way? Choosing differently is the most
   valuable answer available — a live gap between stated and revealed
   preference — and opens a tension. Record the choice, the price, what won,
   what lost, and the tier.
4. **boundary** — Offer concrete costs that would break the principle, drawn
   from the losing side of tensions they already answered. Picking which cost
   breaks you is still a choice under price, not assent.
5. **gate** — Apply [references/promotion.md](references/promotion.md).
6. **record** — Update the principle and append the history entry in one
   pass. Formats in [references/format.md](references/format.md).
7. **predict** — As soon as any principle has a boundary, predict their
   judgment on a held-out item. Do not wait for core: core needs a sentence
   they wrote, and gating self-correction behind it means it never runs. A
   miss opens a tension and re-enters the loop. Ask for the test question
   after a prediction, once they can see what it buys.

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
