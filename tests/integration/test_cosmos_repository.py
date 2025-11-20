"""Manual integration test for Cosmos DB repository layer.

Run this script against a Cosmos DB emulator to verify all container operations.

Prerequisites:
1. Start Cosmos DB emulator:
   docker run -d -p 8081:8081 --name cosmos-emulator \
     mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest

2. Run:
   uv run python test_integration_manual.py
"""

import sys
from dataclasses import dataclass
from typing import Optional

from orbit.auth.strategy import ConnectionStringAuthStrategy
from orbit.exceptions import (
    CosmosInvalidPartitionKeyError,
    CosmosResourceExistsError,
)
from orbit.repositories.cosmos import CosmosContainerRepository

# Cosmos DB Emulator connection string (fixed for all emulator instances)
EMULATOR_CONNECTION_STRING = (
    "AccountEndpoint=https://localhost:8081/;"
    "AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="
)


@dataclass
class EmulatorSettings:
    """Settings for emulator connection."""

    connection_string: Optional[str] = EMULATOR_CONNECTION_STRING
    endpoint: Optional[str] = None
    key: Optional[str] = None


def print_test(test_num: int, description: str) -> None:
    """Print test header."""
    print(f"\n{'='*70}")
    print(f"Test {test_num}: {description}")
    print("=" * 70)


def main():
    """Run all manual integration tests."""
    print("🚀 Starting Cosmos DB Repository Integration Tests")
    print("=" * 70)

    # Initialize
    try:
        settings = EmulatorSettings()
        auth = ConnectionStringAuthStrategy(settings)
        client = auth.get_client()

        # Create test database
        print("\n📦 Creating test database 'orbit-integration-test'...")
        try:
            client.create_database("orbit-integration-test")
            print("✓ Database created")
        except Exception:
            client.get_database_client("orbit-integration-test")
            print("✓ Using existing database")

        # Initialize repository
        repo = CosmosContainerRepository(client, "orbit-integration-test")

    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("\nMake sure the Cosmos DB emulator is running:")
        print("docker run -d -p 8081:8081 --name cosmos-emulator \\")
        print("  mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:latest")
        sys.exit(1)

    # Test 1: List containers in empty database
    print_test(1, "List containers in database")
    try:
        containers = repo.list_containers()
        print(f"✓ Found {len(containers)} containers")
        if containers:
            for c in containers:
                print(f"  - {c['id']}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)

    # Test 2: Create container with partition key /id
    print_test(2, "Create container with partition key /id")
    try:
        result = repo.create_container("integration-test-users", "/id", throughput=400)
        print(f"✓ Created container: {result['id']}")
        print(f"  Partition key: {result['partitionKey']['paths']}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)

    # Test 3: Get properties of created container
    print_test(3, "Get properties of created container")
    try:
        props = repo.get_container_properties("integration-test-users")
        print(f"✓ Retrieved properties for: {props['id']}")
        print(f"  Partition key: {props['partitionKey']['paths']}")
        print(f"  Partition key kind: {props['partitionKey']['kind']}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)

    # Test 4: List containers (should show new container)
    print_test(4, "List containers (after creation)")
    try:
        containers = repo.list_containers()
        container_names = [c["id"] for c in containers]
        print(f"✓ Found {len(containers)} containers:")
        for name in container_names:
            print(f"  - {name}")

        if "integration-test-users" not in container_names:
            print("❌ ERROR: Created container not found in list!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)

    # Test 5: Verify error for creating duplicate container
    print_test(5, "Verify error for creating duplicate container")
    try:
        repo.create_container("integration-test-users", "/id")
        print("❌ ERROR: Should have raised CosmosResourceExistsError!")
        sys.exit(1)
    except CosmosResourceExistsError as e:
        print(f"✓ Expected error caught: {type(e).__name__}")
        print(f"  Message: {e}")
    except Exception as e:
        print(f"❌ Wrong exception type: {type(e).__name__}: {e}")
        sys.exit(1)

    # Test 6: Verify error for invalid partition key path
    print_test(6, "Verify error for invalid partition key path (no leading slash)")
    try:
        repo.create_container("bad-container", "userId")
        print("❌ ERROR: Should have raised CosmosInvalidPartitionKeyError!")
        sys.exit(1)
    except CosmosInvalidPartitionKeyError as e:
        print(f"✓ Expected error caught: {type(e).__name__}")
        print(f"  Message: {e}")
    except Exception as e:
        print(f"❌ Wrong exception type: {type(e).__name__}: {e}")
        sys.exit(1)

    # Test 7: Delete created container
    print_test(7, "Delete created container")
    try:
        repo.delete_container("integration-test-users")
        print("✓ Container deleted successfully")

        # Verify it's gone
        containers = repo.list_containers()
        container_names = [c["id"] for c in containers]
        if "integration-test-users" in container_names:
            print("❌ ERROR: Container still exists after delete!")
            sys.exit(1)
        print("✓ Verified container no longer in list")
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)

    # Test 8: Delete non-existent container (idempotent)
    print_test(8, "Delete non-existent container (idempotent)")
    try:
        repo.delete_container("does-not-exist")
        print("✓ Delete succeeded without error (idempotent)")
    except Exception as e:
        print(f"❌ Should not raise error for missing container: {e}")
        sys.exit(1)

    # Success!
    print("\n" + "=" * 70)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("=" * 70)
    print("\n✓ All 8 manual integration test tasks completed successfully")
    print("\nYou can now mark the following tasks as complete in tasks.md:")
    print("  - Manual test: List containers in emulator database")
    print("  - Manual test: Create container with partition key /id")
    print("  - Manual test: Get properties of created container")
    print("  - Manual test: Delete created container")
    print("  - Manual test: Verify error for creating duplicate container")
    print("  - Manual test: Verify error for invalid partition key path")
    print("  - Manual testing completed successfully")
    print("  - Ready for code review")


if __name__ == "__main__":
    main()
