# cultivate-taste-bud

Work out what you actually value in the work you make, and write it down in a
form an AI agent can use.

It asks you to pick between options. You never have to type an answer.

## Install

```bash
npx skills@latest add LifelongLazyLearner/cultivate-taste-bud
```

If that fails, clone the repo and point your agent at
`skills/cultivate-taste-bud/SKILL.md` directly.

## What a session looks like

Run `/cultivate-taste-bud`. It asks one question at a time, like this:

> **You find a change that saves you a full day every week. It also means a
> teammate has to do a small annoying step, every day, indefinitely. Do you
> make the change?**
>
> **a.** Yes, the time saved is worth more. *A teammate pays a small tax
> forever so you don't pay a large one, and they didn't choose it.*
>
> **b.** Only if they agree to it. *They may say no and you keep losing the
> day. Asking also makes it hard for them to refuse.*
>
> **c.** No, find another way. *A real improvement stays unmade.*
>
> **d.** Skip this one.

Every option costs something, so there is no right answer. What you protect
when something has to give is what gets recorded.

You can stop whenever you like. Nothing is lost, and the next session picks up
where you left off.

## What you end up with

A `TASTE.md` that looks like this:

```markdown
### consent-before-shifting-cost — provisional

**Statement.** Don't move a cost onto someone without their informed
agreement. Treat the agreement as negotiable, not a rubber stamp.

**Boundary.** Reversibility. If it can be undone the moment they object,
acting first is acceptable.
```

At the end of a session it offers to package that profile as its own skill, so
any agent in any project can apply it. It never installs anything unless you
ask.

## The one rule worth knowing

You never have to prove anything. The tool does.

What you say you value is taken as what you value. Nobody asks you to show
you've lived up to it, and your answers aren't ranked by how much they cost
you.

Instead, the profile guesses how you'd judge something it has never seen, and
you tell it whether it got you right. Guess right, and that principle firms up,
because the profile has shown it understood you. Guess wrong, and fixing that
is the profile's job rather than yours. The principle shown above came out of a
wrong guess.

## The packaged skill explains itself

If you take the offer, the skill you get does one thing differently from a
plain profile: it says which principle drove which choice instead of applying
them quietly.

That came out of testing rather than preference. A profile applied silently
produced work its owner couldn't tell apart from anything else, even with their
own principles in it almost word for word. The same profile with its reasoning
shown was picked out correctly. Taste applied invisibly doesn't read as
anyone's.

It also stays out of projects that haven't asked for it. The first time you use
it somewhere, it writes a small opt-in file, and without that file it says
nothing about your work.

## It never edits without asking

Noticing a contradiction earns it the right to raise the subject. It does not
earn the right to change your profile.

## Honest limits

Scoring a guess is itself something you tell it. The profile can't see whether
it really understood you, so it asks. What keeps that from being worthless is
that you are the only person who reads your profile, and scoring generously
just produces a document that lies to you.

The profile is weakest exactly when it is newest, because its confidence comes
from guessing you right and a fresh one has done none of that yet.

People invent reasons for their own judgments. Asking for the choice before the
reason helps, but it doesn't cure it.

It records what you say rather than what you do. That is deliberate: it holds
your standards, and you can hold a standard you have fallen short of. Don't
mistake it for a description of your behaviour.

## Also here

- [`skills/cultivate-taste-bud/`](skills/cultivate-taste-bud/) is the skill
  itself.
- [`docs/`](docs/) covers how it was designed and built, including the parts
  that were wrong first.
- [`skills/cultivate-taste-bud/fixtures/`](skills/cultivate-taste-bud/fixtures/)
  holds two profiles produced by running the method cold, used to check that
  different people don't get pushed toward the same conclusions.
- To check a profile:
  `python3 skills/cultivate-taste-bud/scripts/taste_profile.py TASTE.md log.md`
