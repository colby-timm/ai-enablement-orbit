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
    CosmosInvalidPartitionKeyError,
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
                f"Failed to get properties for container '{name}': " f"{e.status_code}"
            )
            raise CosmosConnectionError(
                f"Failed to get properties for container '{name}': " f"{e.status_code}"
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
