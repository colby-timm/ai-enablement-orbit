# Spec: CLI Query Command

## ADDED Requirements

### Requirement: Execute SQL Queries via CLI

The CLI SHALL provide an `orbit query` command that accepts SQL query text and container name, executes the query via the repository layer, and displays results with RU cost summary.

#### Scenario: Execute simple query from CLI

- **GIVEN** connection to Cosmos DB is configured
- **WHEN** user runs `orbit query --container users "SELECT * FROM c"`
- **THEN** display all items from users container
- **AND** show RU cost summary: "Query completed: 15 items, 5.2 RU"

#### Scenario: Execute query with WHERE clause

- **GIVEN** container "products" with various items
- **WHEN** user runs `orbit query --container products "SELECT * FROM c WHERE c.price > 50"`
- **THEN** display only products with price greater than 50
- **AND** show RU cost and item count

#### Scenario: Execute query missing required container flag

- **GIVEN** user wants to query data
- **WHEN** user runs `orbit query "SELECT * FROM c"` (without --container)
- **THEN** display error: "Error: Missing required flag: --container"
- **AND** show usage example: `orbit query --container <name> "<query>"`

#### Scenario: Execute query with empty query text

- **GIVEN** user provides empty query string
- **WHEN** user runs `orbit query --container users ""`
- **THEN** display error: "Error: Query text cannot be empty"
- **AND** exit with non-zero status code

### Requirement: Support Cross-Partition Query Flag

The CLI SHALL provide `--enable-cross-partition` flag to explicitly opt-in to queries that span multiple partition keys, warning users of potential increased RU costs.

#### Scenario: Execute cross-partition query with flag

- **GIVEN** container "orders" partitioned by customerId
- **WHEN** user runs `orbit query --container orders --enable-cross-partition "SELECT * FROM c WHERE c.total > 100"`
- **THEN** execute query across all partitions
- **AND** display results with RU cost
- **AND** show informational message: "Cross-partition query executed across all partitions"

#### Scenario: Execute cross-partition query without flag

- **GIVEN** container "orders" partitioned by customerId
- **WHEN** user runs `orbit query --container orders "SELECT * FROM c WHERE c.total > 100"` (without flag)
- **THEN** raise error: "Cross-partition query requires --enable-cross-partition flag"
- **AND** suggest adding flag or specifying --partition-key

#### Scenario: Execute partition-specific query

- **GIVEN** container "orders" partitioned by customerId
- **WHEN** user runs `orbit query --container orders --partition-key "CUST123" "SELECT * FROM c"`
- **THEN** execute query within single partition
- **AND** display results with lower RU cost than cross-partition equivalent

### Requirement: Control Result Limits and Pagination

The CLI SHALL provide `--limit` flag to control maximum number of results returned and `--max-item-count` flag to control page size for pagination, with sensible defaults (100 for both).

#### Scenario: Limit results to specific count

- **GIVEN** container "logs" with 1000 items
- **WHEN** user runs `orbit query --container logs --limit 50 "SELECT * FROM c"`
- **THEN** display only first 50 items
- **AND** show message: "Showing 50 of potentially more results"
- **AND** display RU cost for pages consumed

#### Scenario: Use default limit

- **GIVEN** container "products" with 250 items
- **WHEN** user runs `orbit query --container products "SELECT * FROM c"` (no --limit)
- **THEN** display first 100 items (default limit)
- **AND** show message: "Showing 100 of potentially more results"

#### Scenario: Control page size with max-item-count

- **GIVEN** container "data" with 500 items
- **WHEN** user runs `orbit query --container data --max-item-count 25 --limit 100 "SELECT * FROM c"`
- **THEN** fetch results in pages of 25 items
- **AND** stop after 100 total items
- **AND** display 100 items with aggregated RU cost

#### Scenario: Query returns fewer items than limit

- **GIVEN** container "settings" with 10 items
- **WHEN** user runs `orbit query --container settings --limit 100 "SELECT * FROM c"`
- **THEN** display all 10 items
- **AND** show message: "Query completed: 10 items, 2.1 RU"
- **AND** no pagination warning

### Requirement: Format Output as Rich Table

The CLI SHALL format query results as Rich tables with columns matching the SELECT projection, providing human-readable output with proper alignment and truncation for long values.

#### Scenario: Display full document query results

- **GIVEN** query `SELECT * FROM c` returning items with id, name, email properties
- **WHEN** results are displayed
- **THEN** show Rich table with columns: id, name, email
- **AND** rows contain corresponding values
- **AND** long values are truncated with ellipsis

#### Scenario: Display projected query results

- **GIVEN** query `SELECT c.id, c.name FROM c` returning only id and name
- **WHEN** results are displayed
- **THEN** show Rich table with columns: id, name
- **AND** other properties are not displayed

#### Scenario: Display query with no results

- **GIVEN** query `SELECT * FROM c WHERE c.status = 'archived'` returns no items
- **WHEN** results are displayed
- **THEN** show message: "No items matched query."
- **AND** show RU cost: "Query completed: 0 items, 2.5 RU"

