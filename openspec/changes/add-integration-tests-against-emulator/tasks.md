# Implementation Tasks

## Prerequisites

- [ ] Verify all core features are implemented: auth (#1), repository container ops (#2), repository item ops (#3), container CLI (#4), item CLI (#5), query CLI (#6)
- [ ] Install Cosmos DB Emulator on local machine (macOS/Windows/Linux)
- [ ] Verify emulator is accessible at `https://localhost:8081`
- [ ] Obtain emulator connection string with default key
- [ ] Review Azure Cosmos SDK documentation for test patterns
- [ ] Confirm pytest and pytest-cov are installed in dev dependencies

## Project Configuration

- [ ] Add pytest marker for integration tests in `pyproject.toml`:
  - [ ] Add `[tool.pytest.ini_options]` markers configuration
  - [ ] Define `integration` marker: `integration: marks tests as integration tests requiring emulator`
- [ ] Update `Makefile` or create test commands:
  - [ ] Add `test-unit` target: runs unit tests only (excludes integration marker)
  - [ ] Add `test-integration` target: runs integration tests only (requires emulator)
  - [ ] Add `test-all` target: runs both unit and integration tests
- [ ] Update `README.md` with integration test documentation:
  - [ ] Document emulator setup and installation
  - [ ] Document emulator connection string configuration
  - [ ] Document how to run integration tests
  - [ ] Document test database naming convention

## Test Infrastructure

- [ ] Create `tests/integration/` directory
- [ ] Create `tests/integration/__init__.py` (empty or with shared helpers)
- [ ] Create or update `tests/conftest.py` with shared fixtures:
  - [ ] Create `emulator_connection_string` fixture returning emulator connection string
  - [ ] Create `test_settings` fixture with OrbitSettings configured for emulator
  - [ ] Create `test_database_name` fixture returning unique test database name (e.g., `OrbitTestDB`)
  - [ ] Create `cosmos_client` fixture using ConnectionStringAuthStrategy
  - [ ] Create `test_database` fixture that creates/deletes test database
  - [ ] Create `test_container` fixture that creates/deletes test container
  - [ ] Add cleanup logic to ensure resources are deleted after tests

## Integration Test: Authentication

- [ ] Create `tests/integration/test_auth_integration.py`
- [ ] Test successful client creation with emulator connection string:
  - [ ] Use real ConnectionStringAuthStrategy with emulator credentials
  - [ ] Verify CosmosClient is returned and functional
  - [ ] Verify no exceptions raised during initialization
- [ ] Test client can list databases (smoke test for connectivity):
  - [ ] Call client.list_databases() or similar
  - [ ] Verify non-empty result or successful response
- [ ] Test invalid connection string raises appropriate exception:
  - [ ] Use malformed connection string
  - [ ] Verify CosmosAuthError raised with helpful message
- [ ] Mark all tests with `@pytest.mark.integration` decorator

## Integration Test: Container Operations

- [ ] Create `tests/integration/test_containers_integration.py`
- [ ] Test create container with partition key:
  - [ ] Use repository method to create container with specified partition key
  - [ ] Verify container exists in emulator
  - [ ] Verify partition key configuration is correct
- [ ] Test list containers:
  - [ ] Create multiple test containers
  - [ ] Use repository method to list containers
  - [ ] Verify all created containers appear in list
- [ ] Test get container properties:
  - [ ] Create a test container
  - [ ] Use repository method to get container properties
  - [ ] Verify returned properties match expected values (name, partition key)
- [ ] Test delete container:
  - [ ] Create a test container
  - [ ] Use repository method to delete container
  - [ ] Verify container no longer exists
- [ ] Test error handling for duplicate container creation:
  - [ ] Create a container
  - [ ] Attempt to create same container again
  - [ ] Verify appropriate exception raised
- [ ] Mark all tests with `@pytest.mark.integration` decorator
- [ ] Ensure cleanup in teardown or fixtures

## Integration Test: Item Operations

- [ ] Create `tests/integration/test_items_integration.py`
- [ ] Test create item with partition key:
  - [ ] Create test container with partition key
  - [ ] Use repository method to create item
  - [ ] Verify item exists in container
- [ ] Test get item by id and partition key:
  - [ ] Create test item
  - [ ] Use repository method to retrieve item
  - [ ] Verify retrieved item matches created item
- [ ] Test update item:
  - [ ] Create test item
  - [ ] Use repository method to update item properties
  - [ ] Retrieve updated item and verify changes
- [ ] Test delete item:
  - [ ] Create test item
  - [ ] Use repository method to delete item
  - [ ] Verify item no longer exists
- [ ] Test partition key mismatch error:
  - [ ] Create item with partition key value A
  - [ ] Attempt to get item with partition key value B
  - [ ] Verify appropriate exception raised
- [ ] Test item not found error:
  - [ ] Attempt to retrieve non-existent item
  - [ ] Verify appropriate exception raised
- [ ] Mark all tests with `@pytest.mark.integration` decorator
- [ ] Ensure cleanup in teardown or fixtures

## Integration Test: Query Operations

- [ ] Create `tests/integration/test_query_integration.py`
- [ ] Test basic SQL query:
  - [ ] Create test container with multiple items
  - [ ] Execute simple SELECT query
  - [ ] Verify expected items returned
- [ ] Test query with WHERE clause:
  - [ ] Create test items with various properties
  - [ ] Execute query with filter condition
  - [ ] Verify only matching items returned
- [ ] Test cross-partition query:
  - [ ] Create items across multiple partition keys
  - [ ] Execute query without partition key filter
  - [ ] Verify results span multiple partitions
- [ ] Test pagination with max item count:
  - [ ] Create more items than default page size (e.g., 150 items)
  - [ ] Execute query with max_item_count limit (e.g., 100)
  - [ ] Verify pagination works and continuation token is provided
- [ ] Test result set streaming for large queries:
  - [ ] Create large dataset
  - [ ] Execute query and iterate through results
  - [ ] Verify streaming works without loading all results in memory
- [ ] Test RU cost tracking:
  - [ ] Execute query
  - [ ] Verify RU cost is tracked and reported (if feature implemented)
- [ ] Test query with no results:
  - [ ] Execute query with filter that matches no items
  - [ ] Verify empty result set returned without errors
- [ ] Mark all tests with `@pytest.mark.integration` decorator
- [ ] Ensure cleanup in teardown or fixtures

## Integration Test: CLI End-to-End

- [ ] Create `tests/integration/test_cli_e2e_integration.py` (optional but recommended)
- [ ] Test full container lifecycle via CLI:
  - [ ] Invoke `orbit containers create` command
  - [ ] Invoke `orbit containers list` command and verify created container
  - [ ] Invoke `orbit containers delete` command
  - [ ] Verify container removed
- [ ] Test full item lifecycle via CLI:
  - [ ] Create test container
  - [ ] Invoke `orbit items create` with JSON file
  - [ ] Invoke `orbit items get` and verify retrieval
  - [ ] Invoke `orbit items update` with modified JSON
  - [ ] Invoke `orbit items delete` and verify removal
- [ ] Test query command via CLI:
  - [ ] Create test items
  - [ ] Invoke `orbit query` with SQL query
  - [ ] Verify results formatted correctly
- [ ] Test `--yes` flag bypasses confirmation prompts:
  - [ ] Invoke delete command with `--yes` flag
  - [ ] Verify no prompt displayed
- [ ] Test `--json` flag outputs machine-readable format:
  - [ ] Invoke list command with `--json` flag
  - [ ] Parse output as JSON and verify structure
- [ ] Mark all tests with `@pytest.mark.integration` decorator

## Code Quality

- [ ] Run `ruff check tests/integration/` and fix any issues
- [ ] Run `ruff format tests/integration/` to ensure formatting
- [ ] Verify test names follow `test_should_<behavior>_when_<condition>` convention
- [ ] Ensure all tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Verify no test logic (conditionals, loops) in test functions
- [ ] Add docstrings to test functions explaining what is being verified

## Documentation

- [ ] Document emulator setup in `README.md`:
  - [ ] Installation instructions for macOS, Windows, Linux
  - [ ] How to start emulator
  - [ ] Default connection string and credentials
- [ ] Document integration test execution:
  - [ ] Command to run integration tests: `pytest -m integration`
  - [ ] Command to run without integration tests: `pytest -m "not integration"`
  - [ ] Command to run all tests: `pytest`
- [ ] Document test database naming and cleanup:
  - [ ] Explain `OrbitTestDB` convention
  - [ ] Note that tests clean up after themselves
- [ ] Add troubleshooting section:
  - [ ] What to do if emulator is not running
  - [ ] How to reset emulator state if tests fail
  - [ ] Common error messages and solutions

## Validation

- [ ] Run integration tests with emulator running: `pytest -m integration -v`
- [ ] Verify all integration tests pass
- [ ] Run full test suite: `pytest -v`
- [ ] Verify coverage still meets ≥80% threshold: `pytest --cov=orbit --cov-report=term-missing`
- [ ] Manually verify emulator state is clean after test run (no leftover containers)
- [ ] Run `openspec validate add-integration-tests-against-emulator --strict`

## CI/CD Configuration (Optional)

- [ ] Update CI pipeline to support integration tests:
  - [ ] Add job/step to install Cosmos DB Emulator (if supported by CI platform)
  - [ ] Add job/step to start emulator before integration tests
  - [ ] Configure integration test execution in CI
  - [ ] Make integration tests optional or separate from unit test workflow
- [ ] Document CI requirements in contribution guidelines

## Completion Checklist

- [ ] All integration tests created and passing
- [ ] Unit test coverage maintained ≥80%
- [ ] Integration tests properly marked and separable
- [ ] Emulator setup documented
- [ ] Test cleanup verified (no resource leaks)
- [ ] OpenSpec validation passes
- [ ] README updated with integration test instructions
- [ ] Ready for code review
