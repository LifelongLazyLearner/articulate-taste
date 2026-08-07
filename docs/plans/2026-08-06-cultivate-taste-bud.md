# cultivate-taste-bud Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a content-neutral skill that interviews any person into a self-evolving `TASTE.md`, with the promotion gate enforced by a tested script rather than by prose.

**Architecture:** A prompt-driven skill (`SKILL.md` plus cold-loaded references) supplies the interview loop and neutrality rules. A small Python script supplies the deterministic parts — parsing a profile, computing each principle's status from the promotion gate, and resolving history references. The script exists because a gate written only as prose is a gate an agent drifts from; running it costs no context beyond its output.

**Tech Stack:** Markdown skill files. Python 3 standard library only (no dependencies, no install). `unittest` for tests.

**Spec:** [docs/specs/2026-08-06-cultivate-taste-bud-design.md](../specs/2026-08-06-cultivate-taste-bud-design.md), signed off.

> **Superseded — historical record only.** This plan was written before the
> method was tested on a person. The code in
> `skills/cultivate-taste-bud/scripts/` is canonical and no longer matches
> what is described below.
>
> What changed: the evidence-tier ladder and the paid-evidence requirement
> were removed entirely, because asking people to prove their own values is
> both rude and weaker evidence than it looks. A principle now firms up when
> the profile demonstrates it understood the person — by predicting a
> judgment correctly, or by producing work they pick out blind. Every code
> sample below that mentions tiers or `paid_by` is obsolete.
>
> Kept for the record of how it was built, including the parts that were
> wrong. Do not implement from it.

## Execution order

This repo is governed by the author's `TASTE.md`, invoked explicitly. Its
Decision Test asks whether the core value can enter reality now, so the
tasks below are executed in this order rather than in numeric order:

**7 → 8 → 6 → first contact → 1 → 2 → 3 → 4 → 5 → 9**

After Task 6 the skill is runnable end to end by a real person. Stop there,
run one full session against a fixture persona, and fix what that reveals
before building the validator. A validator written before the loop has ever
run is a validator built on a guess.

Tasks 1–5 harden what already works. Task 9 releases it.

---

## Format decision made during planning

The spec's example log header reads `## [2026-08-06] choice | declined-rewrite` while the profile references `[2026-08-06-declined-rewrite]`. Those must resolve to each other. Canonical rule, used by every task below:

**A decision's id is `<date>-<slug>`, composed from the log entry's date and slug.** The log stays readable without repeating the date; the profile references the composed id. The validator composes it.

## File structure

| File | Responsibility |
|---|---|
| `skills/cultivate-taste-bud/SKILL.md` | Loop states and neutrality rules. Nothing else. |
| `skills/cultivate-taste-bud/agents/openai.yaml` | Per-agent metadata, invocation policy |
| `skills/cultivate-taste-bud/references/elicitation.md` | Question bank by tier, tension construction |
| `skills/cultivate-taste-bud/references/format.md` | `TASTE.md` and `log.md` formats |
| `skills/cultivate-taste-bud/references/promotion.md` | Gate, demotion, prediction |
| `skills/cultivate-taste-bud/assets/TASTE.template.md` | Starting profile |
| `skills/cultivate-taste-bud/assets/log.template.md` | Starting history |
| `skills/cultivate-taste-bud/scripts/taste_profile.py` | Parsing, gate, validation, CLI |
| `skills/cultivate-taste-bud/scripts/test_taste_profile.py` | Unit tests |
| `skills/cultivate-taste-bud/fixtures/` | Two opposed personas for the neutrality check |
| `.claude-plugin/plugin.json` | Claude Code plugin manifest |
| `README.md` | Rewritten for open source |

Parsing, the gate, and the CLI live in one module because they change together and the whole file fits in context at once. Tests sit beside it.

**Out of MVP, per spec:** `references/emitting.md` and the emitted personal skill.

---

### Task 1: Scaffold and parser for principles

