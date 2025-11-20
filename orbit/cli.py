"""Typer CLI entrypoint for Orbit.

Provides global flags and root help output. Additional command modules will be
plugged into this app in future changes.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any, Optional

import typer

from .output import OutputAdapter

# Suppress urllib3 SSL warnings when connecting to Cosmos DB emulator
# Emulator uses self-signed certificates on localhost
warnings.filterwarnings(
    "ignore",
    message="Unverified HTTPS request",
    category=Warning,
)

app = typer.Typer(help="Orbit CLI for Azure Cosmos DB (boilerplate phase)")


@dataclass
class OrbitContext:
    json: bool = False
    yes: bool = False
    output: Optional[OutputAdapter] = None

    def init_output(self) -> None:
        # Always recreate to reflect current flags
        self.output = OutputAdapter(json_mode=self.json)


context_state = OrbitContext()


def version_callback(value: bool) -> None:  # pragma: no cover - simple passthrough
    if value:
        from . import VERSION

        typer.echo(f"Orbit version: {VERSION}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    json: bool = typer.Option(
        False,
        "--json",
        help="Emit machine-readable JSON instead of Rich formatting.",
        show_default=True,
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Skip confirmation prompts for mutation operations.",
        show_default=True,
    ),
    version: bool = typer.Option(  # future: move to dedicated command
        False,
        "--version",
        help="Show the Orbit version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Root callback storing global flags in context."""
    # side effects limited to context mutation
    context_state.json = json
    context_state.yes = yes
    context_state.init_output()

    # Show help when no command is provided
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@app.command("demo")
def demo_command() -> None:
    """Placeholder command demonstrating output adapter wiring."""
    data: dict[str, Any] = {"status": "ok", "message": "demo placeholder"}
    context_state.output.render(data)


# Register command groups (after context_state is defined)
from .commands.containers import containers_app  # noqa: E402

app.add_typer(containers_app, name="containers")


if __name__ == "__main__":  # pragma: no cover
    app()
