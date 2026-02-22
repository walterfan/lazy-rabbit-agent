# AI usage guide

This Project Knowledge Pack is intended for both humans and AI assistants.

## How to use this doc set

1. **Locate**: Use 01-repo-map and directory structure to find entry points and key files.
2. **Understand**: Read 00-overview and 02-architecture for purpose, boundaries, and call chains.
3. **Execute**: Use 06-runbook for setup, run, test, and migrate commands.
4. **Verify**: Use 07-testing for test commands and critical paths.

## Conventions in this repo

- **Paths**: Backend code under `backend/app/`; frontend under `frontend/src/`. Secretary agent under `backend/app/services/secretary_agent/`.
- **Specs**: `openspec/specs/` (e.g. personal-secretary-agent); changes in `openspec/changes/`.
- **One-pager**: `docs/PROJECT-KNOWLEDGE-PACK.md` for a single-page cheat sheet.

## Feeding project context to an AI

- Prefer referring to this index and specific numbered docs (00–07) rather than pasting large code blocks.
- For changes, use OpenSpec workflow and `openspec/changes/`; see `.cursor/skills/openspec-*` skills if available.
