# Implementation Tasks

## Prerequisites

- [x] Verify `implement-connection-string-auth` change is complete and merged
- [x] Verify `implement-cosmos-repository-containers` change is complete and merged
- [x] Review Azure Cosmos SDK documentation for item CRUD operations
- [x] Confirm `azure-cosmos` dependency is installed

## Domain Exceptions

- [x] Add `CosmosItemNotFoundError` to `orbit/exceptions.py`
- [x] Add `CosmosPartitionKeyMismatchError` to `orbit/exceptions.py`
- [x] Add `CosmosDuplicateItemError` to `orbit/exceptions.py` (for duplicate IDs in partition)
- [x] Ensure all exceptions inherit from `OrbitError` base class
- [x] Add docstrings explaining when each exception is raised
- [x] Document expected HTTP status codes that trigger each exception

## Repository Protocol Extension

- [x] Open `orbit/repositories/base.py`
- [x] Replace `get_item(item_id)` with `get_item(container_name, item_id, partition_key_value)` signature
- [x] Replace `list_items()` with `list_items(container_name, max_count=100)` signature
- [x] Add `create_item(container_name, item, partition_key_value)` method signature
- [x] Add `update_item(container_name, item_id, item, partition_key_value)` method signature
- [x] Add `delete_item(container_name, item_id, partition_key_value)` method signature
- [x] Add type hints: use `dict[str, Any]` for item data, `str` for IDs and partition keys
- [x] Add comprehensive docstrings explaining parameters, return types, and exceptions
- [x] Remove TODO comments from method signatures

## Concrete Repository Implementation

- [x] Open or create `orbit/repositories/cosmos.py` file
- [x] Import required types: `Dict`, `Any`, `Optional`, `List` from `typing`
- [x] Import `CosmosClient`, `exceptions` from `azure.cosmos`
- [x] Import domain exceptions from `orbit/exceptions`
- [x] Ensure `CosmosItemRepository` class exists (or extend existing repository class)
- [x] Add helper method `_get_container_client(container_name)` to retrieve container client
- [x] Implement `create_item(container_name, item, partition_key_value)`:
  - [x] Validate item is a dictionary with 'id' field
  - [x] Get container client via helper method
  - [x] Call `container.create_item(body=item, partition_key=partition_key_value)`
  - [x] Handle duplicate ID → raise `CosmosDuplicateItemError`
  - [x] Handle partition key mismatch (400) → raise `CosmosPartitionKeyMismatchError`
  - [x] Wrap other SDK exceptions → `CosmosConnectionError`
  - [x] Return created item dictionary
  - [x] Log operation (no secrets, no item content)
- [x] Implement `get_item(container_name, item_id, partition_key_value)`:
  - [x] Get container client via helper method
  - [x] Call `container.read_item(item=item_id, partition_key=partition_key_value)`
  - [x] Handle not found (404) → raise `CosmosItemNotFoundError`
  - [x] Handle partition key mismatch → raise `CosmosPartitionKeyMismatchError`
  - [x] Wrap other SDK exceptions → `CosmosConnectionError`
  - [x] Return item dictionary
  - [x] Log operation (no secrets)
- [x] Implement `update_item(container_name, item_id, item, partition_key_value)`:
  - [x] Validate item is a dictionary
  - [x] Ensure item['id'] matches item_id parameter
  - [x] Get container client via helper method
  - [x] Call `container.upsert_item(body=item, partition_key=partition_key_value)`
  - [x] Handle partition key mismatch → raise `CosmosPartitionKeyMismatchError`
  - [x] Wrap other SDK exceptions → `CosmosConnectionError`
  - [x] Return updated item dictionary
  - [x] Log operation (no secrets)
