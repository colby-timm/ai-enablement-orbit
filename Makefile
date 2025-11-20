# Makefile for Orbit development workflow

.PHONY: help venv install run test test-integration test-manual lint format spec-validate clean distclean

help:
	@echo "Orbit Makefile targets:"
	@echo "  venv            Create virtual environment with uv"
	@echo "  install         Install project + dev dependencies with uv"
	@echo "  run             Run CLI (example: make run ARGS='--help')"
	@echo "  test            Run pytest unit test suite (excludes manual tests)"
	@echo "  test-integration Run integration tests (requires Cosmos emulator)"
	@echo "  test-manual     Run manual integration tests for CLI commands"
	@echo "  lint            Run ruff check"
	@echo "  format          Run ruff format"
	@echo "  spec-validate   Placeholder for openspec validation"
	@echo "  clean           Remove pycache artifacts"
	@echo "  distclean       Remove venv and build artifacts"

venv:
	uv venv

install: venv
	uv pip install -e .[dev]

run:
	uv run python -m orbit.cli $(ARGS)

test:
	uv run pytest --cov=orbit --cov-report=term-missing -m "not manual"

test-integration:
	@echo "Running integration tests (requires Cosmos DB emulator)..."
	@echo "Make sure emulator is running: docker run -d -p 8081:8081 --name cosmos-emulator mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest"
	uv run python tests/integration/test_cosmos_repository.py

test-manual:
	@echo "Running manual integration tests for CLI commands..."
	@echo "Note: Some tests require repository factory wiring (NotImplementedError expected)"
	@echo "Set COSMOS_CONNECTION_STRING if not already set"
	uv run pytest -m manual tests/integration/test_containers_manual.py -v -s

lint:
	uv run ruff check .

format:
	uv run ruff format .

spec-validate:
	@echo "TODO: integrate openspec validation tool (openspec validate add-cli-boilerplate --strict)"

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

distclean: clean
	rm -rf .venv build dist *.egg-info
