"""Base Pydantic model for Orbit domain entities."""

from __future__ import annotations

from pydantic import BaseModel


class OrbitModel(BaseModel):  # pragma: no cover - simple container
    """Shared configuration defaults.

    Future: enable strict mode, custom JSON encoders, and RU metadata.
    """

    class Config:
        validate_assignment = True
        extra = "forbid"
