"""Sample item model used for structural tests."""

from __future__ import annotations

from typing import Optional

from .base import OrbitModel


class Item(OrbitModel):  # pragma: no cover - simple data holder
    id: str
    name: str
    description: Optional[str] = None
