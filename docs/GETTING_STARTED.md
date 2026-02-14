# Getting Started with Lab2FHIR Development

This guide helps you go from zero to coding in minutes using GitHub Codespaces.

## Prerequisites

- GitHub account with Codespaces access
- Basic Python knowledge
- Familiarity with Git

## Step 1: Open in Codespaces

1. Navigate to https://github.com/benlangfeld/Lab2FHIR
2. Click the green "Code" button
3. Select "Codespaces" tab
4. Click "Create codespace on main" (or your branch)
5. Wait for Codespace to build (~2-3 minutes)

The devcontainer will automatically:
- Install Python 3.12
- Install Poetry
- Install GitHub CLI
- Configure VS Code with Python extensions

## Step 2: Set Up GitHub Issues (First Time Only)

```bash
# Navigate to planning directory
cd docs/planning

# Make script executable (if not already)
chmod +x github-issues.sh

# Run the script to create all issues
./github-issues.sh
```

This creates:
- All label definitions
- 6 epic issues
- ~30 feature issues  
- ~50 task issues

**Note**: You need write access to the repository to create issues.

## Step 3: Set Up Project Board (First Time Only)

Follow the guide in `docs/planning/project-board-setup.md`:

1. Go to https://github.com/benlangfeld/Lab2FHIR/projects
2. Click "New project"
3. Choose "Board" template
4. Name it "Lab2FHIR Development"
5. Add columns: Backlog, Ready, In Progress, Review, Done
6. Add all issues to the board
7. Move MVP issues to "Ready" column

## Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
cat > .env << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=your-api-key-here

# Database Configuration (for post-MVP)
DATABASE_URL=postgresql://lab2fhir:lab2fhir@localhost:5432/lab2fhir

# Application Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# FHIR Server Configuration (for post-MVP)
FHIR_SERVER_URL=http://localhost:8080/fhir
FHIR_AUTH_TOKEN=optional-token

# File Storage
UPLOAD_FOLDER=./uploads
MAX_UPLOAD_SIZE=10485760  # 10MB
EOF
```

⚠️ **Important**: Never commit `.env` to Git! It's already in `.gitignore`.

## Step 5: Start Your First Task

### Option A: Create from Scratch (Recommended for Learning)

Start with Task 1.1.1: Initialize Python project

```bash
# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "lab2fhir"
version = "0.1.0"
description = "Convert laboratory PDF reports into FHIR resources"
authors = ["Ben Langfeld <ben@langfeld.me>"]
readme = "README.md"
packages = [{include = "lab2fhir", from = "src"}]

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
ruff = "^0.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

# Install dependencies
poetry install

# Create basic structure
mkdir -p src/lab2fhir
touch src/lab2fhir/__init__.py

# Verify it works
poetry run python -c "import lab2fhir; print('Success!')"
```

### Option B: Use the Template (Faster Start)

Copy the complete `pyproject.toml` from `docs/planning/python-structure.md`:

```bash
# Copy pyproject.toml template from docs
# (Edit it as needed, then)

poetry install
```

## Step 6: Verify Your Setup

Run these commands to verify everything works:

```bash
# Check Python version
python --version
# Should show Python 3.11 or 3.12

# Check Poetry
poetry --version

# Check GitHub CLI
gh --version

# Run tests (will pass with no tests)
poetry run pytest

# Run linter (will pass with no code)
poetry run ruff check .
```

## Step 7: Make Your First Contribution

1. **Pick a task** from the "Ready" column on the project board
2. **Create a branch**:
   ```bash
   git checkout -b feature/task-description
   ```
3. **Write code**
4. **Test your code**:
   ```bash
   make test  # or: poetry run pytest
   ```
5. **Lint your code**:
   ```bash
   make lint  # or: poetry run ruff check .
   ```
6. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: implement task description"
   git push origin feature/task-description
   ```
7. **Open a pull request** on GitHub

## Development Workflow

### Daily Workflow

1. **Pull latest changes**:
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Check the project board** for highest priority "Ready" task

