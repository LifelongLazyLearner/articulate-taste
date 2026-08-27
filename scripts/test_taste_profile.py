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
    parse_log,
    parse_profile,
    validate,
)

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(HERE, "..", "SKILL.md")
README = os.path.join(HERE, "..", "README.md")
README_ZH = os.path.join(HERE, "..", "README.zh-CN.md")
REFERENCES = os.path.join(HERE, "..", "references")
TEMPLATES = os.path.join(HERE, "..", "assets")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


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

    def test_standalone_principles_are_supported(self):
        profile = """# Small profile

### directness — provisional
**Statement.** Lead with the answer.
**Boundary.** Not when context changes the answer.
"""
        self.assertEqual(validate(profile, "# History\n"), [])

    def test_evidence_headings_after_standalone_principles_are_not_principles(self):
        profile = """### directness — provisional
**Statement.** Lead with the answer.
**Boundary.** Not when context changes the answer.

## Evidence
### Session one
**Boundary.** This belongs to evidence, not directness.

## Revision Record
### Earlier wording
"""
        principles = parse_profile(profile)
        self.assertEqual([p.id for p in principles], ["directness"])
        self.assertEqual(principles[0].boundary, "Not when context changes the answer.")
        self.assertEqual(validate(profile, "# History\n"), [])

    def test_schema_shaped_heading_in_sectioned_evidence_is_not_a_principle(self):
        profile = PROFILE + """
## Evidence
### session-note — core
**Statement.** Ordinary evidence prose.
"""
        self.assertEqual([p.id for p in parse_profile(profile)], ["kindness-over-authenticity", "enter-reality"])
        self.assertEqual(validate(profile, LOG), [])


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
        return {ref: Entry(id=ref, action="predict", fields={"result": "hit", "about": "x"})}

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
        entries = {"a": Entry(id="a", action="recognise", fields={"result": "hit", "about": "x"})}
        p = Principle(id="x", declared="core", boundary="stops here", confirmed_by=["a"])
        self.assertEqual(computed_status(p, entries), "core")

    def test_a_failed_recognition_does_not_promote(self):
        entries = {"a": Entry(id="a", action="recognise", fields={"result": "miss", "about": "x"})}
        p = Principle(id="x", declared="core", boundary="stops here", confirmed_by=["a"])
        self.assertEqual(computed_status(p, entries), "provisional")

    def test_recognition_still_needs_a_boundary(self):
        """No boundary, no promotion, however the profile demonstrated itself."""
        entries = {"a": Entry(id="a", action="recognise", fields={"result": "hit", "about": "x"})}
        p = Principle(id="x", declared="core", statement="s", confirmed_by=["a"])
        self.assertEqual(computed_status(p, entries), "candidate")

    def test_unresolved_reference_does_not_promote(self):
        p = Principle(id="x", declared="core", boundary="stops here", confirmed_by=["gone"])
        self.assertEqual(computed_status(p, {}), "provisional")

    def test_hit_without_attribution_does_not_promote(self):
        entries = {"a": Entry(id="a", action="predict", fields={"result": "hit"})}
        p = Principle(id="x", declared="core", boundary="stops here", confirmed_by=["a"])
        self.assertEqual(computed_status(p, entries), "provisional")

    def test_hit_about_another_principle_does_not_promote(self):
        entries = {"a": Entry(id="a", action="predict", fields={"result": "hit", "about": "y"})}
        p = Principle(id="x", declared="core", boundary="stops here", confirmed_by=["a"])
        self.assertEqual(computed_status(p, entries), "provisional")

    def test_substring_attribution_does_not_promote(self):
        entries = {"a": Entry(id="a", action="predict", fields={"result": "hit", "about": "x-extra"})}
        p = Principle(id="x", declared="core", boundary="stops here", confirmed_by=["a"])
        self.assertEqual(computed_status(p, entries), "provisional")


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

    def test_empty_profile_is_not_ready(self):
        self.assertTrue(any("not ready" in error for error in validate("", LOG)))

    def test_empty_template_is_not_ready(self):
        template = read(os.path.join(TEMPLATES, "TASTE.template.md"))
        self.assertTrue(any("not ready" in error for error in validate(template, LOG)))

    def test_unsupported_profile_schema_is_reported(self):
        errors = validate("# Taste\n\nPrinciple: Be direct.\n", LOG)
        self.assertTrue(any("unsupported profile schema" in error for error in errors), errors)

    def test_unsupported_heading_in_principle_region_has_context(self):
        profile = """## Core Principles
### directness - core
**Statement.** Be direct.
**Boundary.** Not when unsafe.
"""
        errors = validate(profile, LOG)
        self.assertTrue(any("unsupported principle heading" in error and "Core Principles" in error for error in errors), errors)

    def test_unsupported_standalone_heading_is_reported(self):
        profile = """### directness - candidate
**Statement.** Be direct.
"""
        errors = validate(profile, LOG)
        self.assertTrue(any("unsupported principle heading" in error for error in errors), errors)

    def test_partially_recognized_profile_rejects_unknown_section(self):
        profile = PROFILE + "\n## Secret Principles\n### novelty — candidate\n**Statement.** Surprise me.\n"
        errors = validate(profile, LOG)
        self.assertTrue(any("unsupported profile section" in error for error in errors), errors)

    def test_principle_without_statement_is_rejected(self):
        profile = """### directness — provisional
**Boundary.** Not when context changes the answer.
"""
        errors = validate(profile, "# History\n")
        self.assertTrue(any("missing or empty Statement" in error for error in errors), errors)

    def test_empty_field_is_rejected(self):
        profile = """### directness — candidate
**Statement.**
"""
        errors = validate(profile, "# History\n")
        self.assertTrue(any("empty principle field" in error for error in errors), errors)

    def test_malformed_heading_stops_fields_leaking_into_previous_principle(self):
        profile = """### first — provisional
**Statement.** First.
**Boundary.** First boundary.
### second - candidate
**Statement.** Second.
**Boundary.** Leaked boundary.
"""
        principles = parse_profile(profile)
        self.assertEqual(len(principles), 1)
        self.assertEqual(principles[0].statement, "First.")
        self.assertEqual(principles[0].boundary, "First boundary.")
        self.assertTrue(any("unsupported principle heading" in error for error in validate(profile, LOG)))

    def test_valid_heading_also_stops_fields_leaking(self):
        profile = """### first — candidate
**Statement.** First.
### second — provisional
**Statement.** Second.
**Boundary.** Second boundary.
"""
        first, second = parse_profile(profile)
        self.assertEqual(first.boundary, "")
        self.assertEqual(second.boundary, "Second boundary.")

    def test_deeper_malformed_heading_stops_field_leakage(self):
        profile = """### first — candidate
**Statement.** First.
#### Evidence note
**Boundary.** Must not leak.
"""
        principle = parse_profile(profile)[0]
        self.assertEqual(principle.boundary, "")
        self.assertTrue(any("unsupported principle heading" in error for error in validate(profile, LOG)))

    def test_mixed_standalone_and_sectioned_schema_is_rejected(self):
        profile = """### first — candidate
**Statement.** First.
## Core Principles
### second — candidate
**Statement.** Second.
"""
        self.assertTrue(any("unsupported mixed" in error for error in validate(profile, LOG)))

    def test_duplicate_principle_id_is_rejected(self):
        profile = """### directness — candidate
**Statement.** First.
### directness — candidate
**Statement.** Second.
"""
        self.assertTrue(any("duplicate principle id" in error for error in validate(profile, LOG)))

    def test_unsupported_field_is_reported_with_principle_context(self):
        profile = PROFILE.replace("**Boundary.** Does not require silence", "**Boundry.** Does not require silence")
        errors = validate(profile, LOG)
        self.assertTrue(any("kindness-over-authenticity" in error and "unsupported principle field" in error for error in errors), errors)

    def test_missing_confirmation_attribution_is_reported_and_not_core(self):
        log = LOG.replace("about: kindness-over-authenticity\n", "")
        errors = validate(PROFILE, log)
        self.assertTrue(any("has no about field" in error for error in errors), errors)
        self.assertNotIn("kindness-over-authenticity", core_ids(PROFILE, log))

    def test_mismatched_confirmation_attribution_is_reported_and_not_core(self):
        log = LOG.replace("about: kindness-over-authenticity", "about: enter-reality")
        errors = validate(PROFILE, log)
        self.assertTrue(any("not exact principle id" in error for error in errors), errors)
        self.assertNotIn("kindness-over-authenticity", core_ids(PROFILE, log))


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


