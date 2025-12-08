#!/bin/bash
# Lint check hook - runs after file writes/edits
# Exit codes: 0 = success, 2 = blocking error (fed back to Claude)

FILE_PATH="$1"

# Skip non-Python files
if [[ ! "$FILE_PATH" =~ \.py$ ]]; then
    exit 0
fi

cd "$CLAUDE_PROJECT_DIR" || exit 1

# Check if the file exists (might have been deleted)
if [[ ! -f "$FILE_PATH" ]]; then
    exit 0
fi

# Basic Python syntax check
if ! python -m py_compile "$FILE_PATH" 2>&1; then
    echo "Syntax error in $FILE_PATH" >&2
    exit 2
fi

exit 0
