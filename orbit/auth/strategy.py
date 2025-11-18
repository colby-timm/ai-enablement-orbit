"""Authentication strategy interfaces and placeholders.

Implements Strategy pattern for future pluggable auth methods.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional, Protocol

from ..config import OrbitSettings
from ..exceptions import CosmosAuthError, CosmosConnectionError

logger = logging.getLogger("orbit.auth")


class AuthStrategy(Protocol):
    def get_client(self) -> Any:  # pragma: no cover - placeholder
        """Return a Cosmos client or raise a domain exception.

        Actual return type will be `azure.cosmos.CosmosClient`. Using Any keeps
        loose coupling until dependency added.
        """
        raise NotImplementedError


@dataclass
class ConnectionStringAuthStrategy:
    settings: OrbitSettings

    def get_client(self) -> Any:  # pragma: no cover - placeholder
        if not self.settings.connection_string:
            raise CosmosAuthError("Connection string not provided.")
        # log sanitized initialization (no secrets)
        logger.info("Initializing connection string auth strategy.")
        # TODO: integrate azure-cosmos: CosmosClient(self.settings.connection_string)
        raise CosmosConnectionError("TODO: implement connection string client creation")


@dataclass
class ManagedIdentityAuthStrategy:
    settings: OrbitSettings
    resource: Optional[str] = None  # placeholder for scope/audience

    def get_client(self) -> Any:  # pragma: no cover - placeholder
        if not self.settings.endpoint:
            raise CosmosAuthError("Endpoint required for managed identity.")
        logger.info("Initializing managed identity auth strategy.")
        # TODO: obtain token via Azure Identity and construct CosmosClient
        raise CosmosConnectionError("TODO: implement managed identity client creation")