3. **Create feature branch**:
   ```bash
   git checkout -b feature/my-task
   ```

4. **Write code** with Copilot assistance

5. **Test frequently**:
   ```bash
   poetry run pytest tests/unit/test_my_feature.py
   ```

6. **Commit small, logical changes**:
   ```bash
   git add .
   git commit -m "feat: add feature X"
   ```

7. **Push and create PR** when done

### Using Copilot Effectively

- **Write clear comments** describing what you want
- **Use descriptive function names** 
- **Write tests first** (Copilot will help implement)
- **Accept/reject suggestions** thoughtfully
- **Ask Copilot Chat** questions about the codebase

Example:
```python
# Extract text from a PDF file using pdfplumber
# Returns the full text content as a string
# Raises ValueError if the file is not a valid PDF
def extract_pdf_text(pdf_path: str) -> str:
    # Copilot will suggest the implementation
```

## Common Commands

```bash
# Install dependencies
make install

# Run tests
make test

# Run tests with coverage
make test-cov

# Run linting
make lint

# Format code
make format

# Clean cache files
make clean

# Run development server (post-MVP)
make run

# Run database migrations (post-MVP)
make migrate
```

## Useful VS Code Shortcuts in Codespaces

- `Ctrl+Shift+P`: Command palette
- `Ctrl+Shift+\``: Open terminal
- `Ctrl+P`: Quick file open
- `F12`: Go to definition
- `Shift+F12`: Find all references
- `Ctrl+Space`: Trigger Copilot
- `Tab`: Accept Copilot suggestion
- `Alt+]`: Next Copilot suggestion

## Getting Help

### Documentation
- Project Brief: `/docs/project-brief.md`
- Planning Docs: `/docs/planning/`
- Python Structure: `/docs/planning/python-structure.md`

### Tools
- **Copilot Chat**: Ask questions about the code
- **GitHub Issues**: Check issue descriptions for context
- **Project Board**: See what others are working on

### Troubleshooting

**Poetry not found**:
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

**Dependencies not installing**:
```bash
poetry lock
poetry install --no-cache
```

**Tests failing**:
```bash
# Clear cache and rerun
make clean
make test
```

**Codespace slow**:
- Restart the Codespace
- Or rebuild the container: Cmd+Shift+P → "Codespaces: Rebuild Container"

## MVP Task Checklist

Work through these tasks in order for a working MVP:

- [ ] Task 1.1.1: Initialize Python project with pyproject.toml
- [ ] Task 1.1.2: Set up package structure (src/lab2fhir/)
- [ ] Task 1.1.4: Add .gitignore for Python projects
- [ ] Task 1.2.2: Configure VS Code settings
- [ ] Task 1.2.3: Add development dependencies
- [ ] Task 2.2.1: Create Flask/FastAPI skeleton
- [ ] Task 2.2.2: Implement PDF upload endpoint
- [ ] Task 3.1.1: Evaluate PDF parsing library
- [ ] Task 3.1.2: Implement text extraction
- [ ] Task 3.2.1: Define JSON schema for lab results
- [ ] Task 3.2.2: Create Pydantic models
- [ ] Task 3.3.1: Set up OpenAI API client
- [ ] Task 3.3.2: Implement structured output
- [ ] Task 3.3.3: Create prompt templates
- [ ] Task 5.1.1: Integrate fhir.resources library
- [ ] Task 5.1.2: Set up FHIR resource builders
- [ ] Task 5.2.1: Create Observation resources
- [ ] Task 5.2.2: Map values and units
- [ ] Task 5.5.1: Create transaction Bundle
- [ ] Task 5.5.2: Include all resources

When all checked, you have a working MVP! 🎉

## Next Steps After MVP

1. Add comprehensive tests
2. Improve error handling and logging
3. Add database persistence
4. Implement FHIR server integration
5. Add unit normalization
6. Support multiple patients
7. Deploy to Heroku

---

**Ready to start?** Pick up Task 1.1.1 and let's build Lab2FHIR! 🚀
