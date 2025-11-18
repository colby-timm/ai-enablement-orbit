# Implementation Tasks

## Prerequisites

- [ ] Verify `implement-connection-string-auth` change is complete and merged
- [ ] Verify `implement-cosmos-repository-containers` change is complete and merged
- [ ] Review Azure Cosmos SDK documentation for item CRUD operations
- [ ] Confirm `azure-cosmos` dependency is installed

## Domain Exceptions

- [ ] Add `CosmosItemNotFoundError` to `orbit/exceptions.py`
- [ ] Add `CosmosPartitionKeyMismatchError` to `orbit/exceptions.py`
- [ ] Add `CosmosDuplicateItemError` to `orbit/exceptions.py` (for duplicate IDs in partition)
- [ ] Ensure all exceptions inherit from `OrbitError` base class
- [ ] Add docstrings explaining when each exception is raised
- [ ] Document expected HTTP status codes that trigger each exception

## Repository Protocol Extension

- [ ] Open `orbit/repositories/base.py`
- [ ] Replace `get_item(item_id)` with `get_item(container_name, item_id, partition_key_value)` signature
- [ ] Replace `list_items()` with `list_items(container_name, max_count=100)` signature
- [ ] Add `create_item(container_name, item, partition_key_value)` method signature
- [ ] Add `update_item(container_name, item_id, item, partition_key_value)` method signature
- [ ] Add `delete_item(container_name, item_id, partition_key_value)` method signature
- [ ] Add type hints: use `dict[str, Any]` for item data, `str` for IDs and partition keys
- [ ] Add comprehensive docstrings explaining parameters, return types, and exceptions
- [ ] Remove TODO comments from method signatures

## Concrete Repository Implementation

- [ ] Open or create `orbit/repositories/cosmos.py` file
- [ ] Import required types: `Dict`, `Any`, `Optional`, `List` from `typing`
- [ ] Import `CosmosClient`, `exceptions` from `azure.cosmos`
- [ ] Import domain exceptions from `orbit/exceptions`
- [ ] Ensure `CosmosItemRepository` class exists (or extend existing repository class)
- [ ] Add helper method `_get_container_client(container_name)` to retrieve container client
- [ ] Implement `create_item(container_name, item, partition_key_value)`:
  - [ ] Validate item is a dictionary with 'id' field
  - [ ] Get container client via helper method
  - [ ] Call `container.create_item(body=item, partition_key=partition_key_value)`
  - [ ] Handle duplicate ID → raise `CosmosDuplicateItemError`
  - [ ] Handle partition key mismatch (400) → raise `CosmosPartitionKeyMismatchError`
  - [ ] Wrap other SDK exceptions → `CosmosConnectionError`
  - [ ] Return created item dictionary
  - [ ] Log operation (no secrets, no item content)
- [ ] Implement `get_item(container_name, item_id, partition_key_value)`:
  - [ ] Get container client via helper method
  - [ ] Call `container.read_item(item=item_id, partition_key=partition_key_value)`
  - [ ] Handle not found (404) → raise `CosmosItemNotFoundError`
  - [ ] Handle partition key mismatch → raise `CosmosPartitionKeyMismatchError`
  - [ ] Wrap other SDK exceptions → `CosmosConnectionError`
  - [ ] Return item dictionary
  - [ ] Log operation (no secrets)
- [ ] Implement `update_item(container_name, item_id, item, partition_key_value)`:
  - [ ] Validate item is a dictionary
  - [ ] Ensure item['id'] matches item_id parameter
  - [ ] Get container client via helper method
  - [ ] Call `container.upsert_item(body=item, partition_key=partition_key_value)`
  - [ ] Handle partition key mismatch → raise `CosmosPartitionKeyMismatchError`
  - [ ] Wrap other SDK exceptions → `CosmosConnectionError`
  - [ ] Return updated item dictionary
  - [ ] Log operation (no secrets)
