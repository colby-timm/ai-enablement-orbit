"""Tests for container management CLI commands.

Uses mocked repository to test command behavior, error handling,
and output formatting without requiring live Cosmos DB connection.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from orbit.cli import app, context_state
from orbit.exceptions import (
    CosmosConnectionError,
    CosmosInvalidPartitionKeyError,
    CosmosQuotaExceededError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)

runner = CliRunner()


@pytest.fixture
def mock_repository() -> MagicMock:
    """Create mock CosmosContainerRepository."""
    return MagicMock()


@pytest.fixture(autouse=True)
def reset_context() -> None:
    """Reset context state before each test."""
    context_state.json = False
    context_state.yes = False
    context_state.init_output()


def _patch_get_repository(mock_repo: MagicMock):
    """Patch _get_repository to return mock."""
    return patch(
        "orbit.commands.containers._get_repository",
        return_value=mock_repo,
    )


# List Command Tests


def test_should_display_containers_in_table_when_list_called(
    mock_repository: MagicMock,
) -> None:
    """List displays containers in Rich table format."""
    mock_repository.list_containers.return_value = [
        {
            "id": "products",
            "partitionKey": {"paths": ["/category"]},
            "throughput": 400,
        },
        {
            "id": "users",
            "partitionKey": {"paths": ["/userId"]},
            "throughput": 800,
        },
    ]

    with _patch_get_repository(mock_repository):
        result = runner.invoke(app, ["containers", "list"])

    assert result.exit_code == 0
    assert "products" in result.stdout
    assert "/category" in result.stdout
    assert "users" in result.stdout
    assert "/userId" in result.stdout


def test_should_return_json_when_list_called_with_json_flag(
    mock_repository: MagicMock,
) -> None:
    """List returns JSON format when --json flag provided."""
    mock_repository.list_containers.return_value = [
        {
            "id": "products",
            "partitionKey": {"paths": ["/category"]},
            "throughput": 400,
        }
    ]

    with _patch_get_repository(mock_repository):
        result = runner.invoke(app, ["--json", "containers", "list"])

    assert result.exit_code == 0
    assert '"containers"' in result.stdout
    assert '"name": "products"' in result.stdout
    assert '"partition_key": "/category"' in result.stdout
    assert '"throughput": 400' in result.stdout


def test_should_show_no_containers_message_when_database_empty(
    mock_repository: MagicMock,
) -> None:
    """List shows 'No containers found' when database is empty."""
    mock_repository.list_containers.return_value = []

    with _patch_get_repository(mock_repository):
        result = runner.invoke(app, ["containers", "list"])

    assert result.exit_code == 0
    assert "No containers found" in result.stdout


def test_should_return_empty_json_when_database_empty_with_json_flag(
    mock_repository: MagicMock,
) -> None:
    """List returns empty JSON array when database empty with --json."""
    mock_repository.list_containers.return_value = []

    with _patch_get_repository(mock_repository):
        result = runner.invoke(app, ["--json", "containers", "list"])

    assert result.exit_code == 0
    assert '{"containers": []}' in result.stdout


def test_should_exit_with_error_when_list_connection_fails(
    mock_repository: MagicMock,
) -> None:
    """List handles connection error with helpful message."""
    mock_repository.list_containers.side_effect = CosmosConnectionError(
        "Connection failed"
    )

    with _patch_get_repository(mock_repository):
        result = runner.invoke(app, ["containers", "list"])

    assert result.exit_code == 1
    assert "Failed to connect to Cosmos DB" in result.stdout


def test_should_exit_with_error_when_database_not_found(
    mock_repository: MagicMock,
) -> None:
    """List handles database not found error."""
    mock_repository.list_containers.side_effect = CosmosResourceNotFoundError(
        "Database not found"
    )

    with _patch_get_repository(mock_repository):
        result = runner.invoke(app, ["containers", "list"])

    assert result.exit_code == 1
    assert "Database not found" in result.stdout


# Create Command Tests


def test_should_create_container_when_valid_inputs_provided(
    mock_repository: MagicMock,
) -> None:
    """Create succeeds with valid container name and partition key."""
    mock_repository.create_container.return_value = {"id": "products"}

    with _patch_get_repository(mock_repository):
        result = runner.invoke(
            app, ["containers", "create", "products", "--partition-key", "/category"]
        )

    assert result.exit_code == 0
    assert "Created container 'products'" in result.stdout
    assert "/category" in result.stdout
    assert "400 RU/s" in result.stdout
    mock_repository.create_container.assert_called_once_with(
        "products", "/category", 400
    )


def test_should_use_custom_throughput_when_provided(
    mock_repository: MagicMock,
) -> None:
    """Create uses custom throughput when --throughput flag provided."""
    mock_repository.create_container.return_value = {"id": "users"}

    with _patch_get_repository(mock_repository):
        result = runner.invoke(
            app,
            [
                "containers",
                "create",
                "users",
                "--partition-key",
                "/userId",
                "--throughput",
                "800",
            ],
        )

    assert result.exit_code == 0
    assert "800 RU/s" in result.stdout
    mock_repository.create_container.assert_called_once_with("users", "/userId", 800)


def test_should_return_json_when_create_called_with_json_flag(
    mock_repository: MagicMock,
) -> None:
    """Create returns JSON format when --json flag provided."""
    mock_repository.create_container.return_value = {"id": "products"}

    with _patch_get_repository(mock_repository):
        result = runner.invoke(
            app,
            [
                "--json",
                "containers",
                "create",
                "products",
                "--partition-key",
                "/category",
            ],
        )

    assert result.exit_code == 0
    assert '"container"' in result.stdout
    assert '"name": "products"' in result.stdout
    assert '"partition_key": "/category"' in result.stdout
    assert '"throughput": 400' in result.stdout


def test_should_reject_partition_key_without_leading_slash() -> None:
    """Create validates partition key starts with '/'."""
    result = runner.invoke(
        app, ["containers", "create", "products", "--partition-key", "category"]
    )

    assert result.exit_code == 2  # Bad parameter
    # Error messages from typer go to stderr
    output = result.stdout + result.stderr
    assert "Partition key must start with '/'" in output


def test_should_exit_with_error_when_container_already_exists(
    mock_repository: MagicMock,
) -> None:
    """Create handles duplicate container error with helpful message."""
    mock_repository.create_container.side_effect = CosmosResourceExistsError(
        "Container 'products' already exists"
    )

    with _patch_get_repository(mock_repository):
        result = runner.invoke(
            app, ["containers", "create", "products", "--partition-key", "/category"]
        )

    assert result.exit_code == 1
    assert "Container 'products' already exists" in result.stdout
    assert "orbit containers list" in result.stdout


def test_should_exit_with_error_when_quota_exceeded(
    mock_repository: MagicMock,
) -> None:
    """Create handles quota exceeded error."""
    mock_repository.create_container.side_effect = CosmosQuotaExceededError(
        "Throughput quota exceeded"
    )

    with _patch_get_repository(mock_repository):
        result = runner.invoke(
            app,
            [
                "containers",
                "create",
                "products",
                "--partition-key",
                "/category",
                "--throughput",
                "10000",
            ],
        )

    assert result.exit_code == 1
    assert "Throughput quota exceeded" in result.stdout


def test_should_exit_with_error_when_partition_key_invalid(
    mock_repository: MagicMock,
) -> None:
    """Create handles invalid partition key error."""
    mock_repository.create_container.side_effect = CosmosInvalidPartitionKeyError(
        "Invalid partition key"
    )

    with _patch_get_repository(mock_repository):
        result = runner.invoke(
            app, ["containers", "create", "products", "--partition-key", "/"]
        )

    assert result.exit_code == 1
    assert "Invalid partition key" in result.stdout


def test_should_exit_with_error_when_create_connection_fails(
    mock_repository: MagicMock,
) -> None:
    """Create handles connection error."""
    mock_repository.create_container.side_effect = CosmosConnectionError(
        "Connection failed"
    )

    with _patch_get_repository(mock_repository):
        result = runner.invoke(
            app, ["containers", "create", "products", "--partition-key", "/category"]
        )

    assert result.exit_code == 1
    assert "Failed to connect to Cosmos DB" in result.stdout


def test_should_exit_with_error_when_invalid_container_name(
    mock_repository: MagicMock,
) -> None:
    """Create handles invalid container name."""
    mock_repository.create_container.side_effect = ValueError("Invalid container name")

    with _patch_get_repository(mock_repository):
        result = runner.invoke(
            app, ["containers", "create", "bad@name", "--partition-key", "/id"]
        )

    assert result.exit_code == 1
    assert "Invalid input" in result.stdout


# Delete Command Tests


def test_should_delete_container_when_user_confirms(
    mock_repository: MagicMock,
) -> None:
    """Delete removes container when user confirms prompt."""
    with _patch_get_repository(mock_repository):
        # CliRunner can simulate user input with 'y' for yes
        result = runner.invoke(app, ["containers", "delete", "products"], input="y\n")

    assert result.exit_code == 0
    assert "Deleted container 'products'" in result.stdout
    mock_repository.delete_container.assert_called_once_with("products")


def test_should_skip_confirmation_when_yes_flag_provided(
    mock_repository: MagicMock,
) -> None:
    """Delete skips confirmation with --yes flag."""
    with _patch_get_repository(mock_repository):
        result = runner.invoke(app, ["--yes", "containers", "delete", "products"])

    assert result.exit_code == 0
    assert "Deleted container 'products'" in result.stdout
    mock_repository.delete_container.assert_called_once_with("products")


def test_should_abort_when_user_declines_confirmation(
    mock_repository: MagicMock,
) -> None:
    """Delete aborts when user declines confirmation."""
    with _patch_get_repository(mock_repository):
        # CliRunner can simulate user input with 'n' for no
        result = runner.invoke(app, ["containers", "delete", "products"], input="n\n")

    assert result.exit_code == 1
    assert "Aborted by user" in result.stdout
    mock_repository.delete_container.assert_not_called()


def test_should_return_json_when_delete_called_with_json_flag(
    mock_repository: MagicMock,
) -> None:
    """Delete returns JSON format when --json flag provided."""
    with _patch_get_repository(mock_repository):
        result = runner.invoke(
            app, ["--yes", "--json", "containers", "delete", "products"]
        )

    assert result.exit_code == 0
    assert '"status": "deleted"' in result.stdout
    assert '"container": "products"' in result.stdout


def test_should_exit_with_error_when_delete_connection_fails(
    mock_repository: MagicMock,
) -> None:
    """Delete handles connection error."""
    mock_repository.delete_container.side_effect = CosmosConnectionError(
        "Connection failed"
    )

    with _patch_get_repository(mock_repository):
        result = runner.invoke(app, ["--yes", "containers", "delete", "products"])

    assert result.exit_code == 1
    assert "Failed to connect to Cosmos DB" in result.stdout


def test_should_succeed_when_deleting_nonexistent_container(
    mock_repository: MagicMock,
) -> None:
    """Delete is idempotent - succeeds even if container doesn't exist."""
    # Repository's delete_container is idempotent, doesn't raise for missing containers
    mock_repository.delete_container.return_value = None

    with _patch_get_repository(mock_repository):
        result = runner.invoke(app, ["--yes", "containers", "delete", "nonexistent"])

    assert result.exit_code == 0
    assert "Deleted container 'nonexistent'" in result.stdout


# Integration Tests


def test_should_show_containers_subcommands_in_help() -> None:
    """Verify containers command group is registered."""
    result = runner.invoke(app, ["containers", "--help"])

    assert result.exit_code == 0
    assert "list" in result.stdout
    assert "create" in result.stdout
    assert "delete" in result.stdout


def test_should_support_global_json_flag_for_all_commands(
    mock_repository: MagicMock,
) -> None:
    """Global --json flag works with all container commands."""
    mock_repository.list_containers.return_value = []

    with _patch_get_repository(mock_repository):
        result = runner.invoke(app, ["--json", "containers", "list"])

    assert result.exit_code == 0
    assert "containers" in result.stdout


def test_should_not_expose_secrets_in_error_messages(
    mock_repository: MagicMock,
) -> None:
    """Verify no connection strings in output."""
    mock_repository.create_container.side_effect = CosmosConnectionError(
        "Connection failed"
    )

    with _patch_get_repository(mock_repository):
        result = runner.invoke(
            app, ["containers", "create", "products", "--partition-key", "/id"]
        )

    assert "AccountEndpoint" not in result.stdout
    assert "AccountKey" not in result.stdout
    assert "connection string" in result.stdout.lower()
