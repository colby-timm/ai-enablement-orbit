# Specification: Item Management CLI Commands

## Overview

Provides CLI commands for managing items (documents) in Cosmos DB containers through Orbit. Exposes item CRUD operations (create, get, update, delete, list) with JSON file input/output support, partition key handling, Rich formatted output, and confirmation prompts following Orbit CLI conventions.

## ADDED Requirements

### Requirement: Item Create Command with JSON File Input

The system SHALL provide an `items create` command that creates new items in containers from JSON file input with partition key validation, handling file I/O errors and duplicate item conflicts gracefully.

**Details**:

- Command: `orbit items create <container> --data <file-path> --partition-key <value>`
- Required: container name (positional), data file path (--data flag), partition key value (--partition-key flag)
- File format: JSON file containing single item object (not array)
- Special case: `--data -` reads from stdin
- Validation: Item must have 'id' field, partition key value must match item's partition key field
- Success output: Rich formatted message with JSON item display or JSON object
- Error handling: File not found, invalid JSON, duplicate item, partition key mismatch, container not found

#### Scenario: Create item from JSON file with valid data

- **GIVEN** a container "products" exists with partition key "/category"
- **AND** a file "product.json" contains: `{"id": "prod123", "category": "electronics", "name": "Laptop"}`
- **WHEN** user runs `orbit items create products --data product.json --partition-key electronics`
- **THEN** item is created in container "products"
- **AND** output shows: "Created item 'prod123' in container 'products'"
- **AND** item JSON is displayed with Rich formatting

#### Scenario: Create item from stdin with dash syntax

- **GIVEN** a container "products" exists
- **WHEN** user runs `echo '{"id": "prod456", "category": "books", "name": "Novel"}' | orbit items create products --data - --partition-key books`
- **THEN** item is created from stdin data
- **AND** output confirms creation

#### Scenario: Create item with JSON output mode

- **GIVEN** valid container and item data
- **WHEN** user runs `orbit items create products --data product.json --partition-key electronics --json`
- **THEN** output is valid JSON: `{"status": "created", "item": {"id": "prod123", ...}}`

#### Scenario: Create item fails when JSON file not found

- **GIVEN** file "missing.json" does not exist
- **WHEN** user runs `orbit items create products --data missing.json --partition-key electronics`
- **THEN** command exits with error: "File not found: missing.json" and exit code 1

#### Scenario: Create item fails when JSON is invalid

- **GIVEN** file "bad.json" contains invalid JSON: `{"id": "prod123", "name":}`
- **WHEN** user runs `orbit items create products --data bad.json --partition-key electronics`
- **THEN** command exits with error: "Invalid JSON in file: bad.json" and exit code 1

#### Scenario: Create item fails when id field missing

- **GIVEN** file "no-id.json" contains: `{"category": "electronics", "name": "Laptop"}`
- **WHEN** user runs `orbit items create products --data no-id.json --partition-key electronics`
- **THEN** command exits with error: "Item must have 'id' field" and exit code 1

#### Scenario: Create item handles duplicate ID error

- **GIVEN** container "products" already has item with ID "prod123" in partition "electronics"
- **WHEN** user runs `orbit items create products --data product.json --partition-key electronics`
- **THEN** command exits with error: "Item 'prod123' already exists in container 'products'" and exit code 1

#### Scenario: Create item handles partition key mismatch

- **GIVEN** file contains: `{"id": "prod123", "category": "electronics"}`
- **WHEN** user runs `orbit items create products --data product.json --partition-key books` (wrong partition key)
- **THEN** command exits with error: "Partition key mismatch: item has 'electronics' but 'books' was provided" and exit code 1

#### Scenario: Create item handles container not found

- **GIVEN** container "missing" does not exist
- **WHEN** user runs `orbit items create missing --data product.json --partition-key electronics`
- **THEN** command exits with error: "Container 'missing' not found" and exit code 1

---

### Requirement: Item Get Command with Partition Key

The system SHALL provide an `items get` command that retrieves a single item by ID and partition key value, displaying formatted JSON output and handling not found and partition key errors gracefully.

**Details**:

- Command: `orbit items get <container> <item-id> --partition-key <value>`
- Required: container name (positional), item ID (positional), partition key value (--partition-key flag)
- Success output: Rich formatted JSON display or JSON object
- Error handling: Item not found, partition key mismatch, container not found

#### Scenario: Get item with valid ID and partition key

- **GIVEN** container "products" has item ID "prod123" in partition "electronics"
- **WHEN** user runs `orbit items get products prod123 --partition-key electronics`
- **THEN** item is retrieved and displayed as formatted JSON
- **AND** all item fields are shown

