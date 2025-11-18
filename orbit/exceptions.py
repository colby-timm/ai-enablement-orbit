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
