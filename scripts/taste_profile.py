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
ANY_FIELD = re.compile(r"^\*\*(?P<name>[^*\n]+)\.\*\*\s*(?P<value>.*)$")
REF = re.compile(r"\[(?P<ref>[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+)\]")
LOG_HEAD = re.compile(r"^## \[(?P<date>\d{4}-\d{2}-\d{2})\] (?P<action>[a-z]+) \| (?P<slug>[a-z0-9-]+)\s*$")
LOG_KV = re.compile(r"^(?P<key>[a-z]+):\s*(?P<value>.+)$")
MARKDOWN_HEADING = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.*)$")

PRINCIPLE_SECTIONS = {"Core Principles", "Provisional Preferences"}
NON_PRINCIPLE_SECTIONS = {
    "Purpose",
    "Open Tensions",
    "Decision Test",
    "Evidence",
    "Revision Record",
    "Scope and Authority",
}
OPTIONAL_FIELDS = {"Named trade"}


#: Events that can confirm a principle. `predict` is the profile guessing a
#: judgment and being right. `recognise` is the profile producing work the
#: person picks out blind against a control — stronger, because it is a forced
#: choice they could have got wrong rather than a score they gave a guess.
CONFIRMING_ACTIONS = ("predict", "recognise")


@dataclass
class Principle:
    id: str
    declared: str
    statement: str = ""
    boundary: str = ""
    test: str = ""
    confirmed_by: list[str] = field(default_factory=list)
    seen_fields: set[str] = field(default_factory=set, repr=False)


@dataclass
class Entry:
    id: str
    action: str
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def result(self) -> str:
        return self.fields.get("result", "")


def _parse_profile(text: str) -> tuple[list[Principle], list[str]]:
    """Read principles out of a TASTE.md.

    A field that does not exist is omitted from the document, never narrated
    — `**Test.** Not yet written` would parse as a test question whose text
    is "Not yet written".
    """
    principles: list[Principle] = []
    errors: list[str] = []
    current: Principle | None = None
    section: str | None = None
    saw_principle_section = False
    principle_ids: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.startswith("## ") and not line.startswith("### "):
            current = None
            section = line[3:].strip()
            if section in PRINCIPLE_SECTIONS:
                if principles and not saw_principle_section:
                    errors.append(
                        f"line {line_number}: unsupported mixed standalone and sectioned principle schema"
                    )
                saw_principle_section = True
            elif section not in NON_PRINCIPLE_SECTIONS:
                errors.append(f"line {line_number}: unsupported profile section {section!r}")
            continue

        heading = HEADING.match(line)
        if heading:
            if section in NON_PRINCIPLE_SECTIONS:
                current = None
                continue
            in_sectioned_region = section in PRINCIPLE_SECTIONS
            if saw_principle_section and not in_sectioned_region:
                errors.append(
                    f"line {line_number}: principle {heading.group('id')} is outside a principle section"
                )
                current = None
                continue
            current = Principle(id=heading.group("id"), declared=heading.group("status"))
            if current.id in principle_ids:
                errors.append(f"line {line_number}: duplicate principle id {current.id!r}")
            principle_ids.add(current.id)
            principles.append(current)
            continue

        markdown_heading = MARKDOWN_HEADING.match(line)
        if markdown_heading:
            context = current.id if current else (section or "standalone principle region")
            if len(markdown_heading.group("marks")) >= 3 and section not in NON_PRINCIPLE_SECTIONS:
                errors.append(
                    f"line {line_number}: unsupported principle heading {line!r} in {context}"
                )
            current = None
            continue

        if current is None:
            continue
        found = FIELD.match(line)
        if not found:
            unsupported = ANY_FIELD.match(line)
            if unsupported and unsupported.group("name") not in OPTIONAL_FIELDS:
                errors.append(
                    f"line {line_number}: {current.id}: unsupported principle field "
                    f"{unsupported.group('name')!r}"
                )
            continue
        name, value = found.group("name"), found.group("value").strip()
        if name in current.seen_fields:
            errors.append(f"line {line_number}: {current.id}: duplicate principle field {name!r}")
        current.seen_fields.add(name)
        if not value:
            errors.append(
                f"line {line_number}: {current.id}: empty principle field {name!r}; omit optional fields"
            )
        if name == "Statement":
            current.statement = value
        elif name == "Boundary":
            current.boundary = value
        elif name == "Test":
            current.test = value
        elif name == "Confirmed by":
            current.confirmed_by = REF.findall(value)
            if value and not current.confirmed_by:
                errors.append(
                    f"line {line_number}: {current.id}: Confirmed by has no supported history reference"
                )
    if not text.strip():
        errors.append("profile not ready: file is empty")
    elif not principles:
        if saw_principle_section:
            errors.append("profile not ready: principle sections contain no recognized principles")
        elif not errors:
            errors.append("unsupported profile schema: no recognized principles")
    return principles, errors


