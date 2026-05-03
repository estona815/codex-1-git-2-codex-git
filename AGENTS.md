# Codex Workspace Rules

## Project Purpose

This workspace is a local automation and organization area for school reports, project folders, code edits, scripts, media/music/video file structures, repeated task automation, Git-based version control, and terminal productivity setup.

## Forbidden Actions

- Do not scan the whole home directory, full Documents folder, cloud-drive roots, browser profiles, or unrelated system folders.
- Do not run destructive commands such as `rm -rf`, `git clean -fd`, `git reset --hard`, history rewrites, force pushes, or bulk permission changes without explicit approval.
- Do not install packages, upgrade tools, modify system settings, or edit shell startup files such as `.zshrc` or `.bashrc` without showing the proposed change first.
- Do not read, print, copy, move, or commit secrets, credentials, browser sessions, SSH keys, cookies, cloud auth files, API keys, tokens, or passwords.

## Sensitive Data Rules

- Treat files matching `.env*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa*`, `id_ed25519*`, `*secret*`, `*token*`, `*credential*`, `*password*`, `*cookie*`, and similar names as protected.
- It is allowed to report protected filenames, but not their contents.
- If a task requires a sensitive value, ask the user to provide it through a safe channel or explain where they should place it locally.
- Keep generated backups and exports out of Git unless the user explicitly asks to version a sanitized artifact.

## Git Checkpoint Rules

- Before changing existing user files, check `git status --short --branch`.
- If unrelated changes exist, summarize them and work around them. Do not overwrite or revert user changes.
- Make small, meaningful commits after stable checkpoints when Git identity is configured.
- Never directly edit `.git`.
- Always report changed files and a practical rollback command after work.

## Before / After Report Format

Before work:

- Current directory
- Git status
- Sensitive filenames detected, if any
- Planned change scope
- Approval-needed risks, if any

After work:

- What changed
- Why it changed
- Verification result
- Rollback command
- Suggested next step

## File and Folder Naming

- Prefer lowercase names with hyphens or underscores.
- Use clear purpose-based folders: `docs`, `reports`, `src`, `scripts`, `assets`, `music`, `video`, `exports`, `backup`, `archive`, and `reference`.
- Keep raw input, working files, and final exports separate.
- Put one-off scratch work under `tmp/`, which is ignored by Git.

## Automation Script Rules

- Prefer portable shell or Python scripts unless the project already uses another stack.
- Scripts should be idempotent when practical: running twice should not damage existing work.
- Scripts must not print secrets or traverse broad personal folders by default.
- Put reusable scripts in `scripts/`.
- Include a short usage message for scripts that take arguments.

## Test and Verification Rules

- Run the smallest useful verification after each change.
- For shell scripts, run `sh -n` or an equivalent syntax check.
- For Python scripts, run `python3 -m py_compile` when applicable.
- For Git changes, run `git status --short --branch`.

## Preferred Work Style

- Be practical and brief.
- Automatically handle safe setup and cleanup.
- Stop and ask only for risky operations: deletion, broad filesystem access, system config edits, external installs, secret handling, or Git history changes.
- Provide copy-paste commands only when the user needs to run something manually.
