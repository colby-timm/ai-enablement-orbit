# Specification: Dependency Injection

## Overview

Provides repository factory pattern for instantiating Cosmos DB repositories with properly configured dependencies (authenticated client, database configuration). Enables CLI commands to access repositories without duplicating connection logic, maintains testability through dependency injection, and caches client instances for performance.

## ADDED Requirements

### Requirement: Repository Factory

The system SHALL provide a `RepositoryFactory` class that instantiates `CosmosContainerRepository` and `CosmosItemRepository` instances with authenticated `CosmosClient` and configured database name from environment variables.

**Details**:

- Class: `RepositoryFactory` in `orbit/factory.py`
- Constructor: accepts `OrbitSettings` instance
- Methods: `get_container_repository()`, `get_item_repository()`
- Client caching: reuses `CosmosClient` across multiple factory method calls
- Configuration source: `ORBIT_DATABASE_NAME`, `ORBIT_COSMOS_CONNECTION_STRING` environment variables
- Error handling: raises `ValueError` for missing database name, propagates `CosmosAuthError` from auth strategy

#### Scenario: Successful container repository instantiation

- **GIVEN** environment variables `ORBIT_DATABASE_NAME=mydb` and `ORBIT_COSMOS_CONNECTION_STRING=AccountEndpoint=...` are set
- **WHEN** CLI command calls `factory.get_container_repository()`
- **THEN** factory loads settings from environment
- **AND** factory creates `ConnectionStringAuthStrategy` with connection string
- **AND** factory calls `strategy.get_client()` to get authenticated `CosmosClient`
- **AND** factory caches client for reuse
- **AND** factory instantiates `CosmosContainerRepository(client=..., database_name="mydb")`
- **AND** factory returns repository instance ready for use

#### Scenario: Missing database name configuration

- **GIVEN** `ORBIT_COSMOS_CONNECTION_STRING` set, but `ORBIT_DATABASE_NAME` not set
- **WHEN** CLI command calls `factory.get_container_repository()`
- **THEN** factory loads settings from environment
- **AND** factory detects `database_name` is None
- **AND** factory raises `ValueError` with message: "Database name not configured. Set ORBIT_DATABASE_NAME environment variable."

#### Scenario: Missing connection string configuration

- **GIVEN** `ORBIT_DATABASE_NAME=mydb` set, but `ORBIT_COSMOS_CONNECTION_STRING` not set
- **WHEN** CLI command calls `factory.get_container_repository()`
- **THEN** factory attempts to create `ConnectionStringAuthStrategy`
- **AND** auth strategy raises `CosmosAuthError` with message about missing connection string
- **AND** factory propagates exception to caller

#### Scenario: Client caching across multiple calls

- **GIVEN** `ORBIT_DATABASE_NAME` and `ORBIT_COSMOS_CONNECTION_STRING` set in environment
- **WHEN** CLI command calls `factory.get_container_repository()` twice
- **THEN** first call creates `CosmosClient` and caches it
- **AND** second call reuses cached `CosmosClient`
- **AND** only one connection established to Cosmos DB
- **AND** both calls return repository instances with same client

#### Scenario: Multiple repository types share client

- **GIVEN** `ORBIT_DATABASE_NAME` and `ORBIT_COSMOS_CONNECTION_STRING` set in environment
- **WHEN** CLI calls `factory.get_container_repository()` then `factory.get_item_repository()`
- **THEN** first call creates and caches `CosmosClient`
- **AND** first call returns `CosmosContainerRepository` instance
- **AND** second call reuses cached client
- **AND** second call returns `CosmosItemRepository` instance
- **AND** both repositories share same client and database name

#### Scenario: Factory supports dependency injection in tests

- **GIVEN** unit test for CLI command function
- **WHEN** test creates mock `OrbitSettings` with test values and passes to `RepositoryFactory`
- **THEN** factory initializes with mock settings
- **AND** test can control configuration without environment variables
- **AND** test can mock `CosmosClient` to avoid real connections
- **AND** test verifies command logic without hitting database

---

### Requirement: Database Name Configuration