#### Scenario: Get item with JSON output mode

- **GIVEN** container "products" has item ID "prod123"
- **WHEN** user runs `orbit items get products prod123 --partition-key electronics --json`
- **THEN** output is valid JSON: `{"item": {"id": "prod123", "category": "electronics", ...}}`

#### Scenario: Get item fails when item not found

- **GIVEN** container "products" has no item ID "missing"
- **WHEN** user runs `orbit items get products missing --partition-key electronics`
- **THEN** command exits with error: "Item 'missing' not found in container 'products'" and exit code 1

#### Scenario: Get item fails when partition key wrong

- **GIVEN** container "products" has item ID "prod123" in partition "electronics"
- **WHEN** user runs `orbit items get products prod123 --partition-key books` (wrong partition key)
- **THEN** command exits with error: "Item 'prod123' not found with partition key 'books'" and exit code 1

#### Scenario: Get item handles container not found

- **GIVEN** container "missing" does not exist
- **WHEN** user runs `orbit items get missing prod123 --partition-key electronics`
- **THEN** command exits with error: "Container 'missing' not found" and exit code 1

---

### Requirement: Item Update Command with Upsert Behavior

The system SHALL provide an `items update` command that updates existing items or creates them if they don't exist (upsert), reading from JSON files with partition key validation and ID consistency checks.

**Details**:

- Command: `orbit items update <container> <item-id> --data <file-path> --partition-key <value>`
- Required: container name, item ID, data file path (--data flag), partition key value (--partition-key flag)
- Behavior: Upsert (create if not exists, replace if exists)
- Validation: Item ID in JSON must match command parameter, partition key must match
- Success output: Rich formatted message with updated item JSON or JSON object
- Error handling: File I/O errors, ID mismatch, partition key mismatch

#### Scenario: Update existing item successfully

- **GIVEN** container "products" has item ID "prod123" in partition "electronics"
- **AND** file "updated.json" contains: `{"id": "prod123", "category": "electronics", "name": "Updated Laptop", "price": 1200}`
- **WHEN** user runs `orbit items update products prod123 --data updated.json --partition-key electronics`
- **THEN** item "prod123" is updated with new data
- **AND** output shows: "Updated item 'prod123' in container 'products'"
- **AND** updated item JSON is displayed

#### Scenario: Update creates item when not exists (upsert)

- **GIVEN** container "products" has no item ID "new123"
- **AND** file "new.json" contains: `{"id": "new123", "category": "electronics", "name": "New Item"}`
- **WHEN** user runs `orbit items update products new123 --data new.json --partition-key electronics`
- **THEN** new item "new123" is created
- **AND** output shows: "Updated item 'new123' in container 'products'"

#### Scenario: Update from stdin with dash syntax

- **GIVEN** container "products" has item ID "prod123"
- **WHEN** user runs `echo '{"id": "prod123", "category": "electronics", "name": "Updated"}' | orbit items update products prod123 --data - --partition-key electronics`
- **THEN** item is updated from stdin data

#### Scenario: Update with JSON output mode

- **GIVEN** valid container and item data
- **WHEN** user runs `orbit items update products prod123 --data updated.json --partition-key electronics --json`
- **THEN** output is valid JSON: `{"status": "updated", "item": {"id": "prod123", ...}}`

#### Scenario: Update fails when item ID in JSON doesn't match parameter

- **GIVEN** command specifies item ID "prod123"
- **AND** file contains: `{"id": "prod456", "category": "electronics"}`
- **WHEN** user runs `orbit items update products prod123 --data updated.json --partition-key electronics`
- **THEN** command exits with error: "Item ID in JSON must match command parameter" and exit code 1

#### Scenario: Update fails when partition key mismatch

- **GIVEN** file contains: `{"id": "prod123", "category": "electronics"}`
- **WHEN** user runs `orbit items update products prod123 --data updated.json --partition-key books` (wrong partition key)
- **THEN** command exits with error: "Partition key mismatch: item has 'electronics' but 'books' was provided" and exit code 1

#### Scenario: Update handles JSON file not found

- **GIVEN** file "missing.json" does not exist
- **WHEN** user runs `orbit items update products prod123 --data missing.json --partition-key electronics`
- **THEN** command exits with error: "File not found: missing.json" and exit code 1

---

### Requirement: Item Delete Command with Confirmation Prompt

The system SHALL provide an `items delete` command that removes items by ID and partition key with confirmation prompts (unless `--yes` flag is provided) to prevent accidental data loss, treating deletion as idempotent.

**Details**:

- Command: `orbit items delete <container> <item-id> --partition-key <value>`
- Required: container name, item ID, partition key value (--partition-key flag)
- Confirmation prompt: "Delete item 'ITEM_ID' from container 'CONTAINER'? This cannot be undone." (unless `--yes` flag)
- Idempotent: No error if item doesn't exist
- Success output: Rich formatted message or JSON object
- Global `--yes` flag skips confirmation

#### Scenario: Delete item with confirmation

- **GIVEN** container "products" has item ID "prod123" in partition "electronics"
- **WHEN** user runs `orbit items delete products prod123 --partition-key electronics` and confirms prompt
- **THEN** item "prod123" is deleted
- **AND** output shows: "Deleted item 'prod123' from container 'products'"

#### Scenario: Delete item skips confirmation with --yes flag

- **GIVEN** container "products" has item ID "prod123"
- **WHEN** user runs `orbit items delete products prod123 --partition-key electronics --yes`
- **THEN** item is deleted without prompting
- **AND** output confirms deletion

#### Scenario: Delete item aborts when user declines

- **GIVEN** container "products" has item ID "prod123"
- **WHEN** user runs `orbit items delete products prod123 --partition-key electronics` and declines confirmation
- **THEN** item "prod123" is NOT deleted
- **AND** output shows: "Aborted by user."
- **AND** command exits with code 1

#### Scenario: Delete item is idempotent when item doesn't exist

- **GIVEN** container "products" has no item ID "missing"
- **WHEN** user runs `orbit items delete products missing --partition-key electronics --yes`
- **THEN** command succeeds without error
- **AND** output shows: "Deleted item 'missing' from container 'products'"

#### Scenario: Delete item with JSON output mode

- **GIVEN** container "products" has item ID "prod123"
- **WHEN** user runs `orbit items delete products prod123 --partition-key electronics --yes --json`
- **THEN** output is valid JSON: `{"status": "deleted", "item_id": "prod123", "container": "products"}`

#### Scenario: Delete item handles container not found

- **GIVEN** container "missing" does not exist
- **WHEN** user runs `orbit items delete missing prod123 --partition-key electronics --yes`
- **THEN** command exits with error: "Container 'missing' not found" and exit code 1

---

### Requirement: Item List Command with Pagination

The system SHALL provide an `items list` command that displays all items in a container with pagination support, formatting output in Rich tables (human-readable) or JSON (machine-readable) with configurable item limits.

**Details**:

- Command: `orbit items list <container> [--max-count <N>]`
- Required: container name (positional)
- Optional: max count (--max-count flag, default: 100)
- Output format: Rich table (default) or JSON (with `--json` flag)
- Table columns: id, partition key field, other fields (dynamically determined)
- Truncation: Long values (> 50 chars) truncated with "..."
- Empty state: Shows "No items found in container 'CONTAINER'" or empty list

#### Scenario: List items in Rich table format

- **GIVEN** container "products" has 3 items
- **WHEN** user runs `orbit items list products`
- **THEN** output shows Rich table with columns for item keys (id, category, name, etc.)
- **AND** each item is a table row
- **AND** long values are truncated with "..."

#### Scenario: List items in JSON format

- **GIVEN** container "products" has 2 items
- **WHEN** user runs `orbit items list products --json`
- **THEN** output is valid JSON: `{"items": [{"id": "prod1", ...}, {"id": "prod2", ...}], "count": 2}`

#### Scenario: List items with custom max count

- **GIVEN** container "products" has 200 items
- **WHEN** user runs `orbit items list products --max-count 50`
- **THEN** at most 50 items are returned
- **AND** items are from first page of results

#### Scenario: List items when container is empty

- **GIVEN** container "products" has no items
- **WHEN** user runs `orbit items list products`
- **THEN** output shows "No items found in container 'products'"
- **AND** JSON mode returns: `{"items": [], "count": 0}`

#### Scenario: List items handles container not found

- **GIVEN** container "missing" does not exist
- **WHEN** user runs `orbit items list missing`
- **THEN** command exits with error: "Container 'missing' not found" and exit code 1

#### Scenario: List items truncates long values in table

- **GIVEN** container "products" has item with field "description" containing 100 characters
- **WHEN** user runs `orbit items list products`
- **THEN** description field is displayed as first 47 chars + "..."

---

### Requirement: Output Format Consistency

All item commands SHALL support both Rich formatted (human-readable) and JSON (machine-readable) output modes activated via the global `--json` flag, with consistent structure across commands.

**Details**:

- Default: Rich formatted text with JSON syntax highlighting for items
- JSON mode: Activated with global `--json` flag
- JSON structure: Consistent keys across commands (status, item, items, count)
- No secrets: Connection strings never appear in output

