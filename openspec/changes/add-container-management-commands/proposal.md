# Change: Add Container Management CLI Commands

## Why

Users need to manage Cosmos DB containers directly from the CLI to create workspaces, provision resources, and manage database structure without switching to Azure Portal or SDK code. Currently, Orbit CLI has only boilerplate commands (`demo`) and lacks any container management capabilities. Container operations are foundational—developers must create containers with proper partition keys before performing any item CRUD operations. This change exposes the container repository layer through intuitive CLI commands following existing CLI patterns (global flags, Rich formatting, confirmation prompts).

## What Changes

- Add `orbit containers` command group to CLI
- Implement `orbit containers list` to display all containers in a database
- Implement `orbit containers create <name>` with required `--partition-key` flag
- Implement `orbit containers delete <name>` with confirmation prompt (unless `--yes`)
- Add optional `--throughput` flag to `create` command (default: 400 RU/s)
- Wire container commands to `CosmosContainerRepository` from repository layer
- Format output using Rich tables for human-readable display
- Support `--json` flag for machine-readable output
- Add proper error handling and user-friendly error messages
- Add comprehensive unit tests for all commands
- Maintain 80%+ test coverage

## Impact

- Affected specs:
  - ADDS new `cli-containers` capability for container management commands
- Affected code:
  - `orbit/cli.py`: Adds `containers` command group registration
  - `orbit/commands/containers.py`: NEW FILE - Container CLI commands
  - `tests/test_containers_commands.py`: NEW FILE - Container command tests
- **BREAKING**: None—adding new commands to existing CLI
- **DEPENDENCIES**: Requires `implement-cosmos-repository-containers` to be complete (provides `CosmosContainerRepository`)
- **ENABLES**: Users can now manage containers end-to-end from CLI before creating items

## Dependencies

- **Requires**: `implement-cosmos-repository-containers` (provides `CosmosContainerRepository` implementation)
- **Requires**: `implement-connection-string-auth` (provides authentication via connection string)
- **Requires**: `add-cli-boilerplate` (provides CLI framework, global flags, output adapter)
- **Enables**: End-to-end container management workflow
- **Blocks**: None—independent feature that can be used immediately

## Notes

- All commands require database name (from connection string or future config)
- `list` command displays: container name, partition key path, throughput (RU/s)
- `create` command validates partition key path format (must start with `/`)
- `delete` command shows confirmation: "Delete container 'CONTAINER_NAME'? This cannot be undone."
- Confirmation skipped when `--yes` flag provided
- Error messages must be actionable (e.g., "Container 'products' already exists. Use 'orbit containers list' to see existing containers.")
- No secrets logged or displayed in output
- Rich tables use proper column alignment and headers
- JSON output follows structure: `{"containers": [...]}` for list, `{"container": {...}}` for create
- Commands should fail fast with clear error messages for missing repository dependencies