**Files:**
- Create: `skills/cultivate-taste-bud/scripts/taste_profile.py`
- Test: `skills/cultivate-taste-bud/scripts/test_taste_profile.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest

from taste_profile import parse_profile

PROFILE = """# Taste Profile

## Core Principles

### kindness-over-authenticity — core

**Statement.** Kindness outranks being unvarnished.

**Boundary.** Does not require silence or dishonesty.

**Test.** Am I using honesty as an excuse for avoidable harm?

**Paid by.** [2026-08-06-declined-rewrite] — turned the work down, lost the client.

### enter-reality — provisional

**Statement.** Ship once the core value can arrive.

**Boundary.** Does not excuse shipping work that fails its quality conditions.
"""


class TestParseProfile(unittest.TestCase):
    def test_parses_id_and_declared_status(self):
        principles = parse_profile(PROFILE)
        self.assertEqual(
            [(p.id, p.declared) for p in principles],
            [("kindness-over-authenticity", "core"), ("enter-reality", "provisional")],
        )

    def test_parses_boundary_test_and_paid_refs(self):
        first = parse_profile(PROFILE)[0]
        self.assertTrue(first.boundary)
        self.assertTrue(first.test)
        self.assertEqual(first.paid_by, ["2026-08-06-declined-rewrite"])

    def test_missing_fields_are_empty(self):
        second = parse_profile(PROFILE)[1]
        self.assertTrue(second.boundary)
        self.assertEqual(second.test, "")
        self.assertEqual(second.paid_by, [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'taste_profile'`

- [ ] **Step 3: Write minimal implementation**

```python
"""Parse and validate a taste profile against the promotion gate."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

HEADING = re.compile(r"^### (?P<id>[a-z0-9-]+) — (?P<status>core|provisional|candidate)\s*$")
FIELD = re.compile(r"^\*\*(?P<name>Statement|Boundary|Test|Paid by)\.\*\*\s*(?P<value>.*)$")
REF = re.compile(r"\[(?P<ref>\d{4}-\d{2}-\d{2}-[a-z0-9-]+)\]")


@dataclass
class Principle:
    id: str
    declared: str
    statement: str = ""
    boundary: str = ""
    test: str = ""
    paid_by: list[str] = field(default_factory=list)


def parse_profile(text: str) -> list[Principle]:
    principles: list[Principle] = []
    current: Principle | None = None
    for line in text.splitlines():
        heading = HEADING.match(line)
        if heading:
            current = Principle(id=heading.group("id"), declared=heading.group("status"))
            principles.append(current)
            continue
        if current is None:
            continue
        found = FIELD.match(line)
        if not found:
            continue
        name, value = found.group("name"), found.group("value").strip()
        if name == "Statement":
            current.statement = value
        elif name == "Boundary":
            current.boundary = value
        elif name == "Test":
            current.test = value
        elif name == "Paid by":
            current.paid_by = REF.findall(value)
    return principles
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: PASS, 3 tests

- [ ] **Step 5: Commit**

```bash
git add skills/cultivate-taste-bud/scripts/
git commit -m "feat: parse principles from a taste profile"
```

---

### Task 2: Parser for the history log

**Files:**
- Modify: `skills/cultivate-taste-bud/scripts/taste_profile.py`
- Test: `skills/cultivate-taste-bud/scripts/test_taste_profile.py`

- [ ] **Step 1: Write the failing test**

Append to the test file, above the `if __name__` block:

```python
from taste_profile import parse_log

LOG = """# History

## [2026-08-06] choice | declined-rewrite
won: kindness-over-authenticity · lost: inner-honesty · tier: 2
price: lost the client

## [2026-08-06] promote | kindness-over-authenticity
boundary + paid evidence from declined-rewrite

## [2026-08-07] choice | named-favourite-album
won: enter-reality · lost: none · tier: 4
price: none
"""


class TestParseLog(unittest.TestCase):
    def test_composes_decision_id_from_date_and_slug(self):
        entries = parse_log(LOG)
        self.assertIn("2026-08-06-declined-rewrite", entries)
        self.assertIn("2026-08-07-named-favourite-album", entries)

    def test_reads_action_and_tier(self):
        entry = parse_log(LOG)["2026-08-06-declined-rewrite"]
        self.assertEqual(entry.action, "choice")
        self.assertEqual(entry.tier, 2)

    def test_entry_without_tier_has_none(self):
        entry = parse_log(LOG)["2026-08-06-kindness-over-authenticity"]
        self.assertEqual(entry.action, "promote")
        self.assertIsNone(entry.tier)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: FAIL with `ImportError: cannot import name 'parse_log'`

- [ ] **Step 3: Write minimal implementation**

Add to `taste_profile.py`:

