# Taste Bud

Work out what you actually value in the work you make — and write it down in
a form an AI agent can use.

It asks you to pick between options. You never have to type an answer.

## Install

```bash
claude plugins install taste-bud          # Claude Code
npx skills@latest add <owner>/taste-bud   # every other agent
```

## What a session looks like

Run `/cultivate-taste-bud`. It asks one question at a time, like this:

> **You find a change that saves you a full day every week. It also means a
> teammate has to do a small annoying step, every day, indefinitely. Do you
> make the change?**
>
> **a.** Yes — the time saved is worth more. *A teammate pays a small tax
> forever so you don't pay a large one, and they didn't choose it.*
>
> **b.** Only if they agree to it. *They may say no and you keep losing the
> day — and asking makes it hard to refuse.*
>
> **c.** No — find another way. *A real improvement stays unmade.*
>
> **d.** Skip this one.

Every option costs something. There is no right answer. What you protect when
something has to give is what gets recorded.

Stop whenever you like. Nothing is lost, and the next session picks up where
you left off.

## What you end up with

A `TASTE.md` that looks like this:

```markdown
### consent-before-shifting-cost — provisional

**Statement.** Don't move a cost onto someone without their informed
agreement. Treat the agreement as negotiable, not a rubber stamp.

**Boundary.** Reversibility. If it can be undone the moment they object,
acting first is acceptable.
```

Point any agent at it, in any project, and it judges your work the way you
would.

## The one rule worth knowing

**You never have to prove anything. The tool does.**

What you say you value is taken as what you value. You're not asked to show
you've lived up to it, and your answers aren't ranked by how much they cost
you.

Instead, the profile guesses how you'd judge something it has never seen, and
you tell it whether it got you right. Guess right, and that principle firms
up — the profile has shown it understood you. Guess wrong, and that's the
profile's problem to fix.

A wrong guess is the useful outcome. The principle shown above was found by
one.

## It never edits without asking

Noticing a contradiction earns it the right to raise the subject, never to
change your profile.

## Honest limits

- **Scoring a guess is itself something you tell it.** The profile can't see
  whether it really understood you — it asks. What keeps that from being
  worthless is that you're the only one who reads your profile, so scoring
  generously just produces a document that lies to you. Nothing to win.
- **It's weakest exactly when it's newest.** Confidence comes from guessing
  you right, so a fresh profile has earned nothing yet.
- **People invent reasons for their own judgments.** Asking for the choice
  before the reason helps. It doesn't cure it.
- **It records what you say, not what you do.** That's deliberate — it's a
  record of your standards, and you can hold a standard you've fallen short
  of. But don't mistake it for a description of your behaviour.

## Also here

- [`skills/cultivate-taste-bud/`](skills/cultivate-taste-bud/) — the skill
- [`TASTE.md`](TASTE.md) — the author's own profile, as an example of the
  output. Not a target for yours.
- [`docs/`](docs/) — how it was designed and built, including what was wrong
  first.
- Check a profile: `python3 skills/cultivate-taste-bud/scripts/taste_profile.py TASTE.md log.md`
