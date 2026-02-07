#!/bin/bash
# Script to create a new release for PyRust
# Usage: ./scripts/create-release.sh <version>
# Example: ./scripts/create-release.sh 0.2.0

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Version number required${NC}"
    echo "Usage: $0 <version>"
    echo "Example: $0 0.2.0"
    exit 1
fi

VERSION=$1
TAG="v${VERSION}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  PyRust Release Creator${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verify we're on main/master
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "main" && "$BRANCH" != "master" ]]; then
    echo -e "${YELLOW}Warning: Not on main/master branch (current: $BRANCH)${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo -e "${RED}Error: You have uncommitted changes${NC}"
    git status -s
    exit 1
fi

# Check if tag already exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo -e "${RED}Error: Tag $TAG already exists${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Creating release for version ${BLUE}$VERSION${NC}"
echo ""

# Update Cargo.toml
echo -e "${YELLOW}➜${NC} Updating Cargo.toml..."
sed -i.bak "s/^version = \".*\"/version = \"$VERSION\"/" Cargo.toml && rm Cargo.toml.bak

# Update pyproject.toml
echo -e "${YELLOW}➜${NC} Updating pyproject.toml..."
sed -i.bak "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml && rm pyproject.toml.bak

# Update __init__.py
echo -e "${YELLOW}➜${NC} Updating python/pyrust/__init__.py..."
sed -i.bak "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" python/pyrust/__init__.py && rm python/pyrust/__init__.py.bak

# Show changes
echo ""
echo -e "${BLUE}Changes:${NC}"
git diff Cargo.toml pyproject.toml python/pyrust/__init__.py

# Confirm
echo ""
read -p "Commit these changes? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Aborted${NC}"
    git checkout Cargo.toml pyproject.toml python/pyrust/__init__.py
    exit 1
fi

# Commit version bump
echo -e "${YELLOW}➜${NC} Committing version bump..."
git add Cargo.toml pyproject.toml python/pyrust/__init__.py
git commit -m "chore: bump version to $VERSION"

# Create tag
echo -e "${YELLOW}➜${NC} Creating git tag $TAG..."
git tag -a "$TAG" -m "Release version $VERSION"

# Show summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Release Prepared Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Version:${NC} $VERSION"
echo -e "${BLUE}Tag:${NC} $TAG"
echo -e "${BLUE}Commit:${NC} $(git rev-parse --short HEAD)"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review the changes:"
echo "     ${BLUE}git show${NC}"
echo ""
echo "  2. Push the changes and tag:"
echo "     ${BLUE}git push origin $BRANCH${NC}"
echo "     ${BLUE}git push origin $TAG${NC}"
echo ""
echo "  3. GitHub Actions will automatically:"
echo "     - Build wheels for all platforms"
echo "     - Run all tests"
echo "     - Create a GitHub release"
echo "     - Publish to PyPI (if configured)"
echo ""
echo -e "${GREEN}Release URL (after push):${NC}"
echo "  https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/releases/tag/$TAG"
echo ""