```python
LOG_HEAD = re.compile(r"^## \[(?P<date>\d{4}-\d{2}-\d{2})\] (?P<action>[a-z]+) \| (?P<slug>[a-z0-9-]+)\s*$")
LOG_KV = re.compile(r"^(?P<key>[a-z_]+):\s*(?P<value>.+)$")
TIER = re.compile(r"tier:\s*(?P<tier>\d)")


@dataclass
class Entry:
    id: str
    action: str
    tier: int | None = None


def parse_log(text: str) -> dict[str, Entry]:
    entries: dict[str, Entry] = {}
    current: Entry | None = None
    for line in text.splitlines():
        head = LOG_HEAD.match(line)
        if head:
            entry_id = f"{head.group('date')}-{head.group('slug')}"
            current = Entry(id=entry_id, action=head.group("action"))
            entries[entry_id] = current
            continue
        if current is None:
            continue
        tier = TIER.search(line)
        if tier:
            current.tier = int(tier.group("tier"))
    return entries
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: PASS, 6 tests

- [ ] **Step 5: Commit**

```bash
git add skills/cultivate-taste-bud/scripts/
git commit -m "feat: parse the history log into decisions"
```

---

### Task 3: The promotion gate

This is Pass Condition 2 made mechanical. A principle supported only by Tier 4 evidence must not reach core.

**Files:**
- Modify: `skills/cultivate-taste-bud/scripts/taste_profile.py`
- Test: `skills/cultivate-taste-bud/scripts/test_taste_profile.py`

- [ ] **Step 1: Write the failing test**

```python
from taste_profile import Entry, Principle, computed_status


class TestPromotionGate(unittest.TestCase):
    def decisions(self, **tiers):
        return {ref: Entry(id=ref, action="choice", tier=tier) for ref, tier in tiers.items()}

    def test_no_boundary_is_candidate(self):
        p = Principle(id="x", declared="core", test="q?", paid_by=["2026-08-06-a"])
        self.assertEqual(computed_status(p, self.decisions(**{"2026-08-06-a": 2})), "candidate")

    def test_boundary_without_test_is_provisional(self):
        p = Principle(id="x", declared="core", boundary="stops here", paid_by=["2026-08-06-a"])
        self.assertEqual(computed_status(p, self.decisions(**{"2026-08-06-a": 2})), "provisional")

    def test_boundary_and_test_and_paid_evidence_is_core(self):
        p = Principle(id="x", declared="core", boundary="stops here", test="q?", paid_by=["2026-08-06-a"])
        self.assertEqual(computed_status(p, self.decisions(**{"2026-08-06-a": 2})), "core")

    def test_tier_four_evidence_alone_cannot_reach_core(self):
        p = Principle(id="x", declared="core", boundary="stops here", test="q?", paid_by=["2026-08-06-a"])
        self.assertEqual(computed_status(p, self.decisions(**{"2026-08-06-a": 4})), "provisional")

    def test_one_strong_decision_among_weak_ones_is_enough(self):
        p = Principle(
            id="x", declared="core", boundary="stops here", test="q?",
            paid_by=["2026-08-06-a", "2026-08-06-b"],
        )
        decisions = self.decisions(**{"2026-08-06-a": 4, "2026-08-06-b": 3})
        self.assertEqual(computed_status(p, decisions), "core")

    def test_unresolved_reference_does_not_confer_core(self):
        p = Principle(id="x", declared="core", boundary="stops here", test="q?", paid_by=["2026-08-06-missing"])
        self.assertEqual(computed_status(p, {}), "provisional")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: FAIL with `ImportError: cannot import name 'computed_status'`

- [ ] **Step 3: Write minimal implementation**

```python
CONFIRMING_TIERS = (1, 2, 3)


def computed_status(principle: Principle, decisions: dict[str, Entry]) -> str:
    """Status implied by the evidence, ignoring what the profile declares.

    Tier is read from the decision, never stored on the principle: a
    denormalised copy drifts. Tier 4 may propose a principle but never
    confirm one.
    """
    if not principle.boundary:
        return "candidate"
    if not principle.test:
        return "provisional"
    for ref in principle.paid_by:
        decision = decisions.get(ref)
        if decision and decision.tier in CONFIRMING_TIERS:
            return "core"
    return "provisional"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: PASS, 12 tests

- [ ] **Step 5: Commit**

```bash
git add skills/cultivate-taste-bud/scripts/
git commit -m "feat: compute principle status from the promotion gate"
```

---

### Task 4: Validation and CLI

**Files:**
- Modify: `skills/cultivate-taste-bud/scripts/taste_profile.py`
- Test: `skills/cultivate-taste-bud/scripts/test_taste_profile.py`

- [ ] **Step 1: Write the failing test**

```python
from taste_profile import validate


