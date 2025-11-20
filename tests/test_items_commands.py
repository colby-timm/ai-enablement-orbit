"""Unit tests for item management commands.

Tests all item CRUD operations with mocked repository layer.
"""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from orbit.cli import app, context_state
from orbit.commands.items import (
    _build_item_table,
    _read_json_file,
)
from orbit.exceptions import (
    CosmosConnectionError,
    CosmosDuplicateItemError,
    CosmosItemNotFoundError,
    CosmosPartitionKeyMismatchError,
    CosmosResourceNotFoundError,
)

runner = CliRunner()


@pytest.fixture
def mock_repository():
    """Mock CosmosContainerRepository for all tests."""
    with patch("orbit.commands.items._get_repository") as mock:
        repo = MagicMock()
        mock.return_value = repo
        yield repo


@pytest.fixture
def sample_item():
    """Sample item data for tests."""
    return {"id": "item123", "category": "electronics", "name": "Laptop", "price": 1000}


@pytest.fixture(autouse=True)
def reset_context():
    """Reset context state before each test."""
    context_state.json = False
    context_state.yes = False
    context_state.init_output()


class TestReadJsonFile:
    """Tests for _read_json_file helper function."""

    def test_should_read_json_file_from_path(self, tmp_path):
        """Read and parse JSON from file path."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"id": "test123", "name": "Test"}')

        result = _read_json_file(str(test_file))

        assert result == {"id": "test123", "name": "Test"}

    def test_should_read_json_from_stdin(self):
        """Read and parse JSON from stdin."""
        with patch("sys.stdin", StringIO('{"id": "stdin123", "name": "Stdin"}')):
            result = _read_json_file("-")

        assert result == {"id": "stdin123", "name": "Stdin"}

    def test_should_fail_when_file_not_found(self):
        """Raise BadParameter when file doesn't exist."""
        with pytest.raises(typer.BadParameter, match="File not found: missing.json"):
            _read_json_file("missing.json")

    def test_should_fail_when_json_invalid(self, tmp_path):
        """Raise BadParameter when JSON is malformed."""
        test_file = tmp_path / "bad.json"
        test_file.write_text('{"id": "test", invalid}')

        with pytest.raises(typer.BadParameter, match="Invalid JSON in file"):
            _read_json_file(str(test_file))

    def test_should_fail_when_json_is_array(self, tmp_path):
        """Raise BadParameter when JSON is array instead of object."""
        test_file = tmp_path / "array.json"
        test_file.write_text('[{"id": "item1"}, {"id": "item2"}]')

        with pytest.raises(typer.BadParameter, match="JSON must be a single object"):
            _read_json_file(str(test_file))


class TestBuildItemTable:
    """Tests for _build_item_table helper function."""

    def test_should_build_table_with_columns(self, sample_item):
        """Create table with columns from item keys."""
        items = [sample_item]

        table = _build_item_table(items)

        assert table.title == "Items"
        # Verify columns match item keys
        column_headers = [col.header for col in table.columns]
        assert "id" in column_headers
        assert "category" in column_headers
        assert "name" in column_headers

    def test_should_truncate_long_values_in_table(self):
        """Truncate values longer than 50 characters."""
        long_value = "x" * 100
        items = [{"id": "test", "description": long_value}]

        table = _build_item_table(items)

        # Check that row contains truncated value
        assert len(table.rows) == 1

    def test_should_handle_empty_list(self):
        """Return empty table when no items provided."""
        table = _build_item_table([])

        assert table.title == "Items"
        assert len(table.rows) == 0


