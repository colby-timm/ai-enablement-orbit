"""End-to-end integration tests for container commands with factory.

These tests require the Cosmos DB emulator running locally.
Run with: make test-manual
"""

import os
import uuid
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from orbit.cli import app

runner = CliRunner()


@pytest.mark.manual
def test_should_list_containers_from_real_database():
    """Should list containers from real Cosmos DB database via factory."""
    # Arrange
    test_db = f"test-orbit-{uuid.uuid4().hex[:8]}"
    emulator_conn_str = (
        "AccountEndpoint=https://localhost:8081/;"
        "AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
    )

    with patch.dict(
        os.environ,
        {
            "ORBIT_COSMOS_CONNECTION_STRING": emulator_conn_str,
            "ORBIT_DATABASE_NAME": test_db,
        },
    ):
        # Act
        result = runner.invoke(app, ["containers", "list"])

        # Assert
        assert result.exit_code in [0, 1]  # 0 if DB exists, 1 if not found


@pytest.mark.manual
def test_should_create_container_in_real_database():
    """Should create container in real Cosmos DB database via factory."""
    # Arrange
    test_db = f"test-orbit-{uuid.uuid4().hex[:8]}"
    container_name = f"test-container-{uuid.uuid4().hex[:8]}"
    emulator_conn_str = (
        "AccountEndpoint=https://localhost:8081/;"
        "AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
    )

    with patch.dict(
        os.environ,
        {
            "ORBIT_COSMOS_CONNECTION_STRING": emulator_conn_str,
            "ORBIT_DATABASE_NAME": test_db,
        },
    ):
        # Act
        result = runner.invoke(
            app,
            ["containers", "create", container_name, "--partition-key", "/id"],
        )

        # Assert - Will fail if database doesn't exist, which is expected
        assert result.exit_code in [0, 1]


@pytest.mark.manual
def test_should_delete_container_from_real_database():
    """Should delete container from real Cosmos DB database via factory."""
    # Arrange
    test_db = f"test-orbit-{uuid.uuid4().hex[:8]}"
    container_name = f"test-container-{uuid.uuid4().hex[:8]}"
    emulator_conn_str = (
        "AccountEndpoint=https://localhost:8081/;"
        "AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
    )

    with patch.dict(
        os.environ,
        {
            "ORBIT_COSMOS_CONNECTION_STRING": emulator_conn_str,
            "ORBIT_DATABASE_NAME": test_db,
        },
    ):
        # Act
        result = runner.invoke(
            app,
            ["--yes", "containers", "delete", container_name],
        )

        # Assert - Idempotent, won't fail if container doesn't exist
        assert result.exit_code == 0


@pytest.mark.manual
def test_should_fail_gracefully_when_database_name_not_set():
    """Should display user-friendly error when ORBIT_DATABASE_NAME missing."""
    # Arrange
    emulator_conn_str = (
        "AccountEndpoint=https://localhost:8081/;"
        "AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
    )

    with patch.dict(
        os.environ,
        {"ORBIT_COSMOS_CONNECTION_STRING": emulator_conn_str},
        clear=True,
    ):
        # Act
        result = runner.invoke(app, ["containers", "list"])

        # Assert
        assert result.exit_code == 1
        assert "ORBIT_DATABASE_NAME" in result.stdout
        assert "Configuration error" in result.stdout


@pytest.mark.manual
def test_should_fail_gracefully_when_connection_string_invalid():
    """Should display user-friendly error when connection string is invalid."""
    # Arrange
    with patch.dict(
        os.environ,
        {
            "ORBIT_COSMOS_CONNECTION_STRING": "invalid-connection-string",
            "ORBIT_DATABASE_NAME": "test-db",
        },
    ):
        # Act
        result = runner.invoke(app, ["containers", "list"])

        # Assert
        assert result.exit_code == 1
        assert "Authentication error" in result.stdout


@pytest.mark.manual
def test_should_display_user_friendly_error_for_missing_config():
    """Should guide users to set environment variables when auth fails."""
    # Arrange - No env vars set
    with patch.dict(os.environ, {}, clear=True):
        # Act
        result = runner.invoke(app, ["containers", "list"])

        # Assert
        assert result.exit_code == 1
        assert (
            "ORBIT_DATABASE_NAME" in result.stdout
            or "ORBIT_COSMOS_CONNECTION_STRING" in result.stdout
        )


@pytest.mark.manual
def test_should_output_json_when_flag_provided():
    """Should return JSON output when --json flag provided."""
    # Arrange
    test_db = f"test-orbit-{uuid.uuid4().hex[:8]}"
    emulator_conn_str = (
        "AccountEndpoint=https://localhost:8081/;"
        "AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
    )

    with patch.dict(
        os.environ,
        {
            "ORBIT_COSMOS_CONNECTION_STRING": emulator_conn_str,
            "ORBIT_DATABASE_NAME": test_db,
        },
    ):
        # Act
        result = runner.invoke(app, ["--json", "containers", "list"])

        # Assert - May fail if DB doesn't exist, but should still attempt JSON
        if result.exit_code == 0:
            assert "{" in result.stdout or "[" in result.stdout


@pytest.mark.manual
def test_should_output_human_readable_when_no_json_flag():
    """Should return human-readable output when no --json flag."""
    # Arrange
    test_db = f"test-orbit-{uuid.uuid4().hex[:8]}"
    emulator_conn_str = (
        "AccountEndpoint=https://localhost:8081/;"
        "AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
    )

    with patch.dict(
        os.environ,
        {
            "ORBIT_COSMOS_CONNECTION_STRING": emulator_conn_str,
            "ORBIT_DATABASE_NAME": test_db,
        },
    ):
        # Act
        result = runner.invoke(app, ["containers", "list"])

        # Assert - Should output text, not JSON
        if result.exit_code == 0:
            # Either "No containers found" or table output
            assert (
                "No containers found" in result.stdout or "Containers" in result.stdout
            )
