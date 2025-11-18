# Makefile for Orbit development workflow

.PHONY: help venv install run test lint format spec-validate clean distclean

help:
	@echo "Orbit Makefile targets:"
	@echo "  venv            Create virtual environment with uv"
	@echo "  install         Install project + dev dependencies with uv"
	@echo "  run             Run CLI (example: make run ARGS='--help')"
	@echo "  test            Run pytest suite"
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