- [ ] Implement `delete_item(container_name, item_id, partition_key_value)`:
  - [ ] Get container client via helper method
  - [ ] Call `container.delete_item(item=item_id, partition_key=partition_key_value)`
  - [ ] Make idempotent: ignore 404 not found errors
  - [ ] Handle partition key mismatch → raise `CosmosPartitionKeyMismatchError`
  - [ ] Wrap other SDK exceptions → `CosmosConnectionError`
  - [ ] Log operation (no secrets)
- [ ] Implement `list_items(container_name, max_count=100)`:
  - [ ] Get container client via helper method
  - [ ] Call `container.query_items(query="SELECT * FROM c", max_item_count=max_count)`
  - [ ] Convert query iterator to list (limit to max_count items)
  - [ ] Handle empty results gracefully (return empty list)
  - [ ] Wrap SDK exceptions → `CosmosConnectionError`
  - [ ] Log operation with item count (no secrets, no item content)
- [ ] Ensure all methods are 5-20 lines (extract helpers if needed)
- [ ] Add type hints to all methods
- [ ] Add comprehensive docstrings with Google-style format

## Error Handling

- [ ] Map SDK `CosmosResourceNotFoundError` (404) for items → domain `CosmosItemNotFoundError`
- [ ] Map SDK `CosmosHttpResponseError` (409 conflict) → domain `CosmosDuplicateItemError`
- [ ] Map SDK `CosmosHttpResponseError` (400 with partition key message) → `CosmosPartitionKeyMismatchError`
- [ ] Map other SDK `CosmosHttpResponseError` → domain `CosmosConnectionError`
- [ ] Include item ID and container name in error messages (not item content)
- [ ] Ensure no secrets in exception messages
- [ ] Log errors with sanitized context (item ID, container name only)

## Validation

- [ ] Validate item dictionaries have required 'id' field before create/update
- [ ] Validate partition key value is not None or empty string
- [ ] Validate container name is not empty
- [ ] Validate max_count for list_items is positive integer
- [ ] Raise `ValueError` for invalid inputs with clear messages

## Testing

- [ ] Create `tests/test_item_repository.py`
- [ ] Mock `CosmosClient`, database, and container objects for all tests
- [ ] Test `create_item()` succeeds with valid item and partition key
- [ ] Test `create_item()` raises error for missing 'id' field
- [ ] Test `create_item()` raises error for duplicate item ID in partition
- [ ] Test `create_item()` raises error for partition key mismatch
- [ ] Test `get_item()` returns correct item for valid ID and partition key
- [ ] Test `get_item()` raises error when item not found
- [ ] Test `get_item()` raises error for partition key mismatch
- [ ] Test `update_item()` succeeds with valid item data
- [ ] Test `update_item()` raises error for partition key mismatch
- [ ] Test `update_item()` raises error when item['id'] doesn't match item_id parameter
- [ ] Test `delete_item()` succeeds for existing item
- [ ] Test `delete_item()` is idempotent (no error for missing item)
- [ ] Test `delete_item()` raises error for partition key mismatch
- [ ] Test `list_items()` returns empty list for container with no items
- [ ] Test `list_items()` returns items up to max_count limit
- [ ] Test `list_items()` handles SDK errors appropriately
- [ ] Test no secrets or item content logged in any scenario
- [ ] Use AAA (Arrange, Act, Assert) pattern in all tests
- [ ] Use descriptive test names: `test_should_<behavior>_when_<condition>`
- [ ] Verify test coverage ≥ 80% for item repository methods

## Documentation

- [ ] Update `orbit/repositories/base.py` docstrings with partition key requirements
- [ ] Document partition key handling in repository implementation
- [ ] Add code examples in docstrings for common usage patterns
- [ ] Document error scenarios and exception types raised

## Code Quality

- [ ] Run `ruff check` and fix any linting errors
- [ ] Run `ruff format` to ensure consistent formatting
- [ ] Verify all functions are 5-20 lines (Clean Code principle)
- [ ] Verify 0-2 parameters per function (use objects for more complex cases)
- [ ] Ensure naming reveals intent (no abbreviations, clear verbs)
- [ ] Remove any commented code or TODO markers
- [ ] Verify no side effects in repository methods
