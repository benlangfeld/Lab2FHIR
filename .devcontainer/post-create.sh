#!/bin/bash

set -euo pipefail

echo "🚀 Setting up Lab2FHIR development environment..."

echo "📦 Installing uv (Python package manager)..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

echo "📦 Installing spec-kit..."
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
export PATH="$HOME/.local/bin:$PATH"
echo "✅ spec-kit CLI installed"

# Write welcome message to first-run-notice.txt
mkdir -p /usr/local/etc/vscode-dev-containers
cat > /usr/local/etc/vscode-dev-containers/first-run-notice.txt << EOF

✅ Installation complete!

Available tools:
  - gh (GitHub CLI): $(gh --version 2>/dev/null | head -1 || echo 'installed')
  - copilot (Copilot CLI): $(copilot --version 2>&1 | head -1 || echo 'run "gh auth login" to enable')
  - specify (spec-kit): $(specify --version 2>/dev/null | head -1 || echo 'installed')

🎉 Your codespace is ready!

Next steps:
  1. Run 'gh auth login' to authenticate with GitHub (for Copilot CLI)
  2. Run 'specify check' to verify your spec-kit environment
  3. Start building Lab2FHIR!
EOF
