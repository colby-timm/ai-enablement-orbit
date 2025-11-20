# Implementation Tasks

## Prerequisites

- [x] Verify `implement-cosmos-repository-containers` change is complete
- [x] Verify `implement-connection-string-auth` change is complete
- [x] Verify `add-cli-boilerplate` change is complete
- [x] Review Typer command group documentation
- [x] Review Rich table formatting documentation

## Container Commands Module

- [x] Create `orbit/commands/__init__.py` (if doesn't exist)
- [x] Create `orbit/commands/containers.py` file
- [x] Import Typer and create `containers_app = typer.Typer(help="Manage Cosmos DB containers")`
- [x] Import `CosmosContainerRepository` from repositories
- [x] Import `OutputAdapter` from `orbit.output`
- [x] Import `require_confirmation` from `orbit.confirmation`
- [x] Import `context_state` from `orbit.cli`
- [x] Import domain exceptions from `orbit.exceptions`

## List Containers Command

- [x] Implement `list_containers()` command function
- [x] Add `@containers_app.command("list")` decorator
- [x] Add docstring: "List all containers in the database."
- [x] Get repository instance (TODO: wire from factory/DI in future change)
- [x] Call `repository.list_containers()`
- [x] Handle `CosmosConnectionError` with user-friendly message
- [x] Handle `CosmosResourceNotFoundError` (database doesn't exist)
- [x] For Rich output:
  - [x] Create Rich `Table` with columns: "Name", "Partition Key", "Throughput (RU/s)"
  - [x] Add row for each container with formatted data
  - [x] Use `console.print(table)` from `context_state.output`
- [x] For JSON output:
  - [x] Create dict: `{"containers": [{"name": ..., "partition_key": ..., "throughput": ...}]}`
  - [x] Use `context_state.output.render(data)`
- [x] Handle empty list gracefully (show "No containers found" or empty table)
- [x] Ensure function length < 20 lines (extract helpers if needed)

## Create Container Command

- [x] Implement `create_container(name: str, partition_key: str, throughput: int = 400)` function
- [x] Add `@containers_app.command("create")` decorator
- [x] Add `name` as positional argument with help text
- [x] Add `--partition-key` as required option: `typer.Option(..., help="Partition key path (e.g., /id)")`
- [x] Add `--throughput` as optional int: `typer.Option(400, help="Throughput in RU/s (default: 400)")`
- [x] Add docstring: "Create a new container with the specified partition key."
- [x] Validate partition key starts with `/`:
  - [x] If invalid, raise `typer.BadParameter("Partition key must start with '/', e.g., /id")`
- [x] Validate container name (alphanumeric, hyphens, max 255 chars)
- [x] Get repository instance
- [x] Call `repository.create_container(name, partition_key, throughput)`
- [x] Handle `CosmosResourceExistsError`:
  - [x] Show error: "Container 'NAME' already exists. Use 'orbit containers list' to see existing containers."
  - [x] Exit with code 1
- [x] Handle `CosmosQuotaExceededError`:
  - [x] Show error: "Throughput quota exceeded. Reduce --throughput value or check account limits."
  - [x] Exit with code 1
- [x] Handle `CosmosInvalidPartitionKeyError`:
  - [x] Show error with actionable message
  - [x] Exit with code 1
- [x] Handle `CosmosConnectionError`:
  - [x] Show error: "Failed to connect to Cosmos DB. Check connection string."
  - [x] Exit with code 1
- [x] For Rich output:
  - [x] Show success message: "Created container 'NAME' with partition key 'KEY' (THROUGHPUT RU/s)"
  - [x] Use Rich formatting for emphasis
- [x] For JSON output:
  - [x] Return: `{"container": {"name": ..., "partition_key": ..., "throughput": ...}}`
- [x] Ensure function length < 20 lines (extract validation helpers)

## Delete Container Command

- [x] Implement `delete_container(name: str)` function
- [x] Add `@containers_app.command("delete")` decorator
- [x] Add `name` as positional argument with help text
- [x] Add docstring: "Delete a container. Requires confirmation unless --yes is provided."
- [x] Build confirmation message: f"Delete container '{name}'? This cannot be undone."
- [x] Call `require_confirmation(message)` (respects `--yes` flag)
- [x] Get repository instance
- [x] Call `repository.delete_container(name)`
- [x] Handle `CosmosConnectionError`:
  - [x] Show error: "Failed to connect to Cosmos DB. Check connection string."
  - [x] Exit with code 1
- [x] For Rich output:
  - [x] Show success: "Deleted container 'NAME'"
  - [x] Use Rich formatting
- [x] For JSON output:
  - [x] Return: `{"status": "deleted", "container": "NAME"}`
- [x] Ensure function length < 20 lines

## CLI Integration

- [x] Open `orbit/cli.py`
- [x] Import containers command app: `from .commands.containers import containers_app`
- [x] Register command group: `app.add_typer(containers_app, name="containers")`
- [x] Verify registration after `app = typer.Typer(...)` line
- [x] Update CLI help text if needed

## Testing - List Command

- [x] Create `tests/test_containers_commands.py`
- [x] Import necessary mocks and fixtures
- [x] Mock `CosmosContainerRepository` for all tests
- [x] Test `list` returns empty table when no containers
- [x] Test `list` displays multiple containers in Rich table format
- [x] Test `list` returns JSON when `--json` flag set
- [x] Test `list` handles `CosmosConnectionError` with proper message
- [x] Test `list` handles `CosmosResourceNotFoundError` (database missing)
- [x] Use `CliRunner` to invoke commands
- [x] Verify output format matches expected Rich table or JSON structure

## Testing - Create Command

- [x] Test `create` succeeds with valid inputs
- [x] Test `create` validates partition key starts with `/`
- [x] Test `create` rejects invalid partition key format
- [x] Test `create` uses default throughput (400 RU/s) when not specified
- [x] Test `create` uses custom throughput when `--throughput` provided
- [x] Test `create` handles `CosmosResourceExistsError` with helpful message
- [x] Test `create` handles `CosmosQuotaExceededError` with helpful message
- [x] Test `create` handles `CosmosInvalidPartitionKeyError`
- [x] Test `create` handles `CosmosConnectionError`
- [x] Test `create` returns JSON format when `--json` flag set
- [x] Test `create` displays Rich formatted success message
- [x] Verify error messages are actionable and user-friendly

## Testing - Delete Command

- [x] Test `delete` requires confirmation by default
- [x] Test `delete` skips confirmation when `--yes` flag provided
- [x] Test `delete` aborts when user declines confirmation
- [x] Test `delete` succeeds when user confirms
- [x] Test `delete` handles `CosmosConnectionError`
- [x] Test `delete` is idempotent (no error for missing container)
- [x] Test `delete` returns JSON format when `--json` flag set
- [x] Test `delete` displays Rich formatted success message
- [x] Mock `require_confirmation` to simulate user responses

## Testing - Integration

- [x] Test command group registered in main app
- [x] Test `orbit containers --help` shows subcommands
- [x] Test global `--json` flag works with all commands
- [x] Test global `--yes` flag works with delete command
- [x] Verify no secrets in output or error messages
- [x] Use AAA pattern in all tests
- [x] Use descriptive test names: `test_should_<behavior>_when_<condition>`

## Code Quality

- [x] Run `ruff check orbit/commands/` and fix issues
- [x] Run `ruff format orbit/commands/` for formatting
- [x] Verify function length < 20 lines
- [x] Verify descriptive variable names (no abbreviations)
- [x] Ensure single responsibility per function
- [x] Verify 0-2 parameters per function
- [x] Add comprehensive docstrings with examples
- [x] Remove all TODO comments from implementation

## Manual Testing

- [x] Test `orbit containers list` with emulator
- [x] Test `orbit containers create test-container --partition-key /id`
- [x] Test `orbit containers create` with invalid partition key
- [x] Test `orbit containers create` duplicate container error
- [x] Test `orbit containers delete test-container` with confirmation
- [x] Test `orbit containers delete test-container --yes` skip confirmation
- [x] Test all commands with `--json` flag
- [x] Verify Rich table formatting is readable
- [x] Verify error messages are helpful

## Validation

- [x] Run full test suite: `pytest tests/ -v`
- [x] Verify coverage: `pytest --cov=orbit --cov-report=term-missing`
- [x] Ensure coverage ≥ 80%
- [x] Run `openspec validate add-container-management-commands --strict`
- [x] Fix any validation errors or warnings

## Completion Checklist

- [x] All tests passing
- [x] Coverage ≥ 80%
- [x] No ruff errors or warnings
- [x] No secrets in logs or output
- [x] OpenSpec validation passes
- [x] Manual testing completed
- [x] Ready for code review
