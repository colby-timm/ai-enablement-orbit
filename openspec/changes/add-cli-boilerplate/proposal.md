# Change: Initialize CLI Boilerplate

## Why
Developers need a structured, type-safe CLI foundation for Orbit before feature-specific work can proceed. Establishing the boilerplate now ensures consistent architecture (repository, factory, strategy, adapter patterns), testability, and compliance with conventions (no secret exposure, confirmation on writes, Rich formatting, Typer ergonomics).

## What Changes
- Scaffold initial Python package structure (`orbit/`) with Typer entrypoint and minimal commands
- ADDED capability: `cli-core` for core CLI behaviors (startup, global options, output formatting, confirmation flows)
- Introduce authentication strategies (connection string, managed identity) abstractions without full implementation logic (placeholders with TODO markers)
- Create repository abstraction interface for Cosmos operations (no concrete implementation yet)
- Define domain models skeleton using Pydantic (placeholder item model + validation base)
- Define custom exception classes (e.g., `CosmosConnectionError`, `CosmosAuthError`)
- Implement confirmation pattern for write operations respecting `--yes` flag (stub)
- Add output formatting adapter using Rich + optional `--json` flag handling (stub)
- Provide environment variable resolution utilities (without printing secrets)
- Add initial test scaffolding to enforce structure and prevent regression (≥ minimal placeholder to grow to 80% later)
- Add ruff config invocation expectation (no config file change yet) and formatting docs
- Emulator support placeholder (detect localhost endpoint, TODO for future container management)
- Plan introduction of a root `Makefile` (not yet added) with targets: `venv`, `install`, `run`, `test`, `lint`, `format`, `spec-validate`, `clean`, `distclean`, `help` to standardize developer workflow; file will be created only after proposal approval.
- **BREAKING (Foundational)**: Establishes architectural contracts other future changes must follow

## Impact

- Affected specs: new `cli-core` capability added
- Affected code: introduces `orbit/` package; future commands will depend on established interfaces
- Enables subsequent feature changes (CRUD, queries, pagination) to hook into consistent auth, repository, and output layers
- No runtime behavioral change for existing systems (project currently empty) but sets mandatory patterns

## Notes

- All concrete Cosmos calls deferred; placeholders marked with `TODO:` to avoid assumptions
- Unit tests will focus on structural presence and flag behaviors (no external calls)
- Makefile intentionally deferred until approval to align with OpenSpec process (removed if previously added during drafting).
