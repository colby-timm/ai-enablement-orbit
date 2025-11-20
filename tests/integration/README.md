# Integration Tests

This directory contains integration tests that require external services.

## Cosmos DB Repository Tests

**File**: `test_cosmos_repository.py`

Tests the repository layer against a real Cosmos DB emulator.

### Prerequisites

1. Start Cosmos DB emulator:
   ```bash
   docker run -d -p 8081:8081 --name cosmos-emulator \
     mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest
   ```

2. Run the test:
   ```bash
   uv run python tests/integration/test_cosmos_repository.py
   ```

### What It Tests

- ✅ List containers in database
- ✅ Create container with partition key
- ✅ Get container properties
- ✅ Delete containers
- ✅ Error handling for duplicates

---

## Manual Container Management CLI Tests

**File**: `test_containers_manual.py`

Manual tests for verifying the full end-to-end CLI user experience including output formatting, error messages, and interactive prompts.

### Prerequisites

1. **Start Cosmos DB Emulator**
   ```bash
   docker run -p 8081:8081 -p 8900:8900 \
     --name cosmos-emulator \
     mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator
   ```

2. **Set Environment Variable**
   
   Emulator default connection string:
   ```bash
   export COSMOS_CONNECTION_STRING="AccountEndpoint=https://localhost:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
   ```

### Running Manual Tests

**Run all manual tests:**
```bash
pytest -m manual tests/integration/test_containers_manual.py -v -s
```

**Run specific test class:**
```bash
pytest -m manual tests/integration/test_containers_manual.py::TestContainersCreateManual -v -s
```

**Run individual test:**
```bash
pytest -m manual tests/integration/test_containers_manual.py::TestContainersCreateManual::test_create_container_with_valid_inputs -v -s
```

### Test Coverage

Manual tests verify:
- ✅ Container list with Rich table output
- ✅ Container list with JSON format
- ✅ Container create with valid/invalid inputs
- ✅ Container create error handling (duplicates, quota exceeded)
- ✅ Container delete with confirmation prompts
- ✅ Container delete with `--yes` flag
- ✅ JSON output formatting for all commands
- ✅ Rich table readability and formatting
- ✅ Error message clarity and helpfulness

### Interpreting Results

Each manual test prints formatted output and includes a manual verification checklist. Tests validate basic assertions but require human judgment for UX quality.

**Example:**
```
============================================================
TEST: Create container with valid inputs
============================================================
Container Name: test-container-1234567890
Exit Code: 0
STDOUT:
Created container 'test-container-1234567890' with partition key '/id' (400 RU/s)
============================================================
```

### Troubleshooting

**Connection refused:**
- Verify emulator is running: `docker ps | grep cosmos`
- Wait 30-60 seconds after starting emulator

**Tests fail with NotImplementedError:**
- Repository factory not yet wired - expected at this stage
- Tests still verify command parsing and output formatting

**Rate limiting (429 errors):**
- Emulator has throughput limits
- Wait between test runs or restart emulator

---

## End-to-End Container Command Tests

**File**: `test_containers_e2e.py`

Tests the complete flow from CLI command through factory, repository, and Cosmos DB using the dependency injection framework.

### Setup Requirements

1. **Start Cosmos DB Emulator**

   ```bash
   docker run -p 8081:8081 --name cosmos-emulator \
     mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator
   ```

2. **Create Test Database**
   - The emulator must have a database created before running tests
   - Use Azure Storage Explorer or the Data Explorer in the emulator

3. **Set Environment Variables**

   ```bash
   export ORBIT_DATABASE_NAME="test-orbit"
   export ORBIT_COSMOS_CONNECTION_STRING="AccountEndpoint=https://localhost:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
   ```

### Running Tests

```bash
# Run all end-to-end tests
pytest -m manual tests/integration/test_containers_e2e.py -v

# Run specific test
pytest -m manual tests/integration/test_containers_e2e.py::test_should_list_containers_from_real_database -v
```

### What These Tests Verify

- ✅ Factory instantiation from environment variables
- ✅ Repository creation via factory
- ✅ Client caching across repository requests
- ✅ Complete round-trip: CLI → factory → repository → Cosmos DB
- ✅ Error messages for missing configuration
- ✅ JSON vs. human-readable output formatting
- ✅ Authentication error handling

### Notes on Factory Testing

These tests exercise the full dependency injection flow:

1. `OrbitSettings.load()` reads environment variables
2. `RepositoryFactory` creates authenticated `CosmosClient`
3. Repository methods interact with real Cosmos DB
4. CLI commands display formatted output

The factory caches the client instance, so tests verify that multiple repository requests reuse the same connection.

---

- ✅ Error handling for invalid partition keys
- ✅ Idempotent delete operations

All tests use the hard-coded emulator connection string, so no environment variables are needed.