class TestValidate(unittest.TestCase):
    def test_clean_profile_reports_nothing(self):
        self.assertEqual(validate(PROFILE, LOG), [])

    def test_overclaimed_status_is_reported(self):
        profile = PROFILE.replace("### enter-reality — provisional", "### enter-reality — core")
        errors = validate(profile, LOG)
        self.assertEqual(len(errors), 1)
        self.assertIn("enter-reality", errors[0])
        self.assertIn("declared core", errors[0])
        self.assertIn("evidence supports provisional", errors[0])

    def test_dangling_reference_is_reported(self):
        profile = PROFILE.replace("2026-08-06-declined-rewrite", "2026-08-06-nonexistent")
        errors = validate(profile, LOG)
        self.assertTrue(any("2026-08-06-nonexistent" in e for e in errors))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: FAIL with `ImportError: cannot import name 'validate'`

- [ ] **Step 3: Write minimal implementation**

```python
def validate(profile_text: str, log_text: str) -> list[str]:
    decisions = parse_log(log_text)
    errors: list[str] = []
    for principle in parse_profile(profile_text):
        for ref in principle.paid_by:
            if ref not in decisions:
                errors.append(f"{principle.id}: paid-by reference {ref} resolves to no history entry")
        implied = computed_status(principle, decisions)
        if implied != principle.declared:
            errors.append(
                f"{principle.id}: declared {principle.declared}, evidence supports {implied}"
            )
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: taste_profile.py <TASTE.md> <log.md>")
        return 2
    with open(argv[1], encoding="utf-8") as handle:
        profile_text = handle.read()
    with open(argv[2], encoding="utf-8") as handle:
        log_text = handle.read()
    errors = validate(profile_text, log_text)
    for error in errors:
        print(error)
    if errors:
        return 1
    print("profile consistent with its evidence")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: PASS, 15 tests

- [ ] **Step 5: Commit**

```bash
git add skills/cultivate-taste-bud/scripts/
git commit -m "feat: validate a profile against its recorded evidence"
```

---

### Task 5: Neutrality check across fixtures

This is Pass Condition 5. Two personas seeded with opposed rejections must not share core principles.

**Files:**
- Create: `skills/cultivate-taste-bud/fixtures/ship-fast/TASTE.md`
- Create: `skills/cultivate-taste-bud/fixtures/ship-fast/log.md`
- Create: `skills/cultivate-taste-bud/fixtures/hold-the-line/TASTE.md`
- Create: `skills/cultivate-taste-bud/fixtures/hold-the-line/log.md`
- Modify: `skills/cultivate-taste-bud/scripts/taste_profile.py`
- Test: `skills/cultivate-taste-bud/scripts/test_taste_profile.py`

- [ ] **Step 1: Write the failing test**

```python
import os

from taste_profile import core_ids, overlapping_cores

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def read_fixture(name):
    base = os.path.join(FIXTURES, name)
    with open(os.path.join(base, "TASTE.md"), encoding="utf-8") as handle:
        profile = handle.read()
    with open(os.path.join(base, "log.md"), encoding="utf-8") as handle:
        log = handle.read()
    return profile, log


class TestNeutrality(unittest.TestCase):
    def test_each_fixture_is_internally_valid(self):
        for name in ("ship-fast", "hold-the-line"):
            profile, log = read_fixture(name)
            self.assertEqual(validate(profile, log), [], f"{name} is inconsistent")

    def test_each_fixture_has_at_least_one_core_principle(self):
        for name in ("ship-fast", "hold-the-line"):
            profile, log = read_fixture(name)
            self.assertTrue(core_ids(profile, log), f"{name} produced no core principle")

    def test_opposed_personas_share_no_core_principle(self):
        a_profile, a_log = read_fixture("ship-fast")
        b_profile, b_log = read_fixture("hold-the-line")
        self.assertEqual(overlapping_cores(a_profile, a_log, b_profile, b_log), set())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: FAIL with `ImportError: cannot import name 'core_ids'`

