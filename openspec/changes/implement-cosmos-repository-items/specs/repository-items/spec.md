# Spec: Repository Item Operations

## ADDED Requirements

### Requirement: Create Items in Containers with Partition Key

The repository SHALL provide a method to create new items in a specified container with explicit partition key value, validating item structure and handling duplicate ID conflicts and partition key mismatches.

#### Scenario: Create item with valid data and partition key

- **GIVEN** a container "users" with partition key "/userId"
- **WHEN** `create_item("users", {"id": "user123", "userId": "user123", "name": "Alice"}, "user123")` is called
- **THEN** the item is created in the container
- **AND** the created item dictionary is returned
- **AND** no exceptions are raised

#### Scenario: Create item with duplicate ID in same partition

- **GIVEN** a container "users" with existing item ID "user123" in partition "user123"
- **WHEN** `create_item("users", {"id": "user123", "userId": "user123", "name": "Bob"}, "user123")` is called
- **THEN** raise `CosmosDuplicateItemError`
- **AND** error message includes item ID and container name

#### Scenario: Create item with partition key mismatch

- **GIVEN** a container "users" with partition key "/userId"
- **WHEN** `create_item("users", {"id": "user123", "userId": "user123"}, "different_user")` is called
- **THEN** raise `CosmosPartitionKeyMismatchError`
- **AND** error message explains partition key in item doesn't match provided value

#### Scenario: Create item without 'id' field

- **GIVEN** an item dictionary without 'id' field
- **WHEN** `create_item("users", {"userId": "user123", "name": "Alice"}, "user123")` is called
- **THEN** raise `ValueError`
- **AND** error message explains 'id' field is required

#### Scenario: Create item in non-existent container

- **GIVEN** no container named "missing"
- **WHEN** `create_item("missing", {"id": "item1"}, "partition1")` is called
- **THEN** raise `CosmosResourceNotFoundError`
- **AND** error message includes container name

#### Scenario: Create item with connection failure

- **GIVEN** the Cosmos DB endpoint is unreachable
- **WHEN** `create_item("users", {"id": "user123"}, "user123")` is called
- **THEN** raise `CosmosConnectionError` with actionable message
- **AND** no secrets are included in error message

### Requirement: Retrieve Items by ID and Partition Key

The repository SHALL provide a method to retrieve a single item by its ID and partition key value, ensuring efficient single-item reads and proper error handling for not found and partition key mismatch scenarios.

#### Scenario: Get item with valid ID and partition key

- **GIVEN** a container "users" with item ID "user123" in partition "user123"
- **WHEN** `get_item("users", "user123", "user123")` is called
- **THEN** return the item dictionary
- **AND** item contains all fields stored in Cosmos DB

#### Scenario: Get item that does not exist

- **GIVEN** a container "users" with no item ID "missing"
- **WHEN** `get_item("users", "missing", "partition1")` is called
- **THEN** raise `CosmosItemNotFoundError`
- **AND** error message includes item ID and container name

#### Scenario: Get item with wrong partition key

- **GIVEN** a container "users" with item ID "user123" in partition "user123"
- **WHEN** `get_item("users", "user123", "wrong_partition")` is called
- **THEN** raise `CosmosItemNotFoundError` or `CosmosPartitionKeyMismatchError`
- **AND** error message explains partition key mismatch

#### Scenario: Get item from non-existent container

- **GIVEN** no container named "missing"
- **WHEN** `get_item("missing", "item1", "partition1")` is called
- **THEN** raise `CosmosResourceNotFoundError`
- **AND** error message includes container name

#### Scenario: Get item with connection failure

- **GIVEN** the Cosmos DB endpoint is unreachable
- **WHEN** `get_item("users", "user123", "user123")` is called
- **THEN** raise `CosmosConnectionError` with actionable message

### Requirement: Update Items with Upsert Behavior

The repository SHALL provide a method to update existing items or create them if they don't exist (upsert), validating item structure and partition key consistency before performing the operation.

#### Scenario: Update existing item successfully

- **GIVEN** a container "users" with item ID "user123" in partition "user123"
- **WHEN** `update_item("users", "user123", {"id": "user123", "userId": "user123", "name": "Alice Updated"}, "user123")` is called
- **THEN** the item is updated with new data
- **AND** the updated item dictionary is returned

#### Scenario: Update creates item if not exists (upsert)

- **GIVEN** a container "users" with no item ID "newuser"
- **WHEN** `update_item("users", "newuser", {"id": "newuser", "userId": "newuser", "name": "New User"}, "newuser")` is called
- **THEN** a new item is created with the provided data
- **AND** the created item dictionary is returned

#### Scenario: Update item with partition key mismatch

- **GIVEN** a container "users" with partition key "/userId"
- **WHEN** `update_item("users", "user123", {"id": "user123", "userId": "user123"}, "different_user")` is called
- **THEN** raise `CosmosPartitionKeyMismatchError`
- **AND** error message explains partition key inconsistency

#### Scenario: Update item with mismatched ID in item body

- **GIVEN** item ID parameter "user123" doesn't match item['id'] "user456"
- **WHEN** `update_item("users", "user123", {"id": "user456", "userId": "user123"}, "user123")` is called
- **THEN** raise `ValueError`
- **AND** error message explains item_id parameter must match item['id'] field

#### Scenario: Update item with connection failure

- **GIVEN** the Cosmos DB endpoint is unreachable
- **WHEN** `update_item("users", "user123", {"id": "user123"}, "user123")` is called
- **THEN** raise `CosmosConnectionError` with actionable message

### Requirement: Delete Items Idempotently

The repository SHALL provide a method to delete items by ID and partition key, treating deletion as idempotent such that deleting a non-existent item does not raise an error, enabling safe cleanup operations.

