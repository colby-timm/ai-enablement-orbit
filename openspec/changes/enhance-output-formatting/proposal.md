# Change: Enhance Output Formatting

## Why

The current OutputAdapter provides minimal formatting—basic Rich console printing and JSON output. As Orbit matures with container management, item CRUD, and query operations, users need professional terminal output: structured tables for list views, syntax-highlighted JSON for data inspection, color-coded error messages for troubleshooting, and progress indicators for long-running operations like bulk queries or container creation. Enhanced formatting improves developer experience, reduces cognitive load, and makes Orbit competitive with modern CLI tools.

## What Changes

- **ENHANCED** capability: `cli-core` output formatting with Rich tables, syntax highlighting, error styling, and progress indicators
- Extend `OutputAdapter` class to support multiple output formats beyond basic print:
  - Rich tables with headers, borders, and column alignment for list operations (containers, items)
  - Syntax highlighting for JSON output using Rich's JSON pretty-printer with color themes
  - Error message formatting with color coding (red for errors, yellow for warnings) and structured context display
  - Progress indicators (spinners, progress bars) for operations exceeding 1 second threshold
- Add output format detection logic: tables for collections, JSON for single items/objects, errors for exceptions
- Preserve existing `--json` flag behavior for machine-readable output (bypasses Rich formatting)
- All formatting respects terminal capabilities (graceful degradation for non-color terminals)
- No breaking changes to existing OutputAdapter interface—new methods added, existing `render()` enhanced

## Impact

- Affected specs: `cli-core` (output formatting requirements)
- Affected code: `orbit/output.py` (OutputAdapter class extension)
- Enhances all CLI commands: containers list/create/delete, items CRUD, query results
- Improves developer experience across all features without changing command contracts
- Dependencies: leverages existing Rich library already in project dependencies
- Testing: unit tests for each output format, integration tests verify correct format selection

## Notes

- Implementation is purely additive—existing commands continue working with enhanced visuals
- Progress indicators only appear for operations >1s to avoid flicker on fast operations
- Error formatting preserves full exception context while improving readability
- JSON output mode (--json) bypasses all Rich formatting for script compatibility
- Future consideration: customizable themes via config file (deferred to separate change)
