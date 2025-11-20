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

    def get_item(
        self, container_name: str, item_id: str, partition_key_value: str
    ) -> dict[str, Any]:
        """Retrieve a single item by ID and partition key.

        Args:
            container_name: Name of the container containing the item.
            item_id: Unique identifier of the item within the partition.
            partition_key_value: Value of the partition key for this item.

        Returns:
            Dictionary containing the item data.

        Raises:
            CosmosItemNotFoundError: Item does not exist.
            CosmosPartitionKeyMismatchError: Partition key mismatch.
            CosmosConnectionError: Connection to Cosmos DB fails.
        """
        ...

    def create_item(
        self, container_name: str, item: dict[str, Any], partition_key_value: str
    ) -> dict[str, Any]:
        """Create a new item in the specified container.

        Args:
            container_name: Name of the container to create the item in.
            item: Item data dictionary (must include 'id' field).
            partition_key_value: Value of the partition key for this item.

        Returns:
            Created item dictionary.

        Raises:
            CosmosDuplicateItemError: Item with this ID already exists in partition.
            CosmosPartitionKeyMismatchError: Partition key mismatch.
            CosmosConnectionError: Connection to Cosmos DB fails.
            ValueError: Item missing 'id' field or invalid inputs.
        """
        ...

    def update_item(
        self,
        container_name: str,
        item_id: str,
        item: dict[str, Any],
        partition_key_value: str,
    ) -> dict[str, Any]:
        """Update an existing item (upsert: create if not exists).

        Args:
            container_name: Name of the container containing the item.
            item_id: Unique identifier of the item to update.
            item: Complete item data dictionary (must include 'id' field).
            partition_key_value: Value of the partition key for this item.

        Returns:
            Updated item dictionary.

        Raises:
            CosmosPartitionKeyMismatchError: Partition key mismatch.
            CosmosConnectionError: Connection to Cosmos DB fails.
            ValueError: Item['id'] doesn't match item_id parameter.
        """
        ...

    def delete_item(
        self, container_name: str, item_id: str, partition_key_value: str
    ) -> None:
        """Delete an item by ID and partition key (idempotent).

        Args:
            container_name: Name of the container containing the item.
            item_id: Unique identifier of the item to delete.
            partition_key_value: Value of the partition key for this item.

        Raises:
            CosmosPartitionKeyMismatchError: Partition key mismatch.
            CosmosConnectionError: Connection to Cosmos DB fails.

        Note:
            Does not raise error if item does not exist.
        """
        ...

    def list_items(
        self, container_name: str, max_count: int = 100
    ) -> list[dict[str, Any]]:
        """List items in container with pagination limit.

        Args:
            container_name: Name of the container to query.
            max_count: Maximum number of items to return (default: 100).

        Returns:
            List of item dictionaries (up to max_count items).

        Raises:
            CosmosConnectionError: Connection to Cosmos DB fails.
            ValueError: max_count is not a positive integer.
        """
        ...
