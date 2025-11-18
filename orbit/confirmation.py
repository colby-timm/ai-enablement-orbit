"""Confirmation utilities respecting global --yes flag.

The module exposes a single function `require_confirmation` used before
mutation operations. Real implementation will integrate Rich prompt styling.
"""

from __future__ import annotations

from typing import Callable

import typer

from .cli import context_state

PromptFunc = Callable[[str], bool]


def default_prompt(message: str) -> bool:  # pragma: no cover - interactive
    return typer.confirm(message)


def require_confirmation(message: str, prompt: PromptFunc = default_prompt) -> None:
    """Abort execution if user declines confirmation.

    Skips prompt when global --yes flag is set.
    """
    if context_state.yes:
        return
    if not prompt(message):  # interactive branch not covered in tests
        typer.echo("Aborted by user.")
        raise typer.Exit(code=1)
