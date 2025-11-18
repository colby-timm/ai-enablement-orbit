# Implementation Tasks

## Prerequisites

- [ ] Verify `implement-cosmos-repository-items` change is complete
- [ ] Verify `implement-connection-string-auth` change is complete
- [ ] Verify `add-cli-boilerplate` change is complete
- [ ] Verify `add-container-management-commands` change is complete
- [ ] Review Typer command group documentation
- [ ] Review Rich table formatting documentation
- [ ] Review JSON file I/O patterns in Python

## Item Commands Module

- [ ] Create `orbit/commands/items.py` file (if `orbit/commands/` doesn't exist, create it)
- [ ] Import Typer and create `items_app = typer.Typer(help="Manage items in Cosmos DB containers")`
- [ ] Import `CosmosItemRepository` from repositories
- [ ] Import `OutputAdapter` from `orbit.output`
- [ ] Import `require_confirmation` from `orbit.confirmation`
- [ ] Import `context_state` from `orbit.cli`
- [ ] Import domain exceptions from `orbit.exceptions`
- [ ] Import `json`, `pathlib.Path` for file operations
- [ ] Import `typer.BadParameter` for validation errors

## Create Item Command

- [ ] Implement `create_item(container: str, data: str, partition_key: str)` function
- [ ] Add `@items_app.command("create")` decorator
- [ ] Add `container` as positional argument with help text: "Container name where item will be created"
- [ ] Add `--data` as required option: `typer.Option(..., help="Path to JSON file containing item data (or '-' for stdin)")`
- [ ] Add `--partition-key` as required option: `typer.Option(..., help="Partition key value for the item")`
- [ ] Add docstring: "Create a new item in the specified container from JSON file."
- [ ] Implement file reading logic:
  - [ ] If `data == "-"`, read from `sys.stdin`
  - [ ] Otherwise, read from file path using `pathlib.Path(data).read_text()`
  - [ ] Handle `FileNotFoundError` with message: "File not found: {data}"
  - [ ] Handle `json.JSONDecodeError` with message: "Invalid JSON in file: {data}"
- [ ] Parse JSON to dictionary
- [ ] Validate item has 'id' field, raise `typer.BadParameter` if missing
- [ ] Get repository instance (TODO: wire from factory/DI in future change)
- [ ] Call `repository.create_item(container, item_dict, partition_key)`
- [ ] Handle `CosmosDuplicateItemError` with user-friendly message
- [ ] Handle `CosmosPartitionKeyMismatchError` with actionable message
- [ ] Handle `CosmosResourceNotFoundError` (container doesn't exist)
- [ ] Handle `CosmosConnectionError` with connection check message
- [ ] For Rich output:
  - [ ] Print success message: "Created item '{item_id}' in container '{container}'"
  - [ ] Print formatted JSON of created item using `rich.json.JSON`
- [ ] For JSON output:
  - [ ] Create dict: `{"status": "created", "item": item_dict}`
  - [ ] Use `context_state.output.render(data)`
- [ ] Ensure function length < 30 lines (extract helpers if needed)

## Get Item Command

- [ ] Implement `get_item(container: str, item_id: str, partition_key: str)` function
- [ ] Add `@items_app.command("get")` decorator
- [ ] Add `container` as positional argument with help text: "Container name"
- [ ] Add `item_id` as positional argument with help text: "Item ID to retrieve"
- [ ] Add `--partition-key` as required option: `typer.Option(..., help="Partition key value")`
- [ ] Add docstring: "Retrieve a single item by ID and partition key."
- [ ] Get repository instance
- [ ] Call `repository.get_item(container, item_id, partition_key)`
- [ ] Handle `CosmosItemNotFoundError` with message: "Item '{item_id}' not found in container '{container}'"
- [ ] Handle `CosmosPartitionKeyMismatchError` with partition key explanation
- [ ] Handle `CosmosResourceNotFoundError` (container doesn't exist)
- [ ] Handle `CosmosConnectionError`
- [ ] For Rich output:
  - [ ] Print formatted JSON of item using `rich.json.JSON`
- [ ] For JSON output:
  - [ ] Create dict: `{"item": item_dict}`
  - [ ] Use `context_state.output.render(data)`
- [ ] Ensure function length < 20 lines

## Update Item Command

- [ ] Implement `update_item(container: str, item_id: str, data: str, partition_key: str)` function
- [ ] Add `@items_app.command("update")` decorator
- [ ] Add `container` as positional argument with help text: "Container name"
- [ ] Add `item_id` as positional argument with help text: "Item ID to update"
- [ ] Add `--data` as required option: `typer.Option(..., help="Path to JSON file with updated item data (or '-' for stdin)")`
- [ ] Add `--partition-key` as required option: `typer.Option(..., help="Partition key value")`
- [ ] Add docstring: "Update an existing item (or create if not exists) from JSON file."
- [ ] Implement file reading logic (same as create):
  - [ ] Read from stdin if `data == "-"`, else read file
  - [ ] Handle `FileNotFoundError` and `JSONDecodeError`
- [ ] Parse JSON to dictionary
- [ ] Validate item has 'id' field matching `item_id` parameter
  - [ ] If mismatch, raise `typer.BadParameter("Item ID in JSON must match command parameter")`
- [ ] Get repository instance
- [ ] Call `repository.update_item(container, item_id, item_dict, partition_key)`
- [ ] Handle `CosmosPartitionKeyMismatchError`
- [ ] Handle `CosmosResourceNotFoundError` (container doesn't exist)
- [ ] Handle `CosmosConnectionError`
- [ ] For Rich output:
  - [ ] Print success message: "Updated item '{item_id}' in container '{container}'"
  - [ ] Print formatted JSON of updated item using `rich.json.JSON`
- [ ] For JSON output:
  - [ ] Create dict: `{"status": "updated", "item": item_dict}`
  - [ ] Use `context_state.output.render(data)`
- [ ] Ensure function length < 30 lines (extract helpers if needed)

## Delete Item Command

- [ ] Implement `delete_item(container: str, item_id: str, partition_key: str)` function
- [ ] Add `@items_app.command("delete")` decorator
- [ ] Add `container` as positional argument with help text: "Container name"
- [ ] Add `item_id` as positional argument with help text: "Item ID to delete"
- [ ] Add `--partition-key` as required option: `typer.Option(..., help="Partition key value")`
- [ ] Add docstring: "Delete an item from the container."
- [ ] Check `context_state.yes` flag:
  - [ ] If `False`, call `require_confirmation(f"Delete item '{item_id}' from container '{container}'? This cannot be undone.")`
  - [ ] If confirmation declined, print "Aborted by user." and exit with code 1
- [ ] Get repository instance
- [ ] Call `repository.delete_item(container, item_id, partition_key)`
- [ ] Handle `CosmosResourceNotFoundError` (container doesn't exist)
- [ ] Handle `CosmosConnectionError`
- [ ] For Rich output:
  - [ ] Print success message: "Deleted item '{item_id}' from container '{container}'"
- [ ] For JSON output:
  - [ ] Create dict: `{"status": "deleted", "item_id": item_id, "container": container}`
  - [ ] Use `context_state.output.render(data)`
- [ ] Ensure function length < 20 lines

## List Items Command

- [ ] Implement `list_items(container: str, max_count: int = 100)` function
- [ ] Add `@items_app.command("list")` decorator
- [ ] Add `container` as positional argument with help text: "Container name"
- [ ] Add `--max-count` as optional int: `typer.Option(100, help="Maximum number of items to retrieve (default: 100)")`
- [ ] Add docstring: "List items in the container with pagination."
- [ ] Get repository instance
- [ ] Call `repository.list_items(container, max_count=max_count)`
- [ ] Handle `CosmosResourceNotFoundError` (container doesn't exist)
- [ ] Handle `CosmosConnectionError`
- [ ] For Rich output:
  - [ ] Create Rich `Table` with dynamic columns based on first item's keys
  - [ ] Add common columns: "id", partition key field (if identifiable), other fields
  - [ ] Truncate long values (> 50 chars) with "..." for readability
  - [ ] Add row for each item
  - [ ] Use `console.print(table)` from `context_state.output`
  - [ ] If no items, print "No items found in container '{container}'"
- [ ] For JSON output:
  - [ ] Create dict: `{"items": items_list, "count": len(items_list)}`
  - [ ] Use `context_state.output.render(data)`
- [ ] Ensure function length < 25 lines (extract table builder helper if needed)

## CLI Integration

- [ ] Open `orbit/cli.py`
- [ ] Import `items_app` from `orbit.commands.items`
- [ ] Add `app.add_typer(items_app, name="items")` after existing command registrations
- [ ] Verify CLI help shows `items` command group

## Helper Functions

- [ ] Create `_read_json_file(file_path: str) -> dict` helper function:
  - [ ] Handle stdin (`"-"`) vs file path
  - [ ] Read and parse JSON
  - [ ] Raise `typer.BadParameter` for file not found or invalid JSON
  - [ ] Return parsed dictionary
- [ ] Create `_build_item_table(items: list[dict]) -> rich.table.Table` helper:
  - [ ] Determine columns from first item's keys
  - [ ] Create Rich table with columns
  - [ ] Truncate long values
  - [ ] Add rows for all items
  - [ ] Return table
- [ ] Add type hints to all helpers

## Unit Tests

- [ ] Create `tests/test_items_commands.py` file
- [ ] Import pytest, items commands, and mocks
- [ ] Mock `CosmosItemRepository` for all tests
- [ ] Mock `context_state.output` for output verification

### Test Create Item Command

- [ ] Test `test_should_create_item_from_file_when_valid_json()`
  - [ ] Mock file reading and repository call
  - [ ] Verify `create_item()` called with correct args
  - [ ] Verify success message output
- [ ] Test `test_should_create_item_from_stdin_when_data_is_dash()`
  - [ ] Mock stdin input
  - [ ] Verify item created correctly
- [ ] Test `test_should_fail_when_json_file_not_found()`
  - [ ] Verify `FileNotFoundError` handled with clear message
- [ ] Test `test_should_fail_when_json_invalid()`
  - [ ] Verify `JSONDecodeError` handled with file path in message
- [ ] Test `test_should_fail_when_item_missing_id_field()`
  - [ ] Verify `BadParameter` raised
- [ ] Test `test_should_handle_duplicate_item_error()`
  - [ ] Mock repository raising `CosmosDuplicateItemError`
  - [ ] Verify user-friendly error message
- [ ] Test `test_should_handle_partition_key_mismatch_on_create()`
  - [ ] Mock repository raising `CosmosPartitionKeyMismatchError`
  - [ ] Verify actionable error message

### Test Get Item Command

- [ ] Test `test_should_get_item_when_exists()`
  - [ ] Mock repository returning item
  - [ ] Verify item output formatted correctly
- [ ] Test `test_should_fail_when_item_not_found()`
  - [ ] Mock repository raising `CosmosItemNotFoundError`
  - [ ] Verify error message includes item ID and container
- [ ] Test `test_should_handle_partition_key_mismatch_on_get()`
  - [ ] Mock repository raising `CosmosPartitionKeyMismatchError`
  - [ ] Verify error explains partition key issue

### Test Update Item Command

- [ ] Test `test_should_update_item_from_file_when_valid()`
  - [ ] Mock file reading and repository call
  - [ ] Verify `update_item()` called correctly
- [ ] Test `test_should_fail_when_item_id_mismatch()`
  - [ ] Item ID in JSON != command parameter
  - [ ] Verify `BadParameter` raised with explanation
- [ ] Test `test_should_handle_partition_key_mismatch_on_update()`
  - [ ] Mock repository raising `CosmosPartitionKeyMismatchError`
  - [ ] Verify error message

### Test Delete Item Command

- [ ] Test `test_should_delete_item_with_confirmation()`
  - [ ] Mock confirmation prompt (accepted)
  - [ ] Verify `delete_item()` called
- [ ] Test `test_should_delete_item_without_confirmation_when_yes_flag()`
  - [ ] Set `context_state.yes = True`
  - [ ] Verify no prompt shown
- [ ] Test `test_should_abort_when_confirmation_declined()`
  - [ ] Mock confirmation prompt (declined)
  - [ ] Verify item NOT deleted
  - [ ] Verify "Aborted by user." message
- [ ] Test `test_should_delete_item_when_container_not_found()`
  - [ ] Mock repository raising `CosmosResourceNotFoundError`
  - [ ] Verify error message includes container name

### Test List Items Command

- [ ] Test `test_should_list_items_in_rich_table_when_items_exist()`
  - [ ] Mock repository returning items list
  - [ ] Verify Rich table created with correct columns
- [ ] Test `test_should_show_no_items_message_when_container_empty()`
  - [ ] Mock repository returning empty list
  - [ ] Verify "No items found" message
- [ ] Test `test_should_list_items_in_json_format_when_json_flag()`
  - [ ] Set `context_state.json = True`
  - [ ] Verify output structure: `{"items": [...], "count": N}`
- [ ] Test `test_should_apply_max_count_pagination()`
  - [ ] Verify `max_count` parameter passed to repository

### Test Helper Functions

- [ ] Test `test_should_read_json_file_from_path()`
  - [ ] Mock file reading
  - [ ] Verify JSON parsed correctly
- [ ] Test `test_should_read_json_from_stdin()`
  - [ ] Mock stdin
  - [ ] Verify JSON parsed correctly
- [ ] Test `test_should_fail_when_file_not_found_in_helper()`
  - [ ] Verify `BadParameter` raised
- [ ] Test `test_should_build_item_table_with_columns()`
  - [ ] Verify table columns match item keys
  - [ ] Verify rows added correctly
- [ ] Test `test_should_truncate_long_values_in_table()`
  - [ ] Verify values > 50 chars truncated with "..."

## Coverage Verification

- [ ] Run `pytest --cov=orbit/commands/items --cov-report=term-missing`
- [ ] Verify coverage ≥ 80%
- [ ] Add tests for any uncovered branches

## Code Quality

- [ ] Run `ruff check orbit/commands/items.py`
- [ ] Run `ruff format orbit/commands/items.py`
- [ ] Verify all functions have type hints
- [ ] Verify all functions have docstrings
- [ ] Verify functions follow single responsibility principle
- [ ] Verify no functions exceed 30 lines

## Integration Validation

- [ ] Run `orbit items --help` and verify help text
- [ ] Run `orbit items create --help` and verify options
- [ ] Run `orbit items get --help` and verify options
- [ ] Run `orbit items update --help` and verify options
- [ ] Run `orbit items delete --help` and verify options
- [ ] Run `orbit items list --help` and verify options
- [ ] Verify all commands appear in root `orbit --help` output

## Documentation

- [ ] Update README.md with item command examples (if applicable)
- [ ] Add inline comments for complex logic (partition key validation, file I/O)
- [ ] Ensure error messages are actionable and user-friendly
