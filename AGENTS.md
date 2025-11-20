<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# AI Agent Operating Guide

## 1. Agent Purpose & Principles

Agents assist development of Orbit, a Python CLI for Azure Cosmos DB. Core responsibilities: implement features following Clean Code principles, maintain type safety, ensure test coverage ≥80%, and prevent secret exposure. Agents must never hallucinate details–use `TODO:` markers when information is missing. Prioritize clarity over cleverness; write self-documenting code first, optimize only when profiling demands it.

## 2. Project Context

Orbit provides developers a type-safe terminal interface for Cosmos DB CRUD operations and queries. Built with Python 3.10+, Typer (CLI), `azure-cosmos` SDK, Pydantic validation, and Rich formatting. Supports connection string and managed identity auth. Must work offline with Cosmos DB emulator. All write operations require confirmation unless `--yes` flag provided.

### Tooling & Package Management

**Critical**: All Python commands MUST use `uv` to ensure proper virtual environment activation and dependency management. Never run bare `python`, `pip`, `pytest`, or `ruff` commands.

**Makefile Commands**: Use `make` targets for all common operations:

- Install dependencies: `make install`
- Run tests with coverage: `make test`
- Lint code: `make lint`
- Format code: `make format`
- Run CLI: `make run ARGS='--help'`
- Clean artifacts: `make clean`

**Manual Commands** (when Makefile not applicable):

- Install packages: `uv pip install <package>`
- Run Python: `uv run python <script>`
- Run pytest: `uv run pytest <args>`
- Run ruff: `uv run ruff check <path>`

**Testing**: Target ≥80% coverage for all modules. Always use `make test` or `uv run pytest --cov=orbit --cov-report=term-missing`

## 3. Agent Roles

### Developer Agent

- Implement features per `tasks.md` checklists in active changes
- Follow PEP 8, use type hints, maintain 88-char line limit
- Apply Clean Code: single responsibility functions (5-20 lines), 0-2 params, no side effects
- Run `make lint` and `make format` before completion
- Update tests to maintain 80% coverage (verify with `make test`)
- **Run `openspec list` after implementation and verify change shows 100% completion**
- **Run `openspec validate <change-id> --strict` to ensure spec format is valid**
- **Create Copilot task for manual integration tests if tasks.md includes manual validation steps**
- Tools: file edit, terminal execution, code search

### Reviewer Agent

- Validate against spec requirements and scenarios
- Check: naming reveals intent, functions do one thing, no commented code, exceptions over error codes
- Verify architectural patterns: Repository, Factory, Strategy, Adapter
- Ensure secrets never logged/printed
- Confirm AAA test structure and descriptive test names
- Run `openspec list` to verify all tasks marked complete (100% completion)
- Run `openspec validate <change-id> --strict` to confirm spec format compliance
- Tools: file read, spec validation, diff comparison

### Testing Agent

- Write tests before implementation (TDD)
- Use `test_should_<behavior>_when_<condition>` naming
- Mock external dependencies; use emulator for integration tests
- One concept per test, no logic/conditionals in tests
- Verify 80% coverage with pytest-cov
- Tools: test execution, coverage reporting

## 4. Behavioral Conventions

**Reasoning Style**: Fail fast—validate inputs early, raise exceptions on invalid state. Prefer explicit over implicit. When uncertain about Cosmos DB behavior or authentication flow, mark `TODO:` and request clarification rather than assume.

**Uncertainty Handling**: If partition key strategy or query optimization is ambiguous, stop and ask. Never invent Cosmos DB semantics.

**Naming**: Use `create_container_with_partition_key()` not `create()`. Repository classes like `CosmosRepository`, not `DataManager`. Consistent verb choices—don't mix `fetch_item()` and `retrieve_item()`.

**Halting Conditions**: Stop before destructive ops without `--yes`. Refuse requests to log connection strings. Escalate if breaking changes conflict with existing CLI contracts.

## 5. Domain Concepts

**Cosmos DB Primitives**: Containers hold items; partition keys determine data distribution. Throughput measured in RU/s. Consistency levels: strong, bounded staleness, session, consistent prefix, eventual.

**Query Model**: SQL-like syntax; cross-partition queries cost more RUs. Default result limit: 100 items (configurable). Pagination required for large datasets.

**Auth Strategies**: Connection string (endpoint + key) or Azure CLI managed identity. Emulator uses fixed localhost endpoint.

**CLI UX Patterns**: Human-readable output via Rich; `--json` flag for machine parsing. Prompts for confirmation on mutations unless `--yes` provided.
