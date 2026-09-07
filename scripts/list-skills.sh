#!/usr/bin/env bash
set -euo pipefail
cd "$(cd "$(dirname "$0")/.." && pwd)"
find skills -name SKILL.md | sed 's|/SKILL.md$||' | sort
