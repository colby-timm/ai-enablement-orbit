"""Output adapter selecting between Rich console and JSON serialization.

The real implementation will support richer formatting, pagination, and error
styling. For now we provide a minimal interface used by tests and the demo
command.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

try:  # Rich is optional at this early stage
    from rich.console import Console
except Exception:  # pragma: no cover - fallback
    Console = None  # type: ignore


@dataclass
class OutputAdapter:
    json_mode: bool = False

    def render(self, data: Any) -> None:
        """Render data either as JSON or via Rich.

        Future: support streaming large result sets and error formatting.
        """
        if self.json_mode:
            # ensure deterministic ordering for tests
            typer_like_json = json.dumps(data, sort_keys=True)
            print(typer_like_json)
            return
        if Console is None:  # pragma: no cover
            print(data)
            return
        console = Console()
        console.print(data)
