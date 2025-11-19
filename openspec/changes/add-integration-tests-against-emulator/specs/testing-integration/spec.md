# Capability: Integration Testing Against Emulator

## ADDED Requirements

### Requirement: Integration Test Infrastructure

The system SHALL provide integration test infrastructure that connects to Cosmos DB Emulator, manages test database lifecycle, and isolates integration tests from unit tests using pytest markers.

#### Scenario: Integration tests use emulator connection

- **GIVEN** Cosmos DB Emulator is running at `https://localhost:8081`
- **WHEN** integration tests execute
- **THEN** tests SHALL connect using emulator connection string
- **AND** no production or cloud resources SHALL be accessed

#### Scenario: Test database lifecycle management

- **GIVEN** integration tests require a test database
- **WHEN** test fixtures set up the test environment
- **THEN** a unique test database SHALL be created (e.g., `OrbitTestDB`)
- **AND** database SHALL be deleted after test execution completes
- **AND** cleanup SHALL occur even if tests fail

#### Scenario: Test containers are cleaned up

- **GIVEN** integration tests create containers
- **WHEN** tests complete or fail
- **THEN** all test containers SHALL be deleted
- **AND** emulator state SHALL be clean for subsequent test runs

#### Scenario: Integration tests are marked separately

- **GIVEN** pytest markers are configured
- **WHEN** integration tests are defined
- **THEN** tests SHALL be decorated with `@pytest.mark.integration`
- **AND** integration tests SHALL be runnable separately via `pytest -m integration`
- **AND** unit tests SHALL be runnable separately via `pytest -m "not integration"`

### Requirement: Authentication Integration Testing

The system SHALL verify end-to-end authentication flows against Cosmos DB Emulator, ensuring ConnectionStringAuthStrategy creates functional clients.

#### Scenario: Successful authentication with emulator

- **GIVEN** emulator connection string is provided
- **WHEN** `ConnectionStringAuthStrategy.get_client()` is invoked
- **THEN** a functional `CosmosClient` instance SHALL be returned
- **AND** client SHALL successfully list databases as smoke test

#### Scenario: Invalid connection string fails appropriately

- **GIVEN** a malformed connection string
- **WHEN** `ConnectionStringAuthStrategy.get_client()` is invoked
- **THEN** `CosmosAuthError` SHALL be raised
- **AND** error message SHALL be actionable

#### Scenario: Emulator connectivity verified

- **GIVEN** emulator is running and accessible
- **WHEN** integration tests create a client
- **THEN** client SHALL successfully communicate with emulator
- **AND** no network errors SHALL occur

### Requirement: Container Operations Integration Testing

The system SHALL verify container lifecycle operations (create, list, get, delete) execute correctly against Cosmos DB Emulator with proper error handling.

#### Scenario: Create container with partition key

- **GIVEN** a test database exists in emulator
- **WHEN** repository creates container with partition key `/id`
- **THEN** container SHALL exist in emulator
- **AND** partition key configuration SHALL match `/id`

#### Scenario: List containers returns created containers

- **GIVEN** multiple test containers are created
- **WHEN** repository lists containers
- **THEN** all created containers SHALL appear in list
- **AND** container metadata SHALL be accurate

#### Scenario: Get container properties returns correct data

- **GIVEN** a test container exists with name `test-container` and partition key `/pk`
- **WHEN** repository retrieves container properties
- **THEN** properties SHALL include name `test-container`
- **AND** properties SHALL include partition key `/pk`

#### Scenario: Delete container removes container

- **GIVEN** a test container exists
- **WHEN** repository deletes container
- **THEN** container SHALL no longer exist in emulator
- **AND** subsequent get operations SHALL fail with not found error

#### Scenario: Duplicate container creation raises error

- **GIVEN** a container named `duplicate-test` exists
- **WHEN** repository attempts to create container with same name
- **THEN** appropriate exception SHALL be raised
- **AND** error message SHALL indicate container already exists

### Requirement: Item Operations Integration Testing

The system SHALL verify item CRUD operations (create, get, update, delete) execute correctly with proper partition key handling and error scenarios.

#### Scenario: Create item with partition key

- **GIVEN** a test container with partition key `/category`
- **WHEN** repository creates item `{"id": "1", "category": "books", "name": "Test"}`
- **THEN** item SHALL exist in emulator
- **AND** item SHALL be retrievable by id and partition key

#### Scenario: Get item by id and partition key

- **GIVEN** an item exists with id `item123` and partition key value `electronics`
- **WHEN** repository retrieves item by id `item123` and partition key `electronics`
- **THEN** retrieved item SHALL match created item
- **AND** all properties SHALL be preserved

#### Scenario: Update item modifies properties

- **GIVEN** an item exists with properties `{"id": "1", "name": "Original"}`
- **WHEN** repository updates item with `{"id": "1", "name": "Updated"}`
- **THEN** subsequent retrieval SHALL return `{"id": "1", "name": "Updated"}`
- **AND** modification SHALL persist in emulator

#### Scenario: Delete item removes item

- **GIVEN** an item exists with id `delete-me`
- **WHEN** repository deletes item by id and partition key
- **THEN** item SHALL no longer exist
- **AND** subsequent get operations SHALL raise not found error

#### Scenario: Partition key mismatch raises error

