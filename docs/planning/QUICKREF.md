# Lab2FHIR Quick Reference Card

## 🎯 One-Liner
PDF lab reports → OpenAI structured parsing → FHIR R4 Bundles → Self-hosted FHIR server

## 🚀 Quick Start (30 seconds)
```bash
# 1. Open in Codespaces
# 2. Create issues:
cd docs/planning && ./github-issues.sh

# 3. Start coding:
git checkout -b feature/init-project
# Work on Task 1.1.1
```

## 📂 Key Files
- **Planning**: `docs/planning/project-breakdown.md`
- **Getting Started**: `docs/GETTING_STARTED.md`
- **Python Setup**: `docs/planning/python-structure.md`
- **Project Board**: `docs/planning/project-board-setup.md`

## 🏗️ MVP Tasks (Critical Path)
1. ✅ Init Python project (1.1.1-1.1.4)
2. ✅ Basic API (2.2.1-2.2.2)
3. ✅ PDF text extraction (3.1.1-3.1.2)
4. ✅ LLM schema (3.2.1-3.2.2)
5. ✅ OpenAI integration (3.3.1-3.3.3)
6. ✅ FHIR generation (5.1.1, 5.1.2, 5.2.1, 5.2.2)
7. ✅ Bundle creation (5.5.1-5.5.2)

**~20-26 hours** to working prototype

## 🏷️ Labels Quick Ref
| Label | Meaning |
|-------|---------|
| `priority: critical` | Blocks MVP |
| `priority: high` | Important for MVP |
| `priority: medium` | Post-MVP |
| `priority: low` | Backlog |
| `epic` | High-level initiative |
| `feature` | User-facing capability |
| `task` | Implementation work |
| `effort: small` | <2h |
| `effort: medium` | 2-4h |
| `effort: large` | >4h |

## 📦 Tech Stack
- **Language**: Python 3.11+
- **API**: FastAPI or Flask
- **Database**: PostgreSQL (post-MVP)
- **FHIR**: fhir.resources
- **PDF**: pdfplumber
- **LLM**: OpenAI API
- **Testing**: pytest, ruff, mypy
- **Deploy**: Heroku
- **Dev**: Codespaces + Copilot

## 🔧 Common Commands
```bash
# Install
poetry install

# Test
make test          # or: poetry run pytest

# Lint
make lint          # or: poetry run ruff check .

# Format
make format        # or: poetry run ruff format .

# Run (post-MVP)
make run           # or: poetry run uvicorn lab2fhir.api.app:app --reload

# Clean
make clean
```

## 🔄 Development Workflow
```bash
# Daily
git checkout main && git pull
# Check board → pick highest priority "Ready" task
git checkout -b feature/my-task
# Code with Copilot
poetry run pytest  # test frequently
git add . && git commit -m "feat: description"
git push && create PR
```

## 📊 Project Stats
- 6 Epics
- ~30 Features
- ~100 Tasks
- 18-20 MVP tasks
- Kanban (no sprints)

## 🎓 Core Principles
1. MVP first, iterate later
2. Test alongside code
3. Use Copilot heavily
4. Small focused commits
5. Priority-driven work
6. WIP limit: 2-3 items

## 🆘 Quick Help
- **Copilot Chat**: Ask questions about code
- **Issues**: Check for task details
- **Docs**: See `docs/planning/`
- **Tests Failing**: `make clean && make test`
- **Poetry Issues**: `poetry lock && poetry install`

## 🎯 MVP Definition
**Input**: PDF lab report  
**Output**: FHIR Bundle JSON file  
**Demo**: `curl -F pdf=@test.pdf localhost:8000/upload → bundle.json`

## 📝 .env Template
```bash
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...  # post-MVP
ENVIRONMENT=development
DEBUG=true
```

## 📞 Resources
- **Repo**: https://github.com/benlangfeld/Lab2FHIR
- **Project Board**: (create via project-board-setup.md)
- **Issues**: Run `./github-issues.sh` to create
- **FHIR R4**: http://hl7.org/fhir/R4/
- **OpenAI**: https://platform.openai.com/docs

---

**Status**: Planning Complete ✅  
**Next**: Run `./github-issues.sh` → Start Task 1.1.1  
**Questions**: Check docs or ask Copilot Chat