def plain_scalar_problems(value: str) -> list[str]:
    """YAML breakages an unquoted frontmatter value can hide.

    A colon followed by a space makes YAML read the rest of the line as a
    nested mapping, the frontmatter fails to parse, and the loader skips the
    skill entirely — reporting the line rather than the colon. Every other
    check in this file passes while the skill will not install at all, which
    is how one shipped.
    """
    problems = []
    if ": " in value:
        problems.append("colon followed by a space")
    if value[:1] in "-?:,[]{}#&*!|>'\"%@`":
        problems.append(f"leading {value[:1]!r}")
    return problems


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
        self.assertEqual(name, "articulate-taste")
        self.assertLessEqual(len(name), 64)
        self.assertRegex(name, r"^[a-z0-9-]+$")

    def test_name_avoids_reserved_words(self):
        name = self.frontmatter()["name"]
        self.assertNotIn("claude", name)
        self.assertNotIn("anthropic", name)

    def test_frontmatter_stays_loadable(self):
        for key, value in self.frontmatter().items():
            self.assertEqual(
                plain_scalar_problems(value), [], f"{key}: {value[:70]}"
            )

    def test_description_states_what_and_when_within_limit(self):
        description = self.frontmatter()["description"]
        self.assertLessEqual(len(description), 1024)
        self.assertIn("Use when", description)


