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
- ✅ Error handling for invalid partition keys
- ✅ Idempotent delete operations

All tests use the hard-coded emulator connection string, so no environment variables are needed.
