# Project Context

## Purpose

Orbit is a command-line application for interacting with Azure Cosmos DB. It provides developers with a simple, type-safe CLI to perform CRUD operations, query data, and manage Cosmos DB resources without leaving the terminal.

## Tech Stack

- Python 3.10+
- Typer (CLI framework)
- Azure Cosmos DB SDK (`azure-cosmos`)
- Pydantic (data validation)
- Rich (terminal formatting and output)

## Project Conventions

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Maximum line length: 88 characters (Black formatter standard)
- Use snake_case for functions and variables
- Use PascalCase for classes
- Docstrings: Google-style format for all public functions and classes
- Run `ruff check` and `ruff format` before committing

### Clean Code Principles

#### Naming

- **Reveal Intent**: Names should express why something exists, what it does, and how it's used
  - Good: `create_container_with_partition_key()`
  - Bad: `create()`, `do_thing()`
- **Use Searchable Names**: Avoid single-letter variables except loop counters
- **Use Problem Domain Names**: Prefer `CosmosRepository` over `DataManager`
- **Be Consistent**: If you use `fetch_item()`, don't also use `retrieve_item()` and `get_item()`

#### Functions

- **Single Responsibility**: Each function does one thing and does it well
- **Small**: Functions should be 5-20 lines ideally, rarely exceed 50
- **Few Arguments**: Aim for 0-2 parameters; 3+ requires strong justification
- **No Side Effects**: Functions shouldn't modify global state or have hidden behaviors
- **Command Query Separation**: Functions either do something (command) or return something (query), not both
- **Prefer Exceptions over Error Codes**: Use Python exceptions for error handling

#### Comments

- **Explain Why, Not What**: Code should be self-documenting; comments explain intent and trade-offs
- **No Commented-Out Code**: Delete it; version control preserves history
- **Warning Comments**: Document consequences, TODOs with owner/date, or legal requirements only

#### Classes

- **Single Responsibility Principle**: Class should have one reason to change
- **Small**: Classes should be cohesive with 5-15 methods max
- **High Cohesion**: All methods should use most instance variables
- **Low Coupling**: Minimize dependencies between classes
- **Organize by Level of Abstraction**: Public methods at top, private helpers at bottom

#### Error Handling

- **Use Exceptions**: Don't return `None` or error codes to signal failure
- **Provide Context**: Include operation details in exception messages
- **Define Exception Classes**: Create domain-specific exceptions (e.g., `CosmosConnectionError`)
- **Don't Return Null**: Use empty collections or raise exceptions instead
- **Write Try-Catch-Finally First**: Design error boundaries upfront

### Architecture Patterns

- **Dependency Inversion**: High-level CLI commands depend on abstractions (interfaces), not concrete Cosmos SDK classes
- **Repository Pattern**: Abstract all Cosmos DB operations behind repository interfaces
- **Factory Pattern**: Use factories to create Cosmos clients with proper configuration
- **Strategy Pattern**: Encapsulate authentication methods (connection string, managed identity) as strategies
- **Adapter Pattern**: Wrap Azure SDK responses into domain models to isolate external dependencies

### Testing Strategy

- **Test-Driven Development**: Write tests before implementation when possible
- **Unit Tests**: Test business logic in isolation using mocks for external dependencies
- **Integration Tests**: Test against Cosmos DB emulator to verify SDK integration
- **Test One Concept Per Test**: Each test function validates one specific behavior
- **Descriptive Test Names**: Use `test_should_<expected_behavior>_when_<condition>`
- **AAA Pattern**: Arrange, Act, Assert structure for all tests
- **No Test Logic**: Tests should have no conditionals or loops
- **Fast Tests**: Unit tests should run in milliseconds
- **Minimum 80% Code Coverage**: Track with pytest-cov
- **Test Files Mirror Source**: `tests/test_<module>.py` structure

### Git Workflow

- Main branch: `main` (protected, requires PR)
- Feature branches: `feature/<description>`
- Commit format: `<type>(<scope>): <description>` (Conventional Commits)
  - Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`
  - Example: `feat(query): add support for cross-partition queries`
- **Atomic Commits**: Each commit represents one logical change
- **Meaningful Messages**: Explain why, not what (code shows what)
- Squash merge to main
- Tag releases with semantic versioning (e.g., `v1.0.0`)

## Domain Context

- **Cosmos DB Concepts**: Containers, items, partition keys, throughput (RU/s), consistency levels
- **Query Language**: SQL-like query syntax for Cosmos DB
- **Authentication**: Connection strings, managed identity support
- **Partitioning Strategy**: Users must understand partition key selection impacts performance
- **CLI UX Goals**: Fast feedback, informative errors, human-readable output by default with JSON option

## Important Constraints

- Must support both connection string and Azure CLI authentication
- CLI must work offline for local Cosmos DB emulator
- Sensitive data (connection strings) must never be logged or printed
- All write operations should prompt for confirmation unless `--yes` flag is provided
- Query results should be paginated for large datasets
- Maximum query result size: 100 items by default (configurable)
- **No Premature Optimization**: Write clear code first, optimize only when profiling reveals bottlenecks
- **Fail Fast**: Validate inputs early and raise exceptions immediately on invalid state

## External Dependencies

- **Azure Cosmos DB**: Primary data store
- **Azure Identity**: For managed identity authentication
- **Azure Cosmos DB Emulator**: For local development and testing
- **Environment Variables**:

  - `COSMOS_ENDPOINT`: Cosmos DB account endpoint
  - `COSMOS_KEY`: Account key (if not using managed identity)
  - `COSMOS_DATABASE`: Default database name