- [ ] **Step 3: Write the fixtures and the implementation**

`fixtures/ship-fast/TASTE.md`:

```markdown
# Taste Profile

## Core Principles

### arrival-beats-polish — core

**Statement.** Work that has not reached anyone has not yet done anything.

**Boundary.** Does not excuse shipping something that misleads or breaks trust.

**Test.** Can the core value reach someone safely today?

**Paid by.** [2026-03-02-shipped-rough-launch] — shipped with known rough edges and took the criticism.
```

`fixtures/ship-fast/log.md`:

```markdown
# History

## [2026-03-02] choice | shipped-rough-launch
won: arrival-beats-polish · lost: craft-before-exposure · tier: 2
price: public criticism of the rough edges

## [2026-03-02] promote | arrival-beats-polish
boundary + paid evidence from shipped-rough-launch
```

`fixtures/hold-the-line/TASTE.md`:

```markdown
# Taste Profile

## Core Principles

### craft-before-exposure — core

**Statement.** Nothing goes out carrying a flaw I already know about.

**Boundary.** Does not licence polishing forever when the flaw is cosmetic.

**Test.** Is there a defect I would be embarrassed to have shipped knowingly?

**Paid by.** [2026-04-11-missed-the-window] — held the release and lost the launch window.
```

`fixtures/hold-the-line/log.md`:

```markdown
# History

## [2026-04-11] choice | missed-the-window
won: craft-before-exposure · lost: arrival-beats-polish · tier: 2
price: lost the launch window entirely

## [2026-04-11] promote | craft-before-exposure
boundary + paid evidence from missed-the-window
```

Add to `taste_profile.py`:

```python
def core_ids(profile_text: str, log_text: str) -> set[str]:
    """Ids of principles the evidence actually supports as core."""
    decisions = parse_log(log_text)
    return {
        p.id
        for p in parse_profile(profile_text)
        if computed_status(p, decisions) == "core"
    }


def overlapping_cores(a_profile: str, a_log: str, b_profile: str, b_log: str) -> set[str]:
    return core_ids(a_profile, a_log) & core_ids(b_profile, b_log)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: PASS, 18 tests

- [ ] **Step 5: Commit**

```bash
git add skills/cultivate-taste-bud/
git commit -m "test: opposed personas produce disjoint core principles"
```

---

### Task 6: Profile and history templates

**Files:**
- Create: `skills/cultivate-taste-bud/assets/TASTE.template.md`
- Create: `skills/cultivate-taste-bud/assets/log.template.md`
- Test: `skills/cultivate-taste-bud/scripts/test_taste_profile.py`

- [ ] **Step 1: Write the failing test**

```python
TEMPLATES = os.path.join(os.path.dirname(__file__), "..", "assets")


class TestTemplates(unittest.TestCase):
    def test_template_carries_every_required_section(self):
        with open(os.path.join(TEMPLATES, "TASTE.template.md"), encoding="utf-8") as handle:
            profile = handle.read()
        for section in (
            "## Purpose",
            "## Core Principles",
            "## Provisional Preferences",
            "## Open Tensions",
            "## Decision Test",
            "## Evidence",
            "## Revision Record",
            "## Scope and Authority",
        ):
            self.assertIn(section, profile)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: FAIL with `FileNotFoundError` for `TASTE.template.md`

- [ ] **Step 3: Write the templates**

`assets/TASTE.template.md`:

```markdown
# Taste Profile

**Version:** 0.1
**Status:** In progress
**Last updated:** <date>

## Purpose

What this profile is for, in the person's own words.

## Core Principles

Principles the evidence supports. Each carries a stable slug id, a boundary,
a test question, and at least one decision that cost something.

## Provisional Preferences

Boundaries drafted, no paid evidence yet. Not yet load-bearing.

## Open Tensions

Unresolved dilemmas, and principles still missing a boundary, a test, or paid
evidence. This section is where the next session resumes.

## Decision Test

The Test line of each core principle, in order.

## Evidence

Sources behind the principles, and what each one demonstrates.

## Revision Record

Prior wording of anything demoted or narrowed, preserved intact.

## Scope and Authority

This profile is guidance, not automatic authority. It applies to a project
only when that project invokes it. It does not override evidence, safety,
explicit constraints, or another person's authority over their own choices.
```

