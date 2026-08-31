# Formats

Two files. `TASTE.md` is the profile and its own resume router. `log.md` is
append-only history. Resolve both from documentation or an explicit
designation before reading or writing. Neither the current directory nor a
`.taste`-style name makes a file canonical. If plausible canonical pairs
remain, ask one decisive question. If the schema is unsupported, stop writes
and request separately authorised review or migration; do not create a
replacement or promote an experimental file.

Two schemas are supported. The legacy schema carries status in each principle
heading. `personal-taste-contract/v1` separates universal and scoped taste while
preserving one canonical profile. Detect the schema already in use and write
only that schema; never convert a real profile merely for convenience.

## Decision ids

A decision's id is `<date>-<slug>`, composed from its history entry. The log
stays readable without repeating the date; the profile references the
composed id.

## Legacy principle

```markdown
### kindness-over-authenticity — core

**Statement.** Kindness outranks being unvarnished.

**Boundary.** Does not require silence or dishonesty.

**Test.** Am I using honesty as an excuse for avoidable harm?

**Confirmed by.** [2026-08-06-blunt-feedback]. The profile predicted this judgment correctly.
```

The heading id is a stable slug. It never changes, so a later split into
per-principle files stays mechanical.

Status is one of `core`, `provisional`, `candidate`, and it belongs in the
heading, never in a directory name. Moving a file to promote it breaks
every inbound reference and severs its history.

**Omit a field that does not exist yet. Never narrate its absence.** Writing
`**Test.** Not yet written` creates a test question whose text is "Not yet
written", and the gate will read it as present. What is missing belongs in
Open Tensions, which is where the next session looks.

`**Named trade.**` is optional: a deviation the person calls a lapse rather
than a boundary, in their own words. `**Test.**` is optional too. Neither
affects status.

`**Confirmed by.**` cites predictions that used the principle and turned out
right. The referenced `predict` or `recognise` entry must be a hit whose
`about:` value is exactly this principle's stable slug. It is the only field
that promotes anything, and only the profile can earn it. Nothing the person
says about themselves goes here.

## Personal taste contract v1

The fenced metadata contains this exact schema marker:

```yaml
schema: personal-taste-contract/v1
stable_baseline: none
```

New profiles use `stable_baseline: none`. A migrated profile lists the exact
comma-separated ids that were already authoritative when this schema was
adopted. That list is frozen migration evidence, not a shortcut for promoting
new rules. Bind a non-empty list to one append-only migration event whose
`baseline:` value is the SHA-256 digest of the comma-joined ids exactly as the
validator normalises them:

```markdown
## [2026-08-31] migrate | personal-taste-contract-v1
schema: personal-taste-contract/v1
baseline: <sha256>
```

The validator rejects unknown ids, a missing or second migration event, and a
baseline whose digest no longer matches. Duplicate history entry ids fail
validation rather than replacing earlier evidence in memory. The validator
also requires exact confirming history for every stable rule outside the
baseline. This makes migration a one-time declaration rather than a reusable
promotion path.

A baseline rule may later move to `Universal Provisional Rules` only after a
defended demotion is logged. Re-stabilizing it requires `Evidence` that cites
an exact confirming prediction or recognition appended after the latest
demotion. A pre-migration demotion does not alter the imported baseline, and
header dates never override append order. The migration baseline itself remains
frozen.

Universal confidence is carried by section placement. A universal provisional
principle looks like this:

```markdown
## Universal Provisional Rules

### recommendation-lowers-entropy

- **Directive:** Recommend one option when the deciding reason is known.
- **Boundary:** Preserve the recipient's choice when their own result or costs
  determine the answer.
- **Operational test:** Can the evidence settle this without taking over a
  recipient-owned decision?
```

`Operational test` is optional for universal rules. Statement plus boundary is
enough for provisional status; the test helps application but gates nothing.

Use `Universal Stable Rules` only for the exact `stable_baseline` or after a
qualifying prediction or recognition cited through `Evidence`. The validator
does not pretend it can reconstruct evidence that predates the canonical log.

A scoped principle uses the same stable slug but declares its reach and
confidence explicitly:

```markdown
## Scoped Taste

### editorial-restraint

- **Applies to:** long-form editorial writing
- **Confidence:** provisional
- **Directive:** Let one image carry the emotional turn.
- **Boundary:** Repetition may remain when comprehension requires it.
- **Operational test:** Does another image add meaning or only emphasis?
- **Evidence:** [2026-08-10-editorial-choice]
```

`Applies to`, `Confidence`, `Directive`, `Boundary`, `Operational test`, and an
exact `Evidence` reference are required for every scoped rule. Confidence is
`provisional` or `stable`. A scoped rule becomes stable only when its evidence
includes a `predict` or `recognise` hit whose `about:` value is exactly that one
stable slug. There is no multi-value `about:` form.

For provisional scoped evidence, a referenced `choice` must name the exact
principle slug in `won:` or `lost:`. Other referenced actions use `about:` with
that exact slug. Merely citing an event that exists is not support.

A direct statement may enter as provisional after its wording, boundary, and
scope are approved. Universal means the evidence supports materially different
domains; otherwise name the medium or context actually tested. Do not infer
brand preference, behaviour, willingness to pay, or a broader medium from a
narrow example. Keep rejected readings and failed predictions in `log.md`, not
as active negative rules unless a recurring false inference needs a boundary.

Keep the `Scoped Taste` section even when it says `There are no active scoped
rules.` Do not pre-create one subsection per anticipated medium.

## Priority between principles

Carried in prose, inside the principle that yields: "when this and
*ship-on-time* collide, correctness wins and I take the delay as a cost."
Order within `Core Principles` or `Universal Stable Rules` reflects it too.
There is no ranking field: only the person may assert priority, and a resolved
tension is where they assert it.

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

Actions: `seed`, `choice`, `promote`, `demote`, `predict`, `recognise`,
`tension`, `leak`.

A `predict` entry needs `about:` and `result:`, because those are what a
principle's **Confirmed by** field resolves against. A `recognise` entry needs
the same, and confirms on the same terms. `about:` contains exactly one stable
principle slug. Missing ids, related ids, and substring matches do not confirm;
there is no multi-value syntax.

A pick from a pair is a `choice`. A 1 or 2 pick records `won:` and `lost:` and
may record a volunteered reason. `Neither` records that both candidates were
rejected and may preserve separate volunteered reasons. `Same` records only
that the comparison paused in this condition, not that the axis is retired
everywhere. `Skip` records no preference inference. No reason is required, and
none of these non-winner outcomes promotes a principle.

Append only. Newest last. Never edit or delete an entry. A history that can
be rewritten cannot serve as evidence.