class TestReferences(unittest.TestCase):
    def test_every_reference_linked_from_skill_exists(self):
        linked = set(re.findall(r"\(references/([a-z-]+\.md)\)", read(SKILL)))
        self.assertEqual(
            linked, {"elicitation.md", "emitting.md", "format.md", "promotion.md"}
        )
        for name in linked:
            self.assertTrue(os.path.exists(os.path.join(REFERENCES, name)), name)


class TestBehaviorDocumentation(unittest.TestCase):
    def test_comparison_outcomes_are_distinct_across_english_docs(self):
        sources = [
            read(SKILL),
            read(os.path.join(REFERENCES, "elicitation.md")),
            read(os.path.join(REFERENCES, "format.md")),
            read(README),
        ]
        for body in sources:
            lowered = body.lower()
            for outcome in ("1", "2", "neither", "same", "skip"):
                self.assertIn(outcome, lowered)
            self.assertIn("reason", lowered)

    def test_bilingual_readmes_describe_the_same_five_outcomes(self):
        english = read(README).lower()
        chinese = read(README_ZH)
        for outcome in ("neither", "same", "skip"):
            self.assertIn(outcome, english)
        for outcome in ("两版都不要", "一样", "跳过"):
            self.assertIn(outcome, chinese)
        self.assertIn("does not claim validation in a\nnew context", english)
        self.assertIn("也不算在新场景里验证过", chinese)

    def test_confirmation_attribution_is_documented_as_one_exact_slug(self):
        for name in ("format.md", "promotion.md"):
            body = read(os.path.join(REFERENCES, name)).lower()
            self.assertIn("exactly one", body)
            self.assertIn("stable", body)
            self.assertIn("slug", body)
            self.assertIn("no multi-value", body)

    def test_canonical_pair_and_relocation_guards_are_documented(self):
        skill = read(SKILL).lower()
        emitting = read(os.path.join(REFERENCES, "emitting.md")).lower()
        for term in ("canonical profile", "canonical append-only", "current directory", "one decisive question"):
            self.assertIn(term, skill)
        for term in ("consumer", "replacement", "recovery", "consent"):
            self.assertIn(term, emitting)
        self.assertNotIn("move the profile in", emitting)

    def test_emitted_skill_stops_on_incompatible_validation_without_editing(self):
        body = read(os.path.join(TEMPLATES, "emitted-skill", "SKILL.md")).lower()
        self.assertIn("unsupported schema", body)
        self.assertRegex(body, r"stop\s+without editing")
        self.assertIn("separately authorised", body)

    def test_wording_approval_preserves_evidence_and_status(self):
        for path in (SKILL, os.path.join(REFERENCES, "elicitation.md"), os.path.join(REFERENCES, "promotion.md")):
            body = read(path).lower()
            self.assertRegex(body, r"stable(?: principle)? id")
            self.assertIn("boundary", body)
            self.assertIn("failed prediction", body)
            self.assertIn("status", body)


class TestEmittedSkillTemplate(unittest.TestCase):
    """The template a person's own skill is built from.

    Its frontmatter has to satisfy the same rules as any other skill once the
    placeholders are filled, or every emitted skill is born invalid.
    """

    PATH = os.path.join(TEMPLATES, "emitted-skill", "SKILL.md")

    def filled(self):
        return (
            read(self.PATH)
            .replace("{{SKILL_NAME}}", "someones-taste")
            .replace("{{PROFILE_SUMMARY}}", "how they judge writing and code")
        )

    def frontmatter(self):
        _, block, _ = self.filled().split("---", 2)
        fields = {}
        for line in block.strip().splitlines():
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
        return fields

    def test_filled_name_obeys_the_spec(self):
        name = self.frontmatter()["name"]
        self.assertRegex(name, r"^[a-z0-9-]+$")
        self.assertLessEqual(len(name), 64)
        self.assertNotIn("claude", name)
        self.assertNotIn("anthropic", name)

    def test_filled_description_states_what_and_when_within_limit(self):
        description = self.frontmatter()["description"]
        self.assertLessEqual(len(description), 1024)
        self.assertIn("Use when", description)

    def test_frontmatter_stays_loadable(self):
        for key, value in self.frontmatter().items():
            self.assertEqual(
                plain_scalar_problems(value), [], f"{key}: {value[:70]}"
            )

    def test_no_placeholder_survives_substitution(self):
        self.assertNotIn("{{", self.filled())

    def test_it_requires_narrating_which_principle_drove_which_choice(self):
        """Silent application produced work its owner could not recognise."""
        body = read(self.PATH).lower()
        self.assertIn("never apply a principle silently", body)
        self.assertIn("which principle", body)

    def test_it_checks_the_opt_in_before_reading_the_profile(self):
        body = read(self.PATH)
        self.assertIn(".taste-opt-in.md", body)
        opt_in = body.index(".taste-opt-in.md")
        loads = body.index("Status means something")
        self.assertLess(opt_in, loads, "opt-in check must come first")


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
