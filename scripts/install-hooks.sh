#!/bin/bash
# Install git hooks for security scanning
# Run this script after cloning the repository
#
# This script configures git to use hooks from .githooks/ directory,
# which means hooks are version-controlled and automatically active.

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Setting up security hooks...${NC}"
echo ""

# Find repository root
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

if [ -z "$REPO_ROOT" ]; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

cd "$REPO_ROOT"

# Check source exists
if [ ! -d ".githooks" ]; then
    echo -e "${RED}Error: .githooks directory not found${NC}"
    exit 1
fi

# Make hooks executable
chmod +x .githooks/pre-commit 2>/dev/null || true
chmod +x .githooks/pre-push 2>/dev/null || true

# Configure git to use .githooks directory
# This is the recommended approach - hooks are version controlled
git config core.hooksPath .githooks

echo -e "${GREEN}✅ Git hooks configured${NC}"
echo ""
echo "Installed hooks:"
echo "  • pre-commit  - Scans staged files for secrets before commit"
echo "  • pre-push    - Scans commits for secrets before push"
echo ""
echo -e "${YELLOW}Protection enabled:${NC}"
echo "  • GitHub, OpenAI, Anthropic, Jira tokens"
echo "  • AWS, Slack, Stripe, Google, Twilio, SendGrid keys"
echo "  • DigitalOcean, NPM, PyPI tokens"
echo "  • Private keys, passwords, connection strings"
echo "  • Base64 encoded secrets"
echo "  • Hardcoded paths"
echo ""
echo -e "${YELLOW}Note:${NC} Server-side scanning is also enabled via GitHub Actions."
echo "      Even if local hooks are bypassed, secrets will be caught on push/PR."
echo ""

# Verify configuration
HOOKS_PATH=$(git config --get core.hooksPath 2>/dev/null || echo "")
if [ "$HOOKS_PATH" = ".githooks" ]; then
    echo -e "${GREEN}✅ Verification passed: core.hooksPath = .githooks${NC}"
else
    echo -e "${RED}⚠️  Warning: core.hooksPath not set correctly${NC}"
    echo "   Expected: .githooks"
    echo "   Got: $HOOKS_PATH"
    exit 1
fi

echo ""
echo "To test the hooks:"
echo "  1. Create a test file with a fake secret"
echo "  2. Try to commit it - should be blocked"
echo ""
echo "Example:"
echo "  # Create a file with a pattern like: ghp_xxxx... or sk-xxxx..."
echo "  git add <file>"
echo '  git commit -m "test"  # Should be blocked!'
