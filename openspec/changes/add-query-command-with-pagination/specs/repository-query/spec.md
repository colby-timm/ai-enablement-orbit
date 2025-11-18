# Spec: Repository Query Operations

## ADDED Requirements

### Requirement: Execute SQL Queries Against Containers

The repository SHALL provide a method to execute SQL queries against specified containers, supporting Cosmos DB SQL API syntax and returning matching items with request unit cost tracking.

#### Scenario: Execute simple SELECT query

- **GIVEN** a container "users" with items `{"id": "1", "name": "Alice"}`, `{"id": "2", "name": "Bob"}`
- **WHEN** `query_items("users", "SELECT * FROM c")` is called
- **THEN** return both items
- **AND** include total RU cost for the query

#### Scenario: Execute query with WHERE clause

- **GIVEN** a container "users" with items having various ages
- **WHEN** `query_items("users", "SELECT * FROM c WHERE c.age > 25")` is called
- **THEN** return only items where age property is greater than 25
- **AND** track RU cost

#### Scenario: Execute query with projection

- **GIVEN** a container "users" with full user objects
- **WHEN** `query_items("users", "SELECT c.id, c.name FROM c")` is called
- **THEN** return items with only id and name properties
- **AND** other properties are excluded

#### Scenario: Execute query against non-existent container

- **GIVEN** no container named "missing"
- **WHEN** `query_items("missing", "SELECT * FROM c")` is called
- **THEN** raise `CosmosResourceNotFoundError`
- **AND** error message includes container name "missing"

#### Scenario: Execute query with syntax error

- **GIVEN** a malformed query "SELCT * FORM c" (typos)
- **WHEN** `query_items("users", "SELCT * FORM c")` is called
- **THEN** raise `CosmosSyntaxError`
- **AND** error message explains SQL syntax issue

### Requirement: Support Cross-Partition Queries

The repository SHALL support queries that span multiple partition keys with explicit opt-in via configuration parameter, warning users of increased RU costs.

#### Scenario: Execute cross-partition query when enabled

- **GIVEN** a container "orders" partitioned by `/customerId` with orders from multiple customers
- **WHEN** `query_items("orders", "SELECT * FROM c WHERE c.total > 100", enable_cross_partition=True)` is called
- **THEN** return matching items across all partitions
- **AND** track total RU cost

#### Scenario: Execute cross-partition query when disabled

- **GIVEN** a container "orders" partitioned by `/customerId`
- **WHEN** `query_items("orders", "SELECT * FROM c", enable_cross_partition=False)` is called without partition key
- **THEN** raise `CosmosQueryError` indicating cross-partition queries are disabled
- **AND** error message suggests enabling cross-partition flag or specifying partition key

#### Scenario: Execute partition-specific query

- **GIVEN** a container "orders" partitioned by `/customerId`
- **WHEN** `query_items("orders", "SELECT * FROM c WHERE c.customerId = 'CUST123'", partition_key="CUST123")` is called
- **THEN** query executes within single partition
- **AND** RU cost is lower than equivalent cross-partition query

### Requirement: Implement Pagination with Configurable Page Size

The repository SHALL handle result pagination automatically using continuation tokens from the SDK, yielding results incrementally to support streaming large datasets without loading all results into memory.

#### Scenario: Paginate query results with default page size

- **GIVEN** a container "products" with 250 items
- **WHEN** `query_items("products", "SELECT * FROM c", max_item_count=100)` is called
- **THEN** yield results in chunks of up to 100 items
- **AND** automatically handle continuation tokens across pages
- **AND** total RU cost reflects all pages

#### Scenario: Paginate query with custom page size

- **GIVEN** a container "products" with 500 items
- **WHEN** `query_items("products", "SELECT * FROM c", max_item_count=50)` is called
- **THEN** yield results in chunks of up to 50 items
- **AND** pagination continues until all results consumed

#### Scenario: Query with no pagination needed

- **GIVEN** a container "settings" with 5 items
- **WHEN** `query_items("settings", "SELECT * FROM c", max_item_count=100)` is called
- **THEN** return all 5 items in single page
- **AND** no continuation token handling required

### Requirement: Track and Report Request Unit Costs

