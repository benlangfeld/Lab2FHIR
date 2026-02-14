# Lab2FHIR Codespace Development Environment

This repository is configured with a GitHub Codespace that comes pre-configured with the following tools:

## 🛠️ Pre-installed Tools

### GitHub Copilot CLI
The GitHub Copilot command-line interface for AI-powered assistance in your terminal.

**Usage:**
```bash
# Authenticate with GitHub first
gh auth login

# Use Copilot CLI
gh copilot suggest "how to parse a PDF in Python"
gh copilot explain "git rebase -i HEAD~3"
```

### Spec Kit
A toolkit for spec-driven development that helps you build software by focusing on specifications first.

**Usage:**
```bash
# Initialize a new spec-driven project
specify init my-project

# Check your environment
specify check

# Get help
specify --help
```

## 🚀 Getting Started

1. **Open in Codespace**: Click the "Code" button on GitHub and select "Create codespace"

2. **Wait for setup**: The devcontainer will automatically:
   - Install GitHub CLI with Copilot extension
   - Install Node.js LTS
   - Install Python 3.11
   - Install spec-kit CLI via uv

3. **Authenticate**: Once the Codespace is ready, authenticate with GitHub:
   ```bash
   gh auth login
   ```

4. **Verify tools**: Check that everything is installed correctly:
   ```bash
   gh copilot --version
   specify --version
   ```

## 📚 Learn More

- [GitHub Copilot CLI](https://docs.github.com/en/copilot/github-copilot-in-the-cli)
- [Spec Kit Documentation](https://github.com/github/spec-kit)
- [Lab2FHIR Project Brief](docs/project-brief.md)

## 🔧 Manual Installation (if needed)

If for some reason the automatic installation doesn't work, you can manually install:

### GitHub Copilot CLI
```bash
gh extension install github/gh-copilot
```

### Spec Kit
```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install spec-kit
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```