The system SHALL load database name from `ORBIT_DATABASE_NAME` environment variable via `OrbitSettings` class, requiring explicit configuration with no default value.

**Details**:

- Environment variable: `ORBIT_DATABASE_NAME`
- Config class: `OrbitSettings` in `orbit/config.py`
- New field: `database_name: str | None`
- Constant: `DATABASE_NAME_ENV = "ORBIT_DATABASE_NAME"`
- Behavior: `OrbitSettings.load()` reads env var, defaults to None if not set
- Validation: Factory raises `ValueError` if database_name is None

#### Scenario: Load database name from environment

- **GIVEN** environment variable `ORBIT_DATABASE_NAME=production-db` is set
- **WHEN** `OrbitSettings.load()` is called
- **THEN** settings object has `database_name="production-db"`

#### Scenario: Database name defaults to None when not set

- **GIVEN** environment variable `ORBIT_DATABASE_NAME` is not set
- **WHEN** `OrbitSettings.load()` is called
- **THEN** settings object has `database_name=None`

#### Scenario: Factory validates database name is configured

- **GIVEN** `OrbitSettings` with `database_name=None`
- **WHEN** factory attempts to instantiate repository
- **THEN** factory validates database name is not None
- **AND** factory raises `ValueError` with message: "Database name not configured. Set ORBIT_DATABASE_NAME environment variable."

---

### Requirement: CLI Command Wiring

The system SHALL replace `_get_repository()` stubs in container commands with factory-based repository instantiation, handling configuration errors gracefully with user-friendly messages.

**Details**:

- Affected commands: `list_containers()`, `create_container()`, `delete_container()` in `orbit/commands/containers.py`
- Pattern: Load `OrbitSettings`, create `RepositoryFactory`, call factory method, use repository
- Error handling: Catch `ValueError` (missing database name) and `CosmosAuthError` (auth failure)
- User messages: Clear, actionable guidance with environment variable examples
- Stateless: Each command invocation creates fresh factory instance

#### Scenario: Container list command uses factory

- **GIVEN** `ORBIT_DATABASE_NAME=test-db` and valid `ORBIT_COSMOS_CONNECTION_STRING` set
- **WHEN** user runs `orbit containers list`
- **THEN** command loads `OrbitSettings` from environment
- **AND** command creates `RepositoryFactory` with settings
- **AND** command calls `factory.get_container_repository()`
- **AND** command uses repository to list containers
- **AND** command displays results in Rich table

#### Scenario: Container create command handles missing database name

- **GIVEN** `ORBIT_COSMOS_CONNECTION_STRING` set, `ORBIT_DATABASE_NAME` not set
- **WHEN** user runs `orbit containers create products --partition-key /id`
- **THEN** factory raises `ValueError` with message about missing database name
- **AND** command catches exception
- **AND** command displays error: "Database name not configured. Set ORBIT_DATABASE_NAME environment variable."
- **AND** command exits with non-zero code

#### Scenario: Container delete command handles auth error

- **GIVEN** `ORBIT_DATABASE_NAME=test-db` set, invalid `ORBIT_COSMOS_CONNECTION_STRING`
- **WHEN** user runs `orbit containers delete products --yes`
- **THEN** auth strategy raises `CosmosAuthError` for malformed connection string
- **AND** factory propagates exception
- **AND** command catches exception
- **AND** command displays error with guidance on connection string format
- **AND** command exits with non-zero code

---

### Requirement: End-to-End Integration

The system SHALL enable full CLI-to-database round trips with emulator, validating factory wiring through integration tests covering repository instantiation, operation execution, and error paths.

**Details**:

- Integration tests: `tests/integration/test_containers_e2e.py`
- Test marker: `@pytest.mark.manual` (requires emulator running)
- Test database: Unique per run (e.g., `test-orbit-{uuid}`)
- Cleanup: Teardown fixtures delete test databases
- Coverage: Success paths (list, create, delete) and error paths (missing config, invalid auth)

#### Scenario: End-to-end container list with emulator

