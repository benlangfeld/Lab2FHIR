#!/bin/bash

set -e

echo "🚀 Setting up Lab2FHIR development environment..."

# Install GitHub Copilot CLI
echo "📦 Installing GitHub Copilot CLI..."
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not found, skipping Copilot CLI installation"
else
    gh extension install github/gh-copilot 2>&1 | grep -v "already installed" || echo "ℹ️  Copilot CLI ready (may require 'gh auth login')"
fi

# Install spec-kit CLI
echo "📦 Installing spec-kit CLI..."

# Check if uv is already installed
if command -v uv &> /dev/null; then
    echo "✅ uv already installed"
else
    # Install uv if not available
    echo "📦 Installing uv (Python package manager)..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        export PATH="$HOME/.local/bin:$PATH"
        echo "✅ uv installed"
    else
        echo "⚠️  Could not install uv automatically"
        echo "    In Codespaces, uv will be installed on first use"
    fi
fi

# Install spec-kit via uv if available
if command -v uv &> /dev/null; then
    echo "📦 Installing spec-kit via uv..."
    if uv tool install specify-cli --from git+https://github.com/github/spec-kit.git 2>&1 | grep -E "(Installed|installed)" || true; then
        export PATH="$HOME/.local/bin:$PATH"
        echo "✅ spec-kit CLI installed"
    else
        echo "ℹ️  spec-kit installation queued for first use"
    fi
else
    echo "ℹ️  spec-kit will be installed on first Codespace launch"
fi

# Verify installations
echo ""
echo "✅ Installation complete!"
echo ""
echo "Available tools:"
if command -v gh &> /dev/null; then
    echo "  - gh (GitHub CLI): $(gh --version 2>/dev/null | head -1 || echo 'installed')"
    echo "  - gh copilot: $(gh copilot --version 2>&1 | head -1 || echo 'run \"gh auth login\" to enable')"
else
    echo "  - gh (GitHub CLI): not available"
fi

if command -v specify &> /dev/null; then
    echo "  - specify (spec-kit): $(specify --version 2>/dev/null | head -1 || echo 'installed')"
else
    echo "  - specify (spec-kit): will be available after first Codespace launch"
fi
echo ""
echo "🎉 Your codespace is ready!"
echo ""
echo "Next steps:"
echo "  1. Run 'gh auth login' to authenticate with GitHub (for Copilot CLI)"
echo "  2. Run 'specify check' to verify your spec-kit environment"
echo "  3. Start building Lab2FHIR!"

