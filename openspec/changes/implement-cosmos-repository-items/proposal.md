# Change: Implement Cosmos Repository for Item Operations

## Why

Repository layer currently has placeholder item methods (`get_item`, `list_items`) with TODOs. Item CRUD operations are essential for developers to create, read, update, and delete documents in Cosmos DB containers. Without these operations, CLI commands for item management cannot be implemented, and developers cannot interact with actual data stored in containers. This change completes the repository abstraction for item-level operations, enabling CLI features and data manipulation workflows. Items cannot exist without containers, making this dependent on container operations being available first.

## What Changes

- Extend `CosmosRepository` protocol with complete item operation methods
- Create concrete repository implementation with item CRUD methods
- Implement `create_item(container_name, item, partition_key_value)` to insert new items
- Implement `get_item(container_name, item_id, partition_key_value)` to retrieve items by ID and partition key
- Implement `update_item(container_name, item_id, item, partition_key_value)` to modify existing items
- Implement `delete_item(container_name, item_id, partition_key_value)` to remove items
- Implement `list_items(container_name, max_count)` with pagination support
- Add proper error handling for partition key mismatches, item not found, and duplicate ID scenarios
- Map Azure SDK exceptions to domain exceptions (CosmosItemNotFoundError, CosmosPartitionKeyMismatchError)
- Ensure all operations validate partition key presence and consistency
- Add comprehensive unit tests with mocked SDK calls
- Maintain 80%+ test coverage

## Impact

- Affected specs:
  - ADDS new `repository-items` capability for item lifecycle operations
- Affected code:
  - `orbit/repositories/base.py`: Replaces placeholder item methods with complete signatures
  - `orbit/repositories/cosmos.py`: Extends with concrete item CRUD implementations
  - `orbit/exceptions.py`: Adds item-specific exceptions (not found, partition key errors)
  - `tests/test_item_repository.py`: NEW FILE - Item repository unit tests
- **BREAKING**: None—completing existing placeholder methods, backward compatible
- **FOUNDATION**: Required by item CLI commands (#5), enables data manipulation workflows

## Dependencies

- **Requires**:
  - `implement-connection-string-auth` (provides working CosmosClient via AuthStrategy)
  - `implement-cosmos-repository-containers` (items must exist in containers)
- **Enables**: Item CLI commands, data manipulation features
- **Blocks**: Cannot implement item management CLI or query results without item operations

## Notes

- Items must be created in existing containers (validate container existence)
- Partition key value must match the container's partition key definition
- Item IDs must be unique within a partition
- `get_item` requires both item ID and partition key value for single-item retrieval
- `update_item` performs upsert by default (create if not exists, replace if exists)
- `delete_item` should be idempotent (no error if item doesn't exist)
- `list_items` defaults to 100 items max (configurable pagination limit)
- All item data treated as JSON-compatible dictionaries
- Must handle SDK exceptions for partition key mismatches (400 status code)
- Must handle SDK exceptions for item not found (404 status code)
- All operations must sanitize error messages to prevent secret exposure