The repository SHALL track RU costs per page and aggregate total costs across all pages, exposing this information to callers for cost monitoring and optimization.

#### Scenario: Track RU cost for single-page query

- **GIVEN** a query that returns results in one page
- **WHEN** `query_items("users", "SELECT * FROM c")` is called
- **THEN** return RU cost from SDK response header `x-ms-request-charge`
- **AND** RU cost is included in result metadata

#### Scenario: Aggregate RU costs across multiple pages

- **GIVEN** a query that spans 3 pages (300 items total, 100 per page)
- **WHEN** `query_items("products", "SELECT * FROM c", max_item_count=100)` is called
- **THEN** track RU cost for each page
- **AND** return total aggregated RU cost: sum of all page costs

#### Scenario: RU cost tracking during pagination

- **GIVEN** a query being consumed iteratively
- **WHEN** caller retrieves first 100 items (page 1)
- **THEN** RU cost reflects only page 1
- **WHEN** caller retrieves next 100 items (page 2)
- **THEN** RU cost reflects pages 1 and 2 combined

### Requirement: Stream Results as Generator

The repository SHALL yield query results incrementally using Python generators to enable memory-efficient processing of large result sets without loading entire dataset into memory.

#### Scenario: Stream large result set

- **GIVEN** a query returning 10,000 items
- **WHEN** `query_items("logs", "SELECT * FROM c")` is called
- **THEN** return a generator yielding items incrementally
- **AND** memory usage remains constant regardless of result count
- **AND** caller can process items one at a time or in batches

#### Scenario: Consume partial results from generator

- **GIVEN** a query returning 500 items
- **WHEN** caller consumes first 100 items from generator
- **THEN** only first 100 items are fetched from SDK
- **AND** remaining items are not fetched until requested
- **AND** RU cost reflects only pages consumed

### Requirement: Handle Query Timeouts Gracefully

The repository SHALL catch query timeout exceptions from the SDK and raise domain-specific exceptions with actionable guidance to narrow query scope or adjust timeout settings.

#### Scenario: Query exceeds default timeout

- **GIVEN** a complex query with multiple JOINs taking > 30 seconds
- **WHEN** `query_items("data", "complex query...")` is called
- **THEN** raise `CosmosQueryTimeoutError`
- **AND** error message suggests simplifying query or increasing timeout

#### Scenario: Query timeout with cross-partition query

- **GIVEN** a cross-partition query scanning millions of items
- **WHEN** query times out
- **THEN** raise `CosmosQueryTimeoutError`
- **AND** error message suggests adding WHERE clause to narrow scope

### Requirement: Sanitize Error Messages to Prevent Secret Exposure

All error messages from query operations SHALL be sanitized to ensure connection strings, account keys, and other sensitive information are never exposed in exceptions or logs.

#### Scenario: SDK exception contains connection string

- **GIVEN** SDK raises exception including connection string in message
- **WHEN** repository catches exception
- **THEN** raise domain exception with sanitized message
- **AND** connection string is removed from error text
- **AND** actionable guidance provided instead

#### Scenario: Query syntax error logged safely

- **GIVEN** user submits query with syntax error
- **WHEN** `CosmosSyntaxError` is raised
- **THEN** log query hash (not full query text if it might contain sensitive filters)
- **AND** error message explains syntax issue without exposing data

### Requirement: Log Query Execution Metadata

The repository SHALL log query execution events at INFO level including container name, query hash, RU cost, item count, and execution time, ensuring no sensitive data or secrets appear in logs.

#### Scenario: Query execution logged successfully

- **GIVEN** a successful query execution
- **WHEN** `query_items("users", "SELECT * FROM c WHERE c.age > 21")` completes
- **THEN** log message includes: "Executed query on container 'users': 42 items, 12.5 RU, 340ms"
- **AND** log does NOT include full query text (may contain sensitive filter values)
- **AND** log does NOT include connection string or keys

#### Scenario: Failed query logged safely

- **GIVEN** a query that fails due to syntax error
- **WHEN** exception is raised
- **THEN** log message includes: "Query failed on container 'users': CosmosSyntaxError"
- **AND** log does NOT include connection string or account keys