- [x] Implement `delete_item(container_name, item_id, partition_key_value)`:
  - [x] Get container client via helper method
  - [x] Call `container.delete_item(item=item_id, partition_key=partition_key_value)`
  - [x] Make idempotent: ignore 404 not found errors
  - [x] Handle partition key mismatch → raise `CosmosPartitionKeyMismatchError`
  - [x] Wrap other SDK exceptions → `CosmosConnectionError`
  - [x] Log operation (no secrets)
- [x] Implement `list_items(container_name, max_count=100)`:
  - [x] Get container client via helper method
  - [x] Call `container.query_items(query="SELECT * FROM c", max_item_count=max_count)`
  - [x] Convert query iterator to list (limit to max_count items)
  - [x] Handle empty results gracefully (return empty list)
  - [x] Wrap SDK exceptions → `CosmosConnectionError`
  - [x] Log operation with item count (no secrets, no item content)
- [x] Ensure all methods are 5-20 lines (extract helpers if needed)
- [x] Add type hints to all methods
- [x] Add comprehensive docstrings with Google-style format

## Error Handling

- [x] Map SDK `CosmosResourceNotFoundError` (404) for items → domain `CosmosItemNotFoundError`
- [x] Map SDK `CosmosHttpResponseError` (409 conflict) → domain `CosmosDuplicateItemError`
- [x] Map SDK `CosmosHttpResponseError` (400 with partition key message) → `CosmosPartitionKeyMismatchError`
- [x] Map other SDK `CosmosHttpResponseError` → domain `CosmosConnectionError`
- [x] Include item ID and container name in error messages (not item content)
- [x] Ensure no secrets in exception messages
- [x] Log errors with sanitized context (item ID, container name only)

## Validation

- [x] Validate item dictionaries have required 'id' field before create/update
- [x] Validate partition key value is not None or empty string
- [x] Validate container name is not empty
- [x] Validate max_count for list_items is positive integer
- [x] Raise `ValueError` for invalid inputs with clear messages

## Testing

- [x] Create `tests/test_item_repository.py`
- [x] Mock `CosmosClient`, database, and container objects for all tests
- [x] Test `create_item()` succeeds with valid item and partition key
- [x] Test `create_item()` raises error for missing 'id' field
- [x] Test `create_item()` raises error for duplicate item ID in partition
- [x] Test `create_item()` raises error for partition key mismatch
- [x] Test `get_item()` returns correct item for valid ID and partition key
- [x] Test `get_item()` raises error when item not found
- [x] Test `get_item()` raises error for partition key mismatch
- [x] Test `update_item()` succeeds with valid item data
- [x] Test `update_item()` raises error for partition key mismatch
- [x] Test `update_item()` raises error when item['id'] doesn't match item_id parameter
- [x] Test `delete_item()` succeeds for existing item
- [x] Test `delete_item()` is idempotent (no error for missing item)
- [x] Test `delete_item()` raises error for partition key mismatch
- [x] Test `list_items()` returns empty list for container with no items
- [x] Test `list_items()` returns items up to max_count limit
- [x] Test `list_items()` handles SDK errors appropriately
- [x] Test no secrets or item content logged in any scenario
- [x] Use AAA (Arrange, Act, Assert) pattern in all tests
- [x] Use descriptive test names: `test_should_<behavior>_when_<condition>`
- [x] Verify test coverage ≥ 80% for item repository methods

## Documentation

- [x] Update `orbit/repositories/base.py` docstrings with partition key requirements
- [x] Document partition key handling in repository implementation
- [x] Add code examples in docstrings for common usage patterns
- [x] Document error scenarios and exception types raised

## Code Quality

- [x] Run `ruff check` and fix any linting errors
- [x] Run `ruff format` to ensure consistent formatting
- [x] Verify all functions are 5-20 lines (Clean Code principle)
- [x] Verify 0-2 parameters per function (use objects for more complex cases)
- [x] Ensure naming reveals intent (no abbreviations, clear verbs)
- [x] Remove any commented code or TODO markers
- [x] Verify no side effects in repository methods