class TestCreateItemCommand:
    """Tests for create item command."""

    def test_should_create_item_from_file_when_valid_json(
        self, mock_repository, sample_item, tmp_path
    ):
        """Create item from JSON file successfully."""
        test_file = tmp_path / "item.json"
        test_file.write_text(json.dumps(sample_item))

        mock_repository.create_item.return_value = sample_item

        result = runner.invoke(
            app,
            [
                "items",
                "create",
                "products",
                "--data",
                str(test_file),
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 0
        assert "Created item 'item123' in container 'products'" in result.stdout
        mock_repository.create_item.assert_called_once_with(
            "products", sample_item, "electronics"
        )

    def test_should_create_item_from_stdin_when_data_is_dash(
        self, mock_repository, sample_item
    ):
        """Create item from stdin input."""
        mock_repository.create_item.return_value = sample_item

        result = runner.invoke(
            app,
            [
                "items",
                "create",
                "products",
                "--data",
                "-",
                "--partition-key",
                "electronics",
            ],
            input=json.dumps(sample_item),
        )

        assert result.exit_code == 0
        assert "Created item 'item123'" in result.stdout
        mock_repository.create_item.assert_called_once()

    def test_should_create_item_with_json_output(
        self, mock_repository, sample_item, tmp_path
    ):
        """Create item with JSON output mode."""
        test_file = tmp_path / "item.json"
        test_file.write_text(json.dumps(sample_item))

        mock_repository.create_item.return_value = sample_item

        result = runner.invoke(
            app,
            [
                "--json",
                "items",
                "create",
                "products",
                "--data",
                str(test_file),
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 0
        output_data = json.loads(result.stdout)
        assert output_data["status"] == "created"
        assert output_data["item"]["id"] == "item123"

    def test_should_fail_when_json_file_not_found(self):
        """Fail with error when JSON file doesn't exist."""
        result = runner.invoke(
            app,
            [
                "items",
                "create",
                "products",
                "--data",
                "missing.json",
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code != 0
        # BadParameter exceptions go to stderr in Typer
        assert (
            "File not found: missing.json" in result.stderr
            or "File not found: missing.json" in result.stdout
        )

    def test_should_fail_when_item_missing_id_field(self, tmp_path):
        """Fail when item doesn't have id field."""
        test_file = tmp_path / "no-id.json"
        test_file.write_text('{"name": "Laptop"}')

        result = runner.invoke(
            app,
            [
                "items",
                "create",
                "products",
                "--data",
                str(test_file),
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code != 0
        # BadParameter exceptions go to stderr in Typer
        assert (
            "Item must have 'id' field" in result.stderr
            or "Item must have 'id' field" in result.stdout
        )

    def test_should_handle_duplicate_item_error(
        self, mock_repository, sample_item, tmp_path
    ):
        """Handle duplicate item error gracefully."""
        test_file = tmp_path / "item.json"
        test_file.write_text(json.dumps(sample_item))

        mock_repository.create_item.side_effect = CosmosDuplicateItemError(
            "Item exists"
        )

        result = runner.invoke(
            app,
            [
                "items",
                "create",
                "products",
                "--data",
                str(test_file),
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 1
        assert "Item 'item123' already exists" in result.stdout

    def test_should_handle_partition_key_mismatch_on_create(
        self, mock_repository, sample_item, tmp_path
    ):
        """Handle partition key mismatch error."""
        test_file = tmp_path / "item.json"
        test_file.write_text(json.dumps(sample_item))

        mock_repository.create_item.side_effect = CosmosPartitionKeyMismatchError(
            "Mismatch"
        )

        result = runner.invoke(
            app,
            [
                "items",
                "create",
                "products",
                "--data",
                str(test_file),
                "--partition-key",
                "books",
            ],
        )

        assert result.exit_code == 1
        assert "Partition key mismatch" in result.stdout

    def test_should_handle_container_not_found_on_create(
        self, mock_repository, sample_item, tmp_path
    ):
        """Handle container not found error."""
        test_file = tmp_path / "item.json"
        test_file.write_text(json.dumps(sample_item))

        mock_repository.create_item.side_effect = CosmosResourceNotFoundError(
            "Container not found"
        )

        result = runner.invoke(
            app,
            [
                "items",
                "create",
                "missing",
                "--data",
                str(test_file),
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 1
        assert "Container 'missing' not found" in result.stdout

    def test_should_handle_connection_error_on_create(
        self, mock_repository, sample_item, tmp_path
    ):
        """Handle connection error."""
        test_file = tmp_path / "item.json"
        test_file.write_text(json.dumps(sample_item))

        mock_repository.create_item.side_effect = CosmosConnectionError(
            "Connection failed"
        )

        result = runner.invoke(
            app,
            [
                "items",
                "create",
                "products",
                "--data",
                str(test_file),
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 1
        assert "Failed to connect to Cosmos DB" in result.stdout


class TestGetItemCommand:
    """Tests for get item command."""

    def test_should_get_item_when_exists(self, mock_repository, sample_item):
        """Retrieve existing item successfully."""
        mock_repository.get_item.return_value = sample_item

        result = runner.invoke(
            app,
            ["items", "get", "products", "item123", "--partition-key", "electronics"],
        )

        assert result.exit_code == 0
        assert "item123" in result.stdout
        mock_repository.get_item.assert_called_once_with(
            "products", "item123", "electronics"
        )

    def test_should_get_item_with_json_output(self, mock_repository, sample_item):
        """Get item with JSON output mode."""
        mock_repository.get_item.return_value = sample_item

        result = runner.invoke(
            app,
            [
                "--json",
                "items",
                "get",
                "products",
                "item123",
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 0
        output_data = json.loads(result.stdout)
        assert output_data["item"]["id"] == "item123"

    def test_should_fail_when_item_not_found(self, mock_repository):
        """Fail when item doesn't exist."""
        mock_repository.get_item.side_effect = CosmosItemNotFoundError("Not found")

        result = runner.invoke(
            app,
            ["items", "get", "products", "missing", "--partition-key", "electronics"],
        )

        assert result.exit_code == 1
        assert "Item 'missing' not found" in result.stdout
        assert "Check item ID and partition key" in result.stdout

    def test_should_handle_partition_key_mismatch_on_get(self, mock_repository):
        """Handle partition key mismatch error."""
        mock_repository.get_item.side_effect = CosmosPartitionKeyMismatchError(
            "Mismatch"
        )

        result = runner.invoke(
            app,
            ["items", "get", "products", "item123", "--partition-key", "wrong"],
        )

        assert result.exit_code == 1
        assert "not found with partition key 'wrong'" in result.stdout

    def test_should_handle_container_not_found_on_get(self, mock_repository):
        """Handle container not found error."""
        mock_repository.get_item.side_effect = CosmosResourceNotFoundError(
            "Container not found"
        )

        result = runner.invoke(
            app,
            ["items", "get", "missing", "item123", "--partition-key", "electronics"],
        )

        assert result.exit_code == 1
        assert "Container 'missing' not found" in result.stdout


class TestUpdateItemCommand:
    """Tests for update item command."""

    def test_should_update_item_from_file_when_valid(
        self, mock_repository, sample_item, tmp_path
    ):
        """Update item from JSON file successfully."""
        test_file = tmp_path / "updated.json"
        test_file.write_text(json.dumps(sample_item))

        mock_repository.update_item.return_value = sample_item

        result = runner.invoke(
            app,
            [
                "items",
                "update",
                "products",
                "item123",
                "--data",
                str(test_file),
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 0
        assert "Updated item 'item123' in container 'products'" in result.stdout
        mock_repository.update_item.assert_called_once_with(
            "products", "item123", sample_item, "electronics"
        )

    def test_should_update_item_with_json_output(
        self, mock_repository, sample_item, tmp_path
    ):
        """Update item with JSON output mode."""
        test_file = tmp_path / "updated.json"
        test_file.write_text(json.dumps(sample_item))

        mock_repository.update_item.return_value = sample_item

        result = runner.invoke(
            app,
            [
                "--json",
                "items",
                "update",
                "products",
                "item123",
                "--data",
                str(test_file),
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 0
        output_data = json.loads(result.stdout)
        assert output_data["status"] == "updated"
        assert output_data["item"]["id"] == "item123"

    def test_should_fail_when_item_id_mismatch(self, tmp_path):
        """Fail when item ID in JSON doesn't match parameter."""
        test_file = tmp_path / "mismatch.json"
        test_file.write_text('{"id": "different", "name": "Test"}')

        result = runner.invoke(
            app,
            [
                "items",
                "update",
                "products",
                "item123",
                "--data",
                str(test_file),
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code != 0
        # BadParameter exceptions go to stderr in Typer
        assert (
            "Item ID in JSON must match command parameter" in result.stderr
            or "Item ID in JSON must match command parameter" in result.stdout
        )

    def test_should_handle_partition_key_mismatch_on_update(
        self, mock_repository, sample_item, tmp_path
    ):
        """Handle partition key mismatch error."""
        test_file = tmp_path / "updated.json"
        test_file.write_text(json.dumps(sample_item))

        mock_repository.update_item.side_effect = CosmosPartitionKeyMismatchError(
            "Mismatch"
        )

        result = runner.invoke(
            app,
            [
                "items",
                "update",
                "products",
                "item123",
                "--data",
                str(test_file),
                "--partition-key",
                "wrong",
            ],
        )

        assert result.exit_code == 1
        assert "Partition key mismatch" in result.stdout

    def test_should_handle_container_not_found_on_update(
        self, mock_repository, sample_item, tmp_path
    ):
        """Handle container not found error."""
        test_file = tmp_path / "updated.json"
        test_file.write_text(json.dumps(sample_item))

        mock_repository.update_item.side_effect = CosmosResourceNotFoundError(
            "Container not found"
        )

        result = runner.invoke(
            app,
            [
                "items",
                "update",
                "missing",
                "item123",
                "--data",
                str(test_file),
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 1
        assert "Container 'missing' not found" in result.stdout


class TestDeleteItemCommand:
    """Tests for delete item command."""

    @patch("orbit.commands.items.require_confirmation")
    def test_should_delete_item_with_confirmation(self, mock_confirm, mock_repository):
        """Delete item with confirmation prompt."""
        mock_confirm.return_value = None  # Confirmation accepted

        result = runner.invoke(
            app,
            [
                "items",
                "delete",
                "products",
                "item123",
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 0
        assert "Deleted item 'item123' from container 'products'" in result.stdout
        mock_repository.delete_item.assert_called_once_with(
            "products", "item123", "electronics"
        )
        mock_confirm.assert_called_once()

    def test_should_delete_item_without_confirmation_when_yes_flag(
        self, mock_repository
    ):
        """Delete item without confirmation when --yes flag provided."""
        result = runner.invoke(
            app,
            [
                "--yes",
                "items",
                "delete",
                "products",
                "item123",
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 0
        assert "Deleted item 'item123'" in result.stdout
        mock_repository.delete_item.assert_called_once_with(
            "products", "item123", "electronics"
        )

    def test_should_delete_item_with_json_output(self, mock_repository):
        """Delete item with JSON output mode."""
        result = runner.invoke(
            app,
            [
                "--yes",
                "--json",
                "items",
                "delete",
                "products",
                "item123",
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 0
        output_data = json.loads(result.stdout)
        assert output_data["status"] == "deleted"
        assert output_data["item_id"] == "item123"
        assert output_data["container"] == "products"

    @patch("orbit.commands.items.require_confirmation")
    def test_should_abort_when_confirmation_declined(
        self, mock_confirm, mock_repository
    ):
        """Abort deletion when user declines confirmation."""
        mock_confirm.side_effect = typer.Exit(1)

        result = runner.invoke(
            app,
            [
                "items",
                "delete",
                "products",
                "item123",
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 1
        mock_repository.delete_item.assert_not_called()

    def test_should_handle_container_not_found_on_delete(self, mock_repository):
        """Handle container not found error."""
        mock_repository.delete_item.side_effect = CosmosResourceNotFoundError(
            "Container not found"
        )

        result = runner.invoke(
            app,
            [
                "--yes",
                "items",
                "delete",
                "missing",
                "item123",
                "--partition-key",
                "electronics",
            ],
        )

        assert result.exit_code == 1
        assert "Container 'missing' not found" in result.stdout


class TestListItemsCommand:
    """Tests for list items command."""

    def test_should_list_items_in_rich_table_when_items_exist(
        self, mock_repository, sample_item
    ):
        """List items in Rich table format."""
        items = [sample_item, {"id": "item456", "category": "books", "name": "Novel"}]
        mock_repository.list_items.return_value = items

        result = runner.invoke(app, ["items", "list", "products"])

        assert result.exit_code == 0
        assert "item123" in result.stdout
        assert "item456" in result.stdout
        mock_repository.list_items.assert_called_once_with("products", max_count=100)

    def test_should_show_no_items_message_when_container_empty(self, mock_repository):
        """Show message when container has no items."""
        mock_repository.list_items.return_value = []

        result = runner.invoke(app, ["items", "list", "products"])

        assert result.exit_code == 0
        assert "No items found in container 'products'" in result.stdout

    def test_should_list_items_in_json_format_when_json_flag(
        self, mock_repository, sample_item
    ):
        """List items in JSON format."""
        items = [sample_item]
        mock_repository.list_items.return_value = items

        result = runner.invoke(app, ["--json", "items", "list", "products"])

        assert result.exit_code == 0
        output_data = json.loads(result.stdout)
        assert output_data["count"] == 1
        assert output_data["items"][0]["id"] == "item123"

    def test_should_list_items_with_json_output_when_empty(self, mock_repository):
        """List items in JSON format when empty."""
        mock_repository.list_items.return_value = []

        result = runner.invoke(app, ["--json", "items", "list", "products"])

        assert result.exit_code == 0
        output_data = json.loads(result.stdout)
        assert output_data["count"] == 0
        assert output_data["items"] == []

    def test_should_apply_max_count_pagination(self, mock_repository, sample_item):
        """Apply custom max count for pagination."""
        mock_repository.list_items.return_value = [sample_item]

        result = runner.invoke(app, ["items", "list", "products", "--max-count", "50"])

        assert result.exit_code == 0
        mock_repository.list_items.assert_called_once_with("products", max_count=50)

    def test_should_handle_container_not_found_on_list(self, mock_repository):
        """Handle container not found error."""
        mock_repository.list_items.side_effect = CosmosResourceNotFoundError(
            "Container not found"
        )

        result = runner.invoke(app, ["items", "list", "missing"])

        assert result.exit_code == 1
        assert "Container 'missing' not found" in result.stdout