def parse_profile(text: str) -> list[Principle]:
    """Read recognized principles; use :func:`validate` for schema errors."""
    return _parse_profile(text)[0]


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
    has demonstrated it understood them — by predicting a judgment correctly,
    or by producing work they picked out blind against a control.
    """
    if not principle.boundary:
        return "candidate"
    for ref in principle.confirmed_by:
        entry = entries.get(ref)
        if (
            entry
            and entry.action in CONFIRMING_ACTIONS
            and entry.result == "hit"
            and entry.fields.get("about") == principle.id
        ):
            return "core"
    return "provisional"


def _unapplied_demotions(principle: Principle, entries: dict[str, Entry]) -> list[str]:
    """Demotions recorded in the history but never applied to the profile.

    Applying a demotion means removing the confirmation it invalidates, which
    lets status recompute on its own. A demotion logged while the confirmation
    still stands is the profile quietly keeping a promotion the person took
    back.
    """
    errors: list[str] = []
    for entry in entries.values():
        if entry.action != "demote" or entry.fields.get("defended") != "yes":
            continue
        if not entry.id.endswith(f"-{principle.id}"):
            continue
        demoted_on = entry.id[:10]
        for ref in principle.confirmed_by:
            if ref[:10] <= demoted_on:
                errors.append(
                    f"{principle.id}: demoted on {demoted_on} but still cites {ref} as confirmation"
                )
    return errors


def validate(profile_text: str, log_text: str) -> list[str]:
    entries = parse_log(log_text)
    principles, errors = _parse_profile(profile_text)
    for principle in principles:
        if not principle.statement:
            errors.append(f"{principle.id}: missing or empty Statement field")
        errors.extend(_unapplied_demotions(principle, entries))
        for ref in principle.confirmed_by:
            entry = entries.get(ref)
            if entry is None:
                errors.append(f"{principle.id}: confirmed-by reference {ref} resolves to no history entry")
            elif entry.action not in CONFIRMING_ACTIONS:
                errors.append(
                    f"{principle.id}: {ref} is a {entry.action} entry, which cannot confirm anything"
                )
            elif entry.result != "hit":
                errors.append(f"{principle.id}: {ref} did not hit")
            elif not entry.fields.get("about"):
                errors.append(
                    f"{principle.id}: {ref} has no about field; expected exact principle id {principle.id}"
                )
            elif entry.fields["about"] != principle.id:
                errors.append(
                    f"{principle.id}: {ref} is about {entry.fields['about']!r}, "
                    f"not exact principle id {principle.id}"
                )
        implied = computed_status(principle, entries)
        if implied != principle.declared:
            errors.append(f"{principle.id}: declared {principle.declared}, history supports {implied}")
    return errors


def core_ids(profile_text: str, log_text: str) -> set[str]:
    """Ids of principles the history actually supports as core."""
    entries = parse_log(log_text)
    return {
        principle.id
        for principle in parse_profile(profile_text)
        if computed_status(principle, entries) == "core"
    }


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
