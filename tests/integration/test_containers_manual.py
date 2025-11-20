"""Manual integration tests for container management commands.

These tests require a running Cosmos DB emulator and should be executed manually
to verify end-to-end behavior with real Cosmos DB connections.

Prerequisites:
1. Start Cosmos DB emulator:
   docker run -p 8081:8081 mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator
2. Set environment variable:
   export COSMOS_CONNECTION_STRING="<emulator-connection-string>"
3. Run tests: pytest tests/integration/test_containers_manual.py -v

Note: These tests are marked with @pytest.mark.manual and are skipped by default.
Run with: pytest -m manual tests/integration/test_containers_manual.py -v
"""

from __future__ import annotations

import os
import subprocess
import time

import pytest


@pytest.fixture(scope="module")
def cosmos_emulator_running():
    """Verify Cosmos DB emulator is accessible."""
    connection_string = os.getenv("COSMOS_CONNECTION_STRING")
    if not connection_string:
        pytest.skip("COSMOS_CONNECTION_STRING not set")
    return connection_string


@pytest.fixture(scope="module")
def test_database_name():
    """Database name to use for testing."""
    return "orbit-test-db"


def run_orbit_command(args: list[str]) -> tuple[int, str, str]:
    """Execute orbit CLI command and return exit code, stdout, stderr.

    Args:
        args: Command arguments (e.g., ["containers", "list"])

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    cmd = ["uv", "run", "python", "-m", "orbit"] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    return result.returncode, result.stdout, result.stderr


@pytest.mark.manual
class TestContainersListManual:
    """Manual tests for 'orbit containers list' command."""

    def test_list_containers_with_emulator(
        self, cosmos_emulator_running: str, test_database_name: str
    ) -> None:
        """Test: orbit containers list with emulator.

        Expected: Lists all containers in Rich table format.
        Verify: Table has columns for Name, Partition Key, Throughput.
        """
        exit_code, stdout, stderr = run_orbit_command(["containers", "list"])

        print(f"\n{'='*60}")
        print("TEST: List containers with emulator")
        print(f"{'='*60}")
        print(f"Exit Code: {exit_code}")
        print(f"STDOUT:\n{stdout}")
        print(f"STDERR:\n{stderr}")
        print(f"{'='*60}\n")

        # Manual verification points:
        assert exit_code in [0, 1], "Command should complete"
        # If exit_code == 0: Verify table shows Name, Partition Key, Throughput columns
        # If exit_code == 1: Verify error message is helpful

    def test_list_containers_json_format(self, cosmos_emulator_running: str) -> None:
        """Test: orbit containers list --json.

        Expected: Returns valid JSON with containers array.
        Verify: Output is parseable JSON, has 'containers' key.
        """
        exit_code, stdout, stderr = run_orbit_command(["--json", "containers", "list"])

        print(f"\n{'='*60}")
        print("TEST: List containers with --json flag")
        print(f"{'='*60}")
        print(f"Exit Code: {exit_code}")
        print(f"STDOUT:\n{stdout}")
        print(f"STDERR:\n{stderr}")
        print(f"{'='*60}\n")

        # Manual verification points:
        # - Output should be valid JSON
        # - Should contain {"containers": [...]} structure
        # - Each container should have: name, partition_key, throughput


@pytest.mark.manual
class TestContainersCreateManual:
    """Manual tests for 'orbit containers create' command."""

    def test_create_container_with_valid_inputs(
        self, cosmos_emulator_running: str
    ) -> None:
        """Test: orbit containers create test-container --partition-key /id.

        Expected: Creates container successfully.
        Verify: Success message shows container name, partition key, throughput.
        """
        container_name = f"test-container-{int(time.time())}"
        exit_code, stdout, stderr = run_orbit_command(
            [
                "containers",
                "create",
                container_name,
                "--partition-key",
                "/id",
            ]
        )

        print(f"\n{'='*60}")
        print("TEST: Create container with valid inputs")
        print(f"{'='*60}")
        print(f"Container Name: {container_name}")
        print(f"Exit Code: {exit_code}")
        print(f"STDOUT:\n{stdout}")
        print(f"STDERR:\n{stderr}")
        print(f"{'='*60}\n")

        # Manual verification points:
        assert exit_code == 0, "Should succeed with valid inputs"
        assert container_name in stdout, "Should show container name"
        assert "/id" in stdout, "Should show partition key"
        assert "400 RU/s" in stdout or "400" in stdout, "Should show throughput"

    def test_create_container_with_invalid_partition_key(
        self, cosmos_emulator_running: str
    ) -> None:
        """Test: orbit containers create with invalid partition key (missing /).

        Expected: Command fails with validation error.
        Verify: Error message mentions partition key must start with '/'.
        """
        exit_code, stdout, stderr = run_orbit_command(
            [
                "containers",
                "create",
                "invalid-test",
                "--partition-key",
                "id",  # Missing leading '/'
            ]
        )

        print(f"\n{'='*60}")
        print("TEST: Create container with invalid partition key")
        print(f"{'='*60}")
        print(f"Exit Code: {exit_code}")
        print(f"STDOUT:\n{stdout}")
        print(f"STDERR:\n{stderr}")
        print(f"{'='*60}\n")

        # Manual verification points:
        assert exit_code != 0, "Should fail with invalid partition key"
        output = stdout + stderr
        assert (
            "Partition key must start with '/'" in output
        ), "Should show validation error"

    def test_create_duplicate_container_error(
        self, cosmos_emulator_running: str
    ) -> None:
        """Test: orbit containers create with duplicate container name.

        Expected: First create succeeds, second create fails with helpful error.
        Verify: Error suggests using 'orbit containers list'.
        """
        container_name = f"duplicate-test-{int(time.time())}"

        # First creation
        exit_code1, stdout1, stderr1 = run_orbit_command(
            [
                "containers",
                "create",
                container_name,
                "--partition-key",
                "/id",
            ]
        )

        # Second creation (should fail)
        exit_code2, stdout2, stderr2 = run_orbit_command(
            [
                "containers",
                "create",
                container_name,
                "--partition-key",
                "/id",
            ]
        )

        print(f"\n{'='*60}")
        print("TEST: Create duplicate container")
        print(f"{'='*60}")
        print(f"Container Name: {container_name}")
        print(f"\nFirst Create - Exit Code: {exit_code1}")
        print(f"STDOUT:\n{stdout1}")
        print(f"\nSecond Create - Exit Code: {exit_code2}")
        print(f"STDOUT:\n{stdout2}")
        print(f"{'='*60}\n")

        # Manual verification points:
        assert exit_code1 == 0, "First creation should succeed"
        assert exit_code2 == 1, "Second creation should fail"
        assert "already exists" in stdout2, "Should mention container exists"
        assert "orbit containers list" in stdout2, "Should suggest listing containers"

    def test_create_container_json_format(self, cosmos_emulator_running: str) -> None:
        """Test: orbit containers create with --json flag.

        Expected: Returns valid JSON with container details.
        Verify: JSON contains container name, partition_key, throughput.
        """
        container_name = f"json-test-{int(time.time())}"
        exit_code, stdout, stderr = run_orbit_command(
            [
                "--json",
                "containers",
                "create",
                container_name,
                "--partition-key",
                "/id",
            ]
        )

        print(f"\n{'='*60}")
        print("TEST: Create container with --json flag")
        print(f"{'='*60}")
        print(f"Container Name: {container_name}")
        print(f"Exit Code: {exit_code}")
        print(f"STDOUT:\n{stdout}")
        print(f"STDERR:\n{stderr}")
        print(f"{'='*60}\n")

        # Manual verification points:
        # - Output should be valid JSON
        # - Should contain {"container": {...}} structure
        # - Container object should have: name, partition_key, throughput


@pytest.mark.manual
class TestContainersDeleteManual:
    """Manual tests for 'orbit containers delete' command."""

    def test_delete_container_with_confirmation(
        self, cosmos_emulator_running: str
    ) -> None:
        """Test: orbit containers delete with confirmation prompt.

        Expected: Shows confirmation prompt, deletes on 'y', aborts on 'n'.
        Verify: Prompt message is clear about irreversibility.

        Note: This test requires interactive input. Run manually with:
            1. Create test container
            2. Run: orbit containers delete test-container
            3. Type 'n' and verify abort message
            4. Run again and type 'y' to confirm deletion
        """
        container_name = f"delete-test-{int(time.time())}"

        # Create container first
        exit_code, stdout, stderr = run_orbit_command(
            [
                "containers",
                "create",
                container_name,
                "--partition-key",
                "/id",
            ]
        )

        print(f"\n{'='*60}")
        print("TEST: Delete container with confirmation (MANUAL STEP)")
        print(f"{'='*60}")
        print(f"Container Name: {container_name}")
        print(f"Container created: Exit Code {exit_code}")
        print("\nMANUAL STEPS:")
        print(f"1. Run: orbit containers delete {container_name}")
        print("2. Type 'n' at prompt and verify 'Aborted by user' message")
        print(f"3. Run: orbit containers delete {container_name}")
        print("4. Type 'y' at prompt and verify deletion success")
        print(f"{'='*60}\n")

    def test_delete_container_with_yes_flag(self, cosmos_emulator_running: str) -> None:
        """Test: orbit containers delete --yes (skip confirmation).

        Expected: Deletes container without prompting.
        Verify: No confirmation prompt, shows success message.
        """
        container_name = f"delete-yes-test-{int(time.time())}"

        # Create container first
        exit_code1, stdout1, stderr1 = run_orbit_command(
            [
                "containers",
                "create",
                container_name,
                "--partition-key",
                "/id",
            ]
        )

        # Delete with --yes flag
        exit_code2, stdout2, stderr2 = run_orbit_command(
            [
                "--yes",
                "containers",
                "delete",
                container_name,
            ]
        )

        print(f"\n{'='*60}")
        print("TEST: Delete container with --yes flag")
        print(f"{'='*60}")
        print(f"Container Name: {container_name}")
        print(f"\nCreate - Exit Code: {exit_code1}")
        print(f"STDOUT:\n{stdout1}")
        print(f"\nDelete - Exit Code: {exit_code2}")
        print(f"STDOUT:\n{stdout2}")
        print(f"{'='*60}\n")

        # Manual verification points:
        assert exit_code1 == 0, "Container creation should succeed"
        assert exit_code2 == 0, "Container deletion should succeed"
        assert (
            f"Deleted container '{container_name}'" in stdout2
        ), "Should show success message"
        assert "?" not in stdout2, "Should not show confirmation prompt"

    def test_delete_container_json_format(self, cosmos_emulator_running: str) -> None:
        """Test: orbit containers delete with --json flag.

        Expected: Returns JSON with deletion status.
        Verify: JSON contains status and container name.
        """
        container_name = f"delete-json-test-{int(time.time())}"

        # Create container first
        exit_code1, stdout1, stderr1 = run_orbit_command(
            [
                "containers",
                "create",
                container_name,
                "--partition-key",
                "/id",
            ]
        )

        # Delete with --json flag
        exit_code2, stdout2, stderr2 = run_orbit_command(
            [
                "--yes",
                "--json",
                "containers",
                "delete",
                container_name,
            ]
        )

        print(f"\n{'='*60}")
        print("TEST: Delete container with --json flag")
        print(f"{'='*60}")
        print(f"Container Name: {container_name}")
        print(f"\nCreate - Exit Code: {exit_code1}")
        print(f"\nDelete - Exit Code: {exit_code2}")
        print(f"STDOUT:\n{stdout2}")
        print(f"{'='*60}\n")

        # Manual verification points:
        # - Output should be valid JSON
        # - Should contain {"status": "deleted", "container": "<name>"}


@pytest.mark.manual
class TestOutputFormattingManual:
    """Manual tests for output formatting and user experience."""

    def test_rich_table_formatting_readable(self, cosmos_emulator_running: str) -> None:
        """Test: Verify Rich table formatting is readable.

        Expected: Table columns are aligned, headers are clear.
        Verify: Manual inspection of table output for readability.
        """
        # Create a few containers for better table display
        containers = [
            (f"products-{int(time.time())}", "/category", 400),
            (f"users-{int(time.time())}", "/userId", 800),
            (f"orders-{int(time.time())}", "/orderId", 600),
        ]

        for name, pk, throughput in containers:
            run_orbit_command(
                [
                    "containers",
                    "create",
                    name,
                    "--partition-key",
                    pk,
                    "--throughput",
                    str(throughput),
                ]
            )

        # List containers
        exit_code, stdout, stderr = run_orbit_command(["containers", "list"])

        print(f"\n{'='*60}")
        print("TEST: Rich table formatting readability")
        print(f"{'='*60}")
        print(f"Exit Code: {exit_code}")
        print(f"STDOUT:\n{stdout}")
        print(f"{'='*60}")
        print("\nMANUAL VERIFICATION:")
        print("1. Are column headers clear (Name, Partition Key, Throughput)?")
        print("2. Are columns properly aligned?")
        print("3. Is the table easy to read at a glance?")
        print("4. Are colors/formatting helping or distracting?")
        print(f"{'='*60}\n")

    def test_error_messages_helpful(self, cosmos_emulator_running: str) -> None:
        """Test: Verify error messages are helpful and actionable.

        Expected: Error messages guide users to resolution.
        Verify: Messages suggest next steps or corrections.
        """
        test_cases = [
            {
                "description": "Invalid partition key",
                "command": ["containers", "create", "test", "--partition-key", "id"],
                "expected": "Partition key must start with '/'",
            },
            {
                "description": "Missing required flag",
                "command": ["containers", "create", "test"],
                "expected": "partition-key",
            },
        ]

        print(f"\n{'='*60}")
        print("TEST: Error message helpfulness")
        print(f"{'='*60}")

        for test_case in test_cases:
            print(f"\n--- {test_case['description']} ---")
            exit_code, stdout, stderr = run_orbit_command(test_case["command"])
            output = stdout + stderr
            print(f"Command: {' '.join(test_case['command'])}")
            print(f"Exit Code: {exit_code}")
            print(f"Output:\n{output}")
            print(f"Expected to contain: {test_case['expected']}")
            print(f"Present: {test_case['expected'].lower() in output.lower()}")

        print(f"\n{'='*60}")
        print("\nMANUAL VERIFICATION:")
        print("1. Are error messages clear and understandable?")
        print("2. Do they suggest what action to take next?")
        print("3. Are they appropriate for beginners?")
        print("4. Do they avoid technical jargon where possible?")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    print("""
Manual Integration Test Suite for Container Management

To run these tests:
1. Start Cosmos DB emulator
2. Set COSMOS_CONNECTION_STRING environment variable
3. Run: pytest -m manual tests/integration/test_containers_manual.py -v -s

Individual test execution:
    pytest -m manual tests/integration/test_containers_manual.py::
TestContainersCreateManual::test_create_container_with_valid_inputs -v -s
    """)
