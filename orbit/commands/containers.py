"""Container management CLI commands.

Provides list, create, and delete operations for Cosmos DB containers.
"""

from __future__ import annotations

from typing import Any

import typer
from rich.table import Table

from orbit.cli import context_state
from orbit.config import OrbitSettings
from orbit.confirmation import require_confirmation
from orbit.exceptions import (
    CosmosAuthError,
    CosmosConnectionError,
    CosmosInvalidPartitionKeyError,
    CosmosQuotaExceededError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)
from orbit.factory import RepositoryFactory
from orbit.repositories.cosmos import CosmosContainerRepository

containers_app = typer.Typer(help="Manage Cosmos DB containers")

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
        # Database name not configured
        typer.echo(f"Configuration error: {e}")
        typer.echo(
            "Set the ORBIT_DATABASE_NAME environment variable to your database name."
        )
        raise typer.Exit(1) from None
    except CosmosAuthError as e:
        # Connection string missing or invalid
        typer.echo(f"Authentication error: {e}")
        typer.echo(
            "Set the ORBIT_COSMOS_CONNECTION_STRING environment variable "
            "with your Cosmos DB connection string."
        )
        raise typer.Exit(1) from None


def _validate_partition_key(partition_key: str) -> None:
    """Validate partition key path format.

    Args:
        partition_key: Partition key path to validate.

    Raises:
        typer.BadParameter: If partition key doesn't start with '/'.
    """
    if not partition_key.startswith("/"):
        raise typer.BadParameter("Partition key must start with '/', e.g., /id")


def _format_containers_table(containers: list[dict[str, Any]]) -> Table:
    """Create Rich table for container list.

    Args:
        containers: List of container metadata dicts.

    Returns:
        Formatted Rich Table.
    """
    table = Table(title="Containers")
    table.add_column("Name", style="cyan")
    table.add_column("Partition Key", style="green")
    table.add_column("Throughput (RU/s)", style="yellow")

    for container in containers:
        name = container.get("id", "")
        partition_key = container.get("partitionKey", {}).get("paths", [""])[0]
        # Throughput may not be present in all scenarios
        throughput = str(container.get("throughput", "N/A"))
        table.add_row(name, partition_key, throughput)

    return table


@containers_app.command("list")
def list_containers() -> None:
    """List all containers in the database."""
    try:
        repository = _get_repository()
        containers = repository.list_containers()

        if not containers:
            if context_state.json:
                context_state.output.render({"containers": []})
            else:
                typer.echo("No containers found")
            return

        if context_state.json:
            formatted = [
                {
                    "name": c.get("id", ""),
                    "partition_key": c.get("partitionKey", {}).get("paths", [""])[0],
                    "throughput": c.get("throughput", "N/A"),
                }
                for c in containers
            ]
            context_state.output.render({"containers": formatted})
        else:
            table = _format_containers_table(containers)
            context_state.output.render(table)

    except CosmosConnectionError:
        typer.echo(CONNECTION_ERROR_MSG)
        raise typer.Exit(1) from None
    except CosmosResourceNotFoundError:
        typer.echo("Database not found. Verify database name in connection string.")
        raise typer.Exit(1) from None


@containers_app.command("create")
def create_container(
    name: str = typer.Argument(..., help="Container name"),
    partition_key: str = typer.Option(
        ..., "--partition-key", help="Partition key path (e.g., /id)"
    ),
    throughput: int = typer.Option(
        400, "--throughput", help="Throughput in RU/s (default: 400)"
    ),
) -> None:
    """Create a new container with the specified partition key."""
    _validate_partition_key(partition_key)

    try:
        repository = _get_repository()
        repository.create_container(name, partition_key, throughput)

        if context_state.json:
            context_state.output.render(
                {
                    "container": {
                        "name": name,
                        "partition_key": partition_key,
                        "throughput": throughput,
                    }
                }
            )
        else:
            typer.echo(
                f"Created container '{name}' with partition key "
                f"'{partition_key}' ({throughput} RU/s)"
            )

    except CosmosResourceExistsError:
        typer.echo(
            f"Container '{name}' already exists. "
            "Use 'orbit containers list' to see existing containers."
        )
        raise typer.Exit(1) from None
    except CosmosQuotaExceededError:
        typer.echo(
            "Throughput quota exceeded. Reduce --throughput value or "
            "check account limits."
        )
        raise typer.Exit(1) from None
    except CosmosInvalidPartitionKeyError as e:
        typer.echo(f"Invalid partition key: {e}")
        raise typer.Exit(1) from None
    except CosmosConnectionError:
        typer.echo(CONNECTION_ERROR_MSG)
        raise typer.Exit(1) from None
    except ValueError as e:
        typer.echo(f"Invalid input: {e}")
        raise typer.Exit(1) from None


@containers_app.command("delete")
def delete_container(
    name: str = typer.Argument(..., help="Container name to delete"),
) -> None:
    """Delete a container. Requires confirmation unless --yes is provided."""
    require_confirmation(f"Delete container '{name}'? This cannot be undone.")

    try:
        repository = _get_repository()
        repository.delete_container(name)

        if context_state.json:
            context_state.output.render({"status": "deleted", "container": name})
        else:
            typer.echo(f"Deleted container '{name}'")

    except CosmosConnectionError:
        typer.echo(CONNECTION_ERROR_MSG)
        raise typer.Exit(1) from None
