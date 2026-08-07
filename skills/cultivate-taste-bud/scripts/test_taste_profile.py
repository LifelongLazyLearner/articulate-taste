"""Tests for the skill package and the promotion rule.

The rule under test: a person's stated value is honoured as given, and a
principle firms up only once the profile has predicted one of their judgments
correctly. Nobody is asked to prove anything about themselves.
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

**Confirmed by.** [2026-08-06-blunt-feedback] — guessed how you'd read it, correctly.

## Provisional Preferences

### enter-reality — provisional

**Statement.** Ship once the core value can arrive.

**Boundary.** Does not excuse shipping work that fails its quality conditions.
"""

LOG = """# History

## [2026-08-06] predict | blunt-feedback
about: kindness-over-authenticity
result: hit

## [2026-08-07] predict | album-artwork
about: enter-reality
result: miss
"""


class TestParseProfile(unittest.TestCase):
    def test_parses_id_and_declared_status(self):
        principles = parse_profile(PROFILE)
        self.assertEqual(
            [(p.id, p.declared) for p in principles],
            [("kindness-over-authenticity", "core"), ("enter-reality", "provisional")],
        )

    def test_parses_boundary_and_confirmations(self):
        first = parse_profile(PROFILE)[0]
        self.assertTrue(first.boundary)
        self.assertEqual(first.confirmed_by, ["2026-08-06-blunt-feedback"])

    def test_omitted_fields_are_empty(self):
        second = parse_profile(PROFILE)[1]
        self.assertTrue(second.boundary)
        self.assertEqual(second.test, "")
        self.assertEqual(second.confirmed_by, [])

    def test_unknown_fields_are_ignored(self):
        profile = PROFILE + "\n**Named trade.** Shipped pretty once and regretted it.\n"
        self.assertEqual(len(parse_profile(profile)), 2)


class TestParseLog(unittest.TestCase):
    def test_composes_event_id_from_date_and_slug(self):
        entries = parse_log(LOG)
        self.assertIn("2026-08-06-blunt-feedback", entries)
        self.assertIn("2026-08-07-album-artwork", entries)

    def test_reads_action_and_result(self):
        entry = parse_log(LOG)["2026-08-06-blunt-feedback"]
        self.assertEqual(entry.action, "predict")
        self.assertEqual(entry.result, "hit")

    def test_reads_arbitrary_fields(self):
        entry = parse_log(LOG)["2026-08-06-blunt-feedback"]
        self.assertEqual(entry.fields["about"], "kindness-over-authenticity")


class TestPromotionRule(unittest.TestCase):
    def hit(self, ref):
        return {ref: Entry(id=ref, action="predict", fields={"result": "hit"})}

    def miss(self, ref):
        return {ref: Entry(id=ref, action="predict", fields={"result": "miss"})}

    def test_no_boundary_is_candidate(self):
        p = Principle(id="x", declared="core", statement="s", confirmed_by=["a"])
        self.assertEqual(computed_status(p, self.hit("a")), "candidate")

    def test_stated_with_a_boundary_is_provisional_immediately(self):
        p = Principle(id="x", declared="provisional", statement="s", boundary="stops here")
        self.assertEqual(computed_status(p, {}), "provisional")

    def test_a_correct_prediction_promotes_to_core(self):
        p = Principle(id="x", declared="core", boundary="stops here", confirmed_by=["a"])
        self.assertEqual(computed_status(p, self.hit("a")), "core")

    def test_a_missed_prediction_does_not_promote(self):
        p = Principle(id="x", declared="core", boundary="stops here", confirmed_by=["a"])
        self.assertEqual(computed_status(p, self.miss("a")), "provisional")

    def test_nothing_the_person_asserts_promotes_on_its_own(self):
        """The person is never the one who has to prove something."""
        p = Principle(id="x", declared="core", statement="s", boundary="b", test="q?")
        self.assertEqual(computed_status(p, {}), "provisional")

    def test_a_non_confirming_entry_does_not_promote(self):
        entries = {"a": Entry(id="a", action="choice", fields={"result": "hit"})}
        p = Principle(id="x", declared="core", boundary="stops here", confirmed_by=["a"])
        self.assertEqual(computed_status(p, entries), "provisional")

    def test_recognition_promotes_like_a_prediction(self):
        """Picking profile-written work out blind is a forced choice they could
        have got wrong, so it confirms as strongly as a correct prediction."""
        entries = {"a": Entry(id="a", action="recognise", fields={"result": "hit"})}
        p = Principle(id="x", declared="core", boundary="stops here", confirmed_by=["a"])
        self.assertEqual(computed_status(p, entries), "core")

    def test_a_failed_recognition_does_not_promote(self):
        entries = {"a": Entry(id="a", action="recognise", fields={"result": "miss"})}
        p = Principle(id="x", declared="core", boundary="stops here", confirmed_by=["a"])
        self.assertEqual(computed_status(p, entries), "provisional")

    def test_recognition_still_needs_a_boundary(self):
        """No boundary, no promotion, however the profile demonstrated itself."""
        entries = {"a": Entry(id="a", action="recognise", fields={"result": "hit"})}
        p = Principle(id="x", declared="core", statement="s", confirmed_by=["a"])
        self.assertEqual(computed_status(p, entries), "candidate")

    def test_unresolved_reference_does_not_promote(self):
        p = Principle(id="x", declared="core", boundary="stops here", confirmed_by=["gone"])
        self.assertEqual(computed_status(p, {}), "provisional")


