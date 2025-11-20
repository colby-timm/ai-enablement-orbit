"""Unit tests for configuration module.

Tests environment variable loading and settings validation.
"""

import os
from unittest.mock import patch

import pytest

from orbit.config import OrbitSettings
from orbit.exceptions import CosmosAuthError


def test_settings_load_includes_database_name():
    """Should load database_name from ORBIT_DATABASE_NAME environment variable."""
    # Arrange
    with patch.dict(os.environ, {"ORBIT_DATABASE_NAME": "test-database"}):
        # Act
        settings = OrbitSettings.load()

        # Assert
        assert settings.database_name == "test-database"


def test_settings_database_name_defaults_to_none_when_not_set():
    """Should default database_name to None when environment variable not set."""
    # Arrange
    with patch.dict(os.environ, {}, clear=True):
        # Act
        settings = OrbitSettings.load()

        # Assert
        assert settings.database_name is None


def test_settings_load_includes_connection_string():
    """Should load connection_string from environment variable."""
    # Arrange
    test_connection_string = (
        "AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=test-key=="
    )
    with patch.dict(
        os.environ, {"ORBIT_COSMOS_CONNECTION_STRING": test_connection_string}
    ):
        # Act
        settings = OrbitSettings.load()

        # Assert
        assert settings.connection_string == test_connection_string


def test_settings_load_raises_error_when_both_connection_string_and_endpoint():
    """Should raise CosmosAuthError when both string and endpoint provided."""
    # Arrange
    with patch.dict(
        os.environ,
        {
            "ORBIT_COSMOS_CONNECTION_STRING": "AccountEndpoint=https://test.documents.azure.com:443/;AccountKey=test-key==",
            "ORBIT_COSMOS_ENDPOINT": "https://test.documents.azure.com:443/",
        },
    ):
        # Act & Assert
        with pytest.raises(CosmosAuthError, match="Ambiguous auth configuration"):
            OrbitSettings.load()
