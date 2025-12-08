#!/bin/bash
# Session summary hook - runs when Claude finishes
# Shows git status and any uncommitted changes

cd "$CLAUDE_PROJECT_DIR" || exit 1

echo "=== Session Summary ==="
echo ""

# Show git status
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current)
    echo "Branch: $BRANCH"

    # Count changes
    STAGED=$(git diff --cached --numstat | wc -l)
    UNSTAGED=$(git diff --numstat | wc -l)
    UNTRACKED=$(git ls-files --others --exclude-standard | wc -l)

    if [[ $STAGED -gt 0 ]] || [[ $UNSTAGED -gt 0 ]] || [[ $UNTRACKED -gt 0 ]]; then
        echo ""
        echo "Uncommitted changes:"
        git status --short
    else
        echo "Working tree clean."
    fi

    # Show recent commits from this session (last 5)
    echo ""
    echo "Recent commits:"
    git log --oneline -5
fi

exit 0
