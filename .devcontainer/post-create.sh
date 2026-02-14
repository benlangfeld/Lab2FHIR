#!/bin/bash

set -euo pipefail

echo "🚀 Setting up Lab2FHIR development environment..."

# Install spec-kit CLI
echo "📦 Installing spec-kit CLI..."

# Install uv if not available
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install spec-kit via uv
echo "📦 Installing spec-kit via uv..."
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
export PATH="$HOME/.local/bin:$PATH"
echo "✅ spec-kit CLI installed"

# Verify installations
echo ""
echo "✅ Installation complete!"
echo ""
echo "Available tools:"
echo "  - gh (GitHub CLI): $(gh --version 2>/dev/null | head -1 || echo 'installed')"
echo "  - copilot (Copilot CLI): $(copilot --version 2>&1 | head -1 || echo 'run \"gh auth login\" to enable')"
echo "  - specify (spec-kit): $(specify --version 2>/dev/null | head -1 || echo 'installed')"
echo ""
echo "🎉 Your codespace is ready!"
echo ""
echo "Next steps:"
echo "  1. Run 'gh auth login' to authenticate with GitHub (for Copilot CLI)"
echo "  2. Run 'specify check' to verify your spec-kit environment"
echo "  3. Start building Lab2FHIR!"

