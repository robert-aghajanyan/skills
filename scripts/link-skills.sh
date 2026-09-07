#!/usr/bin/env bash
set -euo pipefail

# Maintainer-only. Symlinks every skill outside deprecated/ into the local
# harness skill directories, so a `git pull` keeps the installed copies
# current. This is NOT an install route: never run it alongside the plugin, or
# every skill shows up twice. Users install the plugin (see README.md).
#
#   ~/.claude/skills   Claude Code
#   ~/.agents/skills   Codex and other Agent Skills-compatible harnesses

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DESTS=("$HOME/.claude/skills" "$HOME/.agents/skills")

names=(); srcs=()
while IFS= read -r -d '' skill_md; do
  src="$(dirname "$skill_md")"
  names+=("$(basename "$src")"); srcs+=("$src")
done < <(find "$REPO/skills" -name SKILL.md -not -path '*/deprecated/*' -print0)

for DEST in "${DESTS[@]}"; do
  # A $DEST that is itself a symlink into this repo would make us write the
  # per-skill links back into the working copy. Bail instead.
  if [ -L "$DEST" ]; then
    resolved="$(readlink "$DEST")"
    case "$resolved" in
      "$REPO"|"$REPO"/*)
        echo "error: $DEST is a symlink into this repo ($resolved)." >&2
        echo "Remove it and re-run; the script will recreate it as a real dir." >&2
        exit 1 ;;
    esac
  fi

  mkdir -p "$DEST"
  for i in "${!names[@]}"; do
    target="$DEST/${names[$i]}"
    [ -e "$target" ] && [ ! -L "$target" ] && rm -rf "$target"
    ln -sfn "${srcs[$i]}" "$target"
    echo "linked ${names[$i]} -> ${srcs[$i]} ($DEST)"
  done
done
