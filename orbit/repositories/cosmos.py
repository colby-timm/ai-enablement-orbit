"""Concrete Cosmos DB repository implementation.

Wraps azure-cosmos SDK operations with domain exception translation.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import (
    CosmosHttpResponseError,
)
from azure.cosmos.exceptions import (
    CosmosResourceExistsError as SdkResourceExistsError,
)
from azure.cosmos.exceptions import (
    CosmosResourceNotFoundError as SdkResourceNotFoundError,
)

from orbit.exceptions import (
    CosmosConnectionError,
    CosmosDuplicateItemError,
    CosmosInvalidPartitionKeyError,
    CosmosItemNotFoundError,
    CosmosPartitionKeyMismatchError,
    CosmosQuotaExceededError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)

logger = logging.getLogger(__name__)

# Container name validation: alphanumeric, hyphens, max 255 chars
CONTAINER_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9-]{1,255}$")


class CosmosContainerRepository:
    """Repository for Cosmos DB container lifecycle operations.

    Implements container management operations with proper exception handling
    and secret sanitization.
    """

    def __init__(self, client: CosmosClient, database_name: str) -> None:
        """Initialize repository with authenticated client and database.

        Args:
            client: Authenticated CosmosClient from AuthStrategy.
            database_name: Name of the database to operate on.
        """
        self._client = client
        self._database_name = database_name
        self._database = client.get_database_client(database_name)

    def list_containers(self) -> list[dict[str, Any]]:
        """List all containers in the configured database.

        Returns:
            List of container metadata dictionaries.

        Raises:
            CosmosConnectionError: When connection to Cosmos DB fails.
        """
        try:
            containers = list(self._database.list_containers())
            logger.info(f"Listed {len(containers)} containers in database")
            return containers
        except CosmosHttpResponseError as e:
            logger.error(f"Failed to list containers: {e.status_code}")
            raise CosmosConnectionError(
                f"Failed to list containers: {e.status_code}"
            ) from e

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
        self._validate_container_name(name)
        self._validate_partition_key_path(partition_key_path)

        try:
            partition_key = PartitionKey(path=partition_key_path)
            container = self._database.create_container(
                id=name, partition_key=partition_key, offer_throughput=throughput
            )
            logger.info(
                f"Created container '{name}' with partition key "
                f"'{partition_key_path}' and throughput {throughput} RU/s"
            )
            return container.read()
        except SdkResourceExistsError as e:
            raise CosmosResourceExistsError(f"Container '{name}' already exists") from e
        except CosmosHttpResponseError as e:
            if e.status_code == 429 or "quota" in str(e).lower():
                raise CosmosQuotaExceededError(
                    f"Throughput quota exceeded when creating container '{name}'. "
                    "Consider reducing throughput or upgrading account."
                ) from e
            logger.error(f"Failed to create container '{name}': {e.status_code}")
            raise CosmosConnectionError(
                f"Failed to create container '{name}': {e.status_code}"
            ) from e

    def delete_container(self, name: str) -> None:
        """Delete a container by name (idempotent).

        Args:
            name: Container name to delete.

        Raises:
            CosmosConnectionError: Connection to Cosmos DB fails.

        Note:
            Does not raise error if container does not exist.
        """
        try:
            self._database.delete_container(name)
            logger.info(f"Deleted container '{name}'")
        except SdkResourceNotFoundError:
            # Idempotent: silently succeed if container doesn't exist
            logger.info(f"Container '{name}' not found during delete (idempotent)")
        except CosmosHttpResponseError as e:
            logger.error(f"Failed to delete container '{name}': {e.status_code}")
            raise CosmosConnectionError(
                f"Failed to delete container '{name}': {e.status_code}"
            ) from e

    def get_container_properties(self, name: str) -> dict[str, Any]:
        """Retrieve container properties.

        Args:
            name: Container name.

        Returns:
            Dictionary containing name, partition key, throughput, and indexing policy.

        Raises:
            CosmosResourceNotFoundError: Container does not exist.
            CosmosConnectionError: Connection to Cosmos DB fails.
        """
        try:
            container_client = self._database.get_container_client(name)
            properties = container_client.read()
            logger.info(f"Retrieved properties for container '{name}'")
            return properties
        except SdkResourceNotFoundError as e:
            raise CosmosResourceNotFoundError(f"Container '{name}' not found") from e
        except CosmosHttpResponseError as e:
            logger.error(
                f"Failed to get properties for container '{name}': {e.status_code}"
            )
            raise CosmosConnectionError(
                f"Failed to get properties for container '{name}': {e.status_code}"
            ) from e

    def _validate_container_name(self, name: str) -> None:
        """Validate container name follows Cosmos DB rules.

        Args:
            name: Container name to validate.

        Raises:
            ValueError: Name contains invalid characters or exceeds length.
        """
        if not CONTAINER_NAME_PATTERN.match(name):
            raise ValueError(
                f"Invalid container name '{name}'. "
                "Must be alphanumeric with hyphens, max 255 characters."
            )

    def _validate_partition_key_path(self, path: str) -> None:
        """Validate partition key path follows Cosmos DB rules.

        Args:
            path: Partition key path to validate.

        Raises:
            CosmosInvalidPartitionKeyError: Path does not start with '/'.
        """
        if not path.startswith("/"):
            raise CosmosInvalidPartitionKeyError(
                f"Invalid partition key path '{path}'. "
                "Partition key must start with '/'."
            )

    def _get_container_client(self, container_name: str):
        """Get container client for specified container.

        Args:
            container_name: Name of the container.

        Returns:
            ContainerProxy client for operations.
        """
        return self._database.get_container_client(container_name)

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
        if not isinstance(item, dict) or "id" not in item:
            raise ValueError("Item must be a dictionary with 'id' field")
        if not partition_key_value:
            raise ValueError("Partition key value cannot be empty")
        if not container_name:
            raise ValueError("Container name cannot be empty")

        try:
            container = self._get_container_client(container_name)
            created_item = container.create_item(
                body=item, partition_key=partition_key_value
            )
            logger.info(f"Created item '{item['id']}' in container '{container_name}'")
            return created_item
        except SdkResourceExistsError as e:
            raise CosmosDuplicateItemError(
                f"Item with ID '{item['id']}' already exists in partition"
            ) from e
        except CosmosHttpResponseError as e:
            if e.status_code == 400:
                raise CosmosPartitionKeyMismatchError(
                    f"Partition key mismatch for item '{item['id']}'"
                ) from e
            logger.error(f"Failed to create item: {e.status_code}")
            raise CosmosConnectionError(
                f"Failed to create item: {e.status_code}"
            ) from e

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
        try:
            container = self._get_container_client(container_name)
            item = container.read_item(item=item_id, partition_key=partition_key_value)
            logger.info(f"Retrieved item '{item_id}' from container '{container_name}'")
            return item
        except SdkResourceNotFoundError as e:
            raise CosmosItemNotFoundError(
                f"Item '{item_id}' not found in container '{container_name}'"
            ) from e
        except CosmosHttpResponseError as e:
            if e.status_code == 400:
                raise CosmosPartitionKeyMismatchError(
                    f"Partition key mismatch for item '{item_id}'"
                ) from e
            logger.error(f"Failed to get item '{item_id}': {e.status_code}")
            raise CosmosConnectionError(
                f"Failed to get item '{item_id}': {e.status_code}"
            ) from e

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
        if not isinstance(item, dict):
            raise ValueError("Item must be a dictionary")
        if item.get("id") != item_id:
            raise ValueError(
                f"Item 'id' field must match item_id parameter '{item_id}'"
            )

        try:
            container = self._get_container_client(container_name)
            updated_item = container.upsert_item(
                body=item, partition_key=partition_key_value
            )
            logger.info(f"Updated item '{item_id}' in container '{container_name}'")
            return updated_item
        except CosmosHttpResponseError as e:
            if e.status_code == 400:
                raise CosmosPartitionKeyMismatchError(
                    f"Partition key mismatch for item '{item_id}'"
                ) from e
            logger.error(f"Failed to update item '{item_id}': {e.status_code}")
            raise CosmosConnectionError(
                f"Failed to update item '{item_id}': {e.status_code}"
            ) from e

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
        try:
            container = self._get_container_client(container_name)
            container.delete_item(item=item_id, partition_key=partition_key_value)
            logger.info(f"Deleted item '{item_id}' from container '{container_name}'")
        except SdkResourceNotFoundError:
            logger.info(f"Item '{item_id}' not found during delete (idempotent)")
        except CosmosHttpResponseError as e:
            if e.status_code == 400:
                raise CosmosPartitionKeyMismatchError(
                    f"Partition key mismatch for item '{item_id}'"
                ) from e
            logger.error(f"Failed to delete item '{item_id}': {e.status_code}")
            raise CosmosConnectionError(
                f"Failed to delete item '{item_id}': {e.status_code}"
            ) from e

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
        if max_count <= 0:
            raise ValueError("max_count must be a positive integer")

        try:
            container = self._get_container_client(container_name)
            query_items = container.query_items(
                query="SELECT * FROM c", max_item_count=max_count
            )
            items = list(query_items)
            logger.info(f"Listed {len(items)} items from container '{container_name}'")
            return items
        except CosmosHttpResponseError as e:
            logger.error(f"Failed to list items: {e.status_code}")
            raise CosmosConnectionError(f"Failed to list items: {e.status_code}") from e
