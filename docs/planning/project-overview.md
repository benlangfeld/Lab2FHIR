# Lab2FHIR Project Structure - Visual Overview

## 🎯 Project Mission
Transform laboratory PDF reports into validated FHIR R4 resources for self-hosted health record management.

## 📊 Project Statistics
- **6 Epics**: Covering full pipeline from infrastructure to integration
- **~30 Features**: User-facing capabilities and system components
- **~100 Tasks**: Fine-grained implementation work
- **MVP Tasks**: 18-20 critical path items for working prototype
- **Development Approach**: Kanban (continuous flow, no sprints)
- **Priority System**: Critical → High → Medium → Low

## 🏗️ Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Lab2FHIR Data Pipeline                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   PDF File   │─────▶│  Ingestion   │─────▶│   Storage    │
│   Upload     │      │   Layer      │      │  (Postgres)  │
└──────────────┘      └──────────────┘      └──────┬───────┘
                                                    │
┌──────────────┐      ┌──────────────┐            │
│ Text Content │◀─────│     PDF      │◀───────────┘
│  (String)    │      │  Extraction  │
└──────┬───────┘      └──────────────┘
       │
       │              ┌──────────────┐      ┌──────────────┐
       └─────────────▶│     LLM      │─────▶│  Structured  │
                      │   Parsing    │      │     JSON     │
                      └──────────────┘      └──────┬───────┘
                                                    │
┌──────────────┐      ┌──────────────┐            │
│  Validated   │◀─────│Normalization │◀───────────┘
│    Data      │      │ & Validation │
└──────┬───────┘      └──────────────┘
       │
       │              ┌──────────────┐      ┌──────────────┐
       └─────────────▶│     FHIR     │─────▶│    Bundle    │
                      │  Generation  │      │ (Transaction)│
                      └──────────────┘      └──────┬───────┘
                                                    │
┌──────────────┐      ┌──────────────┐            │
│ FHIR Server  │◀─────│    Submit    │◀───────────┘
│  (Fasten)    │      │   to Store   │
└──────────────┘      └──────────────┘
```

## 📦 Epic Breakdown

### Epic 1: 🛠️ Infrastructure (Priority: Critical)
**Goal**: Production-ready Python development environment

| Feature | Tasks | Status | Priority |
|---------|-------|--------|----------|
| F1.1: Python Project Structure | 4 | 🔴 Not Started | Critical |
| F1.2: Development Environment | 4 | 🔴 Not Started | Critical |
| F1.3: Code Quality & Linting | 4 | 🟡 Ready | High |
| F1.4: Testing Infrastructure | 4 | 🟡 Ready | High |
| F1.5: CI/CD Pipeline | 4 | 🟡 Ready | High |
| F1.6: Documentation | 4 | 🟢 Post-MVP | Medium |

**MVP Items**: F1.1, F1.2 (partial F1.3)

---

### Epic 2: 📄 PDF Ingestion Layer (Priority: Critical/High)
**Goal**: Accept, deduplicate, and store PDF uploads

| Feature | Tasks | Status | Priority |
|---------|-------|--------|----------|
| F2.1: Storage Backend | 4 | 🟢 Post-MVP | High |
| F2.2: PDF Upload Handler | 4 | 🔴 Critical | Critical |
| F2.3: Document Management | 4 | 🟢 Post-MVP | High |
| F2.4: Multi-Patient Support | 4 | 🟢 Post-MVP | Medium |

**MVP Items**: F2.2 (Tasks 1-2 only: basic upload endpoint)

---

### Epic 3: 🤖 LLM Parsing Layer (Priority: Critical)
**Goal**: Extract structured lab data from PDFs using OpenAI

| Feature | Tasks | Status | Priority |
|---------|-------|--------|----------|
| F3.1: PDF Text Extraction | 4 | 🔴 Critical | Critical |
| F3.2: LLM Schema Design | 4 | 🔴 Critical | Critical |
| F3.3: OpenAI Integration | 4 | 🔴 Critical | Critical |
| F3.4: Parse Result Storage | 4 | 🟢 Post-MVP | Medium |
| F3.5: Quality Assurance | 4 | 🟢 Post-MVP | Low |

**MVP Items**: F3.1, F3.2, F3.3 (all critical for MVP)

---

### Epic 4: 🧹 Normalization Layer (Priority: High/Medium)
**Goal**: Clean, validate, and standardize extracted data

| Feature | Tasks | Status | Priority |
|---------|-------|--------|----------|
| F4.1: Unit Normalization | 4 | 🟢 Post-MVP | High |
| F4.2: Date Normalization | 4 | 🟢 Post-MVP | High |
| F4.3: Value Validation | 4 | 🟢 Post-MVP | High |
| F4.4: Analyte Canonicalization | 4 | 🟢 Post-MVP | Medium |
| F4.5: Data Quality Checks | 4 | 🟢 Post-MVP | Medium |

**MVP Items**: None (basic pass-through for MVP)

---

### Epic 5: 🏥 FHIR Generation Layer (Priority: Critical)
**Goal**: Convert normalized data to valid FHIR R4 resources

| Feature | Tasks | Status | Priority |
|---------|-------|--------|----------|
| F5.1: FHIR Library Integration | 4 | 🔴 Critical | Critical |
| F5.2: Observation Generation | 4 | 🔴 Critical | Critical |
| F5.3: DiagnosticReport Generation | 4 | 🟢 Post-MVP | High |
| F5.4: DocumentReference Generation | 4 | 🟢 Post-MVP | High |
| F5.5: Bundle Creation | 4 | 🔴 Critical | Critical |
| F5.6: Patient Resource Handling | 4 | 🟢 Post-MVP | Medium |

**MVP Items**: F5.1, F5.2, F5.5 (core FHIR generation)

---

### Epic 6: 🔗 FHIR Store Integration (Priority: High)
**Goal**: Submit bundles to FHIR server with retry logic

| Feature | Tasks | Status | Priority |
|---------|-------|--------|----------|
| F6.1: FHIR Server Client | 4 | 🟢 Post-MVP | High |
| F6.2: Bundle Submission | 4 | 🟢 Post-MVP | High |
| F6.3: Error Handling & Retry | 4 | 🟢 Post-MVP | High |
| F6.4: Status Tracking | 4 | 🟢 Post-MVP | Medium |
| F6.5: Deduplication Logic | 4 | 🟢 Post-MVP | High |

**MVP Items**: None (file output only for MVP)

---

## 🎯 MVP Critical Path

```
START
  ↓
