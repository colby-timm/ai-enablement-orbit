"""Unit tests for repository factory module.

Tests dependency injection, client caching, and error handling.
"""

from unittest.mock import Mock, patch

import pytest

from orbit.config import OrbitSettings
from orbit.exceptions import CosmosAuthError
from orbit.factory import DATABASE_NAME_MISSING_ERROR, RepositoryFactory
from orbit.repositories.cosmos import CosmosContainerRepository


def test_should_create_factory_with_settings():
    """Should initialize factory with OrbitSettings instance."""
    # Arrange
    settings = OrbitSettings(
        connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=test-key==",
        database_name="test-db",
    )

    # Act
    factory = RepositoryFactory(settings)

    # Assert
    assert factory._settings == settings
    assert factory._database_name == "test-db"
    assert factory._client is None  # Not yet initialized


def test_should_cache_cosmos_client_across_calls():
    """Should reuse same CosmosClient instance for multiple repository requests."""
    # Arrange
    settings = OrbitSettings(
        connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=test-key==",
        database_name="test-db",
    )
    factory = RepositoryFactory(settings)

    mock_client = Mock()
    with patch(
        "orbit.factory.ConnectionStringAuthStrategy.get_client",
        return_value=mock_client,
    ):
        # Act
        repo1 = factory.get_container_repository()
        repo2 = factory.get_container_repository()

        # Assert
        assert repo1._client is repo2._client
        assert factory._client is mock_client


def test_should_raise_auth_error_when_connection_string_missing():
    """Should raise CosmosAuthError when connection string not provided."""
    # Arrange
    settings = OrbitSettings(database_name="test-db")  # No connection string
    factory = RepositoryFactory(settings)

    # Act & Assert
    with pytest.raises(CosmosAuthError, match="Connection string not provided"):
        factory.get_container_repository()


def test_should_raise_value_error_when_database_name_missing():
    """Should raise ValueError when ORBIT_DATABASE_NAME not configured."""
    # Arrange
    settings = OrbitSettings(
        connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=test-key=="
    )  # No database name
    factory = RepositoryFactory(settings)

    # Act & Assert
    with pytest.raises(ValueError, match=DATABASE_NAME_MISSING_ERROR):
        factory.get_container_repository()


def test_should_return_container_repository_with_client_and_database():
    """Should instantiate CosmosContainerRepository with client and database."""
    # Arrange
    settings = OrbitSettings(
        connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=test-key==",
        database_name="test-db",
    )
    factory = RepositoryFactory(settings)

    mock_client = Mock()
    with patch(
        "orbit.factory.ConnectionStringAuthStrategy.get_client",
        return_value=mock_client,
    ):
        # Act
        repo = factory.get_container_repository()

        # Assert
        assert isinstance(repo, CosmosContainerRepository)
        assert repo._client is mock_client
        assert repo._database_name == "test-db"


def test_should_return_item_repository_with_client_and_database():
    """Should instantiate repository for item operations with client and database."""
    # Arrange
    settings = OrbitSettings(
        connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=test-key==",
        database_name="test-db",
    )
    factory = RepositoryFactory(settings)

    mock_client = Mock()
    with patch(
        "orbit.factory.ConnectionStringAuthStrategy.get_client",
        return_value=mock_client,
    ):
        # Act
        repo = factory.get_item_repository()

        # Assert
        assert isinstance(repo, CosmosContainerRepository)
        assert repo._client is mock_client
        assert repo._database_name == "test-db"


def test_should_use_connection_string_from_settings():
    """Should pass settings to ConnectionStringAuthStrategy for client creation."""
    # Arrange
    settings = OrbitSettings(
        connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=test-key==",
        database_name="test-db",
    )
    factory = RepositoryFactory(settings)

    mock_client = Mock()
    with patch(
        "orbit.factory.ConnectionStringAuthStrategy"
    ) as mock_auth_strategy_class:
        mock_auth_strategy = Mock()
        mock_auth_strategy.get_client.return_value = mock_client
        mock_auth_strategy_class.return_value = mock_auth_strategy

        # Act
        factory.get_container_repository()

        # Assert
        mock_auth_strategy_class.assert_called_once_with(settings)
        mock_auth_strategy.get_client.assert_called_once()


def test_should_instantiate_repository_with_correct_database_name():
    """Should create repository with database name from settings."""
    # Arrange
    expected_db_name = "production-database"
    settings = OrbitSettings(
        connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=test-key==",
        database_name=expected_db_name,
    )
    factory = RepositoryFactory(settings)

    mock_client = Mock()
    with patch(
        "orbit.factory.ConnectionStringAuthStrategy.get_client",
        return_value=mock_client,
    ):
        # Act
        repo = factory.get_container_repository()

        # Assert
        assert repo._database_name == expected_db_name


def test_should_raise_value_error_on_get_item_repository_when_database_missing():
    """Should raise ValueError when getting item repository without database name."""
    # Arrange
    settings = OrbitSettings(
        connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=test-key=="
    )
    factory = RepositoryFactory(settings)

    # Act & Assert
    with pytest.raises(ValueError, match=DATABASE_NAME_MISSING_ERROR):
        factory.get_item_repository()


def test_should_lazy_initialize_client_on_first_repository_request():
    """Should not create CosmosClient until first repository is requested."""
    # Arrange
    settings = OrbitSettings(
        connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=test-key==",
        database_name="test-db",
    )
    factory = RepositoryFactory(settings)

    # Assert before any repository request
    assert factory._client is None

    # Act
    mock_client = Mock()
    with patch(
        "orbit.factory.ConnectionStringAuthStrategy.get_client",
        return_value=mock_client,
    ):
        factory.get_container_repository()

        # Assert after repository request
        assert factory._client is mock_client