#### Scenario: Rich output uses JSON syntax highlighting for items

- **GIVEN** any item command that outputs item data (create, get, update)
- **WHEN** command executes in default Rich mode
- **THEN** item JSON is displayed with syntax highlighting (colors for keys, values, strings)

#### Scenario: JSON output is valid and parseable

- **GIVEN** any item command with `--json` flag
- **WHEN** command executes successfully
- **THEN** output is valid JSON that can be parsed by `jq` or other tools

#### Scenario: No secrets in output

- **GIVEN** any item command (create, get, update, delete, list)
- **WHEN** command outputs results or errors
- **THEN** connection strings, keys, and sensitive credentials are never displayed

---

### Requirement: Error Handling and User Guidance

All error messages SHALL be actionable and guide users toward resolution, including checking file paths, validating JSON syntax, confirming partition keys, and suggesting command corrections.

**Details**:

- File errors include full file path in message
- JSON errors mention file name and suggest validation
- Item not found errors suggest checking item ID and partition key
- Container not found errors suggest listing containers
- Partition key mismatch errors explain the inconsistency
- All errors exit with non-zero code

#### Scenario: File not found error includes file path

- **GIVEN** user specifies non-existent file
- **WHEN** create or update command runs
- **THEN** error message includes: "File not found: /path/to/missing.json"

#### Scenario: JSON parse error suggests validation

- **GIVEN** file contains invalid JSON
- **WHEN** create or update command runs
- **THEN** error message includes: "Invalid JSON in file: product.json" and suggests checking JSON syntax

#### Scenario: Item not found error is actionable

- **GIVEN** item doesn't exist
- **WHEN** get command runs
- **THEN** error message includes: "Item 'prod123' not found in container 'products'. Check item ID and partition key."

#### Scenario: Container not found suggests next action

- **GIVEN** container doesn't exist
- **WHEN** any item command runs
- **THEN** error message includes: "Container 'missing' not found. Use 'orbit containers list' to see existing containers."

#### Scenario: Partition key mismatch explains inconsistency

- **GIVEN** partition key value doesn't match item field
- **WHEN** create or update command runs
- **THEN** error message explains: "Partition key mismatch: item has 'electronics' but 'books' was provided"

---

### Requirement: JSON File Input Validation

Commands that accept JSON file input (create, update) SHALL validate file format, JSON syntax, and required fields before calling repository methods, providing clear error messages for common mistakes.

**Details**:

- Validate file exists before reading
- Validate JSON is parseable (not malformed)
- Validate JSON is object (not array, string, etc.)
- Validate 'id' field exists
- Validate item ID matches command parameter (update only)

#### Scenario: Validate JSON is object not array

- **GIVEN** file "items.json" contains: `[{"id": "prod1"}, {"id": "prod2"}]` (array)
- **WHEN** user runs `orbit items create products --data items.json --partition-key electronics`
- **THEN** command exits with error: "JSON must be a single object, not an array" and exit code 1

#### Scenario: Validate id field exists before repository call

- **GIVEN** file "no-id.json" contains: `{"name": "Laptop"}`
- **WHEN** user runs `orbit items create products --data no-id.json --partition-key electronics`
- **THEN** command exits with error before calling repository
- **AND** error message: "Item must have 'id' field"

## Dependencies

- Requires: `CosmosItemRepository` from `implement-cosmos-repository-items`
- Requires: `OutputAdapter` from `add-cli-boilerplate`
- Requires: `require_confirmation` from `add-cli-boilerplate`
- Requires: Authentication via `implement-connection-string-auth`
- Requires: `add-container-management-commands` (containers must exist before items)

## Non-Functional Requirements

- **Performance**: Commands complete within 2 seconds for typical operations (single item CRUD)
- **Performance**: List command may take longer for large datasets (paginated results)
- **Usability**: Error messages are beginner-friendly and actionable
- **Security**: No connection strings, keys, or sensitive item content logged or displayed in errors
- **Testability**: 80%+ code coverage with mocked repository layer and file I/O
- **Maintainability**: Functions < 30 lines, single responsibility principle
- **File I/O**: Support both file paths and stdin (`-`) for JSON input

## Future Considerations

- Query command with SQL-like syntax for advanced filtering
- Batch create/update operations (multiple items from array)
- Export command to save items to JSON files
- Item property inspection (detailed metadata, etag, timestamp)
- Pagination tokens for continuing list operations
- Interactive editor mode for create/update (launch editor with template)
- JSON schema validation for item structure
- Dry-run mode for create/update operations
