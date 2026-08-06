"""Tests for the skill package and the promotion gate.

Structural tests cover what a stranger's install depends on. Gate tests cover
the rule the whole method turns on: stated belief may propose a principle,
never confirm one.
"""

import os
import re
import unittest

from taste_profile import (
    Entry,
    Principle,
    computed_status,
    core_ids,
    overlapping_cores,
    parse_log,
    parse_profile,
    predictable_ids,
    validate,
)

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(HERE, "..", "SKILL.md")
REFERENCES = os.path.join(HERE, "..", "references")
TEMPLATES = os.path.join(HERE, "..", "assets")
FIXTURES = os.path.join(HERE, "..", "fixtures")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def read_fixture(name):
    base = os.path.join(FIXTURES, name)
    return read(os.path.join(base, "TASTE.md")), read(os.path.join(base, "log.md"))


PROFILE = """# Taste Profile

## Core Principles

### kindness-over-authenticity — core

**Statement.** Kindness outranks being unvarnished.

**Boundary.** Does not require silence or dishonesty.

**Test.** Am I using honesty as an excuse for avoidable harm?

**Paid by.** [2026-08-06-declined-rewrite] — turned the work down, lost the client.

## Provisional Preferences

### enter-reality — provisional

**Statement.** Ship once the core value can arrive.

**Boundary.** Does not excuse shipping work that fails its quality conditions.
"""

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

    def test_omitted_fields_are_empty(self):
        second = parse_profile(PROFILE)[1]
        self.assertTrue(second.boundary)
        self.assertEqual(second.test, "")
        self.assertEqual(second.paid_by, [])

    def test_unknown_fields_are_ignored(self):
        profile = PROFILE + "\n**Named trade.** Shipped pretty once and regretted it.\n"
        self.assertEqual(len(parse_profile(profile)), 2)


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


class TestPromotionGate(unittest.TestCase):
    def decisions(self, **tiers):
        return {ref: Entry(id=ref, action="choice", tier=tier) for ref, tier in tiers.items()}

    def test_no_boundary_is_candidate(self):
        p = Principle(id="x", declared="core", test="q?", paid_by=["a"])
        self.assertEqual(computed_status(p, self.decisions(a=2)), "candidate")

    def test_boundary_without_test_is_provisional(self):
        p = Principle(id="x", declared="core", boundary="stops here", paid_by=["a"])
        self.assertEqual(computed_status(p, self.decisions(a=2)), "provisional")

    def test_boundary_and_test_and_paid_evidence_is_core(self):
        p = Principle(id="x", declared="core", boundary="stops here", test="q?", paid_by=["a"])
        self.assertEqual(computed_status(p, self.decisions(a=2)), "core")

    def test_tier_four_evidence_alone_cannot_reach_core(self):
        p = Principle(id="x", declared="core", boundary="stops here", test="q?", paid_by=["a"])
        self.assertEqual(computed_status(p, self.decisions(a=4)), "provisional")

    def test_one_strong_decision_among_weak_ones_is_enough(self):
        p = Principle(
            id="x", declared="core", boundary="stops here", test="q?", paid_by=["a", "b"]
        )
        self.assertEqual(computed_status(p, self.decisions(a=4, b=3)), "core")

    def test_unresolved_reference_does_not_confer_core(self):
        p = Principle(id="x", declared="core", boundary="stops here", test="q?", paid_by=["gone"])
        self.assertEqual(computed_status(p, {}), "provisional")


class TestPredictable(unittest.TestCase):
    def test_a_boundary_is_enough_to_predict_from(self):
        self.assertEqual(
            predictable_ids(PROFILE),
            {"kindness-over-authenticity", "enter-reality"},
        )

    def test_provisional_principles_are_predictable(self):
        self.assertIn("enter-reality", predictable_ids(PROFILE))

    def test_a_principle_without_a_boundary_is_not_predictable(self):
        profile = PROFILE.replace(
            "**Boundary.** Does not excuse shipping work that fails its quality conditions.\n",
            "",
        )
        self.assertNotIn("enter-reality", predictable_ids(profile))


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
        self.assertTrue(any("2026-08-06-nonexistent" in error for error in errors))


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


class TestSkillFrontmatter(unittest.TestCase):
    def frontmatter(self):
        _, block, _ = read(SKILL).split("---", 2)
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


class TestReferences(unittest.TestCase):
    def test_every_reference_linked_from_skill_exists(self):
        linked = set(re.findall(r"\(references/([a-z-]+\.md)\)", read(SKILL)))
        self.assertEqual(linked, {"elicitation.md", "format.md", "promotion.md"})
        for name in linked:
            self.assertTrue(os.path.exists(os.path.join(REFERENCES, name)), name)


class TestTemplates(unittest.TestCase):
    def test_template_carries_every_required_section(self):
        profile = read(os.path.join(TEMPLATES, "TASTE.template.md"))
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


if __name__ == "__main__":
    unittest.main()
