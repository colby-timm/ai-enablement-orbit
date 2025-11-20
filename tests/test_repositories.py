"""Tests for Cosmos DB repository implementation."""

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
    CosmosInvalidPartitionKeyError,
    CosmosQuotaExceededError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)
from orbit.repositories.cosmos import CosmosContainerRepository


@pytest.fixture
def mock_cosmos_client():
    """Fixture providing mocked CosmosClient."""
    client = Mock()
    client.get_database_client = Mock()
    return client


@pytest.fixture
def mock_database():
    """Fixture providing mocked database client."""
    return Mock()


@pytest.fixture
def repository(mock_cosmos_client, mock_database):
    """Fixture providing repository with mocked dependencies."""
    mock_cosmos_client.get_database_client.return_value = mock_database
    return CosmosContainerRepository(mock_cosmos_client, "test-db")


class TestListContainers:
    """Tests for list_containers operation."""

    def test_should_return_empty_list_when_no_containers(
        self, repository, mock_database
    ):
        # Arrange
        mock_database.list_containers.return_value = []

        # Act
        result = repository.list_containers()

        # Assert
        assert result == []
        mock_database.list_containers.assert_called_once()

    def test_should_return_container_list_when_multiple_containers(
        self, repository, mock_database
    ):
        # Arrange
        containers = [
            {"id": "users", "partitionKey": {"paths": ["/userId"]}},
            {"id": "orders", "partitionKey": {"paths": ["/orderId"]}},
            {"id": "products", "partitionKey": {"paths": ["/category"]}},
        ]
        mock_database.list_containers.return_value = containers

        # Act
        result = repository.list_containers()

        # Assert
        assert len(result) == 3
        assert result[0]["id"] == "users"
        assert result[1]["id"] == "orders"
        assert result[2]["id"] == "products"

    def test_should_raise_connection_error_when_sdk_fails(
        self, repository, mock_database
    ):
        # Arrange
        mock_database.list_containers.side_effect = CosmosHttpResponseError(
            status_code=503, message="Service unavailable"
        )

        # Act & Assert
        with pytest.raises(CosmosConnectionError) as exc_info:
            repository.list_containers()
        assert "503" in str(exc_info.value)


class TestCreateContainer:
    """Tests for create_container operation."""

    def test_should_create_container_when_valid_inputs(self, repository, mock_database):
        # Arrange
        mock_container = Mock()
        mock_container.read.return_value = {
            "id": "users",
            "partitionKey": {"paths": ["/userId"]},
        }
        mock_database.create_container.return_value = mock_container

        # Act
        result = repository.create_container("users", "/userId", throughput=400)

        # Assert
        assert result["id"] == "users"
        assert mock_database.create_container.called
        call_kwargs = mock_database.create_container.call_args[1]
        assert call_kwargs["id"] == "users"
        assert call_kwargs["offer_throughput"] == 400

    def test_should_use_default_throughput_when_not_specified(
        self, repository, mock_database
    ):
        # Arrange
        mock_container = Mock()
        mock_container.read.return_value = {"id": "users"}
        mock_database.create_container.return_value = mock_container

        # Act
        repository.create_container("users", "/userId")

        # Assert
        call_kwargs = mock_database.create_container.call_args[1]
        assert call_kwargs["offer_throughput"] == 400

    def test_should_raise_error_when_container_already_exists(
        self, repository, mock_database
    ):
        # Arrange
        mock_database.create_container.side_effect = SdkResourceExistsError(
            status_code=409, message="Container already exists"
        )

        # Act & Assert
        with pytest.raises(CosmosResourceExistsError) as exc_info:
            repository.create_container("users", "/userId")
        assert "users" in str(exc_info.value)
        assert "already exists" in str(exc_info.value)

    def test_should_raise_error_when_invalid_partition_key_path(
        self, repository, mock_database
    ):
        # Arrange - partition key without leading slash

        # Act & Assert
        with pytest.raises(CosmosInvalidPartitionKeyError) as exc_info:
            repository.create_container("users", "userId")
        assert "userId" in str(exc_info.value)
        assert "/" in str(exc_info.value)

    def test_should_raise_error_when_invalid_container_name(
        self, repository, mock_database
    ):
        # Arrange - container name with special characters

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            repository.create_container("@users!", "/id")
        assert "@users!" in str(exc_info.value)
        assert "alphanumeric" in str(exc_info.value)

    def test_should_raise_error_when_container_name_too_long(
        self, repository, mock_database
    ):
        # Arrange - container name exceeding 255 characters
        long_name = "a" * 256

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            repository.create_container(long_name, "/id")
        assert "255" in str(exc_info.value)

    def test_should_raise_quota_error_when_throughput_exceeds_limit(
        self, repository, mock_database
    ):
        # Arrange
        error = CosmosHttpResponseError(
            status_code=429, message="Throughput quota exceeded"
        )
        mock_database.create_container.side_effect = error

        # Act & Assert
        with pytest.raises(CosmosQuotaExceededError) as exc_info:
            repository.create_container("users", "/id", throughput=10000)
        assert "quota" in str(exc_info.value).lower()
        assert "users" in str(exc_info.value)

    def test_should_raise_connection_error_when_sdk_fails(
        self, repository, mock_database
    ):
        # Arrange
        mock_database.create_container.side_effect = CosmosHttpResponseError(
            status_code=500, message="Internal server error"
        )

        # Act & Assert
        with pytest.raises(CosmosConnectionError) as exc_info:
            repository.create_container("users", "/id")
        assert "500" in str(exc_info.value)


