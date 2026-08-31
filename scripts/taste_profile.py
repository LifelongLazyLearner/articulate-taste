"""Check a taste profile against its own history.

A principle firms up when the profile has correctly predicted one of the
person's judgments — not when the person has proved anything. Saying what you
value is honoured as given. The tool carries the burden of showing it
understood you, and a wrong guess is the tool's problem.

    python3 taste_profile.py <profile>/TASTE.md <profile>/log.md
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

HEADING = re.compile(r"^### (?P<id>[a-z0-9-]+) — (?P<status>core|provisional|candidate)\s*$")
FIELD = re.compile(r"^\*\*(?P<name>Statement|Boundary|Test|Confirmed by)\.\*\*\s*(?P<value>.*)$")
ANY_FIELD = re.compile(r"^\*\*(?P<name>[^*\n]+)\.\*\*\s*(?P<value>.*)$")
SUPPORTED_CONTRACT_SCHEMA = "personal-taste-contract/v1"
YAML_BLOCK = re.compile(r"```yaml\s*\n(?P<body>.*?)\n```", re.DOTALL)
METADATA_LINE = re.compile(r"^(?P<key>[a-z_]+):\s*(?P<value>.+?)\s*$")
CONTRACT_HEADING = re.compile(r"^### (?P<id>[a-z0-9-]+)\s*$")
CONTRACT_FIELD = re.compile(
    r"^- \*\*(?P<name>Directive|Boundary|Operational test|Priority|Evidence|Open tension|Applies to|Confidence):\*\*\s*(?P<value>.*)$"
)
CONTRACT_ANY_FIELD = re.compile(r"^- \*\*(?P<name>[^*\n]+):\*\*\s*(?P<value>.*)$")
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

CONTRACT_PRINCIPLE_SECTIONS = {
    "Universal Stable Rules": ("stable", "universal"),
    "Universal Provisional Rules": ("provisional", "universal"),
    "Scoped Taste": ("", "scoped"),
}
CONTRACT_NON_PRINCIPLE_SECTIONS = {
    "Scope and Authority",
    "Precedence and Interpretation",
    "Open Tensions",
    "Decision Test",
    "Evidence",
    "Revision Record",
    "Application Semantics",
    "Maintenance Contract",
}
CONTRACT_UNIVERSAL_FIELDS = {
    "Directive",
    "Boundary",
    "Operational test",
    "Priority",
    "Evidence",
    "Open tension",
}
CONTRACT_SCOPED_FIELDS = CONTRACT_UNIVERSAL_FIELDS | {"Applies to", "Confidence"}


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
    scope: str = "universal"
    applies_to: str = ""
    evidence: str = ""
    schema: str = "legacy"
    seen_fields: set[str] = field(default_factory=set, repr=False)


@dataclass
class Entry:
    id: str
    action: str
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def result(self) -> str:
        return self.fields.get("result", "")


def _parse_legacy_profile(text: str) -> tuple[list[Principle], list[str]]:
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


def _parse_contract_profile(text: str) -> tuple[list[Principle], list[str]]:
    """Read a ``personal-taste-contract/v1`` profile.

    This schema keeps universal confidence in section placement and gives
    scoped rules an explicit ``Confidence`` field. The existing stable section
    is an authoritative migration baseline; new scoped promotions still have
    to cite exact confirming history.
    """
    principles: list[Principle] = []
    errors: list[str] = []
    current: Principle | None = None
    section: str | None = None
    saw_principle_section = False
    seen_sections: set[str] = set()
    principle_ids: set[str] = set()

    for line_number, line in enumerate(text.splitlines(), 1):
        if line.startswith("## ") and not line.startswith("### "):
            current = None
            section = line[3:].strip()
            if section in CONTRACT_PRINCIPLE_SECTIONS:
                saw_principle_section = True
                seen_sections.add(section)
            elif section not in CONTRACT_NON_PRINCIPLE_SECTIONS:
                errors.append(f"line {line_number}: unsupported profile section {section!r}")
            continue

        heading = CONTRACT_HEADING.match(line)
        if heading:
            if section not in CONTRACT_PRINCIPLE_SECTIONS:
                if section not in CONTRACT_NON_PRINCIPLE_SECTIONS:
                    errors.append(
                        f"line {line_number}: principle {heading.group('id')} is outside a principle section"
                    )
                current = None
                continue
            declared, scope = CONTRACT_PRINCIPLE_SECTIONS[section]
            current = Principle(
                id=heading.group("id"),
                declared=declared,
                scope=scope,
                schema="personal-taste-contract/v1",
            )
            if current.id in principle_ids:
                errors.append(f"line {line_number}: duplicate principle id {current.id!r}")
            principle_ids.add(current.id)
            principles.append(current)
            continue

        markdown_heading = MARKDOWN_HEADING.match(line)
        if markdown_heading:
            if len(markdown_heading.group("marks")) >= 3 and section in CONTRACT_PRINCIPLE_SECTIONS:
                context = current.id if current else section
                errors.append(
                    f"line {line_number}: unsupported principle heading {line!r} in {context}"
                )
            current = None
            continue

        if current is None:
            continue
        found = CONTRACT_FIELD.match(line)
        if not found:
            unsupported = CONTRACT_ANY_FIELD.match(line)
            if unsupported:
                errors.append(
                    f"line {line_number}: {current.id}: unsupported principle field "
                    f"{unsupported.group('name')!r}"
                )
            continue

        name, value = found.group("name"), found.group("value").strip()
        allowed = CONTRACT_SCOPED_FIELDS if current.scope == "scoped" else CONTRACT_UNIVERSAL_FIELDS
        if name not in allowed:
            errors.append(f"line {line_number}: {current.id}: field {name!r} is invalid for {current.scope} taste")
            continue
        if name in current.seen_fields:
            errors.append(f"line {line_number}: {current.id}: duplicate principle field {name!r}")
        current.seen_fields.add(name)
        if not value:
            errors.append(
                f"line {line_number}: {current.id}: empty principle field {name!r}; omit optional fields"
            )
        if name == "Directive":
            current.statement = value
        elif name == "Boundary":
            current.boundary = value
        elif name == "Operational test":
            current.test = value
        elif name == "Applies to":
            current.applies_to = value
        elif name == "Confidence":
            current.declared = value
        elif name == "Evidence":
            current.evidence = value
            current.confirmed_by = REF.findall(value)

    if not text.strip():
        errors.append("profile not ready: file is empty")
    elif not principles:
        if saw_principle_section:
            errors.append("profile not ready: principle sections contain no recognized principles")
        elif not errors:
            errors.append("unsupported profile schema: no recognized principles")
    missing_sections = set(CONTRACT_PRINCIPLE_SECTIONS) - seen_sections
    for missing in sorted(missing_sections):
        errors.append(f"personal-taste-contract/v1 requires section {missing!r}")

    metadata, metadata_errors = _profile_metadata(text)
    errors.extend(metadata_errors)
    if "stable_baseline" not in metadata:
        errors.append("personal-taste-contract/v1 requires stable_baseline metadata")
    else:
        baseline_ids = _contract_baseline_ids(text)
        known = {principle.id for principle in principles}
        for unknown in sorted(baseline_ids - known):
            errors.append(f"stable_baseline names unknown principle {unknown!r}")
        for principle in principles:
            if principle.id in baseline_ids and principle.scope != "universal":
                errors.append(
                    f"{principle.id}: stable_baseline may contain only universal rules"
                )
    return principles, errors


def _parse_profile(text: str) -> tuple[list[Principle], list[str]]:
    metadata, metadata_errors = _profile_metadata(text)
    if metadata_errors:
        return [], metadata_errors
    schema = metadata.get("schema")
    if schema:
        if schema != SUPPORTED_CONTRACT_SCHEMA:
            return [], [f"unsupported profile schema {schema!r}"]
        return _parse_contract_profile(text)
    return _parse_legacy_profile(text)


def _profile_metadata(text: str) -> tuple[dict[str, str], list[str]]:
    """Read the single fenced YAML metadata block before the first section."""
    preamble = text.split("\n## ", 1)[0]
    blocks = YAML_BLOCK.findall(preamble)
    if not blocks:
        return {}, []
    if len(blocks) != 1:
        return {}, ["profile preamble must contain at most one YAML metadata block"]
    metadata: dict[str, str] = {}
    errors: list[str] = []
    for line in blocks[0].splitlines():
        found = METADATA_LINE.match(line)
        if not found:
            continue
        key, value = found.group("key"), found.group("value")
        if key in metadata:
            errors.append(f"duplicate profile metadata key {key!r}")
        metadata[key] = value
    return metadata, errors


def _contract_baseline_ids(text: str) -> set[str]:
    metadata, _ = _profile_metadata(text)
    raw = metadata.get("stable_baseline", "")
    if not raw or raw == "none":
        return set()
    return {item.strip() for item in raw.split(",") if item.strip()}


def _contract_baseline_payload(text: str) -> str:
    metadata, _ = _profile_metadata(text)
    raw = metadata.get("stable_baseline", "")
    if not raw or raw == "none":
        return ""
    return ",".join(item.strip() for item in raw.split(",") if item.strip())


def _baseline_digest(text: str) -> str:
    return hashlib.sha256(_contract_baseline_payload(text).encode()).hexdigest()


def _field_mentions_slug(value: str, principle_id: str) -> bool:
    return bool(re.search(rf"(?<![a-z0-9-]){re.escape(principle_id)}(?![a-z0-9-])", value))


def _entry_supports_principle(entry: Entry, principle_id: str) -> bool:
    if entry.fields.get("about") == principle_id:
        return True
    if entry.action == "choice":
        return any(
            _field_mentions_slug(entry.fields.get(field, ""), principle_id)
            for field in ("won", "lost")
        )
    return False


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


def _duplicate_log_ids(text: str) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for line in text.splitlines():
        head = LOG_HEAD.match(line)
        if not head:
            continue
        entry_id = f"{head.group('date')}-{head.group('slug')}"
        if entry_id in seen:
            duplicates.add(entry_id)
        seen.add(entry_id)
    return duplicates


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


def _unapplied_demotions(
    principle: Principle, entries: dict[str, Entry], after_index: int = -1
) -> list[str]:
    """Demotions recorded in the history but never applied to the profile.

    Applying a demotion means removing the confirmation it invalidates, which
    lets status recompute on its own. A demotion logged while the confirmation
    still stands is the profile quietly keeping a promotion the person took
    back.
    """
    errors: list[str] = []
    positions = {entry_id: index for index, entry_id in enumerate(entries)}
    for index, entry in enumerate(entries.values()):
        if entry.action != "demote" or entry.fields.get("defended") != "yes":
            continue
        if not entry.id.endswith(f"-{principle.id}"):
            continue
        if index <= after_index:
            continue
        demoted_on = entry.id[:10]
        for ref in principle.confirmed_by:
            if ref in positions and positions[ref] <= positions[entry.id]:
                errors.append(
                    f"{principle.id}: demoted on {demoted_on} but still cites {ref} as confirmation"
                )
    return errors


def _defended_demotions(
    principle: Principle, entries: dict[str, Entry], after_index: int = -1
) -> list[tuple[int, Entry]]:
    return [
        (index, entry)
        for index, entry in enumerate(entries.values())
        if entry.action == "demote"
        and entry.fields.get("defended") == "yes"
        and entry.id.endswith(f"-{principle.id}")
        and index > after_index
    ]


def validate(profile_text: str, log_text: str) -> list[str]:
    entries = parse_log(log_text)
    principles, errors = _parse_profile(profile_text)
    for duplicate in sorted(_duplicate_log_ids(log_text)):
        errors.append(f"duplicate history entry id {duplicate!r}")
    metadata, _ = _profile_metadata(profile_text)
    contract = metadata.get("schema") == SUPPORTED_CONTRACT_SCHEMA
    baseline_ids = _contract_baseline_ids(profile_text) if contract else set()
    migration_index: int | None = None
    if contract and baseline_ids:
        migrations = [
            (index, entry)
            for index, entry in enumerate(entries.values())
            if entry.action == "migrate"
            and entry.fields.get("schema") == SUPPORTED_CONTRACT_SCHEMA
        ]
        if len(migrations) != 1:
            errors.append(
                "non-empty stable_baseline requires exactly one append-only migrate event"
            )
        elif migrations[0][1].fields.get("baseline") != _baseline_digest(profile_text):
            errors.append("stable_baseline does not match its append-only migrate event")
        else:
            migration_index = migrations[0][0]
    entry_positions = {entry_id: index for index, entry_id in enumerate(entries)}
    for principle in principles:
        statement_name = "Directive" if contract else "Statement"
        if not principle.statement:
            errors.append(f"{principle.id}: missing or empty {statement_name} field")
        if contract:
            if not principle.boundary:
                errors.append(f"{principle.id}: missing or empty Boundary field")
            is_baseline = principle.id in baseline_ids
            baseline_demotions = (
                _defended_demotions(principle, entries, migration_index)
                if is_baseline and migration_index is not None
                else []
            )
            demotion_floor = (
                migration_index
                if is_baseline and migration_index is not None
                else -1
            )
            errors.extend(_unapplied_demotions(principle, entries, demotion_floor))
            relevant_demotions = (
                baseline_demotions
                if is_baseline
                else _defended_demotions(principle, entries)
            )
            if is_baseline and principle.declared == "provisional" and not baseline_demotions:
                errors.append(
                    f"{principle.id}: migrated baseline rule cannot become provisional without a defended demotion"
                )
            if principle.scope == "scoped":
                if not principle.applies_to:
                    errors.append(f"{principle.id}: scoped taste requires Applies to")
                if not principle.test:
                    errors.append(f"{principle.id}: scoped taste requires Operational test")
                if principle.declared not in {"stable", "provisional"}:
                    errors.append(
                        f"{principle.id}: scoped Confidence must be 'stable' or 'provisional'"
                    )
                if not principle.evidence:
                    errors.append(f"{principle.id}: scoped taste requires an Evidence reference")
            baseline_reconfirmation = (
                is_baseline and principle.declared == "stable" and bool(baseline_demotions)
            )
            requires_confirmation = principle.declared == "stable" and (
                not is_baseline or baseline_reconfirmation
            )
            if requires_confirmation and not principle.evidence:
                if baseline_reconfirmation:
                    errors.append(
                        f"{principle.id}: re-stabilizing a demoted migration baseline requires a fresh Evidence reference"
                    )
                else:
                    errors.append(
                        f"{principle.id}: new stable rule requires an Evidence reference"
                    )
            if principle.evidence and (not is_baseline or relevant_demotions):
                if not principle.confirmed_by:
                    errors.append(
                        f"{principle.id}: Evidence has no supported history reference"
                    )
                for ref in principle.confirmed_by:
                    entry = entries.get(ref)
                    if entry is None:
                        errors.append(
                            f"{principle.id}: evidence reference {ref} resolves to no history entry"
                        )
                    elif not _entry_supports_principle(entry, principle.id):
                        errors.append(
                            f"{principle.id}: evidence reference {ref} is not about this exact principle"
                        )
            if requires_confirmation:
                latest_demotion = baseline_demotions[-1] if baseline_reconfirmation else None
                confirming = [
                    ref
                    for ref in principle.confirmed_by
                    if ref in entries
                    and entries[ref].action in CONFIRMING_ACTIONS
                    and entries[ref].result == "hit"
                    and entries[ref].fields.get("about") == principle.id
                    and (
                        latest_demotion is None
                        or entry_positions[ref] > latest_demotion[0]
                    )
                ]
                if not confirming:
                    if baseline_reconfirmation:
                        errors.append(
                            f"{principle.id}: re-stabilization requires an exact confirming prediction or recognition appended after {latest_demotion[1].id}"
                        )
                    else:
                        errors.append(
                            f"{principle.id}: stable rule requires an exact confirming prediction or recognition"
                        )
            continue
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
    """Ids active at the strongest confidence level for the detected schema."""
    entries = parse_log(log_text)
    metadata, _ = _profile_metadata(profile_text)
    if metadata.get("schema") == SUPPORTED_CONTRACT_SCHEMA:
        return {
            principle.id
            for principle in parse_profile(profile_text)
            if principle.declared == "stable"
        }
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