┌─────────────────────────────────────┐
│ Phase 1: Project Setup (2-3 hours) │
└─────────────────────────────────────┘
  ├─ Task 1.1.1: Init pyproject.toml
  ├─ Task 1.1.2: Create package structure
  ├─ Task 1.1.4: Add .gitignore
  ├─ Task 1.2.3: Add dev dependencies
  └─ Task 1.3.1: Configure Ruff
  ↓
┌─────────────────────────────────────┐
│ Phase 2: API Setup (3-4 hours)     │
└─────────────────────────────────────┘
  ├─ Task 2.2.1: Create FastAPI app
  └─ Task 2.2.2: Upload endpoint
  ↓
┌─────────────────────────────────────┐
│ Phase 3: PDF Parsing (4-5 hours)   │
└─────────────────────────────────────┘
  ├─ Task 3.1.1: Evaluate PDF libraries
  ├─ Task 3.1.2: Implement extraction
  ├─ Task 3.2.1: Define JSON schema
  └─ Task 3.2.2: Create Pydantic models
  ↓
┌─────────────────────────────────────┐
│ Phase 4: LLM Integration (5-6 hrs) │
└─────────────────────────────────────┘
  ├─ Task 3.3.1: Setup OpenAI client
  ├─ Task 3.3.2: Structured output
  └─ Task 3.3.3: Prompt templates
  ↓
┌─────────────────────────────────────┐
│ Phase 5: FHIR Gen (6-8 hours)      │
└─────────────────────────────────────┘
  ├─ Task 5.1.1: Add fhir.resources
  ├─ Task 5.1.2: Build resource builders
  ├─ Task 5.2.1: Create Observations
  ├─ Task 5.2.2: Map values/units
  ├─ Task 5.5.1: Create Bundle
  └─ Task 5.5.2: Include resources
  ↓
