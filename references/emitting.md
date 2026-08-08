# Packaging the profile as a skill

Read this only when the person accepts the offer. Never install anything
without being asked.

## What gets built

A directory containing a `SKILL.md` and the profile itself, so the two travel
together and there is exactly one canonical copy that every agent resolves to.

```
<their-name>/
├── SKILL.md
├── agents/openai.yaml
├── TASTE.md
└── log.md
```

Move the profile in. Do not copy it and leave a second copy behind, because
two copies drift and neither is authoritative afterwards.

## Naming

They name it. Do not propose a default and do not derive one from their
username; a skill they did not name is a skill they will not recognise in a
list six months later.

Validate what they choose: lowercase letters, digits and hyphens only, 64
characters or fewer, and not containing `claude` or `anthropic`. If the name
is taken in the install directory, say so and ask for another. Never append a
number to make it unique.

## The emitted skill must narrate

This is the whole reason the packaged skill differs from the profile.

Silent application has failed a blind test with register held constant, in
prose containing two of the person's principles almost word for word. That
much is solid: applied is not the same as recognised.

Exposing the reasoning has won a blind test once, with the prose stripped
away, and that run carried confounds its own record names. One confounded win
is not a demonstration. The narration rule rests on the failure, not on the
win: silent application is known to be invisible, so showing the reasoning is
the only lever anyone has tried that is not the agent's own register. The
blind-test conditions and what has confounded them are in
[promotion.md](promotion.md).

So the emitted skill states which principle drove which choice, every time it
judges or produces anything. It also names the choices no principle covered,
because those are the ones it made up.

## Invocation policy

`allow_implicit_invocation: true`, the opposite of the builder's setting.

The builder runs because somebody asked for an interview. The emitted skill
exists so that taste applies without being summoned, and a profile you have to
remember to invoke goes unused.

## Scope: it does not apply everywhere

A profile governs a project only when that project invokes it. The emitted
skill writes `.taste-opt-in.md` into a repository the first time it is used
there, recording which profile applies and any narrowing the person wants.

Because implicit invocation fires before any file check, the emitted skill's
first action is to look for that file. If it is absent, the skill says what it
is and offers to create it, then stops. It does not load the profile and it
does not comment on the work.

## Installing

Shell out to the `skills` CLI rather than writing symlinks by hand:

```bash
npx skills@latest add <directory> -g
```

It prompts for which agents to install to, or takes `-a` to name them. It
symlinks by default, so every agent resolves to one profile and a choice
recorded through one is visible to the rest.

Tell them two things before running it:

- `--copy` duplicates the directory into every selected agent path. That forks
  the record, so a choice written through one agent becomes invisible to the
  others.
- Removing the skill through the CLI removes the profile with it. The profile
  should be version-controlled somewhere independent of where it is installed.

## Template

`assets/emitted-skill/` holds the files to copy. Replace `{{SKILL_NAME}}` with
the name they chose and `{{PROFILE_SUMMARY}}` with one sentence naming what
the profile covers, drawn from their own principles rather than written fresh.
