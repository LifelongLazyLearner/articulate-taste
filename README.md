# articulate-taste

[![Version](https://img.shields.io/github/v/release/LifelongLazyLearner/articulate-taste?label=version)](https://github.com/LifelongLazyLearner/articulate-taste/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![Language](https://img.shields.io/badge/lang-English-blue.svg)](#)
[![GitHub stars](https://img.shields.io/github/stars/LifelongLazyLearner/articulate-taste?style=social)](https://github.com/LifelongLazyLearner/articulate-taste/stargazers)

Language: English | [简体中文](./README.zh-CN.md)

Everyone has taste. Not everyone can say what theirs is.

articulate-taste draws out the taste you already have and writes it down in a
form an AI agent can use. It works like an eye exam. Nobody can state their own
prescription, but everybody can say which of two lenses is clearer. It shows
you two versions of something that differ on one thing, you say which is
better, and it reads your standards off your answers. You never have to type
one.

## Install

```bash
npx skills@latest add LifelongLazyLearner/articulate-taste -g
```

The `-g` flag makes the skill available to your chosen agent across projects.
The installer asks which agent to connect it to; for Claude Code, the user-level
link is `~/.claude/skills/articulate-taste/`. It does not create your profile.
That happens later, in whatever project you run the skill from.

The installer sends anonymous usage data by default. Set
`DISABLE_TELEMETRY=1` if you want to turn that off.

If it fails, clone the repo and point your agent at `SKILL.md` directly.

## What a session looks like

Run `/articulate-taste`. It shows you two versions of the same thing and asks
which is better. 1, 2, or the same:

> **1**
> Your file has passed the size where editing stays responsive. Saves
> currently take about eight seconds.
>
> We suggest splitting it into linked pages. That keeps everything editable,
> and the cost is the single-scroll view. Flattening the finished sections to
> images is faster still, but those sections stop being editable.
>
> **2**
> Your file has passed the size where editing stays responsive. Saves
> currently take about eight seconds.
>
> There are three ways out. Splitting it into linked pages keeps everything
> editable but breaks the single-scroll view. Flattening the finished
> sections to images restores speed and makes those sections uneditable.

Every sentence is aligned except one thing, and it does not tell you what that
thing is until you have answered. Here it is whether the writer recommends or
lays the options out flat. You will usually know which you prefer immediately,
and be able to say why straight afterwards, which is the part that is hard to
produce cold.

Answering "the same" is a real answer. It means that difference does nothing
for you, and it puts that lens away.

When the picks add up to something, it writes them up as a principle, in a few
sentences saying what you seem to value and where that stops. You choose the
wording, or throw the whole thing out. Nothing enters your profile, the file
called `TASTE.md`, that you did not confirm.

You can stop whenever you like. Nothing is lost, and the next session picks up
where you left off.

## What you end up with

A `TASTE.md` of principles that look like this:

```markdown
### recommendation-lowers-entropy — provisional

**Statement.** Say which one you would pick, and carry the reason it rests on.
Laying out options evenly and stopping there leaves the decision cost with the
reader; a recommendation takes some of it back.

**Boundary.** It stops where the reason cannot be given. A bare recommendation
is worse than none. Where you cannot say why, lay out the options and stop.
```

That one came out of two pairs. The first varied whether the writer
recommended anything, and the recommendation won. The second moved the same
difference into a case where the writer could not know the answer, and the
recommendation lost. The boundary is where the second pick flipped, and nobody
had to describe it.

At the end of a session it offers to package that profile as its own skill, so
any agent in any project can apply it. It never installs anything unless you
ask.

## The one rule worth knowing

You never have to prove anything. The tool does.

It takes what you say you value as what you value. Nobody asks you to show
you've lived up to it, and your answers aren't ranked by how much they cost
you.

Instead, the profile has to earn what it claims, one of two ways. It guesses
how you'd judge something it has never seen and you tell it whether it got you
right. Or it writes something, writes a second version with no profile behind
it, and you pick between them without knowing which is which. Get it right,
and that principle firms up, because the profile has shown it understood you.
Get it wrong, and fixing that is the profile's job rather than yours.

## The packaged skill explains itself

If you take the offer, the skill you get does one thing differently from a
plain profile: it says which principle drove which choice instead of applying
them quietly.

That came out of testing rather than preference. A profile applied silently
produced work its owner couldn't tell apart from anything else, even with their
own principles in it almost word for word. Show the reasoning and the same
owner picked the work out correctly. Taste applied invisibly doesn't read as
anyone's.

It also stays out of projects that haven't asked for it. The first time you use
it somewhere, it writes a small opt-in file, and without that file it says
nothing about your work.

## It never edits without asking

Noticing a contradiction earns it the right to raise the subject. It does not
earn the right to change your profile.

## Honest limits

Scoring a guess is itself something you tell it. The profile can't see whether
it really understood you, so it asks. That holds up because you are the only
person who reads your profile: score generously and you end up with a document
that lies to you.

The profile is weakest exactly when it is newest, because its confidence comes
from guessing you right and a fresh one has done none of that yet.

People invent reasons for their own judgments. Asking for the choice before the
reason helps, but it doesn't cure it.

It records what you say rather than what you do. That is deliberate: it holds
your standards, and you can hold a standard you have fallen short of. Don't
mistake it for a description of your behaviour.

## Also here

- [`SKILL.md`](SKILL.md) is the skill itself, with the rest of it in
  [`references/`](references/).
- [`docs/`](docs/) covers how it was designed and built, including the parts
  that were wrong first. It predates the rename and the move to comparison,
  and stays as a record rather than getting corrected.
- [`fixtures/`](fixtures/) holds two profiles produced by running the method
  cold, there to check that the method doesn't push different people toward
  the same conclusions.
- To check a profile:
  `python3 scripts/taste_profile.py TASTE.md log.md`
