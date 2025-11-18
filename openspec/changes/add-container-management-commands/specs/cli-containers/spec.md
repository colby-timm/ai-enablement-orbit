# Specification: Container Management CLI Commands

## Overview

Provides CLI commands for managing Cosmos DB containers through Orbit. Exposes container lifecycle operations (list, create, delete) with Rich formatted output, JSON support, and confirmation prompts following Orbit CLI conventions.

## ADDED Requirements

### Requirement: Container List Command

The system SHALL provide a `containers list` command that displays all containers in the database with formatted output showing container name, partition key path, and throughput.

**Details**:

- Command: `orbit containers list`
- Displays: container name, partition key path, throughput (RU/s)
- Output format: Rich table (default) or JSON (with `--json` flag)
- Empty state: Shows "No containers found" or empty table
- Error handling: Connection errors show actionable messages

#### Scenario: List containers in Rich table format

- **GIVEN** a Cosmos DB database with containers "products" (/category, 400 RU/s) and "users" (/userId, 800 RU/s)
- **WHEN** user runs `orbit containers list`
- **THEN** output shows Rich table with columns "Name", "Partition Key", "Throughput (RU/s)" and two rows with container data

#### Scenario: List containers in JSON format

- **GIVEN** a database with container "products" (/category, 400 RU/s)
- **WHEN** user runs `orbit containers list --json`
- **THEN** output is valid JSON: `{"containers": [{"name": "products", "partition_key": "/category", "throughput": 400}]}`

#### Scenario: List containers when database is empty

- **GIVEN** a database with no containers
- **WHEN** user runs `orbit containers list`
- **THEN** output shows "No containers found" or empty Rich table

#### Scenario: List containers handles connection errors

- **GIVEN** invalid Cosmos DB connection string
- **WHEN** user runs `orbit containers list`
- **THEN** command exits with error: "Failed to connect to Cosmos DB. Check connection string." and exit code 1

---

### Requirement: Container Create Command

The system SHALL provide a `containers create` command that creates containers with specified partition keys and optional throughput configuration, validating inputs and providing clear error messages.

**Details**:

- Command: `orbit containers create <name> --partition-key <path> [--throughput <RUs>]`
- Required: container name (positional), partition key path (--partition-key flag)
- Optional: throughput in RU/s (--throughput flag, default: 400)
- Validation: partition key must start with `/`, name must be valid Cosmos DB identifier
- Success output: Rich formatted message or JSON object
- Error handling: Duplicate container, quota exceeded, invalid inputs

#### Scenario: Create container with default throughput

- **GIVEN** valid Cosmos DB connection
- **WHEN** user runs `orbit containers create products --partition-key /category`
- **THEN** container "products" is created with partition key "/category" and 400 RU/s throughput
- **AND** output shows: "Created container 'products' with partition key '/category' (400 RU/s)"

#### Scenario: Create container with custom throughput

- **GIVEN** valid Cosmos DB connection
- **WHEN** user runs `orbit containers create users --partition-key /userId --throughput 800`
- **THEN** container "users" is created with partition key "/userId" and 800 RU/s throughput

#### Scenario: Create container with JSON output

- **GIVEN** valid Cosmos DB connection
- **WHEN** user runs `orbit containers create products --partition-key /category --json`
- **THEN** output is valid JSON: `{"container": {"name": "products", "partition_key": "/category", "throughput": 400}}`

#### Scenario: Create container validates partition key format

- **GIVEN** valid Cosmos DB connection
- **WHEN** user runs `orbit containers create products --partition-key category` (missing leading `/`)
- **THEN** command exits with error: "Partition key must start with '/', e.g., /id" and exit code 1

#### Scenario: Create container handles duplicate names

- **GIVEN** container "products" already exists
- **WHEN** user runs `orbit containers create products --partition-key /category`
- **THEN** command exits with error: "Container 'products' already exists. Use 'orbit containers list' to see existing containers." and exit code 1

#### Scenario: Create container handles quota exceeded

- **GIVEN** Cosmos DB account at throughput limit
- **WHEN** user runs `orbit containers create products --partition-key /category --throughput 10000`
- **THEN** command exits with error: "Throughput quota exceeded. Reduce --throughput value or check account limits." and exit code 1

---

### Requirement: Container Delete Command

The system SHALL provide a `containers delete` command that removes containers with confirmation prompts (unless `--yes` flag is provided) to prevent accidental data loss.

**Details**:

