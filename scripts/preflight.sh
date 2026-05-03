#!/bin/sh
set -eu

printf 'cwd: %s\n' "$(pwd)"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf '\ngit:\n'
  git status --short --branch
else
  printf '\ngit: not a repository\n'
fi

printf '\ntools:\n'
command -v git >/dev/null 2>&1 && git --version || printf 'git: missing\n'
command -v node >/dev/null 2>&1 && node --version || printf 'node: missing\n'
command -v npm >/dev/null 2>&1 && npm --version || printf 'npm: missing\n'
command -v python3 >/dev/null 2>&1 && python3 --version || printf 'python3: missing\n'
command -v pip3 >/dev/null 2>&1 && pip3 --version || printf 'pip3: missing\n'

printf '\nprotected filenames:\n'
sh scripts/check-sensitive-files.sh . || true
