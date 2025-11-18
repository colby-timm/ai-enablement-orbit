# Implementation Tasks

## Prerequisites

- [ ] Verify `implement-connection-string-auth` change is complete and merged
- [ ] Review Azure Cosmos SDK documentation for database and container operations
- [ ] Confirm `azure-cosmos` dependency is installed (from connection auth change)

## Domain Exceptions

- [ ] Add `CosmosResourceNotFoundError` to `orbit/exceptions.py`
- [ ] Add `CosmosResourceExistsError` to `orbit/exceptions.py`
- [ ] Add `CosmosQuotaExceededError` to `orbit/exceptions.py` (for throughput limits)
- [ ] Add `CosmosInvalidPartitionKeyError` to `orbit/exceptions.py`
- [ ] Ensure all exceptions inherit from `OrbitError` base class
- [ ] Add docstrings explaining when each exception is raised

## Repository Protocol Extension

- [ ] Open `orbit/repositories/base.py`
- [ ] Add `list_containers()` method signature to `CosmosRepository` protocol
- [ ] Add `create_container(name, partition_key_path, throughput)` method signature
- [ ] Add `delete_container(name)` method signature
- [ ] Add `get_container_properties(name)` method signature
- [ ] Add type hints for all method parameters and return types
- [ ] Add docstrings explaining each method's purpose and parameters
- [ ] Mark existing placeholder methods with `# TODO: implement in concrete class`

## Concrete Repository Implementation

- [ ] Create `orbit/repositories/cosmos.py` file
- [ ] Import `CosmosClient` from `azure.cosmos`
- [ ] Import `PartitionKey` from `azure.cosmos.partition_key`
- [ ] Import domain exceptions from `orbit/exceptions`
- [ ] Create `CosmosContainerRepository` class
- [ ] Add `__init__(self, client: CosmosClient, database_name: str)` constructor
- [ ] Store client and database references as instance variables
- [ ] Implement `list_containers()`:
  - [ ] Call `database.list_containers()` from SDK
  - [ ] Return list of container names or container metadata dicts
  - [ ] Wrap SDK exceptions → `CosmosConnectionError`
  - [ ] Log operation (no secrets)
- [ ] Implement `create_container(name, partition_key_path, throughput=400)`:
  - [ ] Validate container name (alphanumeric, hyphens, max 255 chars)
  - [ ] Validate partition key path starts with `/`
  - [ ] Create `PartitionKey(path=partition_key_path)` object
  - [ ] Call `database.create_container(id=name, partition_key=..., offer_throughput=...)`
  - [ ] Handle duplicate container → raise `CosmosResourceExistsError`
  - [ ] Handle throughput quota → raise `CosmosQuotaExceededError`
  - [ ] Wrap other SDK exceptions → `CosmosConnectionError`
  - [ ] Return created container metadata
  - [ ] Log success (no secrets)
- [ ] Implement `delete_container(name)`:
  - [ ] Call `database.delete_container(name)`
  - [ ] Make idempotent (ignore 404 not found)
  - [ ] Wrap SDK exceptions → `CosmosConnectionError`
  - [ ] Log operation (no secrets)
- [ ] Implement `get_container_properties(name)`:
  - [ ] Call `database.get_container_client(name).read()`
  - [ ] Handle not found → raise `CosmosResourceNotFoundError`
  - [ ] Extract: name, partition key definition, throughput, indexing policy
  - [ ] Return properties dict or typed model
  - [ ] Wrap SDK exceptions → `CosmosConnectionError`
  - [ ] Log operation (no secrets)
- [ ] Ensure all methods are 5-20 lines (extract helpers if needed)
- [ ] Add type hints to all methods
- [ ] Add comprehensive docstrings with Google-style format

## Error Handling

- [ ] Map SDK `CosmosResourceNotFoundError` → domain `CosmosResourceNotFoundError`
- [ ] Map SDK `CosmosResourceExistsError` → domain `CosmosResourceExistsError`
- [ ] Map SDK throughput errors → domain `CosmosQuotaExceededError`
- [ ] Map SDK `CosmosHttpResponseError` → appropriate domain exception
- [ ] Include actionable context in all exception messages
- [ ] Ensure no secrets in exception messages
- [ ] Log errors with sanitized context

## Testing

- [ ] Create `tests/test_repositories.py`
- [ ] Mock `CosmosClient` and database objects for all tests
- [ ] Test `list_containers()` returns empty list for no containers
- [ ] Test `list_containers()` returns multiple container names
- [ ] Test `list_containers()` handles SDK connection errors
- [ ] Test `create_container()` succeeds with valid inputs
- [ ] Test `create_container()` raises error for duplicate container name
- [ ] Test `create_container()` raises error for invalid partition key path
- [ ] Test `create_container()` raises error for invalid container name
- [ ] Test `create_container()` raises error for throughput quota exceeded
- [ ] Test `delete_container()` succeeds for existing container
- [ ] Test `delete_container()` is idempotent (no error for missing container)
- [ ] Test `delete_container()` handles SDK errors
- [ ] Test `get_container_properties()` returns correct metadata
- [ ] Test `get_container_properties()` raises error for non-existent container
- [ ] Test `get_container_properties()` handles SDK errors
- [ ] Test no secrets logged in any test scenario
- [ ] Use AAA (Arrange, Act, Assert) pattern in all tests
- [ ] Use descriptive test names: `test_should_<behavior>_when_<condition>`
- [ ] Verify test coverage ≥ 80% for repository module
- [ ] Run `pytest tests/test_repositories.py -v`

## Code Quality

- [ ] Run `ruff check orbit/repositories/` and fix issues
- [ ] Run `ruff format orbit/repositories/` for consistent formatting
- [ ] Verify function length < 20 lines (extract helpers if needed)
- [ ] Verify descriptive variable names (no abbreviations like `cnt`, `pk`)
- [ ] Ensure single responsibility per method
- [ ] Verify 0-2 parameters per method (use dataclass if more needed)
- [ ] Remove all TODO comments from implementation
- [ ] Add/update docstrings with examples where helpful

## Integration Validation

- [ ] Manual test: List containers in emulator database
- [ ] Manual test: Create container with partition key `/id`
- [ ] Manual test: Get properties of created container
- [ ] Manual test: Delete created container
- [ ] Manual test: Verify error for creating duplicate container
- [ ] Manual test: Verify error for invalid partition key path

## Validation

- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Verify coverage: `pytest --cov=orbit --cov-report=term-missing`
- [ ] Ensure coverage ≥ 80% for all modules
- [ ] Run `openspec validate implement-cosmos-repository-containers --strict`
- [ ] Fix any validation errors or warnings

## Completion Checklist

- [ ] All tests passing
- [ ] Coverage ≥ 80%
- [ ] No ruff errors or warnings
- [ ] No secrets in logs or error messages
- [ ] OpenSpec validation passes
- [ ] Manual testing completed successfully
- [ ] Ready for code review
