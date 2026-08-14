#!/usr/bin/env python3
"""Semantic smoke tests for the production-readiness-gate skill.

This script intentionally checks durable contract markers, not exact prose.
It complements the generic skill validator by catching regressions in the
readiness workflow, output shape, local-artifact support, trigger fixtures,
manifest provenance, and clean-install packaging.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path


def read(path: Path) -> str:
    if not path.exists():
        raise AssertionError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    if not path.exists():
        raise AssertionError(f"missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing {label}: {needle!r}")


def require_regex(text: str, pattern: str, label: str) -> None:
    if not re.search(pattern, text, re.MULTILINE):
        raise AssertionError(f"missing {label}: /{pattern}/")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"forbidden {label}: {needle!r}")


def parse_golden_transcripts(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            if not current:
                raise AssertionError("golden transcript heading is empty")
            if current in sections:
                raise AssertionError(f"duplicate golden transcript heading: {current}")
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def combined_digest(skill_dir: Path, relative_paths: list[str]) -> str:
    combined = hashlib.sha256()
    for rel_path in relative_paths:
        path = skill_dir / rel_path
        combined.update(rel_path.encode("utf-8"))
        combined.update(b"\0")
        combined.update(file_digest(path).encode("ascii"))
        combined.update(b"\n")
    return combined.hexdigest()


def validate_manifest(skill_dir: Path) -> str:
    manifest = read_json(skill_dir / "manifest.json")
    if manifest.get("name") != "production-readiness-gate":
        raise AssertionError("manifest name must be production-readiness-gate")
    require(str(manifest.get("version", "")), ".", "manifest semantic-ish version")
    source = manifest.get("source")
    if not isinstance(source, dict):
        raise AssertionError("manifest source must be an object")
    source_type = source.get("type")
    if source_type not in {"local-installed-skill", "git-working-copy"}:
        raise AssertionError(f"manifest source has invalid type: {source_type!r}")
    installed_path = source.get("installed_path")
    if not isinstance(installed_path, str) or not installed_path:
        raise AssertionError("manifest source must include installed_path")
    git_commit = source.get("git_commit")
    if git_commit is not None and not re.fullmatch(r"[0-9a-f]{7,64}", str(git_commit)):
        raise AssertionError("manifest source git_commit must be null or a hex commit id")
    source_tag = source.get("source_tag")
    if source_tag is not None and (not isinstance(source_tag, str) or not source_tag):
        raise AssertionError("manifest source_tag must be a non-empty string when present")
    tracked_files = manifest.get("tracked_files")
    if not isinstance(tracked_files, list) or not tracked_files:
        raise AssertionError("manifest tracked_files must be a non-empty list")

    relative_paths: list[str] = []
    for entry in tracked_files:
        if not isinstance(entry, dict):
            raise AssertionError("manifest tracked_files entries must be objects")
        rel_path = entry.get("path")
        expected_sha = entry.get("sha256")
        if not isinstance(rel_path, str) or rel_path.startswith("/") or ".." in Path(rel_path).parts:
            raise AssertionError(f"manifest has invalid relative path: {rel_path!r}")
        if not isinstance(expected_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
            raise AssertionError(f"manifest has invalid sha256 for {rel_path!r}")
        actual_sha = file_digest(skill_dir / rel_path)
        if actual_sha != expected_sha:
            raise AssertionError(f"manifest sha256 mismatch for {rel_path}: {actual_sha} != {expected_sha}")
        relative_paths.append(rel_path)

    expected_combined = manifest.get("content_sha256")
    actual_combined = combined_digest(skill_dir, relative_paths)
    if actual_combined != expected_combined:
        raise AssertionError(f"manifest content_sha256 mismatch: {actual_combined} != {expected_combined}")
    return actual_combined


def validate_trigger_fixtures(skill_dir: Path, corpus: str) -> int:
    fixture_doc = read_json(skill_dir / "references" / "trigger-fixtures.json")
    fixtures = fixture_doc.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) < 7:
        raise AssertionError("trigger fixture file must include the expected trigger suite")

    seen_ids: set[str] = set()
    near_miss_count = 0
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            raise AssertionError("trigger fixture entries must be objects")
        fixture_id = fixture.get("id")
        if not isinstance(fixture_id, str) or not fixture_id:
            raise AssertionError("trigger fixture is missing id")
        if fixture_id in seen_ids:
            raise AssertionError(f"duplicate trigger fixture id: {fixture_id}")
        seen_ids.add(fixture_id)
        prompt = fixture.get("prompt")
        expected_behavior = fixture.get("expected_behavior")
        should_run_gate = fixture.get("should_run_gate")
        markers = fixture.get("required_markers")
        if not isinstance(prompt, str) or not prompt:
            raise AssertionError(f"trigger fixture {fixture_id} is missing prompt")
        if not isinstance(expected_behavior, str) or not expected_behavior:
            raise AssertionError(f"trigger fixture {fixture_id} is missing expected_behavior")
        if not isinstance(should_run_gate, bool):
            raise AssertionError(f"trigger fixture {fixture_id} is missing should_run_gate")
        if not isinstance(markers, list) or not markers:
            raise AssertionError(f"trigger fixture {fixture_id} must include required markers")
        if should_run_gate is False:
            near_miss_count += 1
        for marker in markers:
            if not isinstance(marker, str) or not marker:
                raise AssertionError(f"trigger fixture {fixture_id} has invalid marker")
            require(corpus, marker, f"trigger fixture marker for {fixture_id}")

    if near_miss_count < 3:
        raise AssertionError("trigger fixtures must include at least three near-miss cases")
    return len(fixtures)


def validate_response_contract_fixtures(skill_dir: Path) -> int:
    fixture_doc = read_json(skill_dir / "references" / "response-contract-fixtures.json")
    golden_transcripts = parse_golden_transcripts(read(skill_dir / "references" / "golden-transcripts.md"))
    fixtures = fixture_doc.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) < 5:
        raise AssertionError("response contract fixture file must include the expected response suite")

    seen_ids: set[str] = set()
    seen_modes: set[str] = set()
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            raise AssertionError("response contract fixture entries must be objects")
        fixture_id = fixture.get("id")
        if not isinstance(fixture_id, str) or not fixture_id:
            raise AssertionError("response contract fixture is missing id")
        if fixture_id in seen_ids:
            raise AssertionError(f"duplicate response contract fixture id: {fixture_id}")
        seen_ids.add(fixture_id)

        prompt = fixture.get("prompt")
        response_mode = fixture.get("response_mode")
        golden_response_id = fixture.get("golden_response_id")
        required_markers = fixture.get("required_response_markers")
        forbidden_markers = fixture.get("forbidden_response_markers")
        if not isinstance(prompt, str) or not prompt:
            raise AssertionError(f"response contract fixture {fixture_id} is missing prompt")
        if response_mode not in {"clarifying_question", "gate_verdict", "no_gate"}:
            raise AssertionError(f"response contract fixture {fixture_id} has invalid response_mode")
        seen_modes.add(response_mode)
        if not isinstance(golden_response_id, str) or not golden_response_id:
            raise AssertionError(f"response contract fixture {fixture_id} is missing golden_response_id")
        golden_response = golden_transcripts.get(golden_response_id)
        if not golden_response:
            raise AssertionError(f"missing golden transcript for {fixture_id}: {golden_response_id}")
        if not isinstance(required_markers, list) or not required_markers:
            raise AssertionError(f"response contract fixture {fixture_id} must include required_response_markers")
        if not isinstance(forbidden_markers, list):
            raise AssertionError(f"response contract fixture {fixture_id} must include forbidden_response_markers")
        for marker in [*required_markers, *forbidden_markers]:
            if not isinstance(marker, str) or not marker:
                raise AssertionError(f"response contract fixture {fixture_id} has invalid response marker")
        for marker in required_markers:
            require(golden_response, marker, f"golden response marker for {fixture_id}")
        for marker in forbidden_markers:
            forbid(golden_response, marker, f"golden response marker for {fixture_id}")

    missing_modes = {"clarifying_question", "gate_verdict", "no_gate"} - seen_modes
    if missing_modes:
        raise AssertionError(f"response contract fixtures missing modes: {sorted(missing_modes)}")
    return len(fixtures)


def run_checks(skill_dir: Path, *, include_clean_install: bool) -> str:
    script_path = skill_dir / "scripts" / "smoke_production_readiness_gate.py"
    skill_md = skill_dir / "SKILL.md"
    rubric = skill_dir / "references" / "readiness-rubric.md"
    risk_checklist = skill_dir / "references" / "risk-surface-checklist.md"
    ledger = skill_dir / "references" / "evidence-ledger-template.md"
    release_notes = skill_dir / "references" / "release-notes.md"
    golden_transcripts = skill_dir / "references" / "golden-transcripts.md"
    trigger_fixtures = skill_dir / "references" / "trigger-fixtures.json"
    response_contracts = skill_dir / "references" / "response-contract-fixtures.json"

    skill_text = read(skill_md)
    rubric_text = read(rubric)
    risk_text = read(risk_checklist)
    ledger_text = read(ledger)
    release_notes_text = read(release_notes)
    golden_transcript_text = read(golden_transcripts)
    fixture_text = read(trigger_fixtures)
    response_contract_text = read(response_contracts)
    corpus = "\n".join(
        [
            skill_text,
            rubric_text,
            risk_text,
            ledger_text,
            release_notes_text,
            golden_transcript_text,
            fixture_text,
            response_contract_text,
        ]
    )

    checks = [
        ("frontmatter name", lambda: require_regex(skill_text, r"^name: production-readiness-gate$", "frontmatter name")),
        ("local target support", lambda: require(skill_text, "local skill directory", "local target support")),
        ("manifest guidance", lambda: require(skill_text, "provenance manifest", "manifest source-of-truth guidance")),
        ("manifest updater command", lambda: require(skill_text, "update_manifest.py", "manifest update command")),
        ("checksum caveat", lambda: require(skill_text, "content checksum", "checksum/version source-of-truth guidance")),
        ("semantic smoke command", lambda: require(skill_text, "smoke_production_readiness_gate.py", "semantic smoke command")),
        ("trigger fixture guidance", lambda: require(skill_text, "trigger fixtures", "trigger fixture guidance")),
        ("response contract guidance", lambda: require(skill_text, "response-contract-fixtures.json", "response contract fixture guidance")),
        ("release notes guidance", lambda: require(skill_text, "release-notes.md", "release notes guidance")),
        ("golden transcript guidance", lambda: require(skill_text, "golden-transcripts.md", "golden transcript guidance")),
        ("trigger expected outcomes", lambda: require(skill_text, "Expected outcome:", "expected outcomes for trigger tests")),
        ("near-miss trigger", lambda: require(skill_text, "Near-miss:", "near-miss trigger test")),
        ("verdict shape", lambda: require(skill_text, "**Verdict**: Ready / Ready With Caveats / Not Ready", "verdict output shape")),
        ("confidence split", lambda: require(skill_text, "Runtime/deployment readiness", "separate runtime confidence")),
        ("residual risk split", lambda: require(skill_text, "Room For Improvement", "room-for-improvement section")),
        ("rubric code score", lambda: require(rubric_text, "## Code/PR/Artifact Readiness", "code readiness rubric")),
        ("rubric runtime score", lambda: require(rubric_text, "## Runtime/Deployment Readiness", "runtime readiness rubric")),
        ("rubric leadership score", lambda: require(rubric_text, "## Leadership-Share Readiness", "leadership readiness rubric")),
        ("risk required proof", lambda: require(risk_text, "For each risky surface, require direct proof", "risk proof standard")),
        ("ledger runtime row", lambda: require(ledger_text, "| Runtime | smoke/dependency check |", "runtime evidence ledger row")),
        ("release notes current version", lambda: require(release_notes_text, "## 1.1.1", "current release notes")),
        ("release notes provenance", lambda: require(release_notes_text, "Source Provenance", "source provenance notes")),
        ("golden transcript local verdict", lambda: require(golden_transcript_text, "## local-skill-verdict", "local skill golden transcript")),
        ("golden response fixture links", lambda: require(response_contract_text, "golden_response_id", "golden response fixture links")),
    ]

    for label, check in checks:
        check()
        print(f"PASS {label}")

    fixture_count = validate_trigger_fixtures(skill_dir, corpus)
    print(f"PASS trigger fixtures ({fixture_count})")

    response_fixture_count = validate_response_contract_fixtures(skill_dir)
    print(f"PASS response contract fixtures ({response_fixture_count})")

    content_sha256 = validate_manifest(skill_dir)
    print("PASS manifest checksums")

    if include_clean_install:
        validate_clean_install(skill_dir)

    return content_sha256


def ignore_clean_copy(dir_name: str, names: list[str]) -> set[str]:
    return {name for name in names if name in {".git", ".DS_Store", "__pycache__"} or name.endswith(".pyc")}


def validate_clean_install(skill_dir: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="production-readiness-gate-clean-") as temp_dir:
        copied_skill = Path(temp_dir) / "production-readiness-gate"
        shutil.copytree(skill_dir, copied_skill, ignore=ignore_clean_copy)
        run_checks(copied_skill, include_clean_install=False)
    print("PASS clean-install smoke")


def main(argv: list[str]) -> int:
    skip_clean_install = False
    args = list(argv[1:])
    if "--skip-clean-install" in args:
        skip_clean_install = True
        args.remove("--skip-clean-install")
    if len(args) > 1:
        raise SystemExit("usage: smoke_production_readiness_gate.py [--skip-clean-install] [skill_dir]")

    script_path = Path(__file__).resolve()
    skill_dir = Path(args[0]).expanduser().resolve() if args else script_path.parents[1]
    content_sha256 = run_checks(skill_dir, include_clean_install=not skip_clean_install)
    print(f"PASS semantic smoke tests for {skill_dir}")
    print(f"content_sha256 {content_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
