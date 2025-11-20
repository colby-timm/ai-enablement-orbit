"""Repository abstraction for Cosmos operations.

Concrete implementations will wrap azure-cosmos SDK interactions.
"""

from __future__ import annotations

from typing import Any, Protocol


class CosmosRepository(Protocol):
    """Abstract repository defining Cosmos data operations.

    Methods are intentionally left as TODO placeholders to avoid premature
    assumptions about query patterns and partition strategies.
    """

    def list_containers(self) -> list[dict[str, Any]]:
        """List all containers in the configured database.

        Returns:
            List of container metadata dictionaries containing name and properties.

        Raises:
            CosmosConnectionError: When connection to Cosmos DB fails.
        """
        ...

    def create_container(
        self, name: str, partition_key_path: str, throughput: int = 400
    ) -> dict[str, Any]:
        """Create a new container with specified partition key.

        Args:
            name: Container name (alphanumeric and hyphens, max 255 chars).
            partition_key_path: Partition key path (must start with '/').
            throughput: RU/s throughput (default: 400, minimum manual throughput).

        Returns:
            Created container metadata.

        Raises:
            CosmosResourceExistsError: Container with this name already exists.
            CosmosInvalidPartitionKeyError: Partition key path is invalid.
            CosmosQuotaExceededError: Throughput quota exceeded.
            CosmosConnectionError: Connection to Cosmos DB fails.
            ValueError: Container name contains invalid characters.
        """
        ...

    def delete_container(self, name: str) -> None:
        """Delete a container by name (idempotent).

        Args:
            name: Container name to delete.

        Raises:
            CosmosConnectionError: Connection to Cosmos DB fails.

        Note:
            Does not raise error if container does not exist.
        """
        ...

    def get_container_properties(self, name: str) -> dict[str, Any]:
        """Retrieve container properties including partition key and throughput.

        Args:
            name: Container name.

        Returns:
            Dictionary containing name, partition key, throughput, and indexing policy.

        Raises:
            CosmosResourceNotFoundError: Container does not exist.
            CosmosConnectionError: Connection to Cosmos DB fails.
        """
        ...

    def get_item(self, item_id: str) -> Any:  # pragma: no cover - placeholder
        """Retrieve a single item by its identifier.

        TODO: define partition key handling and error modes.
        """
        raise NotImplementedError("TODO: implement get_item")

    def list_items(self) -> list[Any]:  # pragma: no cover - placeholder
        """List items with default pagination limit.

        TODO: implement cross-partition queries and RU tracking.
        """
        raise NotImplementedError("TODO: implement list_items")