#### Scenario: Display query with nested objects

- **GIVEN** query returns items with nested address objects
- **WHEN** results are displayed
- **THEN** show nested objects as formatted JSON string in table cell
- **AND** truncate long JSON with ellipsis

### Requirement: Support JSON Output Format

The CLI SHALL support `--json` flag to output query results as machine-readable JSON including items array, total RU cost, and item count for integration with other tools.

#### Scenario: Output query results as JSON

- **GIVEN** successful query execution
- **WHEN** user runs `orbit query --container users --json "SELECT * FROM c"`
- **THEN** output JSON: `{"items": [...], "ru_cost": 5.2, "item_count": 15}`
- **AND** items array contains full item objects
- **AND** no Rich table formatting applied

#### Scenario: Output empty results as JSON

- **GIVEN** query returns no items
- **WHEN** user runs `orbit query --container users --json "SELECT * FROM c WHERE false"`
- **THEN** output JSON: `{"items": [], "ru_cost": 2.5, "item_count": 0}`

### Requirement: Display RU Cost Summary

The CLI SHALL always display total RU cost consumed by the query after results, helping users understand and optimize query performance and costs.

#### Scenario: Display RU cost after single-page query

- **GIVEN** query completes in one page
- **WHEN** results are displayed
- **THEN** show summary: "Query completed: 42 items, 5.8 RU"
- **AND** RU cost matches value from repository

#### Scenario: Display RU cost after multi-page query

- **GIVEN** query fetches 3 pages of results
- **WHEN** results are displayed
- **THEN** show summary: "Query completed: 250 items, 18.3 RU"
- **AND** RU cost is aggregate of all pages consumed

#### Scenario: Display RU cost in JSON mode

- **GIVEN** query executed with --json flag
- **WHEN** JSON is output
- **THEN** `ru_cost` field contains total RU cost as float
- **AND** value matches displayed summary in human-readable mode

### Requirement: Handle Query Errors with Actionable Messages

The CLI SHALL catch query errors from repository layer and display user-friendly, actionable error messages without exposing secrets or technical SDK details.

#### Scenario: Handle query syntax error

- **GIVEN** malformed query with typo
- **WHEN** user runs `orbit query --container users "SELCT * FROM c"`
- **THEN** display error: "Query syntax error: Invalid SQL syntax near 'SELCT'"
- **AND** suggest: "Check query syntax. See Cosmos DB SQL documentation for examples."
- **AND** exit with non-zero status code

#### Scenario: Handle non-existent container error

- **GIVEN** container "missing" does not exist
- **WHEN** user runs `orbit query --container missing "SELECT * FROM c"`
- **THEN** display error: "Container 'missing' not found."
- **AND** suggest: "Use 'orbit containers list' to see available containers."
- **AND** exit with non-zero status code

#### Scenario: Handle connection error

- **GIVEN** Cosmos DB endpoint is unreachable
- **WHEN** user runs `orbit query --container users "SELECT * FROM c"`
- **THEN** display error: "Failed to connect to Cosmos DB."
- **AND** suggest: "Check connection string and network connectivity."
- **AND** no secrets exposed in error message

#### Scenario: Handle query timeout error

- **GIVEN** complex query exceeds timeout
- **WHEN** query times out
- **THEN** display error: "Query timed out."
- **AND** suggest: "Try narrowing query with WHERE clause or increase timeout."

### Requirement: Prevent Secret Exposure in CLI Output

The CLI SHALL ensure connection strings, account keys, and other sensitive information never appear in query output, error messages, or logs.

#### Scenario: Error message excludes connection string

- **GIVEN** connection error occurs
- **WHEN** error message is displayed
- **THEN** message does NOT include connection string
- **AND** message does NOT include account key
- **AND** message provides actionable guidance

#### Scenario: Debug output excludes secrets

- **GIVEN** user runs query with verbose logging
- **WHEN** debug output is generated
- **THEN** logs include query hash, not full query with sensitive filters
- **AND** logs do NOT include connection string or keys

### Requirement: Validate Input Parameters

The CLI SHALL validate all input parameters before executing queries, providing clear error messages for invalid inputs to prevent unnecessary API calls and improve user experience.

#### Scenario: Validate container name is not empty

- **GIVEN** user provides empty container name
- **WHEN** user runs `orbit query --container "" "SELECT * FROM c"`
- **THEN** display error: "Container name cannot be empty"
- **AND** exit without making API call

#### Scenario: Validate limit is positive integer

- **GIVEN** user provides invalid limit value
- **WHEN** user runs `orbit query --container users --limit -10 "SELECT * FROM c"`
- **THEN** display error: "Limit must be a positive integer"
- **AND** exit without making API call

#### Scenario: Validate max-item-count is positive integer

- **GIVEN** user provides invalid page size
- **WHEN** user runs `orbit query --container users --max-item-count 0 "SELECT * FROM c"`
- **THEN** display error: "Max item count must be a positive integer"
- **AND** exit without making API call