#### Scenario: Delete existing item successfully

- **GIVEN** a container "users" with item ID "user123" in partition "user123"
- **WHEN** `delete_item("users", "user123", "user123")` is called
- **THEN** the item is removed from the container
- **AND** subsequent `get_item("users", "user123", "user123")` raises `CosmosItemNotFoundError`

#### Scenario: Delete non-existent item is idempotent

- **GIVEN** a container "users" with no item ID "missing"
- **WHEN** `delete_item("users", "missing", "partition1")` is called
- **THEN** no exception is raised
- **AND** operation completes successfully

#### Scenario: Delete item with partition key mismatch

- **GIVEN** a container "users" with item ID "user123" in partition "user123"
- **WHEN** `delete_item("users", "user123", "wrong_partition")` is called
- **THEN** operation completes without error (idempotent - item not in that partition)

#### Scenario: Delete item from non-existent container

- **GIVEN** no container named "missing"
- **WHEN** `delete_item("missing", "item1", "partition1")` is called
- **THEN** raise `CosmosResourceNotFoundError`
- **AND** error message includes container name

#### Scenario: Delete item with connection failure

- **GIVEN** the Cosmos DB endpoint is unreachable
- **WHEN** `delete_item("users", "user123", "user123")` is called
- **THEN** raise `CosmosConnectionError` with actionable message

### Requirement: List Items with Pagination Support

The repository SHALL provide a method to enumerate items in a container with configurable pagination limit, enabling efficient browsing of container contents with default limit of 100 items.

#### Scenario: List items in container with multiple items

- **GIVEN** a container "users" with 50 items
- **WHEN** `list_items("users")` is called with default max_count
- **THEN** return list of all 50 item dictionaries
- **AND** no exceptions are raised

#### Scenario: List items with custom pagination limit

- **GIVEN** a container "users" with 200 items
- **WHEN** `list_items("users", max_count=50)` is called
- **THEN** return list of up to 50 item dictionaries
- **AND** items are from the first page of results

#### Scenario: List items in empty container

- **GIVEN** a container "users" with no items
- **WHEN** `list_items("users")` is called
- **THEN** return empty list
- **AND** no exceptions are raised

#### Scenario: List items from non-existent container

- **GIVEN** no container named "missing"
- **WHEN** `list_items("missing")` is called
- **THEN** raise `CosmosResourceNotFoundError`
- **AND** error message includes container name

#### Scenario: List items with connection failure

- **GIVEN** the Cosmos DB endpoint is unreachable
- **WHEN** `list_items("users")` is called
- **THEN** raise `CosmosConnectionError` with actionable message

#### Scenario: List items logs count not content

- **GIVEN** a container "users" with sensitive user data
- **WHEN** `list_items("users")` is called
- **THEN** log message includes: "Listed X items from container 'users'"
- **AND** log message does NOT include item content or field values

### Requirement: Validate Partition Key Consistency

All item operations SHALL validate that the partition key value provided matches the item's partition key field value, preventing data corruption and ensuring correct partitioning behavior.

#### Scenario: Validation prevents partition key mismatch on create

- **GIVEN** a container "orders" with partition key "/customerId"
- **WHEN** `create_item("orders", {"id": "order1", "customerId": "cust123"}, "cust456")` is called
- **THEN** raise `CosmosPartitionKeyMismatchError` before SDK call
- **AND** error explains customerId field doesn't match partition key value

#### Scenario: Validation prevents partition key mismatch on update

- **GIVEN** a container "orders" with partition key "/customerId"
- **WHEN** `update_item("orders", "order1", {"id": "order1", "customerId": "cust123"}, "cust456")` is called
- **THEN** raise `CosmosPartitionKeyMismatchError`
- **AND** item is not modified

### Requirement: Translate SDK Exceptions to Domain Exceptions

All Azure Cosmos SDK exceptions SHALL be caught and mapped to appropriate domain-specific exceptions with sanitized messages that never expose connection strings, keys, item content, or other secrets.

#### Scenario: SDK 404 exception mapped to item not found

- **GIVEN** the SDK raises `CosmosResourceNotFoundError` with status 404 for item
- **WHEN** any item operation encounters this error
- **THEN** raise `CosmosItemNotFoundError` (domain exception)
- **AND** error message includes item ID and container name only

#### Scenario: SDK 409 conflict exception mapped to duplicate item

- **GIVEN** the SDK raises `CosmosHttpResponseError` with status 409
- **WHEN** `create_item()` encounters this error
- **THEN** raise `CosmosDuplicateItemError` (domain exception)
- **AND** error message is actionable and secret-free

#### Scenario: SDK partition key error mapped to domain exception

- **GIVEN** the SDK raises `CosmosHttpResponseError` with status 400 and partition key message
- **WHEN** any item operation encounters this error
- **THEN** raise `CosmosPartitionKeyMismatchError` (domain exception)
- **AND** error message explains partition key inconsistency without exposing values

### Requirement: Log Operations Without Exposing Secrets or Content

All repository operations SHALL log operation names, item IDs, and container names at INFO level, ensuring connection strings, account keys, item content, and sensitive field values are never written to logs.

#### Scenario: Item creation logged safely

- **GIVEN** connection string authentication is configured
- **WHEN** `create_item("users", {"id": "user123", "password": "secret"}, "user123")` succeeds
- **THEN** log message includes: "Created item 'user123' in container 'users'"
- **AND** log message does NOT include connection string, password field, or other item content

#### Scenario: Item retrieval logged safely

- **GIVEN** an item with sensitive data is retrieved
- **WHEN** `get_item("users", "user123", "user123")` succeeds
- **THEN** log message includes: "Retrieved item 'user123' from container 'users'"
- **AND** log message does NOT include item content or field values