class TestValidate(unittest.TestCase):
    def test_clean_profile_reports_nothing(self):
        self.assertEqual(validate(PROFILE, LOG), [])

    def test_overclaimed_status_is_reported(self):
        profile = PROFILE.replace("### enter-reality — provisional", "### enter-reality — core")
        errors = validate(profile, LOG)
        self.assertEqual(len(errors), 1)
        self.assertIn("enter-reality", errors[0])
        self.assertIn("declared core", errors[0])
        self.assertIn("history supports provisional", errors[0])

    def test_dangling_reference_is_reported(self):
        profile = PROFILE.replace("2026-08-06-blunt-feedback", "2026-08-06-nonexistent")
        errors = validate(profile, LOG)
        self.assertTrue(any("2026-08-06-nonexistent" in error for error in errors))

    def test_citing_a_missed_prediction_is_reported(self):
        profile = PROFILE.replace("2026-08-06-blunt-feedback", "2026-08-07-album-artwork")
        errors = validate(profile, LOG)
        self.assertTrue(any("did not hit" in error for error in errors))


class TestDemotion(unittest.TestCase):
    """Demotion is applied by removing the confirmation, so status recomputes.

    The validator's job is catching a demotion that was recorded and then not
    applied — the profile quietly keeping a promotion the person took back.
    """

    DEMOTE_LOG = LOG + """
## [2026-08-08] demote | kindness-over-authenticity
defended: yes
prior: Kindness outranks being unvarnished.
"""

    def test_applied_demotion_leaves_the_principle_provisional(self):
        profile = PROFILE.replace(
            "**Confirmed by.** [2026-08-06-blunt-feedback] — guessed how you'd read it, correctly.\n",
            "",
        ).replace("### kindness-over-authenticity — core", "### kindness-over-authenticity — provisional")
        self.assertEqual(validate(profile, self.DEMOTE_LOG), [])
        self.assertEqual(core_ids(profile, self.DEMOTE_LOG), set())

    def test_recorded_but_unapplied_demotion_is_reported(self):
        errors = validate(PROFILE, self.DEMOTE_LOG)
        self.assertTrue(
            any("demoted on 2026-08-08" in error and "still cites" in error for error in errors),
            errors,
        )

    def test_a_lapse_does_not_demote(self):
        """A contradiction the person does not defend leaves the principle alone."""
        log = LOG + """
## [2026-08-08] demote | kindness-over-authenticity
defended: no
"""
        self.assertEqual(validate(PROFILE, log), [])

    def test_a_principle_can_be_reconfirmed_after_demotion(self):
        log = self.DEMOTE_LOG + """
## [2026-08-09] predict | second-look
about: kindness-over-authenticity
result: hit
"""
        profile = PROFILE.replace("2026-08-06-blunt-feedback", "2026-08-09-second-look")
        self.assertEqual(validate(profile, log), [])
        self.assertIn("kindness-over-authenticity", core_ids(profile, log))


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
