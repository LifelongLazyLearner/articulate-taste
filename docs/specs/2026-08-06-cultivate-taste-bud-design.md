# cultivate-taste-bud — design

**Date:** 2026-08-06
**Status:** Proposed, awaiting sign-off
**Distribution:** Open source

## Purpose

A reusable method for helping any person build a taste profile that keeps evolving. The method is content-neutral: it elicits and records what that person actually values, and never steers them toward the author's conclusions.

Default output is `TASTE.md` plus its history. A portable personal skill, so any agent in any project applies the profile, is offered afterward and is out of MVP scope.

## First principles

**Result.** A person who has never met the author runs this skill and ends with a taste profile that is theirs, traceable to their own evidence, and able to correct itself as new evidence arrives.

**Use.** Judging and steering creative work, products, code, and leadership decisions.

**User constraints.** Content-neutral. Open source. Agent-agnostic. Resumable. No arbitrary thresholds. Self-evolving, efficiently and effectively.

**Pass conditions.**

1. A stranger, with no configuration beyond installing the skill, completes one session and obtains a `TASTE.md` containing at least one core principle carrying a boundary, a test question, and paid evidence.
2. No core principle rests on Tier 4 evidence alone. Every one traces to a recorded decision that carried a price.
3. A second session resumes from `TASTE.md` without re-asking anything already answered.
4. A prediction run produces a scored hit or miss, and every miss opens a tension.
5. Two fixture personas seeded with opposed rejections produce core principle sets that do not overlap. Verified by running the skill against both fixtures and diffing the resulting principle ids.
6. A recorded contradiction is detected and surfaced without the person having to ask, and on their confirmation demotes the principle while preserving its prior wording. No demotion is written without that confirmation.

Condition 6 is the self-evolution condition. A profile that only ever accumulates is a profile that cannot be wrong. Detection is unprompted; mutation never is.

**Post-MVP gate.** An agent using an emitted profile makes judgments the person endorses more than the same agent without it. Not evaluable until the emitted skill exists. Recorded because skill-augmented agents frequently fail to outperform the base agent, and a profile that changes nothing is a failed profile.

**Prerequisite.** The repository is under version control before implementation begins. Without it there is no recovery path.

**Unknowns.** None blocking. Installation, agent selection, and adapter creation are delegated to the existing `skills` CLI (`vercel-labs/skills`), which writes canonical skills to `~/.agents/skills/<name>`, symlinks them into each selected agent directory, accepts `-a/--agent` to choose targets, and accepts a local path as a source.

## Non-goals

- Converging anyone on the author's taste. This repo's `TASTE.md` v0.5 is a worked example of output shape, nothing more.
- Producing a style guide, visual language, or tone specification. Taste here means standards of judgment, not surface expression.
- Replacing the person's authority. The method proposes; the person decides.

## Reuse before build

No existing tool elicits an individual's taste. Every shipping "taste skill" installs a prescriptive aesthetic authored by someone else — Taste Skill's minimalist/brutalist/GPT variants, Dragoon0x/taste-skills' typography and spacing checklists. The closest prior work, goose's account of teaching an agent design taste, concludes that taste cannot be automated but preferences can be made legible, and reports the skills-based route needed sustained editorial intervention.

Self-development is justified for the elicitation method. Not for anything else:

| Adapt | Rather than build |
|---|---|
| `/grilling` conventions — one question at a time, always offer a recommended answer, look facts up instead of asking | new interview mechanics |
| `teach`'s workspace shape — `*-FORMAT.md` companion files | a new format documentation scheme |
| `domain-modeling`'s ADR pattern | a new revision-record format |
| The `skills` CLI for install, agent selection, and adapters | hand-rolled symlink and adapter logic |
| `npx skills add <owner>/<repo>` plus a Claude plugin manifest | custom distribution |
| `skills/<name>/` monorepo shape, `agents/*.yaml` per-agent metadata | a bespoke packaging scheme |

## Why there is no graph

An interlinked node graph was the original design, modeled on a persistent LLM-maintained wiki. It was dropped.

Self-evolution requires four things: principles addressable by stable id, an append-only history preserving prior wording, records of the system's own mispredictions, and a per-update cost low enough that people actually pay it. All four fit in two files.

A graph does not enable one verdict to update several principles — an agent editing a flat document does that in the same pass. A graph makes the links explicit, and its real payoff is retrieval once a profile holds far more principles than a single file should carry. That is a scale problem no first profile has.

Direct evidence that flat suffices: this repo's `TASTE.md` v0.5 carries ten principles with boundaries, evidence, and a decision test, through three recorded revisions including two demotions — a complete lifecycle, one file, no graph.

Principle ids are stable slugs so that a later split into per-principle files stays mechanical.

## Evidence model

Every recorded claim carries the tier of evidence behind it.

| Tier | Source | Contamination |
|---|---|---|
| 1 | Artifacts they made, kept, shipped, killed | None — no self-report involved |
| 2 | Real past decisions that carried a price | Low — recalled, but the cost anchors it |
| 3 | Forced choice between two concrete options, made now | Low — choosing beats describing |
| 4 | Stated admiration, stated belief | High — prestige bias, confabulation, cheap assent |

