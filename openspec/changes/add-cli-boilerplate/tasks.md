## 1. Implementation

- [x] 1.1 Create `orbit/` package with `__init__.py`
- [x] 1.2 Add `orbit/cli.py` Typer app entrypoint with placeholder root command
- [x] 1.3 Implement global flags `--json` and `--yes` (stub handlers)
- [x] 1.4 Add confirmation utility (`confirmation.py`) honoring `--yes`
- [x] 1.5 Add output adapter (`output.py`) switching between Rich and JSON
- [x] 1.6 Define auth strategy interfaces (`auth/strategy.py`) and placeholder concrete classes
- [x] 1.7 Add environment variable loader (`config.py`) excluding secret printing
- [x] 1.8 Define repository abstraction (`repositories/base.py`) with TODO methods
- [x] 1.9 Add domain model base (`models/base.py`) and sample item model (`models/item.py`)
- [x] 1.10 Create exception hierarchy (`exceptions.py`) including `CosmosConnectionError`, `CosmosAuthError`
- [x] 1.11 Emulator detection helper (`emulator.py`) returning boolean
- [x] 1.12 Add minimal unit tests asserting structural presence & flag passthrough
- [x] 1.13 Configure ruff (add `pyproject.toml` if absent) and run `ruff check`
- [x] 1.14 Add README section for initial usage
- [x] 1.15 Validate proposal with `openspec validate add-cli-boilerplate --strict`
- [x] 1.16 Create root `Makefile` with targets (venv, install, run, test, lint, format, spec-validate, help)
- [x] 1.17 (Optional) Add `pyproject.toml` packaging skeleton to support `pip install -e .`

## 2. Testing

- [x] 2.1 Test: should_display_help_when_no_args
- [x] 2.2 Test: should_use_json_adapter_when_json_flag
- [x] 2.3 Test: should_skip_confirmation_when_yes_flag
- [x] 2.4 Test: should_raise_no_secret_logging_when_auth_init (mock logger)
- [x] 2.5 Test: should_expose_strategy_interface_contract

## 3. Documentation

- [x] 3.1 Document flags in README
- [x] 3.2 Add contributing note re: confirmation & secrets
