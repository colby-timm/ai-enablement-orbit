# Change: Add Integration Tests Against Emulator

## Why

The current test suite only includes unit tests with mocked dependencies. Without integration tests running against the actual Cosmos DB Emulator, we cannot verify end-to-end flows or catch SDK integration issues, authentication problems, or real-world error scenarios. Integration tests provide confidence that the complete stack works correctly before production deployment, catching issues that unit tests miss.

## What Changes

- Create integration test suite in `tests/integration/` directory
- Implement tests that connect to local Cosmos DB Emulator using connection string authentication
- Add test fixtures for emulator connection setup and database/container lifecycle management
- Test end-to-end authentication flow with connection string strategy
- Test container lifecycle: create, list, get properties, delete operations
- Test item CRUD operations: create, get, update, delete with proper partition key handling
- Test query operations including cross-partition queries, pagination, and result limits
- Add pytest markers to distinguish integration tests from unit tests (`@pytest.mark.integration`)
- Document emulator setup requirements and integration test execution in README
- Configure CI/CD to optionally run integration tests (require emulator running)
- Ensure integration tests clean up resources (containers, items) after execution

## Impact

- Affected specs:
  - ADDS new `testing-integration` capability for integration test requirements
- Affected code:
  - `tests/integration/` (new directory): All integration test files
  - `tests/conftest.py`: Shared fixtures for emulator connection and test database setup
  - `pyproject.toml`: Add pytest markers configuration for integration tests
  - `README.md`: Document how to run integration tests and emulator setup
  - `Makefile` or CI configuration: Add integration test execution commands
- **BREAKING**: None—this is additive testing infrastructure
- **DEPENDS ON**: All previous implementation specs (#1-#6) must be complete for full integration test coverage:
  - Connection String Authentication (#1)
  - Cosmos Repository - Container Operations (#2)
  - Cosmos Repository - Item Operations (#3)
  - Container Management CLI Commands (#4)
  - Item Management CLI Commands (#5)
  - Query Command with Pagination (#6)

## Dependencies

- Requires: All core features implemented (auth, repository, CLI commands)
- Requires: Cosmos DB Emulator installed and running locally
- Requires: `azure-cosmos` SDK already integrated
- Enables: Confidence in production deployments through verified end-to-end testing

## Notes

- Integration tests should use a dedicated test database (e.g., `OrbitTestDB`) to avoid conflicts
- Tests must create and clean up containers/items to prevent resource leaks
- Connection string for emulator: `AccountEndpoint=https://localhost:8081/;AccountKey=<emulator-key>`
- Emulator must be started before running integration tests (document prerequisite)
- Integration tests will be slower than unit tests—run separately via pytest marker
- Consider adding `--integration` flag to test execution or separate make target
- Integration tests should verify real error handling: network failures, auth errors, partition key mismatches
- Aim for 100% coverage of critical paths through integration tests, complementing unit test coverage
