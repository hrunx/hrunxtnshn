#!/bin/bash

# Script to upload hrunxtnshn to GitHub
# Run this script after authenticating with GitHub

set -e

echo "Creating GitHub repository 'hrunxtnshn'..."

# Create repository
gh repo create hrunxtnshn \
  --private \
  --source=. \
  --remote=origin \
  --description="Invisible autonomous research assistant browser extension with Python orchestrator" \
  --push

echo ""
echo "✓ Repository created successfully!"
echo ""
echo "Repository URL: https://github.com/hrunx/hrunxtnshn"
echo ""
echo "Next steps:"
echo "1. Visit the repository on GitHub"
echo "2. Add collaborators if needed"
echo "3. Configure branch protection rules"
echo "4. Add repository topics/tags"
echo ""
