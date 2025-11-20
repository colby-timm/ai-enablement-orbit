# Implementation Tasks: Add Dependency Injection Framework

## 1. Configuration Enhancement (10 tasks)

- [ ] Add `database_name: str | None` field to `OrbitSettings` class in `orbit/config.py`
- [ ] Define constant `DATABASE_NAME_ENV = "ORBIT_DATABASE_NAME"` in `orbit/config.py`
- [ ] Update `OrbitSettings.load()` to read `DATABASE_NAME_ENV` environment variable
- [ ] Add unit test `test_settings_load_includes_database_name` in `tests/test_config.py`
- [ ] Add unit test `test_settings_database_name_defaults_to_none_when_not_set` in `tests/test_config.py`
- [ ] Update `README.md` to document `ORBIT_DATABASE_NAME` environment variable
- [ ] Add example `.env.example` file showing all required environment variables
- [ ] Run `make lint` to verify no style violations
- [ ] Run `make test` to verify 80%+ coverage maintained
- [ ] Commit changes: "feat(config): add database_name field to OrbitSettings"

## 2. Factory Implementation (15 tasks)

- [ ] Create `orbit/factory.py` module with docstring explaining purpose
- [ ] Implement `RepositoryFactory` class with `__init__(self, settings: OrbitSettings)`
- [ ] Add `_client: CosmosClient | None` private attribute for caching
- [ ] Add `_database_name: str` private attribute set from settings
- [ ] Implement `_get_client(self) -> CosmosClient` method with lazy initialization
- [ ] Use `ConnectionStringAuthStrategy` to create client in `_get_client()`
- [ ] Raise `CosmosAuthError` in `_get_client()` when connection string missing
- [ ] Raise `ValueError` in `_get_client()` when database name missing
- [ ] Implement `get_container_repository(self) -> CosmosContainerRepository` method
- [ ] Implement `get_item_repository(self) -> CosmosItemRepository` method
- [ ] Add type hints for all methods and parameters
- [ ] Add docstrings for class and all public methods
- [ ] Run `make lint` to verify no style violations
- [ ] Run `make format` to apply code formatting
- [ ] Commit changes: "feat(factory): implement RepositoryFactory for dependency injection"

## 3. Factory Unit Tests (18 tasks)

- [ ] Create `tests/test_factory.py` module
- [ ] Add test `test_should_create_factory_with_settings` verifying initialization
- [ ] Add test `test_should_cache_cosmos_client_across_calls` verifying client reuse
- [ ] Add test `test_should_raise_auth_error_when_connection_string_missing`
- [ ] Add test `test_should_raise_value_error_when_database_name_missing`
- [ ] Add test `test_should_return_container_repository_with_client_and_database`
- [ ] Add test `test_should_return_item_repository_with_client_and_database`
- [ ] Add test `test_should_use_connection_string_from_settings` mocking auth strategy
- [ ] Add test `test_should_instantiate_repository_with_correct_database_name`
- [ ] Mock `ConnectionStringAuthStrategy.get_client()` in relevant tests
- [ ] Mock `CosmosClient` to avoid real connections in unit tests
- [ ] Use AAA (Arrange-Act-Assert) pattern in all tests
- [ ] Use descriptive test names: `test_should_<behavior>_when_<condition>`
- [ ] Verify no logic or conditionals in test bodies
- [ ] Run `make test` to verify all tests pass
- [ ] Verify coverage ≥80% for `orbit/factory.py`
- [ ] Run `make lint` to verify no style violations
- [ ] Commit changes: "test(factory): add comprehensive unit tests for RepositoryFactory"

## 4. CLI Command Wiring (12 tasks)

