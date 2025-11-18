# Implementation Tasks

## Prerequisites

- [ ] Verify `implement-cosmos-repository-containers` change is complete
- [ ] Verify `implement-connection-string-auth` change is complete
- [ ] Verify `add-cli-boilerplate` change is complete
- [ ] Review Typer command group documentation
- [ ] Review Rich table formatting documentation

## Container Commands Module

- [ ] Create `orbit/commands/__init__.py` (if doesn't exist)
- [ ] Create `orbit/commands/containers.py` file
- [ ] Import Typer and create `containers_app = typer.Typer(help="Manage Cosmos DB containers")`
- [ ] Import `CosmosContainerRepository` from repositories
- [ ] Import `OutputAdapter` from `orbit.output`
- [ ] Import `require_confirmation` from `orbit.confirmation`
- [ ] Import `context_state` from `orbit.cli`
- [ ] Import domain exceptions from `orbit.exceptions`

## List Containers Command

- [ ] Implement `list_containers()` command function
- [ ] Add `@containers_app.command("list")` decorator
- [ ] Add docstring: "List all containers in the database."
- [ ] Get repository instance (TODO: wire from factory/DI in future change)
- [ ] Call `repository.list_containers()`
- [ ] Handle `CosmosConnectionError` with user-friendly message
- [ ] Handle `CosmosResourceNotFoundError` (database doesn't exist)
- [ ] For Rich output:
  - [ ] Create Rich `Table` with columns: "Name", "Partition Key", "Throughput (RU/s)"
  - [ ] Add row for each container with formatted data
  - [ ] Use `console.print(table)` from `context_state.output`
- [ ] For JSON output:
  - [ ] Create dict: `{"containers": [{"name": ..., "partition_key": ..., "throughput": ...}]}`
  - [ ] Use `context_state.output.render(data)`
- [ ] Handle empty list gracefully (show "No containers found" or empty table)
- [ ] Ensure function length < 20 lines (extract helpers if needed)

## Create Container Command

- [ ] Implement `create_container(name: str, partition_key: str, throughput: int = 400)` function
- [ ] Add `@containers_app.command("create")` decorator
- [ ] Add `name` as positional argument with help text
- [ ] Add `--partition-key` as required option: `typer.Option(..., help="Partition key path (e.g., /id)")`
- [ ] Add `--throughput` as optional int: `typer.Option(400, help="Throughput in RU/s (default: 400)")`
- [ ] Add docstring: "Create a new container with the specified partition key."
- [ ] Validate partition key starts with `/`:
  - [ ] If invalid, raise `typer.BadParameter("Partition key must start with '/', e.g., /id")`
- [ ] Validate container name (alphanumeric, hyphens, max 255 chars)
- [ ] Get repository instance
- [ ] Call `repository.create_container(name, partition_key, throughput)`
- [ ] Handle `CosmosResourceExistsError`:
  - [ ] Show error: "Container 'NAME' already exists. Use 'orbit containers list' to see existing containers."
  - [ ] Exit with code 1
- [ ] Handle `CosmosQuotaExceededError`:
  - [ ] Show error: "Throughput quota exceeded. Reduce --throughput value or check account limits."
  - [ ] Exit with code 1
- [ ] Handle `CosmosInvalidPartitionKeyError`:
  - [ ] Show error with actionable message
  - [ ] Exit with code 1
- [ ] Handle `CosmosConnectionError`:
  - [ ] Show error: "Failed to connect to Cosmos DB. Check connection string."
  - [ ] Exit with code 1
- [ ] For Rich output:
  - [ ] Show success message: "Created container 'NAME' with partition key 'KEY' (THROUGHPUT RU/s)"
  - [ ] Use Rich formatting for emphasis
- [ ] For JSON output:
  - [ ] Return: `{"container": {"name": ..., "partition_key": ..., "throughput": ...}}`
- [ ] Ensure function length < 20 lines (extract validation helpers)

## Delete Container Command

- [ ] Implement `delete_container(name: str)` function
- [ ] Add `@containers_app.command("delete")` decorator
- [ ] Add `name` as positional argument with help text
- [ ] Add docstring: "Delete a container. Requires confirmation unless --yes is provided."
- [ ] Build confirmation message: f"Delete container '{name}'? This cannot be undone."
- [ ] Call `require_confirmation(message)` (respects `--yes` flag)
- [ ] Get repository instance
- [ ] Call `repository.delete_container(name)`
- [ ] Handle `CosmosConnectionError`:
  - [ ] Show error: "Failed to connect to Cosmos DB. Check connection string."
  - [ ] Exit with code 1
- [ ] For Rich output:
  - [ ] Show success: "Deleted container 'NAME'"
  - [ ] Use Rich formatting
- [ ] For JSON output:
  - [ ] Return: `{"status": "deleted", "container": "NAME"}`
- [ ] Ensure function length < 20 lines

## CLI Integration

- [ ] Open `orbit/cli.py`
- [ ] Import containers command app: `from .commands.containers import containers_app`
- [ ] Register command group: `app.add_typer(containers_app, name="containers")`
- [ ] Verify registration after `app = typer.Typer(...)` line
- [ ] Update CLI help text if needed

## Testing - List Command

- [ ] Create `tests/test_containers_commands.py`
- [ ] Import necessary mocks and fixtures
- [ ] Mock `CosmosContainerRepository` for all tests
- [ ] Test `list` returns empty table when no containers
- [ ] Test `list` displays multiple containers in Rich table format
- [ ] Test `list` returns JSON when `--json` flag set
- [ ] Test `list` handles `CosmosConnectionError` with proper message
- [ ] Test `list` handles `CosmosResourceNotFoundError` (database missing)
- [ ] Use `CliRunner` to invoke commands
- [ ] Verify output format matches expected Rich table or JSON structure

## Testing - Create Command

- [ ] Test `create` succeeds with valid inputs
- [ ] Test `create` validates partition key starts with `/`
- [ ] Test `create` rejects invalid partition key format
- [ ] Test `create` uses default throughput (400 RU/s) when not specified
- [ ] Test `create` uses custom throughput when `--throughput` provided
- [ ] Test `create` handles `CosmosResourceExistsError` with helpful message
- [ ] Test `create` handles `CosmosQuotaExceededError` with helpful message
- [ ] Test `create` handles `CosmosInvalidPartitionKeyError`
- [ ] Test `create` handles `CosmosConnectionError`
- [ ] Test `create` returns JSON format when `--json` flag set
- [ ] Test `create` displays Rich formatted success message
- [ ] Verify error messages are actionable and user-friendly

## Testing - Delete Command

- [ ] Test `delete` requires confirmation by default
- [ ] Test `delete` skips confirmation when `--yes` flag provided
- [ ] Test `delete` aborts when user declines confirmation
- [ ] Test `delete` succeeds when user confirms
- [ ] Test `delete` handles `CosmosConnectionError`
- [ ] Test `delete` is idempotent (no error for missing container)
- [ ] Test `delete` returns JSON format when `--json` flag set
- [ ] Test `delete` displays Rich formatted success message
- [ ] Mock `require_confirmation` to simulate user responses

## Testing - Integration

- [ ] Test command group registered in main app
- [ ] Test `orbit containers --help` shows subcommands
- [ ] Test global `--json` flag works with all commands
- [ ] Test global `--yes` flag works with delete command
- [ ] Verify no secrets in output or error messages
- [ ] Use AAA pattern in all tests
- [ ] Use descriptive test names: `test_should_<behavior>_when_<condition>`

## Code Quality

- [ ] Run `ruff check orbit/commands/` and fix issues
- [ ] Run `ruff format orbit/commands/` for formatting
- [ ] Verify function length < 20 lines
- [ ] Verify descriptive variable names (no abbreviations)
- [ ] Ensure single responsibility per function
- [ ] Verify 0-2 parameters per function
- [ ] Add comprehensive docstrings with examples
- [ ] Remove all TODO comments from implementation

## Manual Testing

- [ ] Test `orbit containers list` with emulator
- [ ] Test `orbit containers create test-container --partition-key /id`
- [ ] Test `orbit containers create` with invalid partition key
- [ ] Test `orbit containers create` duplicate container error
- [ ] Test `orbit containers delete test-container` with confirmation
- [ ] Test `orbit containers delete test-container --yes` skip confirmation
- [ ] Test all commands with `--json` flag
- [ ] Verify Rich table formatting is readable
- [ ] Verify error messages are helpful

## Validation

- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Verify coverage: `pytest --cov=orbit --cov-report=term-missing`
- [ ] Ensure coverage ≥ 80%
- [ ] Run `openspec validate add-container-management-commands --strict`
- [ ] Fix any validation errors or warnings

## Completion Checklist

- [ ] All tests passing
- [ ] Coverage ≥ 80%
- [ ] No ruff errors or warnings
- [ ] No secrets in logs or output
- [ ] OpenSpec validation passes
- [ ] Manual testing completed
- [ ] Ready for code review
