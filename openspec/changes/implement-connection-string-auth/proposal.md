# Change: Implement Connection String Authentication

## Why

Developers need a working authentication mechanism to connect to Azure Cosmos DB before any data operations can be performed. The current `ConnectionStringAuthStrategy` is a placeholder with TODOs—it raises `CosmosConnectionError` instead of creating a functional client. This change completes the foundation layer required by all repository operations, container management, item CRUD, and query features.

## What Changes

- Complete `ConnectionStringAuthStrategy.get_client()` implementation using `azure-cosmos` SDK
- Integrate `CosmosClient` initialization from connection string with proper error handling
- Add endpoint validation to ensure connection strings contain valid Cosmos DB endpoints
- Implement credential validation and meaningful error messages for authentication failures
- Add azure-cosmos SDK dependency to `pyproject.toml`
- Enhance error handling to distinguish between missing credentials, malformed connection strings, network failures, and invalid credentials
- Update unit tests to validate successful client creation, error scenarios, and secret safety
- Ensure no connection strings or keys are logged or printed (preserve secret safety)

## Impact

- Affected specs:
  - MODIFIES `cli-core` capability (auth strategy now functional)
  - ADDS new `auth-connection-string` capability for connection string authentication specifics
- Affected code:
  - `orbit/auth/strategy.py`: Implements `ConnectionStringAuthStrategy.get_client()`
  - `orbit/exceptions.py`: May add specific auth-related exceptions if needed
  - `pyproject.toml`: Adds `azure-cosmos` dependency
  - `tests/`: Adds comprehensive auth strategy tests
- **BREAKING**: None—existing placeholder never worked, so completing it doesn't break any consumers
- **FOUNDATION**: Required by all features that interact with Cosmos DB (container ops, item CRUD, queries)

## Dependencies

- Requires: `add-cli-boilerplate` change (provides auth strategy interface and exception hierarchy)
- Enables: All subsequent Cosmos DB operations (repository implementations, CLI commands)

## Notes

- Connection string format: `AccountEndpoint=https://...;AccountKey=...`
- Must handle both emulator connection strings (localhost) and cloud endpoints
- Error messages should be actionable but never expose secrets
- Tests must mock `CosmosClient` to avoid requiring live Cosmos DB instance
- Integration tests against emulator will be handled in separate change (#8 from roadmap)
