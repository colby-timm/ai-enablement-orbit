# Orbit CLI for Azure Cosmos DB

> A type-safe, developer-friendly command-line interface for Azure Cosmos DB.

Orbit helps you perform Cosmos DB CRUD operations, run queries with pagination, and manage resources directly from your terminal. It emphasizes clarity, safety, and clean architecture: repository abstractions, authentication strategies, domain models, and Rich-powered output. Designed to work both with live Azure accounts and the local Cosmos DB Emulator.

## Why Orbit?

Cosmos DB is powerful but interacting through raw SDK calls or the portal can become repetitive. Orbit streamlines common tasks while enforcing:

- Type validation via Pydantic
- Explicit authentication strategy (connection string or managed identity)
- Safe mutations (confirmation prompts unless `--yes`)
- Sensible defaults (e.g., max 100 query results unless overridden)
- Separation of concerns (Repository / Factory / Strategy / Adapter patterns)

## Status

Early scaffolding phase. Core CLI commands and package layout are being defined. This README outlines the intended architecture and contributor expectations. See `openspec/project.md` for authoritative specification. Implementation work will progressively replace TODO sections below.

## Getting Started (Boilerplate)

After cloning, create a virtual environment and install dev dependencies:

```bash
make install
```

Show help (placeholder commands only):

```bash
make run ARGS="--help"
```

Demo command with JSON output:

```bash
make run ARGS="--json demo"
```

Global flags implemented at this stage:

| Flag | Purpose | Behavior |
|------|---------|----------|
| `--json` | Machine-readable output | Serializes data to JSON instead of Rich formatting |
| `--yes` | Skip confirmations | Suppresses prompts for future mutation operations |
| `--version` | Show version | Prints version and exits |

Environment variables (scaffolding phase) used by auth strategies:

| Variable | Purpose | Required |
|----------|---------|----------|
| `ORBIT_COSMOS_CONNECTION_STRING` | Full connection string (use instead of endpoint/key pair) | Yes (for connection string auth) |
| `ORBIT_DATABASE_NAME` | Database name for all operations | Yes |
| `ORBIT_COSMOS_ENDPOINT` | Account endpoint when using managed identity (future) | No |
| `ORBIT_COSMOS_KEY` | Primary key for endpoint/key auth (never logged) | No |

> Secrets are never logged or printed; tests enforce absence of secret substrings.

## Features (Planned)

- Container management (create, list, delete) with partition key specification
- Item CRUD with partition-aware operations
- Query execution with pagination and RU cost awareness
- Output modes: human-readable (Rich tables)
- Dual auth: connection string env vars
- Emulator support (offline development)
- Defensive confirmations for write/delete unless `--yes`

## Tech Stack

| Concern         | Library / Tool |
|-----------------|----------------|
| CLI Framework   | Typer          |
| Data Store      | Azure Cosmos DB (`azure-cosmos`) |
| Validation      | Pydantic       |
| Terminal UI     | Rich           |
| Formatting/Lint | Ruff + (Black style 88 chars) |
| Testing         | Pytest + pytest-cov |

### Prerequisites

- Python 3.10+
- Azure Cosmos DB account OR local Cosmos DB Emulator

## Configuration

Orbit requires environment variables to connect to Cosmos DB:

### Environment Variables

| Variable          | Purpose                                  | Required |
|-------------------|-------------------------------------------|----------|
| `ORBIT_DATABASE_NAME` | Database name for all operations | Yes |
| `ORBIT_COSMOS_CONNECTION_STRING` | Full connection string (endpoint + key) | Yes |
| `ORBIT_COSMOS_ENDPOINT` | Account endpoint (for managed identity, future) | No |
| `ORBIT_COSMOS_KEY` | Primary key (never logged) | No |

### Example Setup

```bash
# Using connection string (recommended)
export ORBIT_DATABASE_NAME="mydb"
export ORBIT_COSMOS_CONNECTION_STRING="AccountEndpoint=https://myaccount.documents.azure.com:443/;AccountKey=..."

# Run commands
orbit containers list
```

### Troubleshooting

#### Database name not configured

- Set the `ORBIT_DATABASE_NAME` environment variable
- Example: `export ORBIT_DATABASE_NAME="mydb"`

#### Connection string not provided