`assets/log.template.md`:

```markdown
# History

Append-only. Newest last. One entry per event.

Actions: seed, choice, promote, demote, predict, tension, leak.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: PASS, 20 tests

- [ ] **Step 5: Commit**

```bash
git add skills/cultivate-taste-bud/assets/
git commit -m "feat: add profile and history templates"
```

---

### Task 7: SKILL.md and per-agent metadata

**Files:**
- Create: `skills/cultivate-taste-bud/SKILL.md`
- Create: `skills/cultivate-taste-bud/agents/openai.yaml`
- Test: `skills/cultivate-taste-bud/scripts/test_taste_profile.py`

- [ ] **Step 1: Write the failing test**

```python
SKILL = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")


class TestSkillFrontmatter(unittest.TestCase):
    def frontmatter(self):
        with open(SKILL, encoding="utf-8") as handle:
            text = handle.read()
        _, block, _ = text.split("---", 2)
        fields = {}
        for line in block.strip().splitlines():
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
        return fields

    def test_name_obeys_the_spec(self):
        name = self.frontmatter()["name"]
        self.assertEqual(name, "cultivate-taste-bud")
        self.assertLessEqual(len(name), 64)
        self.assertRegex(name, r"^[a-z0-9-]+$")

    def test_name_avoids_reserved_words(self):
        name = self.frontmatter()["name"]
        self.assertNotIn("claude", name)
        self.assertNotIn("anthropic", name)

    def test_description_states_what_and_when_within_limit(self):
        description = self.frontmatter()["description"]
        self.assertLessEqual(len(description), 1024)
        self.assertIn("Use when", description)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: FAIL with `FileNotFoundError` for `SKILL.md`

- [ ] **Step 3: Write SKILL.md and the agent metadata**

`SKILL.md`:

````markdown
---
name: cultivate-taste-bud
description: Interview a person into their own taste profile — the standards behind their judgment of creative work, products, code, and decisions — and keep it evolving as new evidence arrives. Produces a TASTE.md plus an append-only history. Use when someone wants to cultivate or articulate their taste, build a taste profile, work out what they actually value, or make their standards legible to an agent. Not for applying an existing profile, and not a visual style guide.
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
5. If your own preference shapes a question, append a `leak` entry to the history.
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

## Loop

Enter anywhere, stop anywhere. Read `TASTE.md` first; `Open Tensions` says
where to resume.

1. **seed** — Collect rejections and costly past decisions. Question bank in
   [references/elicitation.md](references/elicitation.md). Distil straight
   into the profile; discard verbatim material unless retention was opted
   into.
2. **tension** — Build a concrete dilemma where two of their own values
   collide, with a stated price. Never generic.
3. **choice** — They choose. Record the choice, the price, what won, what
   lost, and the tier.
4. **boundary** — Only now ask for reasoning: where does this stop, and what
   would make you abandon it?
5. **gate** — Apply [references/promotion.md](references/promotion.md).
6. **record** — Update the principle and append the history entry in one
   pass. Formats in [references/format.md](references/format.md).
7. **predict** — Once a core principle exists, predict their judgment on a
   held-out item. A miss opens a tension and re-enters the loop.

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
````

`agents/openai.yaml`:

```yaml
interface:
  display_name: "Cultivate Taste Bud"
  short_description: "Build your own evolving taste profile"
policy:
  allow_implicit_invocation: false
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: PASS, 23 tests

- [ ] **Step 5: Commit**

```bash
git add skills/cultivate-taste-bud/SKILL.md skills/cultivate-taste-bud/agents/
git commit -m "feat: add the skill entry point and agent metadata"
```

---

### Task 8: Reference files

**Files:**
- Create: `skills/cultivate-taste-bud/references/elicitation.md`
- Create: `skills/cultivate-taste-bud/references/format.md`
- Create: `skills/cultivate-taste-bud/references/promotion.md`
- Test: `skills/cultivate-taste-bud/scripts/test_taste_profile.py`

- [ ] **Step 1: Write the failing test**

```python
REFERENCES = os.path.join(os.path.dirname(__file__), "..", "references")