**Rule:** Tier 4 may *propose* a principle. It may never *confirm* one. Confirmation requires Tier 1–3. A mechanism, not a threshold.

### Why not a plain interview

Interviewing is the weakest instrument available here, and fails in four known ways:

- **Confabulation.** People reliably generate plausible reasons for judgments that are not the actual cause. "Why do you like this" returns a story, not a principle.
- **Prestige contamination.** "Name work you admire" harvests defensible canonical answers rather than the work that moved them.
- **Cheap assent.** An agent proposing a belief and the person agreeing costs nothing, so it carries almost no information. It produces the illusion of a profile.
- **Articulacy filter.** Strong taste in visual and musical domains resists verbalization; a pure interview silently excludes those people.

Interview is retained for exactly one job: **naming the boundary after a choice has already been made.**

## The loop

```
seed ──▶ tension ──▶ choice ──▶ boundary ──▶ gate ──▶ record ──┐
  ▲                                                            │
  └──────────── predict ◀── (profile has ≥1 core) ◀────────────┘
```

States, not a script. Enter anywhere, stop anywhere.

1. **seed** — Collect rejections, costly past decisions, and optionally a corpus of their own artifacts. Distilled straight into the profile; verbatim material is discarded unless retention was opted into.
2. **tension** — Construct a concrete dilemma where two of *their own* candidate values collide, with a stated price. Built from their material, never generic.
3. **choice** — They choose. Record the choice, the price paid, which value won, which lost, and the evidence tier.
4. **boundary** — Only now ask for reasoning: where does this stop, and what would make you abandon it?
5. **gate** — Apply the promotion rule, update status.
6. **record** — Write the principle change and append the history entry in one pass.
7. **predict** — Once at least one core principle exists, predict their judgment on a held-out item. Misses open tensions and re-enter the loop.

**Resume.** Every run reads `TASTE.md` first. Resume points in order: open tensions, principles missing a boundary, principles missing paid evidence, then new seeding. No transcript replay. The profile is usable at any point; unconfirmed material is marked as such.

## Neutrality rules

Inline in `SKILL.md`, not buried in a reference. Content neutrality is the product.

1. Never state a principle the person's evidence does not support.
2. Build tensions only from material already in their profile.
3. Never rank their principles. Priority between principles is theirs alone.
4. Ask for the choice before the reason. Never the reverse.
5. If your own preference shapes a question, record it in the history as a `leak` entry.
6. Change nothing without being asked or without consent. Detecting a contradiction, noticing a gap, or seeing a better wording earns you the right to surface it, never to write it. Volunteering an unrequested opinion about their taste is itself a violation, not only editing the file.

## Question bank

By tier. Lives in `references/elicitation.md`, loaded when the seed or tension state runs.

**Tier 2 — rejection-first opening.** People perform their likes; they perform their dislikes far less.

- What did you kill after investing real work in it? What made it not worth finishing?
- What do you admire but would never make? Why not?
- What is praised in your field that you think is overrated?
- What did you refuse to do for money — and what price would have changed your answer?
- When did you last change your mind about what is good? What broke it?
- Show me something you made that you are not proud of. What is wrong with it?
- What would you replace immediately if it broke, and what would you simply let go?

**Tier 3 — forced choice.** Constructed per person from their own material. Each must name a concrete price. A dilemma without a stated cost is a Tier 4 question in disguise.

**Tier 1 — artifact mining.** Optional. Offered when they have a repo, portfolio, or body of writing. Skipped without penalty; the method must work cold.

## Output

```
<profile root>/
├── TASTE.md    # the profile, and the router for resuming
└── log.md      # append-only history
```

### TASTE.md

Sections: Purpose, Core Principles, Provisional Preferences, Open Tensions, Decision Test, Evidence, Revision Record, Scope and Authority.

Each principle carries a stable slug id and a status:

```markdown
### kindness-over-authenticity — core

**Statement.** ...

**Boundary.** Where it stops, and what would abandon it.

**Test.** The question they ask themselves to check it.

**Paid by.** [2026-08-06-declined-rewrite] — turned the work down, lost the client.
```

`Open Tensions` is what makes the file its own resume router: unresolved dilemmas, and principles still missing a boundary, a test, or paid evidence.

**Priority between principles is carried in prose, inside the principle that yields.** v0.5 demonstrates the form — "survival is the leading one," "outside genuine survival constraints, kindness normally has priority." Order within Core Principles reflects it too. There is no separate ranking field: only the person may assert priority, and a resolved tension is where they assert it.

`Decision Test` is the ordered list of each core principle's `Test` line, authored by the person at promotion time in answer to "what question would you ask yourself to check this?" — not mechanically derived from the boundary prose.

### log.md

Append-only, parseable prefix, newest last:

```
## [2026-08-06] choice | declined-rewrite
won: kindness-over-authenticity · lost: inner-honesty · tier: 2
price: lost the client

## [2026-08-06] promote | kindness-over-authenticity
boundary + paid evidence from declined-rewrite

## [2026-08-07] predict | miss — expected reject, they accepted
opened tension: speed-vs-craft

## [2026-08-07] demote | inner-honesty → provisional
contradicted by accepted-ghostwrite at real cost; prior wording preserved in Revision Record
```

