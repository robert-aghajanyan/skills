# The mp-* skills are ports, not forks

## Context

Seven skills in this repo arrived in August 2026 as a "Codex-derived install" of Matt Pocock's skills, carrying an `mp-` prefix and no record of which upstream version they came from. By September they had quietly diverged: `mp-grill-me` still asked one question at a time while upstream had moved to asking a whole settled frontier per round, and `mp-to-prd` / `mp-to-issues` kept names upstream had already retired in favour of `to-spec` / `to-tickets`.

Divergence with no way to measure it is the worst of both worlds: we get neither upstream's improvements nor a deliberate fork we own.

## Decision

Every `mp-`-prefixed skill is a **port**. Its content matches [mattpocock/skills](https://github.com/mattpocock/skills) byte for byte, and the only permitted differences are mechanical:

1. The skill name gains the `mp-` prefix, and every cross-skill reference inside it is rewritten to our namespace. The prefix is what lets both plugins be installed side by side without colliding.
2. Upstream references to `code-review`, `research`, and `ask-matt` are redirected to our `team-review`, `team-research`, and `which-skill`. Those three upstream skills are therefore not ported: we already answer them.
3. `mp-setup` (upstream `setup-matt-pocock-skills`) is debranded, since it configures *this* repo's skills.

`scripts/check-upstream-sync.py` encodes exactly those rules, reverses them, and diffs against a fresh clone. Zero drift is the expected state, and the debranding in (3) is whitelisted so it never reads as drift.

Licensing follows the port: each `mp-` skill ships an MIT `LICENSE.txt` retaining Matt Pocock's copyright notice alongside ours, rather than this repo's default Apache-2.0.

## Consequences

- **Never hand-edit an `mp-` skill.** An improvement goes upstream as a PR, or becomes a new non-`mp-` skill here. A local edit is drift, and the checker will flag it as such.
- Re-syncing is running the checker, reading the diff, and re-porting what moved. It is not a merge.
- Upstream deletions propagate: a skill that disappears upstream is reported as `GONE UPSTREAM` and should be deleted here too, or consciously adopted as our own by dropping the `mp-` prefix.
- We inherit upstream's judgement calls, including ones we might not make. `mp-implement` still writes `/mp-tdd` rather than the `Call the Skill tool with` phrasing upstream's own conventions mandate. Fidelity beats local tidying: fixing it here would be permanent drift for a cosmetic gain.