END - Working MVP! 🎉
```

**Total Estimated Time**: 20-26 hours of focused development

---

## 📋 Task Prioritization

### 🔴 Critical (Do First)
These tasks block the MVP and should be completed first:

1. **Infrastructure**: 1.1.1, 1.1.2, 1.1.4, 1.2.3
2. **API**: 2.2.1, 2.2.2
3. **Parsing**: 3.1.1, 3.1.2, 3.2.1, 3.2.2
4. **LLM**: 3.3.1, 3.3.2, 3.3.3
5. **FHIR**: 5.1.1, 5.1.2, 5.2.1, 5.2.2, 5.5.1, 5.5.2

**Total**: ~18-20 tasks

### 🟡 High (Do Soon)
Post-MVP polish and essential features:

- Testing infrastructure (F1.4)
- CI/CD setup (F1.5)
- Database storage (F2.1)
- Document management (F2.3)
- Normalization features (F4.1-F4.3)
- FHIR server integration (F6.1-F6.3)

### 🟢 Medium/Low (Do Later)
Nice-to-have features and optimizations:

- Documentation (F1.6)
- Multi-patient support (F2.4)
- Quality assurance (F3.5)
- Advanced FHIR features (F5.3, F5.4, F5.6)
- Status tracking (F6.4)

---

## 🏷️ Label System

### By Type
```
🎯 epic       - High-level initiative
✨ feature    - User-facing capability  
🔧 task       - Implementation work
🐛 bug        - Something broken
⚡ enhancement - Improvement
```

### By Component
```
🛠️ infrastructure  - Dev environment, CI/CD
📄 ingestion       - PDF upload and storage
🤖 parsing         - LLM and text extraction
🧹 normalization   - Data cleaning
🏥 fhir            - FHIR resource generation
🔗 integration     - FHIR server interaction
```

### By Priority
```
🔴 critical  - Blocking MVP
🟡 high      - Important for MVP
🟢 medium    - Post-MVP polish
⚪ low       - Nice to have
```

### By Status
```
📋 backlog      - Not started
✅ ready        - Ready to work
🏃 in-progress  - Active work
👀 review       - Needs review
❌ blocked      - Waiting
✔️ done         - Complete
```

---

## 🔄 Kanban Workflow

```
┌─────────┐   ┌───────┐   ┌─────────┐   ┌────────┐   ┌──────┐
│ Backlog │──▶│ Ready │──▶│   In    │──▶│ Review │──▶│ Done │
│         │   │       │   │Progress │   │        │   │      │
└─────────┘   └───────┘   └─────────┘   └────────┘   └──────┘
  All tasks    Ready to    Active work   PR open    Merged &
  not ready     start      (1-3 items)   & testing  deployed
```

### Rules
1. **WIP Limit**: Max 2-3 items in "In Progress"
2. **Pull System**: Take from "Ready" when capacity available
3. **Priority First**: Always work highest priority ready item
4. **Complete Before Starting**: Finish items before pulling new ones
5. **Review Before Done**: All work goes through review

---

## 🚀 Getting Started Quick Reference

### For First-Time Setup
```bash
# 1. Open in Codespaces or clone locally
# 2. Run issue creation script
cd docs/planning
./github-issues.sh

# 3. Set up project board (follow project-board-setup.md)
# 4. Start coding!
```

### For Daily Development
```bash
# 1. Pull latest
git pull origin main

# 2. Check project board for highest priority "Ready" task

# 3. Create branch
git checkout -b feature/task-description

# 4. Code with Copilot
# 5. Test frequently: make test
# 6. Commit & push
# 7. Create PR
```

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| `project-breakdown.md` | Complete task breakdown (master reference) |
| `github-issues.sh` | Script to create all GitHub issues |
| `project-board-setup.md` | Guide to set up project board |
| `python-structure.md` | Python project structure & templates |
| `README.md` | Planning docs overview |
| `/docs/GETTING_STARTED.md` | Step-by-step developer guide |
| `/docs/project-brief.md` | Original project vision |

---

## 🎓 Key Principles

1. **MVP First**: Get end-to-end working, then iterate
2. **Small Tasks**: Break work into <4 hour chunks
3. **Test Early**: Write tests alongside code
4. **Copilot Assisted**: Use AI to accelerate development
5. **Documentation**: Keep docs updated as you go
6. **Code Quality**: Lint and type-check everything
7. **Iterative**: Continuous improvement over perfection

---

**Status**: ✅ Planning Complete  
**Next Action**: Run `./github-issues.sh` to create issues  
**Start Coding**: Task 1.1.1 - Initialize Python project

---

*Generated: 2026-02-14*  
*Last Updated: 2026-02-14*
