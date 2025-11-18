# Spec: Repository Container Operations

## ADDED Requirements

### Requirement: List Containers in Database

The repository SHALL provide a method to enumerate all containers within the configured Cosmos DB database, returning container names and basic metadata for navigation and discovery purposes.

#### Scenario: List containers in database with multiple containers

- **GIVEN** a Cosmos DB database with containers "users", "orders", "products"
- **WHEN** `list_containers()` is called
- **THEN** return a list containing all three container names
- **AND** no exceptions are raised

#### Scenario: List containers in empty database

- **GIVEN** a Cosmos DB database with no containers
- **WHEN** `list_containers()` is called
- **THEN** return an empty list
- **AND** no exceptions are raised

#### Scenario: List containers when connection fails

- **GIVEN** the Cosmos DB endpoint is unreachable
- **WHEN** `list_containers()` is called
- **THEN** raise `CosmosConnectionError` with actionable message
- **AND** no secrets are included in error message

### Requirement: Create Containers with Partition Key Specification

The repository SHALL support creating new containers with mandatory partition key path and optional throughput configuration, validating inputs and providing clear errors for invalid parameters or quota violations.

#### Scenario: Create container with valid partition key

- **GIVEN** a database with no container named "users"
- **WHEN** `create_container("users", "/userId", throughput=400)` is called
- **THEN** a new container "users" is created with partition key "/userId"
- **AND** throughput is set to 400 RU/s
- **AND** container metadata is returned

#### Scenario: Create container with duplicate name

- **GIVEN** a database with existing container "users"
- **WHEN** `create_container("users", "/id")` is called
- **THEN** raise `CosmosResourceExistsError` indicating container already exists
- **AND** include container name in error message

#### Scenario: Create container with invalid partition key path

- **GIVEN** a partition key path "userId" (missing leading slash)
- **WHEN** `create_container("users", "userId")` is called
- **THEN** raise `CosmosInvalidPartitionKeyError`
- **AND** error message explains partition key must start with "/"

#### Scenario: Create container with invalid name

- **GIVEN** a container name containing special characters "@users!"
- **WHEN** `create_container("@users!", "/id")` is called
- **THEN** raise `ValueError` with naming rules
- **AND** explain valid characters: alphanumeric and hyphens

#### Scenario: Create container exceeding throughput quota

- **GIVEN** account throughput quota is nearly exhausted
- **WHEN** `create_container("users", "/id", throughput=10000)` is called
- **THEN** raise `CosmosQuotaExceededError`
- **AND** error message suggests reducing throughput or upgrading account

#### Scenario: Create container with default throughput

- **GIVEN** no throughput parameter specified
- **WHEN** `create_container("users", "/userId")` is called
- **THEN** container is created with 400 RU/s (minimum throughput)

### Requirement: Delete Containers Idempotently

The repository SHALL support removing containers by name, treating deletion as idempotent such that deleting a non-existent container does not raise an error, enabling safe cleanup operations.

#### Scenario: Delete existing container

- **GIVEN** a database with container "temp_data"
- **WHEN** `delete_container("temp_data")` is called
- **THEN** the container is removed from the database
- **AND** subsequent `list_containers()` does not include "temp_data"

#### Scenario: Delete non-existent container is idempotent

- **GIVEN** a database with no container named "missing"
- **WHEN** `delete_container("missing")` is called
- **THEN** no exception is raised
- **AND** operation completes successfully

#### Scenario: Delete container with connection failure

- **GIVEN** the Cosmos DB endpoint is unreachable
- **WHEN** `delete_container("users")` is called
- **THEN** raise `CosmosConnectionError` with actionable message

### Requirement: Retrieve Container Properties

The repository SHALL provide a method to fetch container properties including partition key definition, throughput configuration, and indexing policy for inspection and validation purposes.

#### Scenario: Get properties of existing container

- **GIVEN** a container "users" with partition key "/userId" and 400 RU/s throughput
- **WHEN** `get_container_properties("users")` is called
- **THEN** return dict/object containing name, partition key path, throughput, and indexing policy

#### Scenario: Get properties of non-existent container

- **GIVEN** a database with no container named "missing"
- **WHEN** `get_container_properties("missing")` is called
- **THEN** raise `CosmosResourceNotFoundError`
- **AND** error message includes the container name "missing"

#### Scenario: Get properties with connection failure

- **GIVEN** the Cosmos DB endpoint is unreachable
- **WHEN** `get_container_properties("users")` is called
- **THEN** raise `CosmosConnectionError` with actionable message

### Requirement: Translate SDK Exceptions to Domain Exceptions

All Azure Cosmos SDK exceptions SHALL be caught and mapped to appropriate domain-specific exceptions with sanitized messages that never expose connection strings, keys, or other secrets.

#### Scenario: SDK exception mapped to domain exception

- **GIVEN** the SDK raises `CosmosHttpResponseError` with status 404
- **WHEN** any repository operation encounters this error
- **THEN** raise `CosmosResourceNotFoundError` (domain exception)
- **AND** error message is actionable and secret-free

### Requirement: Log Operations Without Exposing Secrets

All repository operations SHALL log operation names and outcomes at INFO level, ensuring connection strings, account keys, and other credentials are never written to logs.

#### Scenario: Container creation logged safely

- **GIVEN** connection string authentication is configured
- **WHEN** `create_container("users", "/id")` succeeds
- **THEN** log message includes: "Created container 'users' with partition key '/id'"
- **AND** log message does NOT include connection string or account key

