# Formats

Two files. `TASTE.md` is the profile and its own resume router. `log.md` is
append-only history.

## Decision ids

A decision's id is `<date>-<slug>`, composed from its history entry. The log
stays readable without repeating the date; the profile references the
composed id.

## Principle

```markdown
### kindness-over-authenticity — core

**Statement.** Kindness outranks being unvarnished.

**Boundary.** Does not require silence or dishonesty.

**Test.** Am I using honesty as an excuse for avoidable harm?

**Confirmed by.** [2026-08-06-blunt-feedback] — the profile predicted this judgment correctly.
```

The heading id is a stable slug. It never changes, so a later split into
per-principle files stays mechanical.

Status is one of `core`, `provisional`, `candidate`, and it belongs in the
heading — never in a directory name. Moving a file to promote it breaks
every inbound reference and severs its history.

**Omit a field that does not exist yet. Never narrate its absence.** Writing
`**Test.** Not yet written` creates a test question whose text is "Not yet
written", and the gate will read it as present. What is missing belongs in
Open Tensions, which is where the next session looks.

`**Named trade.**` is optional: a deviation the person calls a lapse rather
than a boundary, in their own words. `**Test.**` is optional too. Neither
affects status.

`**Confirmed by.**` cites predictions that used the principle and turned out
right. It is the only field that promotes anything, and only the profile can
earn it — nothing the person says about themselves goes here.

## Priority between principles

Carried in prose, inside the principle that yields — "when this and
*ship-on-time* collide, correctness wins and I take the delay as a cost."
Order within Core Principles reflects it too. There is no ranking field: only the person may
assert priority, and a resolved tension is where they assert it.

## History entries

```markdown
## [2026-08-06] choice | declined-rewrite
won: kindness-over-authenticity · lost: inner-honesty
price: lost the client

## [2026-08-06] predict | blunt-feedback
about: kindness-over-authenticity
result: hit

## [2026-08-07] predict | album-artwork
about: enter-reality
result: miss
opened: speed-vs-craft

## [2026-08-07] demote | inner-honesty → provisional
contradicted by a choice they still defend; prior wording preserved in the
Revision Record
```

Actions: `seed`, `choice`, `demote`, `predict`, `tension`, `leak`.

A `predict` entry needs `about:` and `result:`, because those are what a
principle's **Confirmed by** field resolves against.

Append only. Newest last. Never edit or delete an entry — a history that can
be rewritten cannot serve as evidence.
