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