class TestDeleteContainer:
    """Tests for delete_container operation."""

    def test_should_delete_existing_container(self, repository, mock_database):
        # Arrange
        mock_database.delete_container.return_value = None

        # Act
        repository.delete_container("temp_data")

        # Assert
        mock_database.delete_container.assert_called_once_with("temp_data")

    def test_should_be_idempotent_when_container_not_found(
        self, repository, mock_database
    ):
        # Arrange
        mock_database.delete_container.side_effect = SdkResourceNotFoundError(
            status_code=404, message="Container not found"
        )

        # Act - should not raise exception
        repository.delete_container("missing")

        # Assert
        mock_database.delete_container.assert_called_once_with("missing")

    def test_should_raise_connection_error_when_sdk_fails(
        self, repository, mock_database
    ):
        # Arrange
        mock_database.delete_container.side_effect = CosmosHttpResponseError(
            status_code=503, message="Service unavailable"
        )

        # Act & Assert
        with pytest.raises(CosmosConnectionError) as exc_info:
            repository.delete_container("users")
        assert "503" in str(exc_info.value)


class TestGetContainerProperties:
    """Tests for get_container_properties operation."""

    def test_should_return_properties_when_container_exists(
        self, repository, mock_database
    ):
        # Arrange
        mock_container_client = Mock()
        mock_container_client.read.return_value = {
            "id": "users",
            "partitionKey": {"paths": ["/userId"], "kind": "Hash"},
            "indexingPolicy": {"automatic": True},
        }
        mock_database.get_container_client.return_value = mock_container_client

        # Act
        result = repository.get_container_properties("users")

        # Assert
        assert result["id"] == "users"
        assert result["partitionKey"]["paths"] == ["/userId"]
        assert "indexingPolicy" in result
        mock_database.get_container_client.assert_called_once_with("users")

    def test_should_raise_error_when_container_not_found(
        self, repository, mock_database
    ):
        # Arrange
        mock_container_client = Mock()
        mock_container_client.read.side_effect = SdkResourceNotFoundError(
            status_code=404, message="Container not found"
        )
        mock_database.get_container_client.return_value = mock_container_client

        # Act & Assert
        with pytest.raises(CosmosResourceNotFoundError) as exc_info:
            repository.get_container_properties("missing")
        assert "missing" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    def test_should_raise_connection_error_when_sdk_fails(
        self, repository, mock_database
    ):
        # Arrange
        mock_container_client = Mock()
        mock_container_client.read.side_effect = CosmosHttpResponseError(
            status_code=500, message="Internal server error"
        )
        mock_database.get_container_client.return_value = mock_container_client

        # Act & Assert
        with pytest.raises(CosmosConnectionError) as exc_info:
            repository.get_container_properties("users")
        assert "500" in str(exc_info.value)


class TestValidation:
    """Tests for input validation helpers."""

    def test_should_accept_valid_container_names(self, repository, mock_database):
        # Arrange
        valid_names = ["users", "my-container", "Container123", "a" * 255]
        mock_container = Mock()
        mock_container.read.return_value = {"id": "test"}
        mock_database.create_container.return_value = mock_container

        # Act & Assert - none should raise validation errors
        for name in valid_names:
            try:
                repository.create_container(name, "/id")
            except ValueError:
                pytest.fail(f"Valid container name '{name}' was rejected")

    def test_should_reject_invalid_container_names(self, repository):
        # Arrange
        invalid_names = [
            "@users",
            "users!",
            "users@domain",
            "user name",
            "users/data",
            "a" * 256,
        ]

        # Act & Assert
        for name in invalid_names:
            with pytest.raises(ValueError):
                repository.create_container(name, "/id")

    def test_should_accept_valid_partition_key_paths(self, repository, mock_database):
        # Arrange
        valid_paths = ["/id", "/userId", "/category", "/user/id"]
        mock_container = Mock()
        mock_container.read.return_value = {"id": "test"}
        mock_database.create_container.return_value = mock_container

        # Act & Assert - none should raise validation errors
        for path in valid_paths:
            try:
                repository.create_container("test", path)
            except CosmosInvalidPartitionKeyError:
                pytest.fail(f"Valid partition key path '{path}' was rejected")

    def test_should_reject_invalid_partition_key_paths(self, repository):
        # Arrange
        invalid_paths = ["id", "userId", "user_id", ""]

        # Act & Assert
        for path in invalid_paths:
            with pytest.raises(CosmosInvalidPartitionKeyError):
                repository.create_container("test", path)


class TestLogging:
    """Tests to ensure no secrets are logged."""

    @patch("orbit.repositories.cosmos.logger")
    def test_should_not_log_secrets_on_create_success(
        self, mock_logger, repository, mock_database
    ):
        # Arrange
        mock_container = Mock()
        mock_container.read.return_value = {"id": "users"}
        mock_database.create_container.return_value = mock_container

        # Act
        repository.create_container("users", "/userId", throughput=400)

        # Assert - check all log calls don't contain connection strings
        for call in mock_logger.info.call_args_list:
            log_message = str(call)
            assert "AccountEndpoint" not in log_message
            assert "AccountKey" not in log_message

    @patch("orbit.repositories.cosmos.logger")
    def test_should_not_log_secrets_on_error(
        self, mock_logger, repository, mock_database
    ):
        # Arrange
        mock_database.create_container.side_effect = CosmosHttpResponseError(
            status_code=500, message="Internal server error"
        )

        # Act
        try:
            repository.create_container("users", "/userId")
        except CosmosConnectionError:
            pass

        # Assert - check all log calls don't contain connection strings
        for call in mock_logger.error.call_args_list:
            log_message = str(call)
            assert "AccountEndpoint" not in log_message
            assert "AccountKey" not in log_message
