# Lab2FHIR Project Planning

This directory contains all project planning and organizational documents for Lab2FHIR.

## Quick Start

**New to the project?** Follow these steps:

1. **Read the Project Brief**: Start with `/docs/project-brief.md` to understand what Lab2FHIR does
2. **Review Project Breakdown**: Read `project-breakdown.md` to see the epic/feature/task structure
3. **Set Up Your Environment**: Follow `python-structure.md` for local development setup
4. **Create GitHub Issues**: Run `./github-issues.sh` to create all planned issues
5. **Set Up Project Board**: Follow `project-board-setup.md` to create the Kanban board
6. **Start with MVP**: Pick up the first MVP task and get coding!

## Documents

### [project-breakdown.md](project-breakdown.md)
Complete project breakdown organized into 6 epics with all features and tasks defined. This is the **master reference** for what needs to be built.

**Contents:**
- 6 Epics covering the full system architecture
- ~30 Features grouped by epic
- ~100 Tasks with clear implementation steps
- MVP definition and sequencing
- Labels and priority system
- Dependency graph

### [github-issues.sh](github-issues.sh)
Executable bash script that creates all GitHub issues, labels, and initial structure.

**Usage:**
```bash
# Prerequisites: GitHub CLI (gh) installed and authenticated
cd docs/planning
./github-issues.sh
```

This will create:
- All label definitions
- 6 epic issues
- ~30 feature issues
- ~50 key task issues (more can be created as needed)

### [project-board-setup.md](project-board-setup.md)
Step-by-step guide to setting up the GitHub Projects V2 Kanban board.

**Includes:**
- Board column configuration
- Custom field setup
- Automation rules
- View configurations
- Workflow guidelines

### [python-structure.md](python-structure.md)
Comprehensive guide to the Python project structure, tooling, and setup.

**Includes:**
- Complete directory structure
- Technology stack decisions
- `pyproject.toml` template
- Makefile template
- `.gitignore` template
- Pre-commit configuration
- Getting started instructions

## Project Methodology

**Kanban Approach**: This project uses Kanban (continuous flow) rather than sprints.

**Key Principles:**
- ✅ **No milestones**: Work flows continuously, prioritized by labels
- ✅ **MVP-first**: Focus on end-to-end functionality, then iterate
- ✅ **Small tasks**: Break work into <4 hour tasks when possible
- ✅ **Priority-driven**: Always work the highest priority "Ready" item
- ✅ **WIP limits**: Limit work-in-progress to 2-3 items at a time

## MVP Definition

The Minimum Viable Product delivers a basic end-to-end flow:

**PDF → Structured Data → FHIR Bundle**

### MVP Features (Priority: Critical)
1. F1.1: Python Project Structure
2. F1.2: Development Environment
3. F2.2: PDF Upload Handler (basic API only)
4. F3.1: PDF Text Extraction
5. F3.2: LLM Schema Design
6. F3.3: OpenAI Integration
7. F5.1: FHIR Library Integration
8. F5.2: Observation Generation
9. F5.5: Bundle Creation

### What's NOT in MVP
- Database persistence (file-based for now)
- Multi-patient support (single patient)
- FHIR server integration (file output only)
- Unit normalization (basic pass-through)
- Complex validation
- Web UI (API only)

## Labels Reference

### Type Labels
- `epic` - High-level initiative spanning multiple features
- `feature` - User-facing capability
- `task` - Implementation work
- `bug` - Something broken
- `enhancement` - Improvement to existing feature

### Component Labels
- `infrastructure` - Dev environment, CI/CD
- `ingestion` - PDF upload and storage
- `parsing` - LLM and text extraction
- `normalization` - Data cleaning and validation
- `fhir` - FHIR resource generation
- `integration` - FHIR server interaction

### Priority Labels
- `priority: critical` - Blocking MVP (do first)
- `priority: high` - Important for MVP (do soon)
- `priority: medium` - Post-MVP polish (do later)
- `priority: low` - Nice to have (backlog)

### Status Labels (Kanban columns)
- `status: backlog` - Not started
- `status: ready` - Ready to work on
- `status: in-progress` - Active work
- `status: review` - Needs review
- `status: blocked` - Waiting on something

### Effort Labels
- `effort: small` - < 2 hours
- `effort: medium` - 2-4 hours
- `effort: large` - > 4 hours

## Architecture Overview

Lab2FHIR follows a pipeline architecture:

```
┌──────────────┐
│ PDF Upload   │
└──────┬───────┘
       │
┌──────▼───────────┐
│ Text Extraction  │
└──────┬───────────┘
       │
┌──────▼───────────┐
│ LLM Parsing      │
│ (Structured JSON)│
└──────┬───────────┘
       │
┌──────▼──────────────┐
│ Normalization       │
│ (Units, Dates, etc) │
└──────┬──────────────┘
       │
┌──────▼────────────┐
│ FHIR Generation   │
│ (Bundle creation) │
└──────┬────────────┘
       │
┌──────▼──────────┐
│ FHIR Store Push │
│ (e.g., Fasten)  │
└─────────────────┘
```

Each layer is independent and testable, connected by well-defined interfaces.

## Technology Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI (recommended) or Flask
- **Database**: PostgreSQL (post-MVP)
- **ORM**: SQLAlchemy 2.0
- **FHIR**: fhir.resources
- **PDF Parsing**: pdfplumber
- **LLM**: OpenAI API
- **Validation**: Pydantic 2.x
- **Testing**: pytest
- **Linting**: ruff
- **Type Checking**: mypy
- **Deployment**: Heroku (initially)
- **Dev Environment**: GitHub Codespaces

## Next Steps

1. **Set up development environment**: 
   - Open repository in GitHub Codespaces
   - Or follow local setup in `python-structure.md`

2. **Create GitHub structure**:
   - Run `./github-issues.sh` to create all issues
   - Follow `project-board-setup.md` to set up the board

3. **Start MVP development**:
   - Pick up Task 1.1.1: Initialize Python project
   - Work through MVP tasks in priority order
   - Use Copilot to accelerate development

4. **Iterate and improve**:
   - Complete MVP features
   - Add tests and documentation
   - Polish and add advanced features
   - Deploy to production

## Questions?

If you have questions about the project structure or planning:

1. Check the project brief: `/docs/project-brief.md`
2. Review this planning directory
3. Look at the created GitHub issues for detailed context
4. Open a discussion on GitHub

## Contributing

See `CONTRIBUTING.md` (to be created in Task 1.6.1) for development guidelines.

---

**Last Updated**: 2026-02-14  
**Status**: Planning Complete, Ready for Implementation
