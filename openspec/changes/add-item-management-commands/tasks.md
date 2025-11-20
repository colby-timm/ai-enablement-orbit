# Implementation Tasks

## Prerequisites

- [x] Verify `implement-cosmos-repository-items` change is complete
- [x] Verify `implement-connection-string-auth` change is complete
- [x] Verify `add-cli-boilerplate` change is complete
- [x] Verify `add-container-management-commands` change is complete
- [x] Review Typer command group documentation
- [x] Review Rich table formatting documentation
- [x] Review JSON file I/O patterns in Python

## Item Commands Module

- [x] Create `orbit/commands/items.py` file (if `orbit/commands/` doesn't exist, create it)
- [x] Import Typer and create `items_app = typer.Typer(help="Manage items in Cosmos DB containers")`
- [x] Import `CosmosItemRepository` from repositories
- [x] Import `OutputAdapter` from `orbit.output`
- [x] Import `require_confirmation` from `orbit.confirmation`
- [x] Import `context_state` from `orbit.cli`
- [x] Import domain exceptions from `orbit.exceptions`
- [x] Import `json`, `pathlib.Path` for file operations
- [x] Import `typer.BadParameter` for validation errors

## Create Item Command

- [x] Implement `create_item(container: str, data: str, partition_key: str)` function
- [x] Add `@items_app.command("create")` decorator
- [x] Add `container` as positional argument with help text: "Container name where item will be created"
- [x] Add `--data` as required option: `typer.Option(..., help="Path to JSON file containing item data (or '-' for stdin)")`
- [x] Add `--partition-key` as required option: `typer.Option(..., help="Partition key value for the item")`
- [x] Add docstring: "Create a new item in the specified container from JSON file."
- [x] Implement file reading logic:
  - [ ] If `data == "-"`, read from `sys.stdin`
  - [ ] Otherwise, read from file path using `pathlib.Path(data).read_text()`
  - [ ] Handle `FileNotFoundError` with message: "File not found: {data}"
  - [ ] Handle `json.JSONDecodeError` with message: "Invalid JSON in file: {data}"
- [x] Parse JSON to dictionary
- [x] Validate item has 'id' field, raise `typer.BadParameter` if missing
- [x] Get repository instance (TODO: wire from factory/DI in future change)
- [x] Call `repository.create_item(container, item_dict, partition_key)`
- [x] Handle `CosmosDuplicateItemError` with user-friendly message
- [x] Handle `CosmosPartitionKeyMismatchError` with actionable message
- [x] Handle `CosmosResourceNotFoundError` (container doesn't exist)
- [x] Handle `CosmosConnectionError` with connection check message
- [x] For Rich output:
  - [ ] Print success message: "Created item '{item_id}' in container '{container}'"
  - [ ] Print formatted JSON of created item using `rich.json.JSON`
- [x] For JSON output:
  - [ ] Create dict: `{"status": "created", "item": item_dict}`
  - [ ] Use `context_state.output.render(data)`
- [x] Ensure function length < 30 lines (extract helpers if needed)

## Get Item Command

- [x] Implement `get_item(container: str, item_id: str, partition_key: str)` function
- [x] Add `@items_app.command("get")` decorator
- [x] Add `container` as positional argument with help text: "Container name"
- [x] Add `item_id` as positional argument with help text: "Item ID to retrieve"
- [x] Add `--partition-key` as required option: `typer.Option(..., help="Partition key value")`
- [x] Add docstring: "Retrieve a single item by ID and partition key."
- [x] Get repository instance
- [x] Call `repository.get_item(container, item_id, partition_key)`
- [x] Handle `CosmosItemNotFoundError` with message: "Item '{item_id}' not found in container '{container}'"
- [x] Handle `CosmosPartitionKeyMismatchError` with partition key explanation
- [x] Handle `CosmosResourceNotFoundError` (container doesn't exist)
- [x] Handle `CosmosConnectionError`
- [x] For Rich output:
  - [ ] Print formatted JSON of item using `rich.json.JSON`
- [x] For JSON output:
  - [ ] Create dict: `{"item": item_dict}`
  - [ ] Use `context_state.output.render(data)`
- [x] Ensure function length < 20 lines

## Update Item Command

- [x] Implement `update_item(container: str, item_id: str, data: str, partition_key: str)` function
- [x] Add `@items_app.command("update")` decorator
- [x] Add `container` as positional argument with help text: "Container name"
- [x] Add `item_id` as positional argument with help text: "Item ID to update"
- [x] Add `--data` as required option: `typer.Option(..., help="Path to JSON file with updated item data (or '-' for stdin)")`
- [x] Add `--partition-key` as required option: `typer.Option(..., help="Partition key value")`
- [x] Add docstring: "Update an existing item (or create if not exists) from JSON file."
- [x] Implement file reading logic (same as create):
  - [ ] Read from stdin if `data == "-"`, else read file
  - [ ] Handle `FileNotFoundError` and `JSONDecodeError`
- [x] Parse JSON to dictionary
- [x] Validate item has 'id' field matching `item_id` parameter
  - [ ] If mismatch, raise `typer.BadParameter("Item ID in JSON must match command parameter")`
- [x] Get repository instance
- [x] Call `repository.update_item(container, item_id, item_dict, partition_key)`
- [x] Handle `CosmosPartitionKeyMismatchError`
- [x] Handle `CosmosResourceNotFoundError` (container doesn't exist)
- [x] Handle `CosmosConnectionError`
- [x] For Rich output:
  - [ ] Print success message: "Updated item '{item_id}' in container '{container}'"
  - [ ] Print formatted JSON of updated item using `rich.json.JSON`
- [x] For JSON output:
  - [ ] Create dict: `{"status": "updated", "item": item_dict}`
  - [ ] Use `context_state.output.render(data)`
- [x] Ensure function length < 30 lines (extract helpers if needed)

## Delete Item Command

- [x] Implement `delete_item(container: str, item_id: str, partition_key: str)` function
- [x] Add `@items_app.command("delete")` decorator
- [x] Add `container` as positional argument with help text: "Container name"
- [x] Add `item_id` as positional argument with help text: "Item ID to delete"
- [x] Add `--partition-key` as required option: `typer.Option(..., help="Partition key value")`
- [x] Add docstring: "Delete an item from the container."
- [x] Check `context_state.yes` flag:
  - [ ] If `False`, call `require_confirmation(f"Delete item '{item_id}' from container '{container}'? This cannot be undone.")`
  - [ ] If confirmation declined, print "Aborted by user." and exit with code 1
- [x] Get repository instance
- [x] Call `repository.delete_item(container, item_id, partition_key)`
- [x] Handle `CosmosResourceNotFoundError` (container doesn't exist)
- [x] Handle `CosmosConnectionError`
- [x] For Rich output:
  - [ ] Print success message: "Deleted item '{item_id}' from container '{container}'"
- [x] For JSON output:
  - [ ] Create dict: `{"status": "deleted", "item_id": item_id, "container": container}`
  - [ ] Use `context_state.output.render(data)`
- [x] Ensure function length < 20 lines

## List Items Command

- [x] Implement `list_items(container: str, max_count: int = 100)` function
- [x] Add `@items_app.command("list")` decorator
- [x] Add `container` as positional argument with help text: "Container name"
- [x] Add `--max-count` as optional int: `typer.Option(100, help="Maximum number of items to retrieve (default: 100)")`
- [x] Add docstring: "List items in the container with pagination."
- [x] Get repository instance
- [x] Call `repository.list_items(container, max_count=max_count)`
- [x] Handle `CosmosResourceNotFoundError` (container doesn't exist)
- [x] Handle `CosmosConnectionError`
- [x] For Rich output:
  - [ ] Create Rich `Table` with dynamic columns based on first item's keys
  - [ ] Add common columns: "id", partition key field (if identifiable), other fields
  - [ ] Truncate long values (> 50 chars) with "..." for readability
  - [ ] Add row for each item
  - [ ] Use `console.print(table)` from `context_state.output`
  - [ ] If no items, print "No items found in container '{container}'"
- [x] For JSON output:
  - [ ] Create dict: `{"items": items_list, "count": len(items_list)}`
  - [ ] Use `context_state.output.render(data)`
- [x] Ensure function length < 25 lines (extract table builder helper if needed)

## CLI Integration

- [x] Open `orbit/cli.py`
- [x] Import `items_app` from `orbit.commands.items`
- [x] Add `app.add_typer(items_app, name="items")` after existing command registrations
- [x] Verify CLI help shows `items` command group

## Helper Functions

- [x] Create `_read_json_file(file_path: str) -> dict` helper function:
  - [ ] Handle stdin (`"-"`) vs file path
  - [ ] Read and parse JSON
  - [ ] Raise `typer.BadParameter` for file not found or invalid JSON
  - [ ] Return parsed dictionary
- [x] Create `_build_item_table(items: list[dict]) -> rich.table.Table` helper:
  - [ ] Determine columns from first item's keys
  - [ ] Create Rich table with columns
  - [ ] Truncate long values
  - [ ] Add rows for all items
  - [ ] Return table
- [x] Add type hints to all helpers

## Unit Tests

- [x] Create `tests/test_items_commands.py` file
- [x] Import pytest, items commands, and mocks
- [x] Mock `CosmosItemRepository` for all tests
- [x] Mock `context_state.output` for output verification

### Test Create Item Command

- [x] Test `test_should_create_item_from_file_when_valid_json()`
  - [ ] Mock file reading and repository call
  - [ ] Verify `create_item()` called with correct args
  - [ ] Verify success message output
- [x] Test `test_should_create_item_from_stdin_when_data_is_dash()`
  - [ ] Mock stdin input
  - [ ] Verify item created correctly
- [x] Test `test_should_fail_when_json_file_not_found()`
  - [ ] Verify `FileNotFoundError` handled with clear message
- [x] Test `test_should_fail_when_json_invalid()`
  - [ ] Verify `JSONDecodeError` handled with file path in message
- [x] Test `test_should_fail_when_item_missing_id_field()`
  - [ ] Verify `BadParameter` raised
- [x] Test `test_should_handle_duplicate_item_error()`
  - [ ] Mock repository raising `CosmosDuplicateItemError`
  - [ ] Verify user-friendly error message
- [x] Test `test_should_handle_partition_key_mismatch_on_create()`
  - [ ] Mock repository raising `CosmosPartitionKeyMismatchError`
  - [ ] Verify actionable error message

### Test Get Item Command

- [x] Test `test_should_get_item_when_exists()`
  - [ ] Mock repository returning item
  - [ ] Verify item output formatted correctly
- [x] Test `test_should_fail_when_item_not_found()`
  - [ ] Mock repository raising `CosmosItemNotFoundError`
  - [ ] Verify error message includes item ID and container
- [x] Test `test_should_handle_partition_key_mismatch_on_get()`
  - [ ] Mock repository raising `CosmosPartitionKeyMismatchError`
  - [ ] Verify error explains partition key issue

### Test Update Item Command

- [x] Test `test_should_update_item_from_file_when_valid()`
  - [ ] Mock file reading and repository call
  - [ ] Verify `update_item()` called correctly
- [x] Test `test_should_fail_when_item_id_mismatch()`
  - [ ] Item ID in JSON != command parameter
  - [ ] Verify `BadParameter` raised with explanation
- [x] Test `test_should_handle_partition_key_mismatch_on_update()`
  - [ ] Mock repository raising `CosmosPartitionKeyMismatchError`
  - [ ] Verify error message

### Test Delete Item Command

- [x] Test `test_should_delete_item_with_confirmation()`
  - [ ] Mock confirmation prompt (accepted)
  - [ ] Verify `delete_item()` called
- [x] Test `test_should_delete_item_without_confirmation_when_yes_flag()`
  - [ ] Set `context_state.yes = True`
  - [ ] Verify no prompt shown
- [x] Test `test_should_abort_when_confirmation_declined()`
  - [ ] Mock confirmation prompt (declined)
  - [ ] Verify item NOT deleted
  - [ ] Verify "Aborted by user." message
- [x] Test `test_should_delete_item_when_container_not_found()`
  - [ ] Mock repository raising `CosmosResourceNotFoundError`
  - [ ] Verify error message includes container name

### Test List Items Command

- [x] Test `test_should_list_items_in_rich_table_when_items_exist()`
  - [ ] Mock repository returning items list
  - [ ] Verify Rich table created with correct columns
- [x] Test `test_should_show_no_items_message_when_container_empty()`
  - [ ] Mock repository returning empty list
  - [ ] Verify "No items found" message
- [x] Test `test_should_list_items_in_json_format_when_json_flag()`
  - [ ] Set `context_state.json = True`
  - [ ] Verify output structure: `{"items": [...], "count": N}`
- [x] Test `test_should_apply_max_count_pagination()`
  - [ ] Verify `max_count` parameter passed to repository

### Test Helper Functions

- [x] Test `test_should_read_json_file_from_path()`
  - [ ] Mock file reading
  - [ ] Verify JSON parsed correctly
- [x] Test `test_should_read_json_from_stdin()`
  - [ ] Mock stdin
  - [ ] Verify JSON parsed correctly
- [x] Test `test_should_fail_when_file_not_found_in_helper()`
  - [ ] Verify `BadParameter` raised
- [x] Test `test_should_build_item_table_with_columns()`
  - [ ] Verify table columns match item keys
  - [ ] Verify rows added correctly
- [x] Test `test_should_truncate_long_values_in_table()`
  - [ ] Verify values > 50 chars truncated with "..."

## Coverage Verification

- [x] Run `pytest --cov=orbit/commands/items --cov-report=term-missing`
- [x] Verify coverage ≥ 80%
- [x] Add tests for any uncovered branches

## Code Quality

- [x] Run `ruff check orbit/commands/items.py`
- [x] Run `ruff format orbit/commands/items.py`
- [x] Verify all functions have type hints
- [x] Verify all functions have docstrings
- [x] Verify functions follow single responsibility principle
- [x] Verify no functions exceed 30 lines

## Integration Validation

- [x] Run `orbit items --help` and verify help text
- [x] Run `orbit items create --help` and verify options
- [x] Run `orbit items get --help` and verify options
- [x] Run `orbit items update --help` and verify options
- [x] Run `orbit items delete --help` and verify options
- [x] Run `orbit items list --help` and verify options
- [x] Verify all commands appear in root `orbit --help` output

## Documentation

- [x] Update README.md with item command examples (if applicable)
- [x] Add inline comments for complex logic (partition key validation, file I/O)
- [x] Ensure error messages are actionable and user-friendly
