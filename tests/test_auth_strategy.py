"""Tests for authentication strategy implementations."""

from unittest.mock import Mock, patch

import pytest
from azure.cosmos.exceptions import CosmosHttpResponseError

from orbit.auth.strategy import ConnectionStringAuthStrategy
from orbit.config import OrbitSettings
from orbit.exceptions import CosmosAuthError, CosmosConnectionError


class TestConnectionStringAuthStrategy:
    """Tests for ConnectionStringAuthStrategy."""

    def test_should_create_client_when_valid_connection_string_provided(self):
        """Verify successful client creation with valid connection string."""
        settings = OrbitSettings(
            connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=dGVzdGtleQ=="
        )
        strategy = ConnectionStringAuthStrategy(settings)

        with patch("orbit.auth.strategy.CosmosClient") as mock_cosmos_client:
            mock_client_instance = Mock()
            mock_cosmos_client.from_connection_string.return_value = (
                mock_client_instance
            )

            client = strategy.get_client()

            assert client == mock_client_instance
            mock_cosmos_client.from_connection_string.assert_called_once_with(
                settings.connection_string
            )

    def test_should_raise_auth_error_when_connection_string_is_none(self):
        """Verify CosmosAuthError raised when connection string is None."""
        settings = OrbitSettings(connection_string=None)
        strategy = ConnectionStringAuthStrategy(settings)

        with pytest.raises(CosmosAuthError) as exc_info:
            strategy.get_client()

        assert "Connection string not provided" in str(exc_info.value)

    def test_should_raise_auth_error_when_connection_string_is_empty(self):
        """Verify CosmosAuthError raised when connection string is empty."""
        settings = OrbitSettings(connection_string="")
        strategy = ConnectionStringAuthStrategy(settings)

        with pytest.raises(CosmosAuthError) as exc_info:
            strategy.get_client()

        assert "empty" in str(exc_info.value).lower()

    def test_should_raise_auth_error_when_connection_string_is_whitespace(self):
        """Verify CosmosAuthError raised when connection string is only whitespace."""
        settings = OrbitSettings(connection_string="   ")
        strategy = ConnectionStringAuthStrategy(settings)

        with pytest.raises(CosmosAuthError) as exc_info:
            strategy.get_client()

        assert "empty" in str(exc_info.value).lower()

    def test_should_raise_auth_error_when_connection_string_is_malformed(self):
        """Verify CosmosAuthError raised for malformed connection string."""
        settings = OrbitSettings(connection_string="invalid-connection-string")
        strategy = ConnectionStringAuthStrategy(settings)

        with patch("orbit.auth.strategy.CosmosClient") as mock_cosmos_client:
            mock_cosmos_client.from_connection_string.side_effect = ValueError(
                "Missing required field"
            )

            with pytest.raises(CosmosAuthError) as exc_info:
                strategy.get_client()

            assert "Malformed connection string" in str(exc_info.value)

    def test_should_raise_auth_error_when_credentials_are_invalid(self):
        """Verify CosmosAuthError raised for invalid credentials (401)."""
        settings = OrbitSettings(
            connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=invalidkey"
        )
        strategy = ConnectionStringAuthStrategy(settings)

        with patch("orbit.auth.strategy.CosmosClient") as mock_cosmos_client:
            mock_error = CosmosHttpResponseError(
                status_code=401, message="Unauthorized"
            )
            mock_cosmos_client.from_connection_string.side_effect = mock_error

            with pytest.raises(CosmosAuthError) as exc_info:
                strategy.get_client()

            assert "Authentication failed" in str(exc_info.value)
            assert "credentials" in str(exc_info.value).lower()

    def test_should_raise_connection_error_when_endpoint_unreachable(self):
        """Verify CosmosConnectionError raised for network issues."""
        settings = OrbitSettings(
            connection_string="AccountEndpoint=https://unreachable.documents.azure.com:443/;AccountKey=key"
        )
        strategy = ConnectionStringAuthStrategy(settings)

        with patch("orbit.auth.strategy.CosmosClient") as mock_cosmos_client:
            mock_error = CosmosHttpResponseError(
                status_code=503, message="Service unavailable"
            )
            mock_cosmos_client.from_connection_string.side_effect = mock_error

            with pytest.raises(CosmosConnectionError) as exc_info:
                strategy.get_client()

            assert "Failed to connect" in str(exc_info.value)

    def test_should_raise_connection_error_for_network_exceptions(self):
        """Verify CosmosConnectionError raised for generic network errors."""
        settings = OrbitSettings(
            connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=key"
        )
        strategy = ConnectionStringAuthStrategy(settings)

        with patch("orbit.auth.strategy.CosmosClient") as mock_cosmos_client:
            mock_cosmos_client.from_connection_string.side_effect = Exception(
                "Network connection failed"
            )

            with pytest.raises(CosmosConnectionError) as exc_info:
                strategy.get_client()

            assert "Network error" in str(exc_info.value)

    def test_should_handle_emulator_connection_string(self):
        """Verify emulator connection strings are accepted."""
        settings = OrbitSettings(
            connection_string="AccountEndpoint=https://localhost:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
        )
        strategy = ConnectionStringAuthStrategy(settings)

        with patch("orbit.auth.strategy.CosmosClient") as mock_cosmos_client:
            mock_client_instance = Mock()
            mock_cosmos_client.from_connection_string.return_value = (
                mock_client_instance
            )

            client = strategy.get_client()

            assert client == mock_client_instance

    def test_should_not_log_secrets_on_success(self, caplog):
        """Verify no secrets are logged during successful initialization."""
        import logging

        caplog.set_level(logging.INFO)

        connection_string = "AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=secretkey123"
        settings = OrbitSettings(connection_string=connection_string)
        strategy = ConnectionStringAuthStrategy(settings)

        with patch("orbit.auth.strategy.CosmosClient") as mock_cosmos_client:
            mock_client_instance = Mock()
            mock_cosmos_client.from_connection_string.return_value = (
                mock_client_instance
            )

            strategy.get_client()

            # Check logs don't contain connection string or key
            log_messages = " ".join([record.message for record in caplog.records])
            assert "AccountKey" not in log_messages
            assert "secretkey123" not in log_messages
            assert connection_string not in log_messages
            assert "Initializing connection string auth strategy" in log_messages

    def test_should_not_log_secrets_on_error(self, caplog):
        """Verify no secrets are logged during error scenarios."""
        import logging

        caplog.set_level(logging.INFO)

        connection_string = "AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=secretkey123"
        settings = OrbitSettings(connection_string=connection_string)
        strategy = ConnectionStringAuthStrategy(settings)

        with patch("orbit.auth.strategy.CosmosClient") as mock_cosmos_client:
            mock_cosmos_client.from_connection_string.side_effect = ValueError(
                "Invalid format"
            )

            with pytest.raises(CosmosAuthError):
                strategy.get_client()

            # Check logs and error messages don't contain secrets
            log_messages = " ".join([record.message for record in caplog.records])
            assert "secretkey123" not in log_messages
            assert connection_string not in log_messages

    def test_should_wrap_unexpected_exceptions_in_auth_error(self):
        """Verify unexpected exceptions are wrapped appropriately."""
        settings = OrbitSettings(
            connection_string="AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=key"
        )
        strategy = ConnectionStringAuthStrategy(settings)

        with patch("orbit.auth.strategy.CosmosClient") as mock_cosmos_client:
            mock_cosmos_client.from_connection_string.side_effect = RuntimeError(
                "Unexpected error"
            )

            with pytest.raises(CosmosAuthError) as exc_info:
                strategy.get_client()

            assert "Unexpected error during authentication" in str(exc_info.value)
