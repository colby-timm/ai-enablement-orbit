"""Custom exception hierarchy for Orbit.

Sensitive values (connection strings, keys) must never appear in messages.
"""

from __future__ import annotations


class OrbitError(Exception):
    """Base error for domain-specific exceptions."""


class CosmosConnectionError(OrbitError):
    """Raised when establishing a connection to Cosmos fails."""


class CosmosAuthError(OrbitError):
    """Raised when authentication configuration is invalid or unsupported."""


class CosmosResourceNotFoundError(OrbitError):
    """Raised when a requested Cosmos DB resource does not exist.

    Typically occurs when attempting to access a container, item, or database
    that has not been created or has been deleted.
    """


class CosmosResourceExistsError(OrbitError):
    """Raised when attempting to create a resource that already exists.

    Typically occurs when creating a container or database with a name that
    is already in use.
    """


class CosmosQuotaExceededError(OrbitError):
    """Raised when an operation exceeds account or resource quotas.

    Typically occurs when requesting throughput that exceeds available quota
    or attempting to create resources beyond account limits.
    """


class CosmosInvalidPartitionKeyError(OrbitError):
    """Raised when a partition key path is invalid.

    Partition key paths must start with '/' and follow Cosmos DB naming rules.
    """


class CosmosItemNotFoundError(OrbitError):
    """Raised when a requested item does not exist.

    Occurs when attempting to retrieve or delete an item by ID and partition
    key that has not been created or has been deleted. HTTP status code: 404.
    """


class CosmosPartitionKeyMismatchError(OrbitError):
    """Raised when partition key value doesn't match container definition.

    Occurs when the provided partition key value is inconsistent with the
    container's partition key path or when the item's partition key field
    doesn't match the provided value. HTTP status code: 400.
    """


class CosmosDuplicateItemError(OrbitError):
    """Raised when attempting to create an item with duplicate ID in partition.

    Occurs when creating an item with an ID that already exists within the
    same partition. Use update_item for upsert behavior. HTTP status code: 409.
    """
