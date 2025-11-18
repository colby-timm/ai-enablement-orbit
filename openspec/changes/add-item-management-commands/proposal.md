# Change: Add Item Management CLI Commands

## Why

Users need to perform CRUD operations on items within Cosmos DB containers directly from the CLI to manage data without writing custom code or switching to Azure Portal. Currently, Orbit CLI has container management (`orbit containers`) but lacks item-level operations. Item management is essential for developers to create documents, read data, update records, and delete items with proper partition key handling. This change exposes the item repository layer through intuitive CLI commands following existing CLI patterns (global flags, Rich formatting, JSON file input/output, confirmation prompts). Without these commands, developers cannot interact with actual data stored in containers, limiting Orbit to structure management only.

## What Changes

- Add `orbit items` command group to CLI
- Implement `orbit items create <container> --data <json-file>` to insert items from JSON files
- Implement `orbit items get <container> <item-id> --partition-key <value>` to retrieve single items
- Implement `orbit items update <container> <item-id> --data <json-file>` with upsert behavior
- Implement `orbit items delete <container> <item-id> --partition-key <value>` with confirmation prompt (unless `--yes`)
- Add `orbit items list <container>` to display all items in a container with pagination
- Support `--partition-key` flag for create, get, update, delete commands (required for single-item operations)
- Support `--data` flag for create/update accepting JSON file paths or stdin (`-`)
- Support `--max-count` flag for list command (default: 100 items)
- Format output using Rich tables and JSON pretty-printing for human-readable display
- Support `--json` flag for machine-readable output
- Wire item commands to `CosmosItemRepository` from repository layer
- Add proper error handling for partition key mismatches, item not found, and file parsing errors
- Add comprehensive unit tests for all commands
- Maintain 80%+ test coverage

## Impact

- Affected specs:
  - ADDS new `cli-items` capability for item management commands
- Affected code:
  - `orbit/cli.py`: Adds `items` command group registration
  - `orbit/commands/items.py`: NEW FILE - Item CLI commands
  - `tests/test_items_commands.py`: NEW FILE - Item command tests
- **BREAKING**: None—adding new commands to existing CLI
- **DEPENDENCIES**: Requires `implement-cosmos-repository-items` to be complete (provides item CRUD repository)
- **ENABLES**: End-to-end data manipulation workflow from CLI

## Dependencies

- **Requires**: `implement-cosmos-repository-items` (provides `CosmosItemRepository` implementation with CRUD methods)
- **Requires**: `implement-connection-string-auth` (provides authentication via connection string)
- **Requires**: `add-cli-boilerplate` (provides CLI framework, global flags, output adapter)
- **Requires**: `add-container-management-commands` (users must create containers before adding items)
- **Enables**: Complete CRUD workflow for Cosmos DB data management from CLI
- **Blocks**: None—independent feature that can be used immediately once dependencies are met

## Notes

- All commands require database name (from connection string or future config)
- Item operations require partition key value (from `--partition-key` flag)
- `create` and `update` commands accept JSON files via `--data` flag (path or `-` for stdin)
- `get` command outputs item as formatted JSON
- `list` command displays items in Rich table format (truncates long values) or JSON array
- `delete` command shows confirmation: "Delete item 'ITEM_ID' from container 'CONTAINER'? This cannot be undone."
- Confirmation skipped when `--yes` flag provided
- Item ID must be present in JSON data for create/update operations
- Partition key value must match the value in item's partition key field
- Error messages must be actionable (e.g., "Item 'item123' not found in container 'products'. Check item ID and partition key.")
- No secrets or sensitive item content logged or displayed in error messages
- JSON input files must contain valid JSON objects (single item, not arrays)
- Rich table output for `list` command shows key columns: id, partition key field, other fields (truncated)
- JSON output follows structure: `{"item": {...}}` for single items, `{"items": [...]}` for lists
- Commands should fail fast with clear error messages for missing repository dependencies
- File I/O errors (missing file, invalid JSON) should have clear error messages with file path
