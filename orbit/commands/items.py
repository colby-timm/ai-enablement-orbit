"""Item management CLI commands.

Provides CRUD operations for items in Cosmos DB containers.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import typer
from rich.json import JSON
from rich.table import Table

from orbit.cli import context_state
from orbit.config import OrbitSettings
from orbit.confirmation import require_confirmation
from orbit.exceptions import (
    CosmosAuthError,
    CosmosConnectionError,
    CosmosDuplicateItemError,
    CosmosItemNotFoundError,
    CosmosPartitionKeyMismatchError,
    CosmosResourceNotFoundError,
)
from orbit.factory import RepositoryFactory
from orbit.repositories.cosmos import CosmosContainerRepository

items_app = typer.Typer(help="Manage items in Cosmos DB containers")

# Help text constants
CONTAINER_NAME_HELP = "Container name"
PARTITION_KEY_HELP = "Partition key value"

# Error message constants
CONNECTION_ERROR_MSG = "Failed to connect to Cosmos DB. Check connection string."


def _get_repository() -> CosmosContainerRepository:
    """Get repository instance from factory.

    Returns:
        CosmosContainerRepository: Configured repository instance.

    Raises:
        typer.Exit: When configuration is invalid or auth fails.
    """
    try:
        settings = OrbitSettings.load()
        factory = RepositoryFactory(settings)
        return factory.get_container_repository()
    except ValueError as e:
        typer.echo(f"Configuration error: {e}")
        typer.echo(
            "Set the ORBIT_DATABASE_NAME environment variable to your database name."
        )
        raise typer.Exit(1) from None
    except CosmosAuthError as e:
        typer.echo(f"Authentication error: {e}")
        typer.echo(
            "Set the ORBIT_COSMOS_CONNECTION_STRING environment variable "
            "with your Cosmos DB connection string."
        )
        raise typer.Exit(1) from None


def _read_json_file(file_path: str) -> dict[str, Any]:
    """Read and parse JSON from file or stdin.

    Args:
        file_path: Path to JSON file or '-' for stdin.

    Returns:
        Parsed JSON dictionary.

    Raises:
        typer.BadParameter: When file not found or JSON is invalid.
    """
    try:
        if file_path == "-":
            content = sys.stdin.read()
        else:
            content = Path(file_path).read_text()

        data = json.loads(content)

        if not isinstance(data, dict):
            raise typer.BadParameter("JSON must be a single object, not an array")

        return data
    except FileNotFoundError:
        raise typer.BadParameter(f"File not found: {file_path}") from None
    except json.JSONDecodeError:
        raise typer.BadParameter(f"Invalid JSON in file: {file_path}") from None


def _build_item_table(items: list[dict[str, Any]]) -> Table:
    """Create Rich table for item list.

    Args:
        items: List of item dictionaries.

    Returns:
        Formatted Rich Table.
    """
    table = Table(title="Items")

    if not items:
        return table

    # Get columns from first item
    first_item = items[0]
    for key in first_item.keys():
        table.add_column(key, style="cyan")

    # Add rows with truncation for long values
    for item in items:
        row_values = []
        for key in first_item.keys():
            value = str(item.get(key, ""))
            if len(value) > 50:
                value = value[:47] + "..."
            row_values.append(value)
        table.add_row(*row_values)

    return table


@items_app.command("create")
def create_item(
    container: str = typer.Argument(
        ..., help="Container name where item will be created"
    ),
    data: str = typer.Option(
        ...,
        "--data",
        help="Path to JSON file containing item data (or '-' for stdin)",
    ),
    partition_key: str = typer.Option(..., "--partition-key", help=PARTITION_KEY_HELP),
) -> None:
    """Create a new item in the specified container from JSON file."""
    item_data = _read_json_file(data)

    if "id" not in item_data:
        raise typer.BadParameter("Item must have 'id' field")

    try:
        repository = _get_repository()
        created_item = repository.create_item(container, item_data, partition_key)

        if context_state.json:
            context_state.output.render({"status": "created", "item": created_item})
        else:
            typer.echo(f"Created item '{item_data['id']}' in container '{container}'")
            context_state.output.render(JSON(json.dumps(created_item, indent=2)))

    except CosmosDuplicateItemError:
        typer.echo(
            f"Item '{item_data['id']}' already exists in container '{container}'"
        )
        raise typer.Exit(1) from None
    except CosmosPartitionKeyMismatchError:
        typer.echo(
            f"Partition key mismatch: item partition key "
            f"doesn't match '{partition_key}'"
        )
        raise typer.Exit(1) from None
    except CosmosResourceNotFoundError:
        typer.echo(
            f"Container '{container}' not found. "
            "Use 'orbit containers list' to see existing containers."
        )
        raise typer.Exit(1) from None
    except CosmosConnectionError:
        typer.echo(CONNECTION_ERROR_MSG)
        raise typer.Exit(1) from None


@items_app.command("get")
def get_item(
    container: str = typer.Argument(..., help=CONTAINER_NAME_HELP),
    item_id: str = typer.Argument(..., help="Item ID to retrieve"),
    partition_key: str = typer.Option(..., "--partition-key", help=PARTITION_KEY_HELP),
) -> None:
    """Retrieve a single item by ID and partition key."""
    try:
        repository = _get_repository()
        item = repository.get_item(container, item_id, partition_key)

        if context_state.json:
            context_state.output.render({"item": item})
        else:
            context_state.output.render(JSON(json.dumps(item, indent=2)))

    except CosmosItemNotFoundError:
        typer.echo(
            f"Item '{item_id}' not found in container '{container}'. "
            "Check item ID and partition key."
        )
        raise typer.Exit(1) from None
    except CosmosPartitionKeyMismatchError:
        typer.echo(f"Item '{item_id}' not found with partition key '{partition_key}'")
        raise typer.Exit(1) from None
    except CosmosResourceNotFoundError:
        typer.echo(
            f"Container '{container}' not found. "
            "Use 'orbit containers list' to see existing containers."
        )
        raise typer.Exit(1) from None
    except CosmosConnectionError:
        typer.echo(CONNECTION_ERROR_MSG)
        raise typer.Exit(1) from None


@items_app.command("update")
def update_item(
    container: str = typer.Argument(..., help=CONTAINER_NAME_HELP),
    item_id: str = typer.Argument(..., help="Item ID to update"),
    data: str = typer.Option(
        ...,
        "--data",
        help="Path to JSON file with updated item data (or '-' for stdin)",
    ),
    partition_key: str = typer.Option(..., "--partition-key", help=PARTITION_KEY_HELP),
) -> None:
    """Update an existing item (or create if not exists) from JSON file."""
    item_data = _read_json_file(data)

    if "id" not in item_data:
        raise typer.BadParameter("Item must have 'id' field")

    if item_data["id"] != item_id:
        raise typer.BadParameter("Item ID in JSON must match command parameter")

    try:
        repository = _get_repository()
        updated_item = repository.update_item(
            container, item_id, item_data, partition_key
        )

        if context_state.json:
            context_state.output.render({"status": "updated", "item": updated_item})
        else:
            typer.echo(f"Updated item '{item_id}' in container '{container}'")
            context_state.output.render(JSON(json.dumps(updated_item, indent=2)))

    except CosmosPartitionKeyMismatchError:
        typer.echo(
            f"Partition key mismatch: item partition key "
            f"doesn't match '{partition_key}'"
        )
        raise typer.Exit(1) from None
    except CosmosResourceNotFoundError:
        typer.echo(
            f"Container '{container}' not found. "
            "Use 'orbit containers list' to see existing containers."
        )
        raise typer.Exit(1) from None
    except CosmosConnectionError:
        typer.echo(CONNECTION_ERROR_MSG)
        raise typer.Exit(1) from None


@items_app.command("delete")
def delete_item(
    container: str = typer.Argument(..., help=CONTAINER_NAME_HELP),
    item_id: str = typer.Argument(..., help="Item ID to delete"),
    partition_key: str = typer.Option(..., "--partition-key", help=PARTITION_KEY_HELP),
) -> None:
    """Delete an item from the container."""
    require_confirmation(
        f"Delete item '{item_id}' from container '{container}'? This cannot be undone."
    )

    try:
        repository = _get_repository()
        repository.delete_item(container, item_id, partition_key)

        if context_state.json:
            context_state.output.render(
                {"status": "deleted", "item_id": item_id, "container": container}
            )
        else:
            typer.echo(f"Deleted item '{item_id}' from container '{container}'")

    except CosmosResourceNotFoundError:
        typer.echo(
            f"Container '{container}' not found. "
            "Use 'orbit containers list' to see existing containers."
        )
        raise typer.Exit(1) from None
    except CosmosConnectionError:
        typer.echo(CONNECTION_ERROR_MSG)
        raise typer.Exit(1) from None


@items_app.command("list")
def list_items(
    container: str = typer.Argument(..., help=CONTAINER_NAME_HELP),
    max_count: int = typer.Option(
        100, "--max-count", help="Maximum number of items to retrieve (default: 100)"
    ),
) -> None:
    """List items in the container with pagination."""
    try:
        repository = _get_repository()
        items = repository.list_items(container, max_count=max_count)

        if not items:
            if context_state.json:
                context_state.output.render({"items": [], "count": 0})
            else:
                typer.echo(f"No items found in container '{container}'")
            return

        if context_state.json:
            context_state.output.render({"items": items, "count": len(items)})
        else:
            table = _build_item_table(items)
            context_state.output.render(table)

    except CosmosResourceNotFoundError:
        typer.echo(
            f"Container '{container}' not found. "
            "Use 'orbit containers list' to see existing containers."
        )
        raise typer.Exit(1) from None
    except CosmosConnectionError:
        typer.echo(CONNECTION_ERROR_MSG)
        raise typer.Exit(1) from None
