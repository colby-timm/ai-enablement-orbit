# Capability: Connection String Authentication

## ADDED Requirements

### Requirement: Create Cosmos Client from Connection String

The system SHALL initialize an `azure.cosmos.CosmosClient` instance from a valid connection string, handling authentication and endpoint validation with clear error reporting.

#### Scenario: Successful client creation with valid connection string

- **GIVEN** a connection string with format `AccountEndpoint=https://...;AccountKey=...`
- **WHEN** `ConnectionStringAuthStrategy.get_client()` is invoked
- **THEN** a configured `CosmosClient` instance SHALL be returned
- **AND** no secrets SHALL be logged or printed

#### Scenario: Missing connection string raises error

- **GIVEN** `OrbitSettings.connection_string` is None
- **WHEN** `ConnectionStringAuthStrategy.get_client()` is invoked
- **THEN** `CosmosAuthError` SHALL be raised with message "Connection string not provided."

#### Scenario: Empty connection string raises error

- **GIVEN** `OrbitSettings.connection_string` is an empty string
- **WHEN** `ConnectionStringAuthStrategy.get_client()` is invoked
- **THEN** `CosmosAuthError` SHALL be raised with actionable error message

#### Scenario: Malformed connection string raises error

- **GIVEN** a connection string missing required fields (e.g., no AccountKey)
- **WHEN** `ConnectionStringAuthStrategy.get_client()` is invoked
- **THEN** `CosmosAuthError` SHALL be raised
- **AND** error message SHALL indicate malformed connection string without exposing partial credentials

#### Scenario: Invalid credentials detected

- **GIVEN** a connection string with incorrect AccountKey
- **WHEN** `ConnectionStringAuthStrategy.get_client()` attempts to authenticate
- **THEN** `CosmosAuthError` SHALL be raised
- **AND** error message SHALL indicate authentication failure without exposing the key

#### Scenario: Unreachable endpoint detected

- **GIVEN** a connection string with unreachable endpoint (network error)
- **WHEN** `ConnectionStringAuthStrategy.get_client()` is invoked
- **THEN** `CosmosConnectionError` SHALL be raised
- **AND** error message SHALL indicate network or endpoint issue

#### Scenario: Emulator connection string accepted

- **GIVEN** a connection string with `AccountEndpoint=https://localhost:8081/`
- **WHEN** `ConnectionStringAuthStrategy.get_client()` is invoked
- **THEN** client SHALL initialize successfully for emulator usage

#### Scenario: Sanitized logging on initialization

- **GIVEN** any connection string
- **WHEN** `ConnectionStringAuthStrategy.get_client()` initializes the client
- **THEN** logs SHALL contain "Initializing connection string auth strategy" or similar
- **AND** logs SHALL NOT contain connection string, AccountKey, or AccountEndpoint values

### Requirement: Domain Exception Mapping

The system SHALL map Azure Cosmos SDK exceptions to Orbit domain exceptions, preserving error context while ensuring secret safety.

#### Scenario: SDK authentication exception mapped

- **GIVEN** `azure.cosmos` raises an authentication-related exception
- **WHEN** exception is caught in `get_client()`
- **THEN** exception SHALL be re-raised as `CosmosAuthError`
- **AND** original error context SHALL be included (without secrets)

#### Scenario: SDK network exception mapped

- **GIVEN** `azure.cosmos` raises a network or connection exception
- **WHEN** exception is caught in `get_client()`
- **THEN** exception SHALL be re-raised as `CosmosConnectionError`
- **AND** original error context SHALL be included

#### Scenario: Unknown SDK exceptions handled

- **GIVEN** `azure.cosmos` raises an unexpected exception
- **WHEN** exception is caught in `get_client()`
- **THEN** exception SHALL be wrapped in appropriate domain exception
- **AND** stack trace SHALL be preserved for debugging

## MODIFIED Requirements

### Requirement: Auth Strategy Interface Compliance (from cli-core)

The `ConnectionStringAuthStrategy` SHALL fully implement the `AuthStrategy` protocol by returning a functional `CosmosClient` instead of raising placeholder exceptions.

#### Scenario: Remove TODO placeholder

- **GIVEN** the current implementation raises `CosmosConnectionError("TODO: implement...")`
- **WHEN** this change is complete
- **THEN** `get_client()` SHALL return a working `CosmosClient` or raise a real domain exception
- **AND** no TODO comments SHALL remain in the implementation
