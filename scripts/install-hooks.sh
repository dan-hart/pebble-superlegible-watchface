#!/bin/bash
# Install git hooks for security scanning
# Run this script after cloning the repository

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Find repository root
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

if [ -z "$REPO_ROOT" ]; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

HOOKS_SOURCE="$REPO_ROOT/.githooks"
HOOKS_DEST="$REPO_ROOT/.git/hooks"

# Check source exists
if [ ! -d "$HOOKS_SOURCE" ]; then
    echo -e "${RED}Error: .githooks directory not found${NC}"
    exit 1
fi

# Install pre-commit hook
if [ -f "$HOOKS_SOURCE/pre-commit" ]; then
    cp "$HOOKS_SOURCE/pre-commit" "$HOOKS_DEST/pre-commit"
    chmod +x "$HOOKS_DEST/pre-commit"
    echo -e "${GREEN}✅ Pre-commit hook installed${NC}"
else
    echo -e "${RED}Error: pre-commit hook not found in .githooks/${NC}"
    exit 1
fi

echo ""
echo "Git hooks installed successfully!"
echo "The pre-commit hook will now scan for secrets before each commit."
echo ""
echo "To test the hook, try staging a file with a fake secret:"
echo "  echo 'api_key = \"test123\"' > /tmp/test.txt"
echo "  git add /tmp/test.txt"
echo "  git commit -m 'test'  # Should be blocked"
