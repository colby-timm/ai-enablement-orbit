"""Environment configuration loader.

Resolves environment variables without printing secret material.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from .exceptions import CosmosAuthError

# expected environment variables (names chosen for clarity)
CONNECTION_STRING_ENV = "ORBIT_COSMOS_CONNECTION_STRING"
ENDPOINT_ENV = "ORBIT_COSMOS_ENDPOINT"
KEY_ENV = "ORBIT_COSMOS_KEY"


@dataclass
class OrbitSettings:
    connection_string: Optional[str] = None
    endpoint: Optional[str] = None
    key: Optional[str] = None

    @classmethod
    def load(cls) -> "OrbitSettings":
        settings = cls(
            connection_string=os.getenv(CONNECTION_STRING_ENV),
            endpoint=os.getenv(ENDPOINT_ENV),
            key=os.getenv(KEY_ENV),
        )
        # minimal validation placeholder
        if settings.connection_string and (settings.key or settings.endpoint):
            raise CosmosAuthError(
                "Ambiguous auth configuration: provide either connection "
                "string or endpoint/key pair."
            )
        return settings
