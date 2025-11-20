# Implementation Tasks

## Prerequisites

- [x] Verify `implement-connection-string-auth` change is complete and merged
- [x] Review Azure Cosmos SDK documentation for database and container operations
- [x] Confirm `azure-cosmos` dependency is installed (from connection auth change)

## Domain Exceptions

- [x] Add `CosmosResourceNotFoundError` to `orbit/exceptions.py`
- [x] Add `CosmosResourceExistsError` to `orbit/exceptions.py`
- [x] Add `CosmosQuotaExceededError` to `orbit/exceptions.py` (for throughput limits)
- [x] Add `CosmosInvalidPartitionKeyError` to `orbit/exceptions.py`
- [x] Ensure all exceptions inherit from `OrbitError` base class
- [x] Add docstrings explaining when each exception is raised

## Repository Protocol Extension

- [x] Open `orbit/repositories/base.py`
- [x] Add `list_containers()` method signature to `CosmosRepository` protocol
- [x] Add `create_container(name, partition_key_path, throughput)` method signature
- [x] Add `delete_container(name)` method signature
- [x] Add `get_container_properties(name)` method signature
- [x] Add type hints for all method parameters and return types
- [x] Add docstrings explaining each method's purpose and parameters
- [x] Mark existing placeholder methods with `# TODO: implement in concrete class`

## Concrete Repository Implementation

- [x] Create `orbit/repositories/cosmos.py` file
- [x] Import `CosmosClient` from `azure.cosmos`
- [x] Import `PartitionKey` from `azure.cosmos.partition_key`
- [x] Import domain exceptions from `orbit/exceptions`
- [x] Create `CosmosContainerRepository` class
- [x] Add `__init__(self, client: CosmosClient, database_name: str)` constructor
- [x] Store client and database references as instance variables
- [x] Implement `list_containers()`:
  - [x] Call `database.list_containers()` from SDK
  - [x] Return list of container names or container metadata dicts
  - [x] Wrap SDK exceptions → `CosmosConnectionError`
  - [x] Log operation (no secrets)
- [x] Implement `create_container(name, partition_key_path, throughput=400)`:
  - [x] Validate container name (alphanumeric, hyphens, max 255 chars)
  - [x] Validate partition key path starts with `/`
  - [x] Create `PartitionKey(path=partition_key_path)` object
  - [x] Call `database.create_container(id=name, partition_key=..., offer_throughput=...)`
  - [x] Handle duplicate container → raise `CosmosResourceExistsError`
  - [x] Handle throughput quota → raise `CosmosQuotaExceededError`
  - [x] Wrap other SDK exceptions → `CosmosConnectionError`
  - [x] Return created container metadata
  - [x] Log success (no secrets)
- [x] Implement `delete_container(name)`:
  - [x] Call `database.delete_container(name)`
  - [x] Make idempotent (ignore 404 not found)
  - [x] Wrap SDK exceptions → `CosmosConnectionError`
  - [x] Log operation (no secrets)
- [x] Implement `get_container_properties(name)`:
  - [x] Call `database.get_container_client(name).read()`
  - [x] Handle not found → raise `CosmosResourceNotFoundError`
  - [x] Extract: name, partition key definition, throughput, indexing policy
  - [x] Return properties dict or typed model
  - [x] Wrap SDK exceptions → `CosmosConnectionError`
  - [x] Log operation (no secrets)
- [x] Ensure all methods are 5-20 lines (extract helpers if needed)
- [x] Add type hints to all methods
- [x] Add comprehensive docstrings with Google-style format

## Error Handling

- [x] Map SDK `CosmosResourceNotFoundError` → domain `CosmosResourceNotFoundError`
- [x] Map SDK `CosmosResourceExistsError` → domain `CosmosResourceExistsError`
- [x] Map SDK throughput errors → domain `CosmosQuotaExceededError`
- [x] Map SDK `CosmosHttpResponseError` → appropriate domain exception
- [x] Include actionable context in all exception messages
- [x] Ensure no secrets in exception messages
- [x] Log errors with sanitized context

## Testing

- [x] Create `tests/test_repositories.py`
- [x] Mock `CosmosClient` and database objects for all tests
- [x] Test `list_containers()` returns empty list for no containers
- [x] Test `list_containers()` returns multiple container names
- [x] Test `list_containers()` handles SDK connection errors
- [x] Test `create_container()` succeeds with valid inputs
- [x] Test `create_container()` raises error for duplicate container name
- [x] Test `create_container()` raises error for invalid partition key path
- [x] Test `create_container()` raises error for invalid container name
- [x] Test `create_container()` raises error for throughput quota exceeded
- [x] Test `delete_container()` succeeds for existing container
- [x] Test `delete_container()` is idempotent (no error for missing container)
- [x] Test `delete_container()` handles SDK errors
- [x] Test `get_container_properties()` returns correct metadata
- [x] Test `get_container_properties()` raises error for non-existent container
- [x] Test `get_container_properties()` handles SDK errors
- [x] Test no secrets logged in any test scenario
- [x] Use AAA (Arrange, Act, Assert) pattern in all tests
- [x] Use descriptive test names: `test_should_<behavior>_when_<condition>`
- [x] Verify test coverage ≥ 80% for repository module
- [x] Run `pytest tests/test_repositories.py -v`

## Code Quality

- [x] Run `ruff check orbit/repositories/` and fix issues
- [x] Run `ruff format orbit/repositories/` for consistent formatting
- [x] Verify function length < 20 lines (extract helpers if needed)
- [x] Verify descriptive variable names (no abbreviations like `cnt`, `pk`)
- [x] Ensure single responsibility per method
- [x] Verify 0-2 parameters per method (use dataclass if more needed)
- [x] Remove all TODO comments from implementation
- [x] Add/update docstrings with examples where helpful

## Integration Validation

- [x] Manual test: List containers in emulator database
- [x] Manual test: Create container with partition key `/id`
- [x] Manual test: Get properties of created container
- [x] Manual test: Delete created container
- [x] Manual test: Verify error for creating duplicate container
- [x] Manual test: Verify error for invalid partition key path

## Validation

- [x] Run full test suite: `pytest tests/ -v`
- [x] Verify coverage: `pytest --cov=orbit --cov-report=term-missing`
- [x] Ensure coverage ≥ 80% for all modules
- [x] Run `openspec validate implement-cosmos-repository-containers --strict`
- [x] Fix any validation errors or warnings

## Completion Checklist

- [x] All tests passing
- [x] Coverage ≥ 80%
- [x] No ruff errors or warnings
- [x] No secrets in logs or error messages
- [x] OpenSpec validation passes
- [x] Manual testing completed successfully
- [x] Ready for code review