class TestReferences(unittest.TestCase):
    def test_every_reference_linked_from_skill_exists(self):
        with open(SKILL, encoding="utf-8") as handle:
            skill = handle.read()
        linked = set(re.findall(r"\(references/([a-z-]+\.md)\)", skill))
        self.assertEqual(linked, {"elicitation.md", "format.md", "promotion.md"})
        for name in linked:
            self.assertTrue(os.path.exists(os.path.join(REFERENCES, name)), name)
```

Add `import re` to the top of the test file if it is not already there.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: FAIL, `elicitation.md` does not exist

- [ ] **Step 3: Write the references**

> **Superseded by what shipped.** Tasks 7, 8, and 6 are complete, and the
> reference files on disk are canonical. The content quoted below was the
> plan's draft and has since changed under first-contact testing — the
> question bank now opens with forced choice rather than recall, and every
> question is a pick. Read the shipped files, not these excerpts.

`references/elicitation.md`:

```markdown
# Elicitation

## Why not a plain interview

Interviewing is the weakest instrument here and fails four ways:
confabulation (people invent plausible causes for their own judgments),
prestige contamination (asking what they admire harvests safe canonical
answers), cheap assent (agreeing to a proposed belief costs nothing, so it
carries almost no information), and the articulacy filter (strong taste in
visual and musical domains resists words).

Interview is for exactly one job: naming the boundary after a choice has
already been made.

## Tier 2 — rejection-first opening

People perform their likes. They perform their dislikes far less. Open here.

- What did you kill after investing real work in it? What made it not worth
  finishing?
- What do you admire but would never make? Why not?
- What is praised in your field that you think is overrated?
- What did you refuse to do for money — and what price would have changed
  your answer?
- When did you last change your mind about what is good? What broke it?
- Show me something you made that you are not proud of. What is wrong with it?
- What would you replace immediately if it broke, and what would you let go?

## Tier 3 — forced choice

Built per person from their own material. Every dilemma names a concrete
price. A dilemma without a stated cost is a Tier 4 question in disguise.

Construction: take two candidate values already in their profile, find a
situation from their own history or plans where both cannot hold, and state
what each choice costs them specifically.

## Tier 1 — artifact mining

Optional. Offer when they have a repo, portfolio, or body of writing. Read
what they shipped, kept, and deleted. Skip without penalty — the method must
work cold for someone with nothing to mine.

## One question at a time

Ask one question, wait, then ask the next. Offer your recommended answer so
they can accept it in a word. Look facts up rather than asking for them.

## Any question can be declined

These questions ask about failure, refusal, and work someone is not proud
of. That is where the evidence is, and it is also exposing.

Say once, at the start, that any question can be skipped without a reason.
When someone declines, move on immediately — no rephrasing it as a gentler
version, no returning to it later, no noting that they avoided it. Record
only that the area is unexplored, never that they were unwilling.

A profile built by pressure is not evidence of their taste. It is evidence
of what they will say to end an uncomfortable conversation.
```

`references/format.md`:

```markdown
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
```

`references/promotion.md`:

```markdown
# Promotion, demotion, prediction

## Gate

- boundary present → provisional
- boundary present, test present, and at least one paid decision at tier 1–3
  → core
- otherwise → candidate

Tier is read from the recorded decision, never copied onto the principle. A
denormalised copy drifts.

The test question is authored by the person at promotion time, in answer to
"what question would you ask yourself to check this?" Do not derive it
mechanically from the boundary prose.

## Demotion

The same gate run backwards, and the heart of self-evolution. A recorded
choice that contradicts a core principle at real cost is detected without
waiting to be asked, and surfaced: here is the principle, here is the choice
that contradicts it, here is what it cost. They decide.

On confirmation, demote and move the prior wording to the Revision Record
intact. Without confirmation, write nothing and record the contradiction as
an open tension so it resurfaces later rather than being lost.

Detection is unprompted. Mutation never is.

Growth is never rewritten as though the earlier understanding never existed.
A revision may represent a more accurate account of the same underlying
person.

## Prediction

Once a core principle exists, predict their judgment on an item the profile
was not built from, and the reasoning. They score it.

A miss is not their failure. It is the highest-quality evidence the system
can obtain about itself — every miss opens a tension and re-enters the loop.

