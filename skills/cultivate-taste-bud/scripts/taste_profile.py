"""Check a taste profile against its own history.

A principle firms up when the profile has correctly predicted one of the
person's judgments — not when the person has proved anything. Saying what you
value is honoured as given. The tool carries the burden of showing it
understood you, and a wrong guess is the tool's problem.

    python3 taste_profile.py <profile>/TASTE.md <profile>/log.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

HEADING = re.compile(r"^### (?P<id>[a-z0-9-]+) — (?P<status>core|provisional|candidate)\s*$")
FIELD = re.compile(r"^\*\*(?P<name>Statement|Boundary|Test|Confirmed by)\.\*\*\s*(?P<value>.*)$")
REF = re.compile(r"\[(?P<ref>[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+)\]")
LOG_HEAD = re.compile(r"^## \[(?P<date>\d{4}-\d{2}-\d{2})\] (?P<action>[a-z]+) \| (?P<slug>[a-z0-9-]+)\s*$")
LOG_KV = re.compile(r"^(?P<key>[a-z]+):\s*(?P<value>.+)$")


@dataclass
class Principle:
    id: str
    declared: str
    statement: str = ""
    boundary: str = ""
    test: str = ""
    confirmed_by: list[str] = field(default_factory=list)


@dataclass
class Entry:
    id: str
    action: str
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def result(self) -> str:
        return self.fields.get("result", "")


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
        elif name == "Confirmed by":
            current.confirmed_by = REF.findall(value)
    return principles


def parse_log(text: str) -> dict[str, Entry]:
    """Read the history, keyed by event id.

    An event's id is `<date>-<slug>`, composed here so the log itself stays
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
        pair = LOG_KV.match(line)
        if pair:
            current.fields.setdefault(pair.group("key"), pair.group("value").strip())
    return entries


def computed_status(principle: Principle, entries: dict[str, Entry]) -> str:
    """The status the history supports, ignoring what the profile declares.

    Nobody is asked to prove a value. A principle stated with a boundary is
    honoured as provisional immediately. It reaches core only once the profile
    has predicted one of the person's judgments correctly using it, which is
    the tool demonstrating it understood them rather than the reverse.
    """
    if not principle.boundary:
        return "candidate"
    for ref in principle.confirmed_by:
        entry = entries.get(ref)
        if entry and entry.action == "predict" and entry.result == "hit":
            return "core"
    return "provisional"


def validate(profile_text: str, log_text: str) -> list[str]:
    entries = parse_log(log_text)
    errors: list[str] = []
    for principle in parse_profile(profile_text):
        for ref in principle.confirmed_by:
            entry = entries.get(ref)
            if entry is None:
                errors.append(f"{principle.id}: confirmed-by reference {ref} resolves to no history entry")
            elif entry.action != "predict":
                errors.append(f"{principle.id}: {ref} is a {entry.action} entry, not a prediction")
            elif entry.result != "hit":
                errors.append(f"{principle.id}: {ref} is a prediction that did not hit")
        implied = computed_status(principle, entries)
        if implied != principle.declared:
            errors.append(f"{principle.id}: declared {principle.declared}, history supports {implied}")
    return errors


def predictable_ids(profile_text: str) -> set[str]:
    """Principles a prediction may draw on: anything with a stated boundary."""
    return {p.id for p in parse_profile(profile_text) if p.boundary}


def core_ids(profile_text: str, log_text: str) -> set[str]:
    """Ids of principles the history actually supports as core."""
    entries = parse_log(log_text)
    return {
        principle.id
        for principle in parse_profile(profile_text)
        if computed_status(principle, entries) == "core"
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
    print("profile consistent with its history")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv))
