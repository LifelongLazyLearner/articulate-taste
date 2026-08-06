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

**Paid by.** [2026-08-06-declined-rewrite] — turned the work down, lost the client.
```

The heading id is a stable slug. It never changes, so a later split into
per-principle files stays mechanical.

Status is one of `core`, `provisional`, `candidate`, and it belongs in the
heading — never in a directory name. Moving a file to promote it breaks
every inbound reference and severs its history.

## Priority between principles

Carried in prose, inside the principle that yields — "outside genuine
survival constraints, kindness normally has priority." Order within Core
Principles reflects it too. There is no ranking field: only the person may
assert priority, and a resolved tension is where they assert it.

## History entries

```markdown
## [2026-08-06] choice | declined-rewrite
won: kindness-over-authenticity · lost: inner-honesty · tier: 2
price: lost the client

## [2026-08-06] promote | kindness-over-authenticity
boundary + paid evidence from declined-rewrite

## [2026-08-07] predict | miss — expected reject, they accepted
opened tension: speed-vs-craft

## [2026-08-07] demote | inner-honesty → provisional
contradicted by accepted-ghostwrite at real cost; prior wording preserved in
Revision Record
```

Actions: `seed`, `choice`, `promote`, `demote`, `predict`, `tension`, `leak`.

Append only. Newest last. Never edit or delete an entry — a history that can
be rewritten cannot serve as evidence.
