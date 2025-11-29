#!/bin/bash
# Full repository security scan
# Scans entire git history for secrets using trufflehog
#
# Usage: ./scripts/scan-repo.sh [--install]
#
# Options:
#   --install    Install trufflehog if not present (requires Docker or Go)

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

if [ -z "$REPO_ROOT" ]; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

cd "$REPO_ROOT"

# Check for --install flag
if [ "$1" = "--install" ]; then
    echo -e "${CYAN}Installing trufflehog...${NC}"

    # Try Docker first
    if command -v docker &> /dev/null; then
        echo "Using Docker to run trufflehog..."
        docker pull trufflesecurity/trufflehog:latest
        echo -e "${GREEN}✅ trufflehog Docker image pulled${NC}"
        TRUFFLEHOG_CMD="docker run --rm -v $(pwd):/repo trufflesecurity/trufflehog:latest"
    # Try Go install
    elif command -v go &> /dev/null; then
        echo "Installing via go install..."
        go install github.com/trufflesecurity/trufflehog/v3@latest
        echo -e "${GREEN}✅ trufflehog installed via go${NC}"
        TRUFFLEHOG_CMD="trufflehog"
    # Try Homebrew
    elif command -v brew &> /dev/null; then
        echo "Installing via Homebrew..."
        brew install trufflehog
        echo -e "${GREEN}✅ trufflehog installed via Homebrew${NC}"
        TRUFFLEHOG_CMD="trufflehog"
    else
        echo -e "${RED}Error: Could not install trufflehog${NC}"
        echo "Please install Docker, Go, or Homebrew first."
        exit 1
    fi
    exit 0
fi

echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Full Repository Security Scan${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Determine how to run trufflehog
TRUFFLEHOG_CMD=""

if command -v trufflehog &> /dev/null; then
    TRUFFLEHOG_CMD="trufflehog"
elif command -v docker &> /dev/null; then
    # Check if image exists
    if docker image inspect trufflesecurity/trufflehog:latest &> /dev/null; then
        TRUFFLEHOG_CMD="docker run --rm -v $(pwd):/repo trufflesecurity/trufflehog:latest"
    fi
fi

if [ -z "$TRUFFLEHOG_CMD" ]; then
    echo -e "${YELLOW}trufflehog not found. Running basic pattern scan instead.${NC}"
    echo ""

    # Fall back to basic grep scanning
    echo -e "${CYAN}Scanning git history for common secret patterns...${NC}"

    PATTERNS=(
        'ghp_[a-zA-Z0-9]{36}'
        'sk-[a-zA-Z0-9]{20,}'
        'sk-ant-'
        'AKIA[0-9A-Z]{16}'
        'xox[bpas]-'
        'sk_live_'
        '-----BEGIN.*PRIVATE KEY-----'
    )

    FOUND=0
    for pattern in "${PATTERNS[@]}"; do
        echo -n "  Checking pattern: $pattern ... "
        MATCHES=$(git log -p --all -S "$pattern" --oneline 2>/dev/null | head -20 || true)
        if [ -n "$MATCHES" ]; then
            echo -e "${RED}FOUND${NC}"
            echo "$MATCHES" | head -10
            FOUND=1
        else
            echo -e "${GREEN}clean${NC}"
        fi
    done

    echo ""
    if [ $FOUND -eq 1 ]; then
        echo -e "${RED}⚠️  Potential secrets found in git history!${NC}"
        echo "Consider using trufflehog for more detailed analysis:"
        echo "  ./scripts/scan-repo.sh --install"
        exit 1
    else
        echo -e "${GREEN}✅ No obvious secrets found in git history${NC}"
    fi
    exit 0
fi

# Run trufflehog
echo -e "${CYAN}Running trufflehog scan on git history...${NC}"
echo "This may take a few minutes for large repositories."
echo ""

if [[ "$TRUFFLEHOG_CMD" == docker* ]]; then
    # Docker mode - scan mounted /repo
    $TRUFFLEHOG_CMD git file:///repo --only-verified
else
    # Native mode
    $TRUFFLEHOG_CMD git file://. --only-verified
fi

RESULT=$?

echo ""
if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ Scan complete - No verified secrets found${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
else
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ⚠️  Secrets detected! See above for details.${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "To remove secrets from git history, consider using:"
    echo "  - git filter-branch"
    echo "  - BFG Repo-Cleaner (https://rtyley.github.io/bfg-repo-cleaner/)"
    echo ""
    echo "After cleaning history, force push may be required."
fi

exit $RESULT
