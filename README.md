# Lab2FHIR

Unlock structured insights from your lab reports

**Transform laboratory PDF reports into FHIR-compliant clinical resources for self-hosted health record management.**

## Overview

Lab2FHIR is a self-hosted pipeline that converts structured laboratory PDF reports into validated FHIR R4 resources. It uses LLM-powered parsing to extract lab values and generates standards-compliant FHIR Observations, DiagnosticReports, and DocumentReferences.

**Key Features:**
- 📄 PDF text extraction and parsing
- 🤖 OpenAI-powered structured data extraction
- 🏥 FHIR R4 resource generation
- 🔒 Self-hosted, PHI-safe operation
- 👥 Multi-patient support (human & veterinary)
- 🔄 Deterministic deduplication

## Project Status

🚧 **In Planning** - Project structure complete, ready for implementation

## Quick Links

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Step-by-step setup for new developers
- **[Project Brief](docs/project-brief.md)** - Vision and architecture
- **[Project Planning](docs/planning/)** - Epics, features, and tasks
- **[Quick Reference](docs/planning/QUICKREF.md)** - Handy cheat sheet

## Architecture

```
PDF Upload → Text Extraction → LLM Parsing → Normalization → FHIR Generation → FHIR Store
```

See [Project Brief](docs/project-brief.md) for detailed architecture.

## Technology Stack

- **Python 3.11+** with Poetry
- **FastAPI** for REST API
- **OpenAI API** for structured parsing
- **fhir.resources** for FHIR R4 compliance
- **PostgreSQL** for persistence
- **GitHub Codespaces** for development
- **Heroku** for deployment

## Getting Started

### For Developers

1. **Open in Codespaces** (recommended) or clone locally
2. **Read the [Getting Started Guide](docs/GETTING_STARTED.md)**
3. **Create GitHub Issues**: Run `docs/planning/github-issues.sh`
4. **Start coding**: Pick up Task 1.1.1 from the project board

### Quick Start
```bash
# Open in GitHub Codespaces or clone
git clone https://github.com/benlangfeld/Lab2FHIR.git
cd Lab2FHIR

# Create issues and project board
cd docs/planning
./github-issues.sh
# Follow project-board-setup.md

# Start first task
git checkout -b feature/init-project
# Work on Task 1.1.1: Initialize Python project
```

## Project Structure

```
Lab2FHIR/
├── docs/
│   ├── project-brief.md          # Vision and architecture
│   ├── GETTING_STARTED.md        # Developer onboarding
│   └── planning/                 # Project planning docs
│       ├── project-breakdown.md  # Complete task breakdown
│       ├── github-issues.sh      # Issue creation script
│       ├── project-board-setup.md # Board configuration
│       └── python-structure.md   # Code structure guide
├── src/lab2fhir/                 # Main package (to be created)
├── tests/                        # Test suite (to be created)
├── .devcontainer/                # Codespaces config
└── .github/workflows/            # CI/CD pipelines
```

## Development Workflow

Lab2FHIR uses **Kanban methodology** (continuous flow, no sprints):

1. Check project board for highest priority "Ready" task
2. Create feature branch
3. Implement with GitHub Copilot assistance
4. Test with `make test`
5. Lint with `make lint`
6. Create pull request
7. Review and merge

See [Getting Started Guide](docs/GETTING_STARTED.md) for detailed workflow.

## MVP Roadmap

The MVP delivers a basic end-to-end pipeline:

✅ **Phase 1**: Project setup  
✅ **Phase 2**: PDF upload API  
✅ **Phase 3**: Text extraction  
✅ **Phase 4**: LLM parsing  
✅ **Phase 5**: FHIR generation  
⬜ **Phase 6**: FHIR server integration (post-MVP)

~20-26 hours of focused development for working prototype.

## Contributing

This is currently a solo project. Once the MVP is complete, contribution guidelines will be added.

For now:
1. Read the [Project Brief](docs/project-brief.md)
2. Check the [Project Planning](docs/planning/) docs
3. Follow the development workflow above

## License

To be determined.

## Contact

Ben Langfeld - [GitHub](https://github.com/benlangfeld)

---

**Status**: 📋 Planning Complete → 🚀 Ready for Implementation  
**Next Steps**: Create GitHub issues → Start Task 1.1.1
