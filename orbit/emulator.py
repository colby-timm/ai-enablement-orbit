"""Emulator detection helper.

Future implementations may manage the emulator lifecycle. For now we only
provide a boolean predicate.
"""

from __future__ import annotations

from typing import Optional

EMULATOR_HOST_MARKERS = ["localhost", "127.0.0.1"]


def is_emulator(endpoint: Optional[str]) -> bool:
    if not endpoint:
        return False
    lowered = endpoint.lower()
    return any(marker in lowered for marker in EMULATOR_HOST_MARKERS)
