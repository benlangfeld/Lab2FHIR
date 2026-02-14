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
copilot suggest "how to parse a PDF in Python"
copilot explain "git rebase -i HEAD~3"
```

### Spec Kit
A toolkit for spec-driven development that helps you build software by focusing on specifications first.

**Usage:**
```bash
specify check

specify --help
```

## 🚀 Getting Started

1. **Open in Codespace**: Click the "Code" button on GitHub and select "Create codespace"

2. **Wait for setup**: The devcontainer will automatically:
   - Install GitHub CLI and Copilot CLI
   - Install Python 3.11 & uv
   - Install spec-kit CLI

3. **Authenticate**: Once the Codespace is ready, authenticate with GitHub:
   ```bash
   gh auth login
   ```

4. **Verify tools**: Check that everything is installed correctly:
   ```bash
   copilot --version
   specify --version
   ```

## 📚 Learn More

- [GitHub Copilot CLI](https://docs.github.com/en/copilot/github-copilot-in-the-cli)
- [Spec Kit Documentation](https://github.com/github/spec-kit)
- [Lab2FHIR Project Brief](docs/project-brief.md)