- **GIVEN** an item exists with partition key value `books`
- **WHEN** repository attempts to get item with incorrect partition key value `movies`
- **THEN** appropriate exception SHALL be raised
- **AND** error message SHALL indicate partition key mismatch

#### Scenario: Item not found raises error

- **GIVEN** no item exists with id `nonexistent`
- **WHEN** repository attempts to retrieve item
- **THEN** appropriate exception SHALL be raised
- **AND** error message SHALL indicate item not found

### Requirement: Query Operations Integration Testing

The system SHALL verify query execution including SQL syntax, cross-partition queries, pagination, and result limits against Cosmos DB Emulator.

#### Scenario: Basic SQL query returns items

- **GIVEN** test container has items `[{"id": "1", "name": "A"}, {"id": "2", "name": "B"}]`
- **WHEN** query executes `SELECT * FROM c`
- **THEN** result SHALL contain both items
- **AND** item properties SHALL be complete

#### Scenario: Query with WHERE clause filters results

- **GIVEN** test items with `category` property values `books`, `movies`, `music`
- **WHEN** query executes `SELECT * FROM c WHERE c.category = 'books'`
- **THEN** result SHALL contain only items with category `books`
- **AND** other items SHALL be excluded

#### Scenario: Cross-partition query returns results from multiple partitions

- **GIVEN** test items distributed across partition keys `A`, `B`, `C`
- **WHEN** query executes without partition key filter
- **THEN** result SHALL include items from all partitions
- **AND** query SHALL execute successfully

#### Scenario: Pagination with max item count

- **GIVEN** test container has 150 items
- **WHEN** query executes with `max_item_count=100`
- **THEN** first page SHALL return 100 items
- **AND** continuation token SHALL be provided
- **AND** subsequent request with token SHALL return remaining 50 items

#### Scenario: Query with no results returns empty set

- **GIVEN** test container has items with `status` property values `active`, `inactive`
- **WHEN** query executes `SELECT * FROM c WHERE c.status = 'deleted'`
- **THEN** result SHALL be empty list
- **AND** no errors SHALL be raised

#### Scenario: Result set streaming for large queries

- **GIVEN** test container has 1000 items
- **WHEN** query executes and iterates through results
- **THEN** results SHALL stream without loading all items in memory
- **AND** iteration SHALL complete successfully

### Requirement: CLI End-to-End Integration Testing

The system SHALL verify complete CLI workflows including container management, item operations, and queries execute correctly from command-line invocation.

#### Scenario: Container lifecycle via CLI

- **GIVEN** emulator is running and CLI is configured
- **WHEN** `orbit containers create test-cli-container --partition-key /id` executes
- **THEN** container SHALL be created in emulator
- **AND** `orbit containers list` SHALL show `test-cli-container`
- **AND** `orbit containers delete test-cli-container --yes` SHALL remove container

#### Scenario: Item lifecycle via CLI

- **GIVEN** test container exists
- **WHEN** `orbit items create test-container item.json` executes
- **THEN** item SHALL be created
- **AND** `orbit items get test-container --id <id> --partition-key <pk>` SHALL retrieve item
- **AND** `orbit items update test-container updated.json` SHALL modify item
- **AND** `orbit items delete test-container --id <id> --partition-key <pk> --yes` SHALL remove item

#### Scenario: Query command via CLI

- **GIVEN** test container has items
- **WHEN** `orbit query test-container "SELECT * FROM c WHERE c.type = 'test'"` executes
- **THEN** matching items SHALL be displayed
- **AND** output SHALL be formatted with Rich by default

#### Scenario: JSON output flag works end-to-end

- **GIVEN** test container exists
- **WHEN** `orbit containers list --json` executes
- **THEN** output SHALL be valid JSON
- **AND** JSON SHALL contain container metadata

#### Scenario: Yes flag bypasses confirmation

- **GIVEN** test container exists
- **WHEN** `orbit containers delete test-container --yes` executes
- **THEN** container SHALL be deleted without prompt
- **AND** command SHALL complete without user interaction

### Requirement: Test Documentation and Setup

The system SHALL provide clear documentation for emulator setup, integration test execution, and troubleshooting to enable developers to run tests locally.

#### Scenario: Emulator setup documented

- **GIVEN** new developer reads README
- **WHEN** following emulator setup instructions
- **THEN** developer SHALL be able to install emulator
- **AND** developer SHALL be able to start emulator
- **AND** developer SHALL know default connection string

#### Scenario: Integration test execution documented

- **GIVEN** developer wants to run integration tests
- **WHEN** reading test documentation
- **THEN** documentation SHALL show `pytest -m integration` command
- **AND** documentation SHALL show how to run only unit tests
- **AND** documentation SHALL explain emulator prerequisite

#### Scenario: Troubleshooting guide available

- **GIVEN** integration tests fail due to emulator issues
- **WHEN** developer consults troubleshooting section
- **THEN** documentation SHALL list common errors
- **AND** documentation SHALL provide solutions (e.g., "start emulator", "check port 8081")

#### Scenario: Test cleanup behavior documented

- **GIVEN** developer is concerned about test pollution
- **WHEN** reading test documentation
- **THEN** documentation SHALL explain automatic cleanup
- **AND** documentation SHALL note test database naming convention
- **AND** documentation SHALL explain how to manually reset emulator if needed
