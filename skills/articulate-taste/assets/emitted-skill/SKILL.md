---
name: {{SKILL_NAME}}
description: Judge and steer work against a specific person's recorded taste profile, covering {{PROFILE_SUMMARY}}. Explains which principle drove which choice rather than applying them silently. Use when reviewing or producing work in a project that has opted in to this profile, or when someone asks whether something matches their standards. Not for building a profile from scratch.
---

# {{SKILL_NAME}}

Apply one person's recorded standards to the work in front of you, and say out
loud which standard drove which choice.

The profile lives beside this file: `TASTE.md` holds the principles, `log.md`
holds their history.

## First, check the project opted in

Before reading the profile, look for `.taste-opt-in.md` in the repository root.

If it is missing, say that this profile has not been invoked for this project,
offer to create the file, and stop. Do not load `TASTE.md`, do not judge
anything, and do not comment on the work. A profile governs a project only
when that project invokes it.

If it is present, read it. It may narrow the scope to particular directories
or kinds of work.

## Always narrate

Never apply a principle silently. Every judgment and every choice states which
principle it came from, quoting the principle's own wording.

Work shaped by a profile without visible reasoning is indistinguishable from
work shaped by nothing. The narration is what makes it recognisable as theirs,
and it is also what lets them catch you being wrong.

At the end of anything you produce, name the choices no principle covered.
Those are the ones you made up, and they should be labelled as yours rather
than passed off as theirs.

## Status means something

- **core** principles have been confirmed: the profile predicted this person
  correctly, or produced work they picked out blind. Lean on these.
- **provisional** principles are stated with a boundary and nothing has tested
  them yet. Apply them, and say that they are untested when they decide
  something important.
- **candidate** principles have no boundary. Do not apply them. Mention them
  only if the work happens to bear on one.

Every principle has a boundary saying where it stops. Check the boundary before
applying the principle, because most disagreements live there rather than in
the statement.

## Modes

**Judge.** Score the work against the profile. For each principle that bears on
it, say whether the work meets it, quote the principle, and point at the
specific part of the work. Where two principles conflict, say so and quote both
rather than picking for them.

**Apply.** Steer work in progress. Same narration: as choices come up, say
which principle decided them.

**Record.** When they make a decision that a principle bears on, offer to
append it to `log.md`. Offer, never do it unasked.

## Never change the profile without being asked

Noticing that a choice contradicts a principle earns you the right to raise it.
It does not earn the right to edit anything.

Say what you noticed, quote the principle, and let them decide. If they defend
the contradicting choice, that is a real boundary and the profile may need
revising. If they call it a lapse, the principle stands: judging your own
behaviour against a standard is evidence the standard holds.

Either way, they write the change, not you.

## Check your own bookkeeping

```bash
python3 scripts/taste_profile.py TASTE.md log.md
```

Reports any principle claiming a status its history does not support. Run it
after appending anything.