- Command: `orbit containers delete <name>`
- Confirmation prompt: "Delete container 'NAME'? This cannot be undone." (unless `--yes` flag)
- Idempotent: No error if container doesn't exist
- Success output: Rich formatted message or JSON object
- Global `--yes` flag skips confirmation

#### Scenario: Delete container with confirmation

- **GIVEN** container "products" exists
- **WHEN** user runs `orbit containers delete products` and confirms prompt
- **THEN** container "products" is deleted
- **AND** output shows: "Deleted container 'products'"

#### Scenario: Delete container skips confirmation with --yes flag

- **GIVEN** container "products" exists
- **WHEN** user runs `orbit containers delete products --yes`
- **THEN** container "products" is deleted without prompting
- **AND** output shows: "Deleted container 'products'"

#### Scenario: Delete container aborts when user declines

- **GIVEN** container "products" exists
- **WHEN** user runs `orbit containers delete products` and declines confirmation
- **THEN** container "products" is NOT deleted
- **AND** output shows: "Aborted by user."
- **AND** command exits with code 1

#### Scenario: Delete container is idempotent

- **GIVEN** container "products" does not exist
- **WHEN** user runs `orbit containers delete products --yes`
- **THEN** command succeeds without error
- **AND** output shows: "Deleted container 'products'"

#### Scenario: Delete container with JSON output

- **GIVEN** container "products" exists
- **WHEN** user runs `orbit containers delete products --yes --json`
- **THEN** output is valid JSON: `{"status": "deleted", "container": "products"}`

#### Scenario: Delete container handles connection errors

- **GIVEN** invalid Cosmos DB connection
- **WHEN** user runs `orbit containers delete products --yes`
- **THEN** command exits with error: "Failed to connect to Cosmos DB. Check connection string." and exit code 1

---

### Requirement: Output Format Consistency

All container commands SHALL support both Rich formatted (human-readable) and JSON (machine-readable) output modes activated via the global `--json` flag.

**Details**:

- Default: Rich tables, formatted text with colors/emphasis
- JSON mode: Activated with global `--json` flag
- JSON structure: Consistent keys across commands
- No secrets: Connection strings never appear in output

#### Scenario: Rich output uses tables for lists

- **GIVEN** database with multiple containers
- **WHEN** user runs `orbit containers list`
- **THEN** output is Rich table with aligned columns and headers

#### Scenario: JSON output is valid and parseable

- **GIVEN** any container command with `--json` flag
- **WHEN** command executes successfully
- **THEN** output is valid JSON that can be parsed by `jq` or other tools

#### Scenario: No secrets in output

- **GIVEN** any container command (list, create, delete)
- **WHEN** command outputs results or errors
- **THEN** connection strings and keys are never displayed

---

### Requirement: Error Handling and User Guidance

All error messages SHALL be actionable and guide users toward resolution, including checking connection strings, listing existing resources, and showing correct input formats.

**Details**:

- Connection errors suggest checking connection string
- Duplicate container errors suggest list existing containers
- Quota errors suggest reducing throughput or checking limits
- Validation errors show correct format examples
- All errors exit with non-zero code

#### Scenario: Connection error provides actionable guidance

- **GIVEN** invalid connection string
- **WHEN** user runs any container command
- **THEN** error message includes: "Check connection string" or similar guidance

#### Scenario: Validation error shows correct format

- **GIVEN** invalid partition key format
- **WHEN** user runs create command
- **THEN** error message shows example: "e.g., /id"

#### Scenario: Duplicate resource error suggests next action

- **GIVEN** container already exists
- **WHEN** user attempts to create duplicate
- **THEN** error message suggests: "Use 'orbit containers list' to see existing containers."

## Dependencies

- Requires: `CosmosContainerRepository` from `implement-cosmos-repository-containers`
- Requires: `OutputAdapter` from `add-cli-boilerplate`
- Requires: `require_confirmation` from `add-cli-boilerplate`
- Requires: Authentication via `implement-connection-string-auth`

## Non-Functional Requirements

- **Performance**: Commands complete within 2 seconds for typical operations
- **Usability**: Error messages are beginner-friendly and actionable
- **Security**: No connection strings or keys logged or displayed
- **Testability**: 80%+ code coverage with mocked repository layer
- **Maintainability**: Functions < 20 lines, single responsibility principle

## Future Considerations

- Container update operations (throughput scaling)
- Container property inspection (detailed metadata)
- Batch container operations
- Container templates or presets
- Integration with configuration files for database selection