Hits are recorded but confer no promotion. A prediction the profile got right
shows only that the profile is self-consistent.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest test_taste_profile -v`
Expected: PASS, 24 tests

- [ ] **Step 5: Commit**

```bash
git add skills/cultivate-taste-bud/references/
git commit -m "feat: add elicitation, format, and promotion references"
```

---

### Task 9: Distribution manifest and README

**Files:**
- Create: `.claude-plugin/plugin.json`
- Modify: `README.md`

- [ ] **Step 1: Write the plugin manifest**

```json
{
  "name": "taste-bud",
  "description": "Cultivate your own taste profile, and keep it evolving.",
  "version": "0.1.0",
  "skills": ["./skills/cultivate-taste-bud"]
}
```

- [ ] **Step 2: Verify the skill is discoverable**

Run: `npx skills@latest add ./skills/cultivate-taste-bud --list`
Expected: lists `cultivate-taste-bud` without installing anything.

If the manifest schema is rejected, correct it against the error and re-run. The schema was not verified during design.

- [ ] **Step 3: Rewrite README.md**

```markdown
# Taste Bud

A method for cultivating your own taste profile — the standards behind how
you judge creative work, products, code, and decisions — and keeping it
evolving as new evidence arrives.

It is content-neutral. It elicits what *you* value and records it. It does
not install anyone else's aesthetic.

## Install

```bash
claude plugins install taste-bud          # Claude Code
npx skills@latest add <owner>/taste-bud   # every other agent
```

## Use

Run `/cultivate-taste-bud`. It interviews you, one question at a time, and
writes a `TASTE.md` plus an append-only `log.md`. Stop whenever you like —
the profile is usable at any point, and the next session resumes from
`Open Tensions`.

## How it works

Taste is elicited by forced tradeoffs over your own examples, not by asking
what you believe. Evidence is graded: what you made and killed, decisions
that cost you something, choices made under a stated price, and — weakest —
what you say you admire. Stated belief may propose a principle. It may never
confirm one.

A principle becomes core only when it has an explicit boundary, a test
question you wrote, and at least one decision where holding it cost you.
There are no thresholds and no magic numbers.

The profile predicts your judgment on things it was not built from. When it
misses, that is the best evidence it can get about itself, and it revises.

## Honest limits

- It depends on your having had costly choices to recall. Early in a career,
  that layer is thin.
- People invent plausible reasons for their own judgments. The method works
  around this by asking for the choice before the reason, but it cannot
  eliminate it.
- The prediction gate measures agreement between the profile and what you
  say, not what you do. It catches drift, not self-deception.
- The profile is only as honest as your willingness to record choices that
  embarrass you.

## Verify a profile

```bash
python3 skills/cultivate-taste-bud/scripts/taste_profile.py TASTE.md log.md
```

Reports any principle claiming a status its evidence does not support.

## Privacy

Raw transcripts are discarded by default. An installed profile is symlinked
into every agent directory you select, so anything kept inside it sits in
that many file-discovery paths. Opt-in retention is stored outside the skill
directory.
```

- [ ] **Step 4: Run the full suite once more**

Run: `cd skills/cultivate-taste-bud/scripts && python3 -m unittest -v`
Expected: PASS, 24 tests

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin/ README.md
git commit -m "feat: add plugin manifest and rewrite README for release"
```

---

## Verification against pass conditions

| # | Condition | Where it is verified |
|---|---|---|
| 1 | Stranger completes a session, gets a core principle with boundary, test, paid evidence | Task 6 templates + Task 7 loop; end-to-end run |
| 2 | No core principle rests on Tier 4 alone | Task 3, `test_tier_four_evidence_alone_cannot_reach_core` |
| 3 | Second session resumes from `TASTE.md` | Task 6, `Open Tensions` section required by test |
| 4 | Prediction produces hit/miss, miss opens a tension | Task 8, `references/promotion.md`; format in Task 8 |
| 5 | Opposed personas produce disjoint core sets | Task 5, `test_opposed_personas_share_no_core_principle` |
| 6 | A contradiction is surfaced unprompted; demotion written only on confirmation, prior wording preserved | Task 8, demotion section; Revision Record required by Task 6 test |

Conditions 1, 4, and 6 are prompt-driven and cannot be unit-tested. They are verified by running the skill end to end against a fixture persona after Task 9, which is the first honest check that the loop works.

## Not in this plan

- The emitted personal skill and `references/emitting.md` — out of MVP per spec.
- Publishing anywhere. Not authorized.
- Running the skill against real personal answers. Not authorized.
- Migrating this repo's `TASTE.md` v0.5.
