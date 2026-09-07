#!/usr/bin/env python3
"""Regression tests for validate_clean_gate.py."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR = SCRIPT_DIR / "validate_clean_gate.py"
FIXTURES = SCRIPT_DIR.parent / "references" / "golden-ledgers.json"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_clean_gate", VALIDATOR)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load validator: {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE_LEDGER: dict[str, Any] = {
    "pr": 123,
    "mode": "fast-strict",
    "risk_level": "high",
    "head_sha": "abc123",
    "github": {
        "headRefOid": "abc123",
        "baseRefName": "main",
        "headRefName": "feature/pr-branch",
        "mergeable": "MERGEABLE",
        "mergeStateStatus": "CLEAN",
    },
    "workspace": {
        "strategy": "temp-clone",
        "clean": True,
    },
    "review_structure": {
        "source_skill": "team-review-plus",
        "source_skill_loaded": True,
        "team_review_skill_loaded": True,
        "parallel_agents_requested": True,
        "reasoning_effort": "xhigh",
        "reviewer_count": 4,
        "lenses": ["security", "performance", "correctness", "guardrails"],
        "initial_discovery_full": True,
        "post_fix_verification": "ledger-focused",
        "final_clean_room": True,
    },
    "execution_policy": {
        "push_requested": True,
        "pushed": True,
        "remote_head_verified": True,
        "merged": False,
    },
    "fix_scope": {
        "allowed_severities": ["CRITICAL", "WARNING"],
        "suggestions_blocking": False,
        "fixed_low_severity": False,
        "user_requested_low_severity_cleanup": False,
    },
    "round_limits": {
        "max_fix_rounds": 3,
        "fix_rounds_used": 1,
        "stopped_for_repeat_blocker": False,
    },
    "rounds": [
        {
            "round": 1,
            "head_sha": "abc123",
            "review_mode": "parallel-team-review",
            "critical": 1,
            "warning": 1,
            "suggestion": 0,
            "summary": "Initial discovery",
        }
    ],
    "findings": [
        {
            "id": "F1",
            "finding": "Unsafe variant accepted",
            "severity": "WARNING",
            "status": "closed",
            "file": "src/example.py",
            "proof": "pytest tests/test_example.py -q",
            "fixed_by": "abc123",
            "verified_by": "final calibration",
        }
    ],
    "risk_surfaces": [
        {
            "surface": "URL allowlist",
            "status": "closed",
            "entrypoints": ["CLI"],
            "negative_tests": ["userinfo host rejected"],
            "observed_behavior": "Unsafe variants fail closed",
        }
    ],
    "final_calibration": {
        "head_sha": "abc123",
        "review_mode": "clean-room-team-review-plus",
        "fresh": True,
        "independent": True,
        "context_isolated": True,
        "critical": 0,
        "warning": 0,
        "commands": ["pytest tests/test_example.py -q"],
    },
    "clean_passes": [
        {
            "name": "post-fix full review",
            "head_sha": "abc123",
            "review_mode": "ledger-focused-verification",
            "fresh": True,
            "independent": True,
            "critical": 0,
            "warning": 0,
        },
        {
            "name": "final clean-room calibration",
            "head_sha": "abc123",
            "review_mode": "clean-room-team-review-plus",
            "fresh": True,
            "independent": True,
            "critical": 0,
            "warning": 0,
        },
    ],
    "external_reviews": [
        {
            "source": "fresh-session-team-review",
            "head_sha": "abc123",
            "review_mode": "team-review-plus",
            "context_isolated": True,
            "team_review_skill_loaded": True,
            "critical": 0,
            "warning": 0,
            "proof": "fresh session/team-review output",
            "artifact_path": "",
            "reconciled": True,
        }
    ],
}


def clone() -> dict[str, Any]:
    ledger = copy.deepcopy(BASE_LEDGER)
    artifact = Path(tempfile.gettempdir()) / "pr-clean-review-external-review.md"
    artifact.write_text("Team Review Summary\n\nNo critical issues or warnings.\n", encoding="utf-8")
    ledger["external_reviews"][0]["artifact_path"] = str(artifact)
    return ledger


def fixture_clone(name: str) -> dict[str, Any]:
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    ledger = copy.deepcopy(fixtures[name])
    artifact = Path(tempfile.gettempdir()) / f"pr-clean-review-{name}.md"
    artifact.write_text("Team Review Summary\n\nNo critical issues or warnings.\n", encoding="utf-8")
    ledger["external_reviews"][0]["artifact_path"] = str(artifact)
    return ledger


def expect(name: str, ledger: dict[str, Any], should_pass: bool, **kwargs: Any) -> None:
    validator = _load_validator()
    errors = validator.validate(ledger, **kwargs)
    passed = not errors
    if passed != should_pass:
        state = "PASS" if passed else "FAIL"
        raise AssertionError(f"{name}: expected {should_pass}, got {state}: {errors}")
    print(f"{name}: {'PASS' if should_pass else 'FAIL as expected'}")


def expect_cli(
    name: str,
    ledger: dict[str, Any],
    should_pass: bool,
    *extra_args: str,
) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger_path = Path(tmpdir) / "ledger.json"
        ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
        result = subprocess.run(
            ["python3", str(VALIDATOR), str(ledger_path), *extra_args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    passed = result.returncode == 0
    if passed != should_pass:
        output = (result.stdout + result.stderr).strip()
        state = "PASS" if passed else "FAIL"
        raise AssertionError(f"{name}: expected {should_pass}, got {state}: {output}")
    print(f"{name}: {'PASS' if should_pass else 'FAIL as expected'}")


def main() -> int:
    expect("valid high-risk mergeable", clone(), True)
    expect("golden high-risk mergeable", fixture_clone("valid_high_risk_mergeable"), True)
    expect_cli("cli valid high-risk mergeable", clone(), True)

    blocked = clone()
    blocked["github"]["mergeStateStatus"] = "BLOCKED"
    expect("blocked merge state", blocked, False)
    expect("blocked code-clean-only", blocked, True, code_clean_only=True)
    expect_cli("cli blocked merge state", blocked, False)
    expect_cli("cli blocked code-clean-only", blocked, True, "--code-clean-only")

    wrong_mode = clone()
    wrong_mode["mode"] = "loose"
    expect("wrong mode", wrong_mode, False)
    expect_cli("cli wrong mode", wrong_mode, False)

    one_pass = clone()
    one_pass["clean_passes"] = one_pass["clean_passes"][:1]
    expect("high risk one clean pass", one_pass, False)

    low_risk = clone()
    low_risk["risk_level"] = "normal"
    low_risk["round_limits"]["max_fix_rounds"] = 2
    low_risk["clean_passes"] = low_risk["clean_passes"][:1]
    expect("normal risk one clean pass", low_risk, True)
    expect("normal risk forced two passes", low_risk, False, require_two_clean_passes=True)

    dirty = clone()
    dirty["workspace"]["clean"] = False
    expect("dirty workspace", dirty, False)

    no_team_skill = clone()
    no_team_skill["review_structure"]["source_skill_loaded"] = False
    expect("team-review skill not loaded", no_team_skill, False)

    downgraded_effort = clone()
    downgraded_effort["review_structure"]["reasoning_effort"] = "medium"
    expect("parallel team-review downgraded effort", downgraded_effort, False)

    missing_lens = clone()
    missing_lens["review_structure"]["lenses"] = [
        "security",
        "correctness",
        "guardrails",
    ]
    expect("missing performance lens", missing_lens, False)

    nonparallel_missing_lens = clone()
    nonparallel_missing_lens["risk_level"] = "normal"
    nonparallel_missing_lens["round_limits"]["max_fix_rounds"] = 2
    nonparallel_missing_lens["review_structure"]["parallel_agents_requested"] = False
    nonparallel_missing_lens["rounds"][0]["review_mode"] = "team-review"
    nonparallel_missing_lens["review_structure"]["lenses"] = [
        "security",
        "correctness",
        "guardrails",
    ]
    expect("nonparallel missing performance lens", nonparallel_missing_lens, False)

    missing_initial_discovery = clone()
    missing_initial_discovery["review_structure"]["initial_discovery_full"] = False
    expect("missing full initial discovery", missing_initial_discovery, False)

    missing_clean_room = clone()
    missing_clean_room["review_structure"]["final_clean_room"] = False
    expect("missing final clean-room review", missing_clean_room, False)

    missing_context_isolation = clone()
    missing_context_isolation["final_calibration"]["context_isolated"] = False
    expect("final calibration not context isolated", missing_context_isolation, False)

    no_external_review = clone()
    no_external_review["external_reviews"] = []
    expect("missing external final review", no_external_review, False)

    external_warning = clone()
    external_warning["external_reviews"][0]["warning"] = 1
    expect("external final review warning", external_warning, False)

    external_not_isolated = clone()
    external_not_isolated["external_reviews"][0]["context_isolated"] = False
    expect("external review not isolated", external_not_isolated, False)

    missing_artifact = clone()
    missing_artifact["external_reviews"][0]["artifact_path"] = "/no/such/external-review.md"
    expect("external review missing artifact", missing_artifact, False)

    pushed_without_request = clone()
    pushed_without_request["execution_policy"]["push_requested"] = False
    expect("pushed without request", pushed_without_request, False)

    merged = clone()
    merged["execution_policy"]["merged"] = True
    expect("merged branch", merged, False)

    low_fix = clone()
    low_fix["fix_scope"]["allowed_severities"].append("SUGGESTION")
    expect("suggestion in default fix scope", low_fix, False)

    suggestion_blocking = clone()
    suggestion_blocking["fix_scope"]["suggestions_blocking"] = True
    expect("suggestions blocking by default", suggestion_blocking, False)

    too_many_rounds = clone()
    too_many_rounds["risk_level"] = "normal"
    too_many_rounds["round_limits"]["max_fix_rounds"] = 3
    expect("too many normal fix rounds", too_many_rounds, False)

    repeat_blocker = clone()
    repeat_blocker["round_limits"]["stopped_for_repeat_blocker"] = True
    expect("repeat blocker stop is not clean", repeat_blocker, False)

    missing_probe = clone()
    missing_probe["risk_surfaces"][0]["negative_tests"] = []
    expect("missing negative probe", missing_probe, False)

    duplicate = clone()
    duplicate["findings"].append(copy.deepcopy(duplicate["findings"][0]))
    expect("duplicate finding id", duplicate, False)

    stale_final = clone()
    stale_final["final_calibration"]["head_sha"] = "old"
    expect("stale final calibration head", stale_final, False)

    missing_final_head = clone()
    del missing_final_head["final_calibration"]["head_sha"]
    expect("missing final calibration head", missing_final_head, False)

    print("matrix complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
