"""Check a taste profile against the evidence recorded in its history.

The promotion gate is deterministic, so it lives in code rather than in
prose an agent can drift from. Run it after a session:

    python3 taste_profile.py <profile>/TASTE.md <profile>/log.md

It reports principles claiming a status their evidence does not support, and
references that resolve to nothing. It has no opinion about anyone's taste.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

HEADING = re.compile(r"^### (?P<id>[a-z0-9-]+) — (?P<status>core|provisional|candidate)\s*$")
FIELD = re.compile(r"^\*\*(?P<name>Statement|Boundary|Test|Paid by)\.\*\*\s*(?P<value>.*)$")
REF = re.compile(r"\[(?P<ref>[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+)\]")
LOG_HEAD = re.compile(r"^## \[(?P<date>\d{4}-\d{2}-\d{2})\] (?P<action>[a-z]+) \| (?P<slug>[a-z0-9-]+)\s*$")
TIER = re.compile(r"tier:\s*(?P<tier>\d)")

#: Tiers that can confirm a principle. Tier 4 — stated admiration, stated
#: belief — may propose one, never confirm it.
CONFIRMING_TIERS = (1, 2, 3)


@dataclass
class Principle:
    id: str
    declared: str
    statement: str = ""
    boundary: str = ""
    test: str = ""
    paid_by: list[str] = field(default_factory=list)


@dataclass
class Entry:
    id: str
    action: str
    tier: int | None = None


def parse_profile(text: str) -> list[Principle]:
    """Read principles out of a TASTE.md.

    A field that does not exist is omitted from the document, never narrated
    — `**Test.** Not yet written` would parse as a test question whose text
    is "Not yet written".
    """
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


def parse_log(text: str) -> dict[str, Entry]:
    """Read the history, keyed by decision id.

    A decision's id is `<date>-<slug>`, composed here so the log itself stays
    readable without repeating the date on every line.
    """
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


def computed_status(principle: Principle, decisions: dict[str, Entry]) -> str:
    """The status the evidence supports, ignoring what the profile declares.

    Tier is read from the decision, never stored on the principle: a
    denormalised copy drifts away from what it was copied from.
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


def validate(profile_text: str, log_text: str) -> list[str]:
    decisions = parse_log(log_text)
    errors: list[str] = []
    for principle in parse_profile(profile_text):
        for ref in principle.paid_by:
            if ref not in decisions:
                errors.append(f"{principle.id}: paid-by reference {ref} resolves to no history entry")
        implied = computed_status(principle, decisions)
        if implied != principle.declared:
            errors.append(f"{principle.id}: declared {principle.declared}, evidence supports {implied}")
    return errors


def predictable_ids(profile_text: str) -> set[str]:
    """Principles a prediction may draw on.

    A stated boundary is enough. Prediction deliberately does not wait for a
    principle to reach core, because core requires a test question the person
    wrote, and gating the self-correcting half of the method behind the one
    thing people decline to do means it never runs at all.
    """
    return {p.id for p in parse_profile(profile_text) if p.boundary}


def core_ids(profile_text: str, log_text: str) -> set[str]:
    """Ids of principles the evidence actually supports as core."""
    decisions = parse_log(log_text)
    return {
        principle.id
        for principle in parse_profile(profile_text)
        if computed_status(principle, decisions) == "core"
    }


def overlapping_cores(a_profile: str, a_log: str, b_profile: str, b_log: str) -> set[str]:
    """Core principles two profiles share. Opposed people should share none."""
    return core_ids(a_profile, a_log) & core_ids(b_profile, b_log)


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
