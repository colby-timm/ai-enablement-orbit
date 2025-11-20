# Change: Add Dependency Injection Framework

## Why

CLI commands currently cannot instantiate repositories because there's no mechanism to wire together authentication, configuration, and repository dependencies. Every command has a `_get_repository()` stub that raises `NotImplementedError("Repository factory not yet implemented")`. Developers cannot use `orbit containers` or future `orbit items` commands with real Cosmos DB instances—the commands validate inputs and format output but fail when accessing the database. Without dependency injection, each command would need to duplicate connection logic, configuration loading, and error handling, violating DRY principles and making the codebase brittle. This change introduces a lightweight factory pattern to instantiate repositories with proper auth and config, enabling end-to-end CLI functionality while maintaining testability through dependency inversion.

## What Changes

- Add `orbit/factory.py` module with repository factory functions
- Create `RepositoryFactory` class to encapsulate dependency creation
- Implement `get_container_repository()` factory method returning `CosmosContainerRepository` instances
- Implement `get_item_repository()` factory method returning `CosmosItemRepository` instances (for future use)
- Load configuration from environment variables (`ORBIT_DATABASE_NAME`, existing `ORBIT_COSMOS_CONNECTION_STRING`)
- Create `CosmosClient` using existing `ConnectionStringAuthStrategy` from auth module
- Cache `CosmosClient` instance per factory to avoid redundant connections
- Replace all `_get_repository()` stubs in `orbit/commands/containers.py` with factory calls
- Add configuration validation with actionable error messages when required env vars missing
- Handle factory initialization errors gracefully with user-friendly CLI output
- Add comprehensive unit tests for factory module
- Add integration tests verifying commands work end-to-end with emulator
- Maintain 80%+ test coverage

## Impact

- Affected specs:
  - ADDS new `dependency-injection` capability for repository instantiation
  - MODIFIES `cli-containers` capability (commands now fully functional)
  - MODIFIES `cli-core` capability (adds global database configuration)
- Affected code:
  - `orbit/factory.py`: NEW FILE - Repository factory implementation
  - `orbit/config.py`: MODIFIES - Add `database_name` field to `OrbitSettings`
  - `orbit/commands/containers.py`: MODIFIES - Replace `_get_repository()` stub with factory
  - `tests/test_factory.py`: NEW FILE - Factory unit tests
  - `tests/integration/test_containers_e2e.py`: NEW FILE - End-to-end integration tests
- **BREAKING**: None—internal refactoring, no CLI interface changes
- **DEPENDENCIES**: Requires completed `implement-connection-string-auth` and `implement-cosmos-repository-containers`
- **ENABLES**: Functional container management commands, foundation for item management commands

## Dependencies

- **Requires**: `implement-connection-string-auth` (provides `ConnectionStringAuthStrategy` and auth error handling)
- **Requires**: `implement-cosmos-repository-containers` (provides `CosmosContainerRepository` to instantiate)
- **Requires**: `add-cli-boilerplate` (provides CLI framework and `OrbitSettings`)
- **Requires**: `add-container-management-commands` (provides commands to wire factory into)
- **Enables**: Fully functional `orbit containers` commands against real Cosmos DB
- **Enables**: Future `orbit items` commands with minimal additional factory code
- **Blocks**: None—unblocks container command usage immediately

## Notes

- Factory uses simple functions, not a DI library (favor minimal dependencies)
- `CosmosClient` cached per factory instance to avoid connection overhead
- Database name required via `ORBIT_DATABASE_NAME` environment variable (no CLI flag yet)
- Factory methods raise domain exceptions (`CosmosAuthError`, `CosmosConnectionError`) not generic errors
- Error messages guide users to set missing environment variables with examples
- Factory is singleton-like but testable through dependency injection of settings
- Commands instantiate factory once per invocation (stateless CLI design)
- Future changes can add CLI flag `--database` as override for env var
- No secrets logged—factory never prints connection strings or keys
- Integration tests verify full round-trip: CLI → factory → repository → emulator
