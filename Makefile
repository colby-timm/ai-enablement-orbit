# Makefile for Orbit development workflow

.PHONY: help venv install run test test-integration lint format spec-validate clean distclean

help:
	@echo "Orbit Makefile targets:"
	@echo "  venv            Create virtual environment with uv"
	@echo "  install         Install project + dev dependencies with uv"
	@echo "  run             Run CLI (example: make run ARGS='--help')"
	@echo "  test            Run pytest unit test suite"
	@echo "  test-integration Run integration tests (requires Cosmos emulator)"
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
	uv run pytest --cov=orbit --cov-report=term-missing

test-integration:
	@echo "Running integration tests (requires Cosmos DB emulator)..."
	@echo "Make sure emulator is running: docker run -d -p 8081:8081 --name cosmos-emulator mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest"
	uv run python tests/integration/test_cosmos_repository.py

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
