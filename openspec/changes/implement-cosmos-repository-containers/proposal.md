# Change: Implement Cosmos Repository for Container Operations

## Why

Repository layer is currently a placeholder with only item-level operations defined (get_item, list_items). Container management is foundational—containers must exist before items can be created, queried, or managed. Without container operations, developers cannot create workspaces, provision resources, or manage Cosmos DB structure through Orbit CLI. This change extends the repository abstraction to support container lifecycle operations, enabling downstream CLI commands and data management features.

## What Changes

- Extend `CosmosRepository` protocol with container operation methods
- Create concrete `CosmosContainerRepository` class implementing container operations
- Implement `list_containers()` to enumerate all containers in a database
- Implement `create_container(name, partition_key_path, throughput)` with partition key specification
- Implement `delete_container(name)` to remove containers
- Implement `get_container_properties(name)` to retrieve container metadata
- Add proper error handling for duplicate containers, not found scenarios, and throughput limits
- Map Azure SDK exceptions to domain exceptions (CosmosResourceNotFoundError, CosmosResourceExistsError)
- Ensure all operations use the authenticated CosmosClient from AuthStrategy
- Add comprehensive unit tests with mocked SDK calls
- Maintain 80%+ test coverage

## Impact

- Affected specs:
  - ADDS new `repository-containers` capability for container lifecycle operations
- Affected code:
  - `orbit/repositories/base.py`: Extends `CosmosRepository` protocol with container methods
  - `orbit/repositories/cosmos.py`: NEW FILE - Concrete implementation
  - `orbit/exceptions.py`: Adds resource-specific exceptions (not found, exists, quota)
  - `tests/test_repositories.py`: NEW FILE - Repository unit tests
- **BREAKING**: None—extending protocol, existing placeholder methods unchanged
- **FOUNDATION**: Required by container CLI commands (#4), item operations (#3 need containers to exist), and query operations (#6 query containers)

## Dependencies

- **Requires**: `implement-connection-string-auth` (provides working CosmosClient via AuthStrategy)
- **Enables**: Container CLI commands, item operations, query operations
- **Blocks**: Cannot implement item CRUD or container CLI until this is complete

## Notes

- Repository accepts database name at initialization (from settings or CLI arg)
- Container names must be valid per Cosmos DB naming rules (alphanumeric, hyphens, max 255 chars)
- Partition key paths must start with `/` (e.g., `/userId`, `/category`)
- Throughput defaults to 400 RU/s (minimum for manual throughput)
- Delete operations should be idempotent (no error if container doesn't exist)
- Properties include: container name, partition key definition, throughput, indexing policy
- Must handle both manual and autoscale throughput configurations
- All SDK calls must be wrapped for proper exception translation to domain exceptions
