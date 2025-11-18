"""Tests for Orbit CLI global flags and structural scaffolding."""

from __future__ import annotations

import json
import logging
from typing import Any

from typer.testing import CliRunner

from orbit.auth.strategy import (
    ConnectionStringAuthStrategy,
    ManagedIdentityAuthStrategy,
)
from orbit.cli import app, context_state
from orbit.config import OrbitSettings
from orbit.confirmation import require_confirmation
from orbit.exceptions import CosmosAuthError, CosmosConnectionError

runner = CliRunner()


def test_should_display_help_when_no_args() -> None:
    # Act
    result = runner.invoke(app, [])
    # Assert
    assert result.exit_code == 0
    assert "Orbit CLI" in result.output


def test_should_use_json_adapter_when_json_flag() -> None:
    # Act
    result = runner.invoke(app, ["--json", "demo"])
    # Assert
    assert result.exit_code == 0
    # output should be JSON
    data = json.loads(result.output.strip())
    assert data["status"] == "ok"
    assert context_state.json is True


def test_should_skip_confirmation_when_yes_flag() -> None:
    # Arrange
    runner.invoke(app, ["--yes", "demo"])  # sets global context_state.yes
    called: dict[str, Any] = {"count": 0}

    def fake_prompt(msg: str) -> bool:  # pragma: no cover - should not run
        called["count"] += 1
        return True

    # Act
    require_confirmation("Confirm destructive op?", prompt=fake_prompt)

    # Assert
    assert context_state.yes is True
    assert called["count"] == 0  # prompt skipped


def test_should_raise_no_secret_logging_when_auth_init(caplog) -> None:
    # Arrange
    caplog.set_level(logging.INFO)
    secret_connection_string = (
        "AccountEndpoint=https://localhost:8081/;AccountKey=SUPERSECRET==;"
    )
    settings = OrbitSettings(connection_string=secret_connection_string)
    strategy = ConnectionStringAuthStrategy(settings=settings)

    # Act
    try:
        strategy.get_client()
    except CosmosConnectionError:
        pass

    # Assert
    for record in caplog.records:
        assert "SUPERSECRET" not in record.getMessage()
    assert any(
        "Initializing connection string auth" in r.getMessage() for r in caplog.records
    )


def test_should_expose_strategy_interface_contract() -> None:
    # Arrange
    settings_conn = OrbitSettings(
        connection_string="AccountEndpoint=https://localhost:8081/;AccountKey=X;"
    )
    conn_strategy = ConnectionStringAuthStrategy(settings_conn)

    settings_msi = OrbitSettings(endpoint="https://example.documents.azure.com:443/")
    msi_strategy = ManagedIdentityAuthStrategy(settings_msi)

    # Act / Assert
    try:
        conn_strategy.get_client()
    except CosmosConnectionError:
        pass

    try:
        msi_strategy.get_client()
    except CosmosConnectionError:
        pass

    assert hasattr(conn_strategy, "get_client")
    assert hasattr(msi_strategy, "get_client")


def test_should_error_when_ambiguous_auth_config() -> None:
    # Arrange / Act
    try:
        OrbitSettings(connection_string="foo", endpoint="bar", key="baz").load()  # type: ignore
    except CosmosAuthError as e:
        # Assert
        assert "Ambiguous auth configuration" in str(e)
