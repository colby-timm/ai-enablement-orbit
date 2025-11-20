"""Unit tests for Cosmos DB item repository operations.

Tests follow AAA pattern with descriptive naming:
test_should_<behavior>_when_<condition>.
All external dependencies are mocked.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from azure.cosmos.exceptions import (
    CosmosHttpResponseError,
)
from azure.cosmos.exceptions import (
    CosmosResourceExistsError as SdkResourceExistsError,
)
from azure.cosmos.exceptions import (
    CosmosResourceNotFoundError as SdkResourceNotFoundError,
)

from orbit.exceptions import (
    CosmosConnectionError,
    CosmosDuplicateItemError,
    CosmosItemNotFoundError,
    CosmosPartitionKeyMismatchError,
)
from orbit.repositories.cosmos import CosmosContainerRepository


@pytest.fixture
def mock_cosmos_client() -> Mock:
    """Create a mock CosmosClient for testing."""
    return Mock()


@pytest.fixture
def mock_database(mock_cosmos_client: Mock) -> Mock:
    """Create a mock database client."""
    database = Mock()
    mock_cosmos_client.get_database_client.return_value = database
    return database


@pytest.fixture
def repository(
    mock_cosmos_client: Mock, mock_database: Mock
) -> CosmosContainerRepository:
    """Create repository instance with mocked dependencies."""
    return CosmosContainerRepository(mock_cosmos_client, "test-db")


@pytest.fixture
def mock_container(mock_database: Mock) -> Mock:
    """Create a mock container client."""
    container = Mock()
    mock_database.get_container_client.return_value = container
    return container


class TestCreateItem:
    """Tests for create_item operation."""

    def test_should_create_item_when_valid_inputs_provided(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        item = {"id": "item-1", "name": "Test Item"}
        partition_key_value = "partition-1"
        mock_container.create_item.return_value = item

        # Act
        result = repository.create_item("test-container", item, partition_key_value)

        # Assert
        assert result == item
        mock_container.create_item.assert_called_once_with(
            body=item, partition_key=partition_key_value
        )

    def test_should_raise_error_when_item_missing_id_field(
        self, repository: CosmosContainerRepository
    ):
        # Arrange
        item = {"name": "Test Item"}
        partition_key_value = "partition-1"

        # Act & Assert
        with pytest.raises(
            ValueError, match="Item must be a dictionary with 'id' field"
        ):
            repository.create_item("test-container", item, partition_key_value)

    def test_should_raise_error_when_item_not_dictionary(
        self, repository: CosmosContainerRepository
    ):
        # Arrange
        item = "not-a-dict"
        partition_key_value = "partition-1"

        # Act & Assert
        with pytest.raises(
            ValueError, match="Item must be a dictionary with 'id' field"
        ):
            repository.create_item("test-container", item, partition_key_value)

    def test_should_raise_error_when_partition_key_empty(
        self, repository: CosmosContainerRepository
    ):
        # Arrange
        item = {"id": "item-1", "name": "Test Item"}

        # Act & Assert
        with pytest.raises(ValueError, match="Partition key value cannot be empty"):
            repository.create_item("test-container", item, "")

    def test_should_raise_error_when_container_name_empty(
        self, repository: CosmosContainerRepository
    ):
        # Arrange
        item = {"id": "item-1", "name": "Test Item"}
        partition_key_value = "partition-1"

        # Act & Assert
        with pytest.raises(ValueError, match="Container name cannot be empty"):
            repository.create_item("", item, partition_key_value)

    def test_should_raise_duplicate_error_when_item_id_exists(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        item = {"id": "item-1", "name": "Test Item"}
        partition_key_value = "partition-1"
        mock_container.create_item.side_effect = SdkResourceExistsError()

        # Act & Assert
        with pytest.raises(
            CosmosDuplicateItemError,
            match="Item with ID 'item-1' already exists in partition",
        ):
            repository.create_item("test-container", item, partition_key_value)

    def test_should_raise_partition_key_mismatch_when_400_error(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        item = {"id": "item-1", "name": "Test Item"}
        partition_key_value = "partition-1"
        error = CosmosHttpResponseError(status_code=400, message="Bad request")
        mock_container.create_item.side_effect = error

        # Act & Assert
        with pytest.raises(
            CosmosPartitionKeyMismatchError,
            match="Partition key mismatch for item 'item-1'",
        ):
            repository.create_item("test-container", item, partition_key_value)

    def test_should_raise_connection_error_when_sdk_fails(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        item = {"id": "item-1", "name": "Test Item"}
        partition_key_value = "partition-1"
        error = CosmosHttpResponseError(status_code=500, message="Server error")
        mock_container.create_item.side_effect = error

        # Act & Assert
        with pytest.raises(CosmosConnectionError, match="Failed to create item: 500"):
            repository.create_item("test-container", item, partition_key_value)


class TestGetItem:
    """Tests for get_item operation."""

    def test_should_return_item_when_valid_id_and_partition_key(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        item = {"id": "item-1", "name": "Test Item"}
        mock_container.read_item.return_value = item

        # Act
        result = repository.get_item("test-container", "item-1", "partition-1")

        # Assert
        assert result == item
        mock_container.read_item.assert_called_once_with(
            item="item-1", partition_key="partition-1"
        )

    def test_should_raise_not_found_error_when_item_missing(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        mock_container.read_item.side_effect = SdkResourceNotFoundError()

        # Act & Assert
        with pytest.raises(
            CosmosItemNotFoundError,
            match="Item 'item-1' not found in container 'test-container'",
        ):
            repository.get_item("test-container", "item-1", "partition-1")

    def test_should_raise_partition_key_mismatch_when_400_error(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        error = CosmosHttpResponseError(status_code=400, message="Bad request")
        mock_container.read_item.side_effect = error

        # Act & Assert
        with pytest.raises(
            CosmosPartitionKeyMismatchError,
            match="Partition key mismatch for item 'item-1'",
        ):
            repository.get_item("test-container", "item-1", "partition-1")

    def test_should_raise_connection_error_when_sdk_fails(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        error = CosmosHttpResponseError(status_code=500, message="Server error")
        mock_container.read_item.side_effect = error

        # Act & Assert
        with pytest.raises(
            CosmosConnectionError, match="Failed to get item 'item-1': 500"
        ):
            repository.get_item("test-container", "item-1", "partition-1")


class TestUpdateItem:
    """Tests for update_item operation."""

    def test_should_update_item_when_valid_inputs_provided(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        item = {"id": "item-1", "name": "Updated Item"}
        partition_key_value = "partition-1"
        mock_container.upsert_item.return_value = item

        # Act
        result = repository.update_item(
            "test-container", "item-1", item, partition_key_value
        )

        # Assert
        assert result == item
        mock_container.upsert_item.assert_called_once_with(
            body=item, partition_key=partition_key_value
        )

    def test_should_raise_error_when_item_not_dictionary(
        self, repository: CosmosContainerRepository
    ):
        # Arrange
        item = "not-a-dict"

        # Act & Assert
        with pytest.raises(ValueError, match="Item must be a dictionary"):
            repository.update_item("test-container", "item-1", item, "partition-1")

    def test_should_raise_error_when_item_id_mismatch(
        self, repository: CosmosContainerRepository
    ):
        # Arrange
        item = {"id": "item-2", "name": "Test Item"}

        # Act & Assert
        with pytest.raises(
            ValueError, match="Item 'id' field must match item_id parameter 'item-1'"
        ):
            repository.update_item("test-container", "item-1", item, "partition-1")

    def test_should_raise_partition_key_mismatch_when_400_error(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        item = {"id": "item-1", "name": "Updated Item"}
        error = CosmosHttpResponseError(status_code=400, message="Bad request")
        mock_container.upsert_item.side_effect = error

        # Act & Assert
        with pytest.raises(
            CosmosPartitionKeyMismatchError,
            match="Partition key mismatch for item 'item-1'",
        ):
            repository.update_item("test-container", "item-1", item, "partition-1")

    def test_should_raise_connection_error_when_sdk_fails(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        item = {"id": "item-1", "name": "Updated Item"}
        error = CosmosHttpResponseError(status_code=500, message="Server error")
        mock_container.upsert_item.side_effect = error

        # Act & Assert
        with pytest.raises(
            CosmosConnectionError, match="Failed to update item 'item-1': 500"
        ):
            repository.update_item("test-container", "item-1", item, "partition-1")


class TestDeleteItem:
    """Tests for delete_item operation."""

    def test_should_delete_item_when_item_exists(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        mock_container.delete_item.return_value = None

        # Act
        repository.delete_item("test-container", "item-1", "partition-1")

        # Assert
        mock_container.delete_item.assert_called_once_with(
            item="item-1", partition_key="partition-1"
        )

    def test_should_be_idempotent_when_item_not_found(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        mock_container.delete_item.side_effect = SdkResourceNotFoundError()

        # Act - should not raise exception
        repository.delete_item("test-container", "item-1", "partition-1")

        # Assert
        mock_container.delete_item.assert_called_once_with(
            item="item-1", partition_key="partition-1"
        )

    def test_should_raise_partition_key_mismatch_when_400_error(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        error = CosmosHttpResponseError(status_code=400, message="Bad request")
        mock_container.delete_item.side_effect = error

        # Act & Assert
        with pytest.raises(
            CosmosPartitionKeyMismatchError,
            match="Partition key mismatch for item 'item-1'",
        ):
            repository.delete_item("test-container", "item-1", "partition-1")

    def test_should_raise_connection_error_when_sdk_fails(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        error = CosmosHttpResponseError(status_code=500, message="Server error")
        mock_container.delete_item.side_effect = error

        # Act & Assert
        with pytest.raises(
            CosmosConnectionError, match="Failed to delete item 'item-1': 500"
        ):
            repository.delete_item("test-container", "item-1", "partition-1")


class TestListItems:
    """Tests for list_items operation."""

    def test_should_return_empty_list_when_no_items(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        mock_container.query_items.return_value = []

        # Act
        result = repository.list_items("test-container")

        # Assert
        assert result == []
        mock_container.query_items.assert_called_once_with(
            query="SELECT * FROM c", max_item_count=100
        )

    def test_should_return_items_up_to_max_count(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        items = [{"id": f"item-{i}", "name": f"Item {i}"} for i in range(5)]
        mock_container.query_items.return_value = items

        # Act
        result = repository.list_items("test-container", max_count=10)

        # Assert
        assert result == items
        assert len(result) == 5
        mock_container.query_items.assert_called_once_with(
            query="SELECT * FROM c", max_item_count=10
        )

    def test_should_use_default_max_count_when_not_specified(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        mock_container.query_items.return_value = []

        # Act
        repository.list_items("test-container")

        # Assert
        mock_container.query_items.assert_called_once_with(
            query="SELECT * FROM c", max_item_count=100
        )

    def test_should_raise_error_when_max_count_not_positive(
        self, repository: CosmosContainerRepository
    ):
        # Act & Assert
        with pytest.raises(ValueError, match="max_count must be a positive integer"):
            repository.list_items("test-container", max_count=0)

        with pytest.raises(ValueError, match="max_count must be a positive integer"):
            repository.list_items("test-container", max_count=-1)

    def test_should_raise_connection_error_when_sdk_fails(
        self, repository: CosmosContainerRepository, mock_container: Mock
    ):
        # Arrange
        error = CosmosHttpResponseError(status_code=500, message="Server error")
        mock_container.query_items.side_effect = error

        # Act & Assert
        with pytest.raises(CosmosConnectionError, match="Failed to list items: 500"):
            repository.list_items("test-container")


class TestLoggingSecurity:
    """Tests to verify no secrets or sensitive content are logged."""

    @patch("orbit.repositories.cosmos.logger")
    def test_should_not_log_item_content_when_creating(
        self,
        mock_logger: Mock,
        repository: CosmosContainerRepository,
        mock_container: Mock,
    ):
        # Arrange
        item = {"id": "item-1", "secret": "sensitive-data"}
        mock_container.create_item.return_value = item

        # Act
        repository.create_item("test-container", item, "partition-1")

        # Assert
        log_call = mock_logger.info.call_args[0][0]
        assert "item-1" in log_call
        assert "test-container" in log_call
        assert "sensitive-data" not in log_call

    @patch("orbit.repositories.cosmos.logger")
    def test_should_not_log_item_content_when_listing(
        self,
        mock_logger: Mock,
        repository: CosmosContainerRepository,
        mock_container: Mock,
    ):
        # Arrange
        items = [{"id": "item-1", "secret": "sensitive-data"}]
        mock_container.query_items.return_value = items

        # Act
        repository.list_items("test-container")

        # Assert
        log_call = mock_logger.info.call_args[0][0]
        assert "1 items" in log_call
        assert "test-container" in log_call
        assert "sensitive-data" not in log_call