- [ ] Import `RepositoryFactory` in `orbit/commands/containers.py`
- [ ] Import `OrbitSettings` in `orbit/commands/containers.py`
- [ ] Replace `_get_repository()` stub in `list_containers()` with factory call
- [ ] Replace `_get_repository()` stub in `create_container()` with factory call
- [ ] Replace `_get_repository()` stub in `delete_container()` with factory call
- [ ] Instantiate `OrbitSettings.load()` once per command function
- [ ] Pass settings to `RepositoryFactory` constructor
- [ ] Call `factory.get_container_repository()` to get repository instance
- [ ] Add error handling for `ValueError` (missing database name) with user-friendly message
- [ ] Add error handling for `CosmosAuthError` with actionable guidance
- [ ] Run `make lint` to verify no style violations
- [ ] Commit changes: "feat(cli): wire RepositoryFactory into container commands"

## 5. Integration Tests (20 tasks)

- [ ] Create `tests/integration/test_containers_e2e.py` module
- [ ] Add `@pytest.mark.manual` decorator to all tests (requires emulator)
- [ ] Add test `test_should_list_containers_from_real_database` using emulator
- [ ] Add test `test_should_create_container_in_real_database` using emulator
- [ ] Add test `test_should_delete_container_from_real_database` using emulator
- [ ] Add test `test_should_fail_gracefully_when_database_name_not_set`
- [ ] Add test `test_should_fail_gracefully_when_connection_string_invalid`
- [ ] Add test `test_should_display_user_friendly_error_for_missing_config`
- [ ] Use `os.environ` to set `ORBIT_DATABASE_NAME` for test database
- [ ] Use emulator connection string: `AccountEndpoint=https://localhost:8081/...`
- [ ] Create unique test database per test run (e.g., `test-orbit-{uuid}`)
- [ ] Clean up test databases after test execution in fixture teardown
- [ ] Verify JSON output when `--json` flag used in CLI invocation
- [ ] Verify human-readable output when no flags used
- [ ] Run tests with `make test-manual` (requires emulator running)
- [ ] Document emulator setup in `tests/integration/README.md`
- [ ] Add test execution instructions to README
- [ ] Run `make lint` to verify no style violations
- [ ] Verify all 8 manual tests pass with emulator running
- [ ] Commit changes: "test(integration): add end-to-end tests for container commands"

## 6. Documentation (10 tasks)

- [ ] Update `README.md` "Configuration" section with `ORBIT_DATABASE_NAME` variable
- [ ] Add "Environment Variables" table with all required vars and descriptions
- [ ] Update `README.md` "Usage" section with example showing env var setup
- [ ] Add troubleshooting section for "Database name not configured" error
- [ ] Add troubleshooting section for "Connection string missing" error
- [ ] Create `.env.example` with commented examples for all env vars
- [ ] Update `tests/integration/README.md` with factory testing notes
- [ ] Add docstring to `RepositoryFactory` class explaining usage pattern
- [ ] Run `make lint` to verify markdown formatting
- [ ] Commit changes: "docs: update README with dependency injection and configuration"

## 7. Validation and Completion (10 tasks)

- [ ] Run `make clean` to remove cached artifacts
- [ ] Run `make install` to ensure fresh environment
- [ ] Run `make test` and verify 93+ tests pass with ≥80% coverage
- [ ] Run `make test-manual` with emulator and verify 8 manual tests pass
- [ ] Run `make lint` and verify zero errors
- [ ] Run `openspec list` and verify change shows 100% completion
- [ ] Run `openspec validate add-dependency-injection-framework --strict` successfully
- [ ] Test CLI manually: `ORBIT_DATABASE_NAME=mydb ORBIT_COSMOS_CONNECTION_STRING=... uv run orbit containers list`
- [ ] Verify factory caches client (check for single connection in logs)
- [ ] Final commit: "chore: mark add-dependency-injection-framework complete"

---

**Total Tasks**: 95 tasks across 7 phases
**Estimated Effort**: 4-6 hours for implementation, 2-3 hours for testing
**Dependencies**: Requires completed auth, repository, and CLI command changes