- Set the `ORBIT_COSMOS_CONNECTION_STRING` environment variable
- Get your connection string from Azure Portal → Cosmos DB account → Keys
- Example: `export ORBIT_COSMOS_CONNECTION_STRING="AccountEndpoint=...;AccountKey=..."`

> Secrets are never logged or printed. Tests enforce absence of secret material in outputs.

## Usage Examples (Planned CLI Commands)

```bash
# List containers
orbit containers list

# Create a container with partition key
orbit containers create --name orders --partition-key /customerId --yes

# Insert an item (will prompt unless --yes)
orbit items create --container orders --file order.json

# Fetch an item by id & partition
orbit items get --container orders --id 1234 --partition-key-value CUST-88 --json

# Query items with pagination
orbit query --container orders --sql "SELECT * FROM c WHERE c.status = 'OPEN'" --limit 50

# Delete a container (confirmation required unless --yes)
orbit containers delete --name orders
```

All commands will adopt Typer help text, rich formatting, and domain-specific exceptions. Until code exists, treat these as conceptual placeholders.

## Design Principles

Derived from `openspec/project.md`:

- Reveal intent with explicit naming (e.g., `create_container_with_partition_key()`)
- Fail fast: validate inputs before network calls
- Single responsibility functions (5–20 lines ideally)
- Command/query separation: functions either mutate or return data
- Repository pattern isolating Cosmos SDK specifics
- Adapter wrapping SDK responses into internal models
- No leakage of secrets (keys never logged)

## Error Handling

- Domain exception classes (planned): `CosmosConnectionError`, `CosmosQueryError`, `CosmosItemNotFoundError`
- Never return `None` for failures—raise exceptions or return empty collections
- Include context (operation, container, id) in exception messages

## Testing Strategy

Orbit targets ≥80% coverage.

- Unit tests: pure business logic, mocking Cosmos interactions
- Integration tests: run against Emulator (localhost) when available
- Naming: `test_should_<behavior>_when_<condition>`
- Structure: Arrange / Act / Assert; no conditionals or loops in tests
- Use `pytest-cov` for coverage reports

Example (future):

```python
def test_should_create_container_when_valid_partition_key():
    # Arrange: mock repository
    # Act: invoke create_container_with_partition_key()
    # Assert: container exists with expected metadata
    pass  # TODO: Implement once source is available
```

## Contributing

1. Create feature branch: `feature/<description>`
2. Add or update spec in `openspec/specs/` if introducing notable behavior
3. Write tests first (TDD when feasible)
4. Implement code (PEP 8, 88-char lines, full type hints)
5. Run: `ruff format . && ruff check . && pytest --cov`
6. Open a PR referencing spec; squash merge after review

Commit format (Conventional Commits):

```text
feat(container): add partition key validation
fix(query): handle cross-partition RU spikes
```

## Security & Privacy

- Do NOT print or log `COSMOS_KEY` or full connection strings
- Confirm destructive operations unless `--yes`
- Sanitize outputs for JSON mode (no secret fields)

## Roadmap (Initial)

- [ ] Establish package structure (`orbit/` module, repositories, strategies)
  - [x] Boilerplate implemented (this change)
- [ ] Define auth strategy interfaces & implementations
- [ ] Implement container list/create/delete
- [ ] Implement item CRUD
- [ ] Implement query with pagination and RU reporting
- [ ] Add Rich output formatting layer
- [ ] Add JSON output flag
- [ ] Add integration tests against Emulator
- [ ] Publish initial PyPI release

## License

MIT License © 2025 Colby Timm. See `LICENSE` for full text.

## Follow-ups (Not in this change)

The following items are intentionally deferred and tracked via OpenSpec:

- Concrete Cosmos repository implementation
- Pagination and query command suite
- Emulator lifecycle management (start/stop)
- Performance profiling hooks (RU cost aggregation, latency tracing)

## Disclaimer

This project is in early development. Some sections contain TODO placeholders and planned interfaces that may evolve. Refer to `openspec/project.md` and change proposals for authoritative, versioned intentions.

## Acknowledgments

Built as a capstone for AI enablement—showcasing collaborative agent-driven development practices.

---

Questions or ideas? Open an issue or propose a spec under `openspec/specs/`.
