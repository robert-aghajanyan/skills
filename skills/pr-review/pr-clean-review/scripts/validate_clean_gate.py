#!/usr/bin/env python3
"""Validate the PR clean-review evidence ledger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BLOCKING_SEVERITIES = {"CRITICAL", "WARNING"}
CLOSED_STATUSES = {"closed", "fixed", "disproven"}
WORKSPACE_STRATEGIES = {"current-clean", "worktree", "temp-clone", "archive-snapshot"}
ALLOWED_FIX_SEVERITIES = {"CRITICAL", "WARNING"}
ALLOWED_MODES = {"fast-strict"}
REQUIRED_TEAM_REVIEW_LENSES = {"security", "performance", "correctness", "guardrails"}
REVIEW_SOURCE_SKILLS = {"team-review", "team-review-plus"}
EXTERNAL_REVIEW_SOURCES = {"fresh-session-team-review", "fresh-subagent-team-review"}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"ledger not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON at {exc.lineno}:{exc.colno}: {exc.msg}") from None

    if not isinstance(data, dict):
        raise SystemExit("ledger root must be a JSON object")
    return data


def _as_list(value: Any, field: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    return value


def _text(value: Any) -> str:
    return str(value or "").strip()


def _is_true(value: Any) -> bool:
    return value is True or _text(value).lower() == "true"


def _validate_clean_pass(
    clean_pass: dict[str, Any],
    *,
    index: int,
    head_sha: str,
) -> list[str]:
    errors: list[str] = []
    name = _text(clean_pass.get("name")) or f"#{index}"

    if _text(clean_pass.get("head_sha")) != head_sha:
        errors.append(f"clean pass {name}: head_sha must match ledger head_sha")
    if clean_pass.get("critical") != 0:
        errors.append(f"clean pass {name}: critical must be 0")
    if clean_pass.get("warning") != 0:
        errors.append(f"clean pass {name}: warning must be 0")
    if not _text(clean_pass.get("review_mode")):
        errors.append(f"clean pass {name}: review_mode is required")
    if not _is_true(clean_pass.get("fresh")):
        errors.append(f"clean pass {name}: fresh must be true")
    if not _is_true(clean_pass.get("independent")):
        errors.append(f"clean pass {name}: independent must be true")

    return errors


def _validate_required_lenses(review_structure: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    lenses = review_structure.get("lenses")
    if not isinstance(lenses, list):
        errors.append("review_structure.lenses must be a list")
        return errors

    normalized_lenses = {_text(lens).lower() for lens in lenses}
    missing = sorted(REQUIRED_TEAM_REVIEW_LENSES - normalized_lenses)
    if missing:
        errors.append("review_structure.lenses missing required lenses: " + ", ".join(missing))
    return errors


def validate(
    data: dict[str, Any],
    *,
    code_clean_only: bool = False,
    require_two_clean_passes: bool = False,
) -> list[str]:
    errors: list[str] = []

    head_sha = _text(data.get("head_sha"))
    if not head_sha:
        errors.append("head_sha is required")

    mode = _text(data.get("mode"))
    if mode not in ALLOWED_MODES:
        allowed = ", ".join(sorted(ALLOWED_MODES))
        errors.append(f"mode must be one of: {allowed}")

    risk_level = _text(data.get("risk_level")).lower()
    if risk_level in {"high", "critical"}:
        require_two_clean_passes = True

    github = data.get("github")
    if not isinstance(github, dict):
        errors.append("github object is required")
        github = {}

    github_head = _text(github.get("headRefOid"))
    if not github_head:
        errors.append("github.headRefOid is required")
    elif head_sha and github_head != head_sha:
        errors.append("github.headRefOid must match ledger head_sha")

    for field in ("baseRefName", "headRefName"):
        if not _text(github.get(field)):
            errors.append(f"github.{field} is required")

    workspace = data.get("workspace")
    if not isinstance(workspace, dict):
        errors.append("workspace object is required")
        workspace = {}

    strategy = _text(workspace.get("strategy")).lower()
    if strategy not in WORKSPACE_STRATEGIES:
        accepted = ", ".join(sorted(WORKSPACE_STRATEGIES))
        errors.append(f"workspace.strategy must be one of: {accepted}")
    if not _is_true(workspace.get("clean")):
        errors.append("workspace.clean must be true")

    review_structure = data.get("review_structure")
    if not isinstance(review_structure, dict):
        errors.append("review_structure object is required")
        review_structure = {}

    source_skill = _text(review_structure.get("source_skill"))
    if source_skill not in REVIEW_SOURCE_SKILLS:
        allowed = ", ".join(sorted(REVIEW_SOURCE_SKILLS))
        errors.append(f"review_structure.source_skill must be one of: {allowed}")
    if not _is_true(review_structure.get("source_skill_loaded")):
        errors.append("review_structure.source_skill_loaded must be true")
    if source_skill == "team-review-plus" and not _is_true(
        review_structure.get("team_review_skill_loaded")
    ):
        errors.append(
            "review_structure.team_review_skill_loaded must be true when source_skill is team-review-plus"
        )
    if not _is_true(review_structure.get("initial_discovery_full")):
        errors.append("review_structure.initial_discovery_full must be true")
    if not _text(review_structure.get("post_fix_verification")):
        errors.append("review_structure.post_fix_verification is required")
    if not _is_true(review_structure.get("final_clean_room")):
        errors.append("review_structure.final_clean_room must be true")
    errors.extend(_validate_required_lenses(review_structure))

    review_modes: list[str] = []

    execution_policy = data.get("execution_policy")
    if not isinstance(execution_policy, dict):
        errors.append("execution_policy object is required")
        execution_policy = {}

    if _is_true(execution_policy.get("merged")):
        errors.append("execution_policy.merged must be false")
    if _is_true(execution_policy.get("pushed")):
        if not _is_true(execution_policy.get("push_requested")):
            errors.append("execution_policy.pushed requires push_requested true")
        if not _is_true(execution_policy.get("remote_head_verified")):
            errors.append("execution_policy.pushed requires remote_head_verified true")

    fix_scope = data.get("fix_scope")
    if not isinstance(fix_scope, dict):
        errors.append("fix_scope object is required")
        fix_scope = {}

    allowed_severities = fix_scope.get("allowed_severities")
    if not isinstance(allowed_severities, list) or not allowed_severities:
        errors.append("fix_scope.allowed_severities must be a non-empty list")
    else:
        normalized = {_text(item).upper() for item in allowed_severities}
        unsupported = sorted(normalized - ALLOWED_FIX_SEVERITIES)
        if unsupported:
            errors.append(
                "fix_scope.allowed_severities may only include CRITICAL and WARNING"
            )

    if _is_true(fix_scope.get("fixed_low_severity")) and not _is_true(
        fix_scope.get("user_requested_low_severity_cleanup")
    ):
        errors.append(
            "fix_scope.fixed_low_severity requires user_requested_low_severity_cleanup true"
        )
    if _is_true(fix_scope.get("suggestions_blocking")):
        errors.append("fix_scope.suggestions_blocking must be false by default")

    round_limits = data.get("round_limits")
    if not isinstance(round_limits, dict):
        errors.append("round_limits object is required")
        round_limits = {}

    max_fix_rounds = round_limits.get("max_fix_rounds")
    fix_rounds_used = round_limits.get("fix_rounds_used")
    if not isinstance(max_fix_rounds, int) or max_fix_rounds < 1:
        errors.append("round_limits.max_fix_rounds must be a positive integer")
    elif risk_level in {"high", "critical"} and max_fix_rounds > 3:
        errors.append("round_limits.max_fix_rounds must not exceed 3 for high-risk PRs")
    elif risk_level not in {"high", "critical"} and max_fix_rounds > 2:
        errors.append("round_limits.max_fix_rounds must not exceed 2 for normal PRs")
    if not isinstance(fix_rounds_used, int) or fix_rounds_used < 0:
        errors.append("round_limits.fix_rounds_used must be a non-negative integer")
    elif isinstance(max_fix_rounds, int) and fix_rounds_used > max_fix_rounds:
        errors.append("round_limits.fix_rounds_used must not exceed max_fix_rounds")
    if _is_true(round_limits.get("stopped_for_repeat_blocker")):
        errors.append("round_limits.stopped_for_repeat_blocker must be false")

    try:
        rounds = _as_list(data.get("rounds"), "rounds")
    except ValueError as exc:
        errors.append(str(exc))
        rounds = []

    if not rounds:
        errors.append("rounds must include at least the initial discovery pass")
    else:
        first_round = rounds[0]
        if not isinstance(first_round, dict):
            errors.append("round #1 must be an object")
        else:
            if not _text(first_round.get("head_sha")):
                errors.append("round #1 head_sha is required")
            if not _text(first_round.get("review_mode")):
                errors.append("round #1 review_mode is required")
            else:
                review_modes.append(_text(first_round.get("review_mode")).lower())

    final = data.get("final_calibration")
    if not isinstance(final, dict):
        errors.append("final_calibration object is required")
        final = {}

    final_head = _text(final.get("head_sha"))
    if not final_head:
        errors.append("final_calibration.head_sha is required")
    elif head_sha and final_head != head_sha:
        errors.append("final_calibration.head_sha must match ledger head_sha")

    for count_field in ("critical", "warning"):
        value = final.get(count_field)
        if value != 0:
            errors.append(f"final_calibration.{count_field} must be 0")

    if not _text(final.get("review_mode")):
        errors.append("final_calibration.review_mode is required")
    else:
        review_modes.append(_text(final.get("review_mode")).lower())
    if not _is_true(final.get("fresh")):
        errors.append("final_calibration.fresh must be true")
    if not _is_true(final.get("independent")):
        errors.append("final_calibration.independent must be true")
    if not _is_true(final.get("context_isolated")):
        errors.append("final_calibration.context_isolated must be true")

    commands = final.get("commands")
    if not isinstance(commands, list) or not any(_text(cmd) for cmd in commands):
        errors.append("final_calibration.commands must include at least one command or probe")

    try:
        findings = _as_list(data.get("findings"), "findings")
    except ValueError as exc:
        errors.append(str(exc))
        findings = []

    seen_ids: set[str] = set()
    for index, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            errors.append(f"finding #{index} must be an object")
            continue

        finding_id = _text(finding.get("id")) or f"#{index}"
        if finding_id in seen_ids:
            errors.append(f"duplicate finding id: {finding_id}")
        seen_ids.add(finding_id)

        severity = _text(finding.get("severity")).upper()
        status = _text(finding.get("status")).lower()
        if severity in BLOCKING_SEVERITIES:
            for field in ("finding", "file"):
                if not _text(finding.get(field)):
                    errors.append(f"{finding_id}: {field} is required")
            if status not in CLOSED_STATUSES:
                errors.append(f"{finding_id}: blocking finding is not closed")
            for field in ("proof", "fixed_by", "verified_by"):
                if not _text(finding.get(field)):
                    errors.append(f"{finding_id}: {field} is required")

    try:
        surfaces = _as_list(data.get("risk_surfaces"), "risk_surfaces")
    except ValueError as exc:
        errors.append(str(exc))
        surfaces = []

    for index, surface in enumerate(surfaces, start=1):
        if not isinstance(surface, dict):
            errors.append(f"risk surface #{index} must be an object")
            continue

        name = _text(surface.get("surface")) or f"#{index}"
        status = _text(surface.get("status")).lower()
        if status not in CLOSED_STATUSES:
            errors.append(f"risk surface {name}: status must be closed/fixed/disproven")

        entrypoints = surface.get("entrypoints")
        if not isinstance(entrypoints, list) or not any(_text(item) for item in entrypoints):
            errors.append(f"risk surface {name}: entrypoints are required")

        negative_tests = surface.get("negative_tests")
        if not isinstance(negative_tests, list) or not any(_text(item) for item in negative_tests):
            errors.append(f"risk surface {name}: at least one negative test is required")

        if not _text(surface.get("observed_behavior")):
            errors.append(f"risk surface {name}: observed_behavior is required")

    if not code_clean_only:
        mergeable = _text(github.get("mergeable")).upper()
        merge_state = _text(github.get("mergeStateStatus")).upper()
        if mergeable != "MERGEABLE":
            errors.append("github.mergeable must be MERGEABLE")
        if merge_state != "CLEAN":
            errors.append("github.mergeStateStatus must be CLEAN")

    try:
        clean_passes = _as_list(data.get("clean_passes"), "clean_passes")
    except ValueError as exc:
        errors.append(str(exc))
        clean_passes = []

    if clean_passes:
        for index, clean_pass in enumerate(clean_passes, start=1):
            if not isinstance(clean_pass, dict):
                errors.append(f"clean pass #{index} must be an object")
                continue
            if _text(clean_pass.get("review_mode")):
                review_modes.append(_text(clean_pass.get("review_mode")).lower())
            errors.extend(_validate_clean_pass(clean_pass, index=index, head_sha=head_sha))

    if require_two_clean_passes:
        if len(clean_passes) < 2:
            errors.append("clean_passes must include two clean independent passes")
        else:
            last_two = clean_passes[-2:]
            for index, clean_pass in enumerate(last_two, start=len(clean_passes) - 1):
                if isinstance(clean_pass, dict):
                    errors.extend(_validate_clean_pass(clean_pass, index=index, head_sha=head_sha))

    team_parallel_requested = any("parallel" in mode and "team-review" in mode for mode in review_modes)
    if _is_true(review_structure.get("parallel_agents_requested")) or team_parallel_requested:
        if not _is_true(review_structure.get("parallel_agents_requested")):
            errors.append("review_structure.parallel_agents_requested must be true")
        if _text(review_structure.get("reasoning_effort")).lower() != "xhigh":
            errors.append("review_structure.reasoning_effort must be xhigh")
        reviewer_count = review_structure.get("reviewer_count")
        if not isinstance(reviewer_count, int) or reviewer_count < 4:
            errors.append("review_structure.reviewer_count must be at least 4")
        if not _is_true(review_structure.get("initial_discovery_full")):
            errors.append("review_structure.initial_discovery_full must be true")
        if not _is_true(review_structure.get("final_clean_room")):
            errors.append("review_structure.final_clean_room must be true")

    try:
        external_reviews = _as_list(data.get("external_reviews"), "external_reviews")
    except ValueError as exc:
        errors.append(str(exc))
        external_reviews = []

    if not external_reviews:
        errors.append("external_reviews must include at least one fresh final team-review")

    for index, review in enumerate(external_reviews, start=1):
        if not isinstance(review, dict):
            errors.append(f"external review #{index} must be an object")
            continue
        name = _text(review.get("source")) or f"#{index}"
        if name not in EXTERNAL_REVIEW_SOURCES:
            allowed = ", ".join(sorted(EXTERNAL_REVIEW_SOURCES))
            errors.append(f"external review {name}: source must be one of: {allowed}")
        if _text(review.get("head_sha")) != head_sha:
            errors.append(f"external review {name}: head_sha must match ledger head_sha")
        if "team-review" not in _text(review.get("review_mode")).lower():
            errors.append(f"external review {name}: review_mode must include team-review")
        if not _is_true(review.get("context_isolated")):
            errors.append(f"external review {name}: context_isolated must be true")
        if not _is_true(review.get("team_review_skill_loaded")):
            errors.append(f"external review {name}: team_review_skill_loaded must be true")
        if review.get("critical") != 0:
            errors.append(f"external review {name}: critical must be 0")
        if review.get("warning") != 0:
            errors.append(f"external review {name}: warning must be 0")
        if not _text(review.get("proof")):
            errors.append(f"external review {name}: proof is required")
        artifact_path = _text(review.get("artifact_path"))
        if not artifact_path:
            errors.append(f"external review {name}: artifact_path is required")
        else:
            path = Path(artifact_path).expanduser()
            if not path.is_file():
                errors.append(f"external review {name}: artifact_path must exist as a file")
            elif path.stat().st_size <= 0:
                errors.append(f"external review {name}: artifact_path must be non-empty")
        if not _is_true(review.get("reconciled")):
            errors.append(f"external review {name}: reconciled must be true")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path, help="Path to the JSON evidence ledger")
    parser.add_argument(
        "--code-clean-only",
        action="store_true",
        help="Validate the code-review gate without requiring GitHub merge-box eligibility",
    )
    parser.add_argument(
        "--require-two-clean-passes",
        action="store_true",
        help="Require two clean independent review passes on the current head",
    )
    args = parser.parse_args(argv)

    data = _load_json(args.ledger)
    errors = validate(
        data,
        code_clean_only=args.code_clean_only,
        require_two_clean_passes=args.require_two_clean_passes,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    mode = "code-clean" if args.code_clean_only else "mergeable"
    print(f"OK: ledger satisfies {mode} gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
