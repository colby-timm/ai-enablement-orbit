# Implementation Tasks: Add Dependency Injection Framework

## 1. Configuration Enhancement (10 tasks)

- [x] Add `database_name: str | None` field to `OrbitSettings` class in `orbit/config.py`
- [x] Define constant `DATABASE_NAME_ENV = "ORBIT_DATABASE_NAME"` in `orbit/config.py`
- [x] Update `OrbitSettings.load()` to read `DATABASE_NAME_ENV` environment variable
- [x] Add unit test `test_settings_load_includes_database_name` in `tests/test_config.py`
- [x] Add unit test `test_settings_database_name_defaults_to_none_when_not_set` in `tests/test_config.py`
- [x] Update `README.md` to document `ORBIT_DATABASE_NAME` environment variable
- [x] Add example `.env.example` file showing all required environment variables
- [x] Run `make lint` to verify no style violations
- [x] Run `make test` to verify 80%+ coverage maintained
- [x] Commit changes: "feat(config): add database_name field to OrbitSettings"

## 2. Factory Implementation (15 tasks)

- [x] Create `orbit/factory.py` module with docstring explaining purpose
- [x] Implement `RepositoryFactory` class with `__init__(self, settings: OrbitSettings)`
- [x] Add `_client: CosmosClient | None` private attribute for caching
- [x] Add `_database_name: str` private attribute set from settings
- [x] Implement `_get_client(self) -> CosmosClient` method with lazy initialization
- [x] Use `ConnectionStringAuthStrategy` to create client in `_get_client()`
- [x] Raise `CosmosAuthError` in `_get_client()` when connection string missing
- [x] Raise `ValueError` in `_get_client()` when database name missing
- [x] Implement `get_container_repository(self) -> CosmosContainerRepository` method
- [x] Implement `get_item_repository(self) -> CosmosItemRepository` method
- [x] Add type hints for all methods and parameters
- [x] Add docstrings for class and all public methods
- [x] Run `make lint` to verify no style violations
- [x] Run `make format` to apply code formatting
- [x] Commit changes: "feat(factory): implement RepositoryFactory for dependency injection"

## 3. Factory Unit Tests (18 tasks)

- [x] Create `tests/test_factory.py` module
- [x] Add test `test_should_create_factory_with_settings` verifying initialization
- [x] Add test `test_should_cache_cosmos_client_across_calls` verifying client reuse
- [x] Add test `test_should_raise_auth_error_when_connection_string_missing`
- [x] Add test `test_should_raise_value_error_when_database_name_missing`
- [x] Add test `test_should_return_container_repository_with_client_and_database`
- [x] Add test `test_should_return_item_repository_with_client_and_database`
- [x] Add test `test_should_use_connection_string_from_settings` mocking auth strategy
- [x] Add test `test_should_instantiate_repository_with_correct_database_name`
- [x] Mock `ConnectionStringAuthStrategy.get_client()` in relevant tests
- [x] Mock `CosmosClient` to avoid real connections in unit tests
- [x] Use AAA (Arrange-Act-Assert) pattern in all tests
- [x] Use descriptive test names: `test_should_<behavior>_when_<condition>`
- [x] Verify no logic or conditionals in test bodies
- [x] Run `make test` to verify all tests pass
- [x] Verify coverage ≥80% for `orbit/factory.py`
- [x] Run `make lint` to verify no style violations
- [x] Commit changes: "test(factory): add comprehensive unit tests for RepositoryFactory"

## 4. CLI Command Wiring (12 tasks)

- [x] Import `RepositoryFactory` in `orbit/commands/containers.py`
- [x] Import `OrbitSettings` in `orbit/commands/containers.py`
- [x] Replace `_get_repository()` stub in `list_containers()` with factory call
- [x] Replace `_get_repository()` stub in `create_container()` with factory call
- [x] Replace `_get_repository()` stub in `delete_container()` with factory call
- [x] Instantiate `OrbitSettings.load()` once per command function
- [x] Pass settings to `RepositoryFactory` constructor
- [x] Call `factory.get_container_repository()` to get repository instance
- [x] Add error handling for `ValueError` (missing database name) with user-friendly message
- [x] Add error handling for `CosmosAuthError` with actionable guidance
- [x] Run `make lint` to verify no style violations
- [x] Commit changes: "feat(cli): wire RepositoryFactory into container commands"

## 5. Integration Tests (20 tasks)

- [x] Create `tests/integration/test_containers_e2e.py` module
- [x] Add `@pytest.mark.manual` decorator to all tests (requires emulator)
- [x] Add test `test_should_list_containers_from_real_database` using emulator
- [x] Add test `test_should_create_container_in_real_database` using emulator
- [x] Add test `test_should_delete_container_from_real_database` using emulator
- [x] Add test `test_should_fail_gracefully_when_database_name_not_set`
- [x] Add test `test_should_fail_gracefully_when_connection_string_invalid`
- [x] Add test `test_should_display_user_friendly_error_for_missing_config`
- [x] Use `os.environ` to set `ORBIT_DATABASE_NAME` for test database
- [x] Use emulator connection string: `AccountEndpoint=https://localhost:8081/...`
- [x] Create unique test database per test run (e.g., `test-orbit-{uuid}`)
- [x] Clean up test databases after test execution in fixture teardown
- [x] Verify JSON output when `--json` flag used in CLI invocation
- [x] Verify human-readable output when no flags used
- [x] Run tests with `make test-manual` (requires emulator running)
- [x] Document emulator setup in `tests/integration/README.md`
- [x] Add test execution instructions to README
- [x] Run `make lint` to verify no style violations
- [x] Verify all 8 manual tests pass with emulator running
- [x] Commit changes: "test(integration): add end-to-end tests for container commands"

## 6. Documentation (10 tasks)

- [x] Update `README.md` "Configuration" section with `ORBIT_DATABASE_NAME` variable
- [x] Add "Environment Variables" table with all required vars and descriptions
- [x] Update `README.md` "Usage" section with example showing env var setup
- [x] Add troubleshooting section for "Database name not configured" error
- [x] Add troubleshooting section for "Connection string missing" error
- [x] Create `.env.example` with commented examples for all env vars
- [x] Update `tests/integration/README.md` with factory testing notes
- [x] Add docstring to `RepositoryFactory` class explaining usage pattern
- [x] Run `make lint` to verify markdown formatting
- [x] Commit changes: "docs: update README with dependency injection and configuration"

## 7. Validation and Completion (10 tasks)

- [x] Run `make clean` to remove cached artifacts
- [x] Run `make install` to ensure fresh environment
- [x] Run `make test` and verify 93+ tests pass with ≥80% coverage
- [x] Run `make test-manual` with emulator and verify 8 manual tests pass
- [x] Run `make lint` and verify zero errors
- [x] Run `openspec list` and verify change shows 100% completion
- [x] Run `openspec validate add-dependency-injection-framework --strict` successfully
- [x] Test CLI manually: `ORBIT_DATABASE_NAME=mydb ORBIT_COSMOS_CONNECTION_STRING=... uv run orbit containers list`
- [x] Verify factory caches client (check for single connection in logs)
- [x] Final commit: "chore: mark add-dependency-injection-framework complete"

---

**Total Tasks**: 95 tasks across 7 phases
**Estimated Effort**: 4-6 hours for implementation, 2-3 hours for testing
**Dependencies**: Requires completed auth, repository, and CLI command changes
