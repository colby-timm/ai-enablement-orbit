# Implementation Tasks: Add Query Command with Pagination

## Prerequisites

- [ ] Verify `implement-connection-string-auth` is complete
- [ ] Verify `implement-cosmos-repository-containers` is complete
- [ ] Review Azure Cosmos DB SQL query syntax documentation
- [ ] Review azure-cosmos SDK query_items() API and pagination patterns

## Repository Layer (Backend)

### Add Query Method to Repository Protocol

- [ ] Update `orbit/repositories/base.py` to add `query_items()` method signature
- [ ] Define method parameters: `container_name`, `query`, `enable_cross_partition`, `max_item_count`, `partition_key`
- [ ] Define return type: iterator/generator yielding items and RU cost metadata
- [ ] Add docstring with parameter descriptions and usage examples

### Implement Query Repository Method

- [ ] Create `orbit/repositories/cosmos_repository.py` (or extend existing if created)
- [ ] Implement `query_items()` method using `container_client.query_items()`
- [ ] Configure `enable_cross_partition_query` parameter based on flag
- [ ] Set `max_item_count` for page size control
- [ ] Implement continuation token handling for pagination
- [ ] Track RU costs from response headers (`x-ms-request-charge`)
- [ ] Yield results as generator to support streaming
- [ ] Map SDK exceptions to domain exceptions (e.g., `CosmosSyntaxError`, `CosmosConnectionError`)
- [ ] Sanitize error messages to exclude secrets
- [ ] Add logging for query execution (log query hash, not full query with sensitive data)

### Error Handling

- [ ] Create `CosmosSyntaxError` exception for malformed queries
- [ ] Create `CosmosQueryError` for general query execution failures
- [ ] Handle partition key mismatch errors with actionable messages
- [ ] Handle timeout errors with suggestions to narrow query or increase timeout
- [ ] Test error scenarios: invalid SQL, missing container, connection failure

## CLI Layer (Frontend)

### Create Query Command

- [ ] Create `orbit/commands/query.py` with Typer command structure
- [ ] Define `query()` function with Typer annotations
- [ ] Add required argument: `query_text` (SQL query string)
- [ ] Add required flag: `--container` / `-c` (container name)
- [ ] Add optional flag: `--limit` / `-l` (max results, default: 100)
- [ ] Add optional flag: `--max-item-count` / `-m` (page size, default: 100)
- [ ] Add optional flag: `--enable-cross-partition` / `-x` (boolean flag)
- [ ] Add optional flag: `--partition-key` / `-p` (specific partition key value)
- [ ] Support global `--json` flag for output format
- [ ] Validate inputs: container name not empty, query not empty

### Wire Query Command to Repository

- [ ] Inject or instantiate `CosmosRepository` in command
- [ ] Pass authentication context from global config
- [ ] Call `repository.query_items()` with command parameters
- [ ] Iterate results from generator
- [ ] Accumulate items up to `--limit`
- [ ] Track total RU cost across pages

### Output Formatting

- [ ] Use `OutputAdapter` or Rich for human-readable formatting
- [ ] Display results as Rich table with dynamic columns based on SELECT projection
- [ ] Show RU cost summary after results: "Query completed: 42 items, 15.3 RU"
- [ ] Implement `--json` output: `{"items": [...], "ru_cost": 15.3, "item_count": 42}`
- [ ] Handle empty result sets gracefully: "No items matched query."
- [ ] Implement progress indicator for long-running queries (optional)

### Register Command in CLI

- [ ] Import `query` command in `orbit/cli.py`
- [ ] Register command with Typer app: `app.command(name="query")(query)`
- [ ] Verify command appears in `orbit --help`

## Testing

### Unit Tests - Repository Layer

- [ ] Test `query_items()` with simple SELECT query
- [ ] Test pagination: verify continuation token handling
- [ ] Test cross-partition query execution
- [ ] Test partition key specific query
- [ ] Test RU cost tracking and accumulation
- [ ] Test error handling: invalid query syntax
- [ ] Test error handling: non-existent container
- [ ] Test error handling: connection failure
- [ ] Mock azure-cosmos SDK responses

### Unit Tests - CLI Layer

- [ ] Test `orbit query` with valid query and container
- [ ] Test `--limit` flag controls result count
- [ ] Test `--max-item-count` flag controls page size
- [ ] Test `--enable-cross-partition` flag behavior
- [ ] Test `--partition-key` flag usage
- [ ] Test `--json` output format structure
- [ ] Test error messages for missing required flags
- [ ] Test error messages for empty query
- [ ] Mock repository responses

### Integration Tests (Emulator)

- [ ] Setup Cosmos DB emulator with test data
- [ ] Test end-to-end: simple SELECT query returns expected items
- [ ] Test cross-partition query with `--enable-cross-partition`
- [ ] Test pagination with result sets > 100 items
- [ ] Test RU cost accuracy against SDK reported values
- [ ] Test query with WHERE clause filtering
- [ ] Test query with ORDER BY and aggregates (COUNT, SUM)
- [ ] Verify no secrets in logs or output

## Documentation

- [ ] Add usage examples to `README.md` or docs
- [ ] Document query syntax limitations (link to Cosmos DB docs)
- [ ] Document RU cost implications of cross-partition queries
- [ ] Add troubleshooting guide for common query errors
- [ ] Document pagination behavior and limits

## Validation

- [ ] Run `ruff check` and `ruff format` on all new/modified files
- [ ] Verify 80%+ test coverage with `pytest --cov`
- [ ] Run `openspec validate add-query-command-with-pagination --strict`
- [ ] Test manually with Cosmos DB emulator
- [ ] Verify no secrets in logs: `orbit query --container users "SELECT * FROM c" 2>&1 | grep -i "AccountEndpoint\|AccountKey"`
- [ ] Verify help text: `orbit query --help`
