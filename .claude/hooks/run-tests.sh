#!/bin/bash
# Run tests hook - can be called manually or as part of workflow
# Exit codes: 0 = all tests pass, 2 = test failures (fed back to Claude)

cd "$CLAUDE_PROJECT_DIR" || exit 1

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Install with: pip install pytest" >&2
    exit 2
fi

# Run tests with short output
echo "Running tests..."
if pytest --tb=short -q "$@" 2>&1; then
    echo "All tests passed!"
    exit 0
else
    echo "Some tests failed." >&2
    exit 2
fi