- **GIVEN** Cosmos DB emulator running at `localhost:8081` with test database `test-orbit-e2e`
- **WHEN** user runs `ORBIT_DATABASE_NAME=test-orbit-e2e ORBIT_COSMOS_CONNECTION_STRING=... orbit containers list`
- **THEN** CLI creates `OrbitSettings` from environment
- **AND** CLI instantiates `RepositoryFactory` with settings
- **AND** CLI calls `factory.get_container_repository()`
- **AND** factory creates client, connects to emulator, returns repository
- **AND** command calls `repository.list_containers()`
- **AND** command displays containers in Rich table
- **AND** CLI exits successfully

#### Scenario: End-to-end container create with emulator

- **GIVEN** Cosmos DB emulator running with test database
- **WHEN** user runs `ORBIT_DATABASE_NAME=test-db ORBIT_COSMOS_CONNECTION_STRING=... orbit containers create products --partition-key /id`
- **THEN** factory creates repository connected to emulator
- **AND** command creates container "products" with partition key "/id"
- **AND** command displays success message
- **AND** container exists in emulator database

#### Scenario: Integration test verifies missing config handling

- **GIVEN** integration test with `ORBIT_DATABASE_NAME` unset
- **WHEN** test invokes container command
- **THEN** factory raises `ValueError` with clear error message
- **AND** test verifies error message includes "Set ORBIT_DATABASE_NAME environment variable"

---

### Requirement: No Secrets Exposure

The system SHALL never log, print, or expose connection strings, keys, or other secrets in factory error messages, logs, or exception details.

**Details**:

- Factory errors: Generic messages only (e.g., "Connection string invalid")
- No logging: Factory does not log connection strings or keys
- Exception details: Auth errors sanitized before propagation
- Documentation: Warns developers not to print settings objects

#### Scenario: Factory error does not expose connection string

- **GIVEN** `ORBIT_COSMOS_CONNECTION_STRING` with sensitive key
- **WHEN** factory creates client and encounters auth error
- **THEN** error message does not include connection string or key
- **AND** only generic error message displayed: "Failed to authenticate with Cosmos DB. Check connection string format."

#### Scenario: Factory logs never contain secrets

- **GIVEN** factory initialization with valid connection string
- **WHEN** factory creates client and logs debug information
- **THEN** logs do not contain connection string, endpoint, or key values
- **AND** logs only contain sanitized information like "Creating Cosmos client from connection string"

## Constraints

- **No Global State**: Factory does not use module-level globals or singletons—each CLI invocation creates fresh factory instance.
- **No Implicit Defaults**: Factory does not assume default database name; explicit configuration required.
- **No Third-Party DI**: Factory uses plain Python; no dependency injection libraries (e.g., `injector`, `dependency-injector`).
- **Single Responsibility**: Factory only creates repositories; does not perform operations or business logic.
- **Minimal Parameters**: Factory methods take 0-2 parameters; complex config encapsulated in `OrbitSettings`.
- **Fail Fast**: Factory validates configuration at initialization, not lazily; raises errors immediately if invalid.
- **Stateless Commands**: CLI commands do not retain state between invocations; each run is independent.
- **Type Safety**: All factory code uses type hints; passes mypy strict checks.
- **Test Coverage**: Factory module maintains ≥80% coverage; all branches tested.
- **Clean Code**: Factory methods 5-20 lines, single responsibility, 0-2 params, no side effects.

## Dependencies

- **Module**: `orbit/config.py` (`OrbitSettings` class for configuration loading)
- **Module**: `orbit/auth/strategy.py` (`ConnectionStringAuthStrategy` for client creation)
- **Module**: `orbit/repositories/cosmos.py` (`CosmosContainerRepository`, `CosmosItemRepository`)
- **Module**: `orbit/exceptions.py` (`CosmosAuthError`, `CosmosConnectionError`)
- **SDK**: `azure-cosmos` (`CosmosClient` for database operations)
- **Change**: Requires completed `implement-connection-string-auth`
- **Change**: Requires completed `implement-cosmos-repository-containers`
- **Change**: Requires completed `implement-cosmos-repository-items` (for item repository support)
