"""Repository factory for dependency injection.

Instantiates repositories with proper authentication and configuration.
Caches CosmosClient to avoid redundant connections.
"""

from __future__ import annotations

from typing import Optional

from azure.cosmos import CosmosClient

from .auth.strategy import ConnectionStringAuthStrategy
from .config import OrbitSettings
from .repositories.cosmos import CosmosContainerRepository

# Error message for missing database name
DATABASE_NAME_MISSING_ERROR = (
    "Database name not configured. Set ORBIT_DATABASE_NAME environment variable."
)


class RepositoryFactory:
    """Factory for creating repository instances with dependency injection.

    Encapsulates the creation of repositories, handling authentication
    strategy selection, client initialization, and database configuration.
    Caches the CosmosClient instance to reuse connections across repository
    requests within the same factory instance.

    Usage:
        settings = OrbitSettings.load()
        factory = RepositoryFactory(settings)
        container_repo = factory.get_container_repository()
        item_repo = factory.get_item_repository()  # Returns same repo type
    """

    def __init__(self, settings: OrbitSettings) -> None:
        """Initialize factory with configuration settings.

        Args:
            settings: OrbitSettings instance with connection and database config.
        """
        self._settings = settings
        self._client: Optional[CosmosClient] = None
        self._database_name: Optional[str] = settings.database_name

    def _get_client(self) -> CosmosClient:
        """Get or create CosmosClient instance.

        Lazy initialization with caching to avoid redundant connections.
        Uses ConnectionStringAuthStrategy for authentication.

        Returns:
            CosmosClient: Authenticated client instance.

        Raises:
            CosmosAuthError: When connection string is missing or invalid.
            ValueError: When database name is not configured.
        """
        if self._client is None:
            # Validate database name before creating client
            if not self._database_name:
                raise ValueError(DATABASE_NAME_MISSING_ERROR)

            # Use ConnectionStringAuthStrategy to create client
            auth_strategy = ConnectionStringAuthStrategy(self._settings)
            self._client = auth_strategy.get_client()

        return self._client

    def get_container_repository(self) -> CosmosContainerRepository:
        """Create CosmosContainerRepository instance.

        Returns:
            CosmosContainerRepository: Repository for container operations.

        Raises:
            CosmosAuthError: When connection string is missing or invalid.
            ValueError: When database name is not configured.
        """
        client = self._get_client()
        if not self._database_name:
            raise ValueError(DATABASE_NAME_MISSING_ERROR)
        return CosmosContainerRepository(client, self._database_name)

    def get_item_repository(self) -> CosmosContainerRepository:
        """Create CosmosContainerRepository instance for item operations.

        Returns:
            CosmosContainerRepository: Repository for item operations.

        Raises:
            CosmosAuthError: When connection string is missing or invalid.
            ValueError: When database name is not configured.

        Note:
            Returns same repository type as get_container_repository().
            Item operations are methods on CosmosContainerRepository.
        """
        client = self._get_client()
        if not self._database_name:
            raise ValueError(DATABASE_NAME_MISSING_ERROR)
        return CosmosContainerRepository(client, self._database_name)
