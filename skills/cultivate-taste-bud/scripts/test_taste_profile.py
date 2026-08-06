"""Structural tests for the skill package.

These cover what a stranger's install depends on: valid frontmatter, and
references that actually resolve. Gate and parsing tests arrive with the
validator.
"""

import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(HERE, "..", "SKILL.md")
REFERENCES = os.path.join(HERE, "..", "references")
TEMPLATES = os.path.join(HERE, "..", "assets")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


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