Actions: `seed`, `choice`, `promote`, `demote`, `predict`, `tension`, `leak`.

## Promotion, demotion, prediction

Lives in `references/promotion.md`.

**Promotion:**

- boundary present → `provisional`
- boundary present, test present, and at least one paid decision at tier 1–3 → `core`
- otherwise → `candidate`

Tier is read from the recorded decision, never stored a second time on the principle. A denormalized copy drifts.

**Demotion** is the same gate run backwards, and it is the heart of self-evolution. A recorded choice that contradicts a core principle at real cost is detected without waiting to be asked and surfaced to the person: here is the principle, here is the choice that contradicts it, here is what it cost. They decide.

On confirmation the principle is demoted and the prior wording moves to the Revision Record intact. Without confirmation nothing is written, and the contradiction is recorded as an open tension so it resurfaces rather than being lost. Growth is never rewritten as though the earlier understanding never existed.

**Prediction.** A miss is not the person's failure; it is the highest-quality evidence the system can obtain about itself. Every miss opens a tension and re-enters the loop. Hits are recorded but confer no promotion — a prediction the profile got right only shows the profile is self-consistent.

## Skill layout

```
skills/cultivate-taste-bud/
├── SKILL.md              # loop states + neutrality rules only
├── agents/openai.yaml    # per-agent metadata and invocation policy
├── references/
│   ├── elicitation.md    # question bank, tension construction
│   ├── format.md         # TASTE.md and log.md formats
│   ├── promotion.md      # gate, demotion, prediction
│   └── emitting.md       # opt-in personal skill
└── assets/               # TASTE.md and log.md templates
```

Skills live under `skills/<name>/` even with only one. Siblings are cheap under that shape and expensive to retrofit, and `-s <name>` lets a person take one skill from a repo of many.

**Invocation policy.** `cultivate-taste-bud` sets `allow_implicit_invocation: false` — multi-session, expensive, personal; it runs because someone asked, never because a model inferred they wanted interviewing. The emitted skill sets it true, because a profile you must remember to invoke goes unused.

## Distribution and installation

```bash
claude plugins install taste-bud                 # Claude Code
npx skills@latest add <owner>/taste-bud          # every other agent
```

The `skills` CLI reads Claude plugin manifests, so one manifest serves both. Exact manifest schema verified at implementation time.

## Optional personal skill

Read from `references/emitting.md` only when the offer is accepted. Out of MVP.

- Person names it freely. Validated: lowercase letters, digits, hyphens; ≤64 characters; no reserved words (`claude`, `anthropic`). Collision prompts for a different name, never auto-suffixed.
- The chosen name is recorded in `TASTE.md` frontmatter as canonical; every reference resolves through that value, never a hardcoded string.
- `description` generated from a template so a stranger's skill list shows what it does and when it fires.
- Modes: judge work against the Decision Test, apply the profile to work in progress, record new choices back into the profile.
- The profile files live inside the emitted skill directory, so profile and procedure travel together with exactly one canonical copy.

Installation shells out to the same CLI, which prompts for agents or accepts `-a`:

```bash
npx skills add <emitted-dir> -g
```

Two consequences surfaced before running it: `--copy` forks the canonical record, so a choice written through one agent is invisible to the rest; and removing the skill through the CLI removes the profile with it, so the profile should be version-controlled independently of installation.

**Per-repo opt-in.** The profile does not apply everywhere. `TASTE.md`'s Scope and Authority section requires that it govern a project only when that project invokes it, so the emitted skill writes a small opt-in file into a repo on first use, recording which profile applies and any narrowing. Because implicit invocation fires before any file check, the skill's first action is to look for that file; absent, it stops without loading the profile.

## Governance

Publishing is an external write and a release, requiring authorization covering that effect separately from approval of this design. Nothing here authorizes publication.

Raw transcripts are discarded by default. Opt-in retention writes them outside the skill directory, gitignored, with a warning before any commit that would include them. This matters because an installed profile is symlinked into every selected agent's directory, so its contents sit in as many file-discovery paths as the person selected agents. The person running the skill is the only data recipient; the method performs no external writes.

## Known limitations

- The method depends on the person having had costly choices to recall. Someone early in their career produces a thinner Tier 2 layer and leans on Tier 3.
- Forced-choice dilemmas are only as good as the seed. A shallow seed produces generic tensions.
- The prediction gate measures agreement between the profile and the person's stated judgment, not their behavior. It catches drift, not self-deception.
- The profile is only as honest as the person choosing to record choices that embarrass them.

## Deferred

- Splitting `TASTE.md` into per-principle files, if a profile ever outgrows one document. Stable slug ids keep this mechanical.
- Migrating this repo's `TASTE.md` v0.5 into the format. Method ships first.
- Team or shared profiles, where conflicting choices from different people must be reconciled.
- A manual install path for anyone without the `skills` CLI. Only worth writing if it blocks real users.
