# Change: Add Query Command with Pagination

## Why

Developers need a powerful CLI command to query Cosmos DB using SQL syntax without writing custom code. While Orbit supports basic CRUD operations on individual items, it lacks query capabilities for retrieving multiple items based on complex criteria. Queries are essential for data exploration, debugging, reporting, and batch operations. This change adds `orbit query` command supporting full SQL query syntax, cross-partition queries, configurable pagination, RU cost tracking, and result streaming—enabling developers to efficiently explore and analyze data directly from the terminal.

## What Changes

- Add `orbit query` command to CLI for executing SQL queries against containers
- Implement repository layer method `query_items()` with SQL query support
- Support cross-partition queries with proper SDK configuration
- Add pagination with configurable limit (default: 100 items per page)
- Track and report Request Unit (RU) costs for each query execution
- Implement result set streaming to handle large datasets efficiently
- Support `--limit` flag to control maximum results returned (default: 100)
- Support `--max-item-count` flag to control page size (default: 100)
- Add `--enable-cross-partition` flag for explicit cross-partition query opt-in
- Format output using Rich for human-readable display
- Support `--json` flag for machine-readable output
- Display RU cost summary after query execution
- Add comprehensive error handling for malformed queries and SDK errors
- Add unit and integration tests maintaining 80%+ coverage
- Document query limitations and best practices

## Impact

- Affected specs:
  - ADDS new `cli-query` capability for SQL query command
  - ADDS new `repository-query` capability for query repository methods
- Affected code:
  - `orbit/cli.py`: Registers `query` command
  - `orbit/commands/query.py`: NEW FILE - Query CLI command implementation
  - `orbit/repositories/base.py`: Add `query_items()` method signature
  - `orbit/repositories/cosmos_repository.py`: Implement `query_items()` with azure-cosmos SDK
  - `tests/test_query_command.py`: NEW FILE - Query command tests
  - `tests/test_repository_query.py`: NEW FILE - Repository query tests
- **BREAKING**: None—adding new command to existing CLI
- **DEPENDENCIES**:
  - Requires `implement-connection-string-auth` (authentication)
  - Requires `implement-cosmos-repository-containers` (container access)
- **ENABLES**: Developers can now query and explore Cosmos DB data with SQL syntax

## Dependencies

- **Requires**: `implement-connection-string-auth` (provides authentication)
- **Requires**: `implement-cosmos-repository-containers` (provides container access for queries)
- **Enables**: Advanced data exploration, reporting, and batch data retrieval workflows
- **Blocks**: None—independent feature that can be used immediately

## Notes

- Query syntax follows Cosmos DB SQL API specification
- Cross-partition queries disabled by default (require `--enable-cross-partition` flag)
- Pagination automatically handles continuation tokens from SDK
- RU cost tracked per page and aggregated for total query cost
- Large result sets streamed to avoid memory issues
- Query timeout defaults to SDK default (configurable in future enhancement)
- Error messages provide actionable guidance for query syntax errors
- No secrets logged or displayed in output
- Results formatted as Rich table with columns matching SELECT projection
- JSON output structure: `{"items": [...], "ru_cost": 12.5, "item_count": 100}`
- Command validates required flags: `--container` to specify target container
- Query parameters support for parameterized queries (future enhancement)
- Consider adding `--raw` flag for unformatted SDK response (future enhancement)
