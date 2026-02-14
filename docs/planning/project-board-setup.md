# Lab2FHIR Project Board Configuration

This document describes how to set up the GitHub Projects V2 board for Lab2FHIR.

## Board Setup

### 1. Create a New Project (V2)

1. Go to your repository: https://github.com/benlangfeld/Lab2FHIR
2. Click "Projects" tab
3. Click "New project"
4. Select "Board" template
5. Name it "Lab2FHIR Development"

### 2. Configure Board Columns

Set up the following columns (in this order):

1. **Backlog**
   - Description: Issues not yet ready to work on
   - Automation: None

2. **Ready**
   - Description: Issues ready to be picked up
   - Automation: None

3. **In Progress**
   - Description: Currently being worked on
   - Automation: Auto-move when issue assigned

4. **Review**
   - Description: Waiting for review or testing
   - Automation: Auto-move when PR created

5. **Done**
   - Description: Completed and merged
   - Automation: Auto-move when issue closed

### 3. Add Custom Fields

Add these custom fields to track additional metadata:

#### Epic (Single Select)
- Epic 1: Infrastructure
- Epic 2: Ingestion
- Epic 3: Parsing
- Epic 4: Normalization
- Epic 5: FHIR Generation
- Epic 6: Integration

#### Priority (Single Select)
- Critical
- High
- Medium
- Low

#### Effort (Single Select)
- Small (< 2 hours)
- Medium (2-4 hours)
- Large (> 4 hours)

#### Component (Single Select)
- Infrastructure
- Ingestion
- Parsing
- Normalization
- FHIR
- Integration

#### Iteration (Text)
- MVP
- Polish
- Enhancement
- Production

### 4. Add All Issues to Project

After running `github-issues.sh`, add all created issues to the project:

```bash
# Using GitHub CLI
gh project item-add <PROJECT_NUMBER> --owner benlangfeld --url https://github.com/benlangfeld/Lab2FHIR/issues/<ISSUE_NUMBER>
```

Or use the GitHub UI:
1. Go to the project board
2. Click "+ Add item"
3. Search for and add all issues

### 5. Configure Views

Create these views for different perspectives:

#### View 1: Kanban (Default)
- Group by: Status
- Sort by: Priority (descending)
- Filter: None

#### View 2: By Epic
- Group by: Epic
- Sort by: Priority
- Filter: None

#### View 3: MVP Focus
- Group by: Status
- Sort by: Priority
- Filter: Iteration = "MVP"

#### View 4: By Component
- Group by: Component
- Sort by: Priority
- Filter: Status ≠ "Done"

### 6. Set Up Automations

Configure built-in automations:

1. **Auto-add to project**
   - Trigger: Issue created
   - Action: Add to "Backlog" column

2. **Move to In Progress**
   - Trigger: Issue assigned
   - Action: Move to "In Progress"

3. **Move to Review**
   - Trigger: PR opened that references issue
   - Action: Move to "Review"

4. **Move to Done**
   - Trigger: Issue closed
   - Action: Move to "Done"

### 7. Organize Initial Issues

After adding all issues, organize them:

1. **Backlog**: All non-MVP tasks
2. **Ready**: MVP tasks that can be started immediately:
   - Task 1.1.1: Initialize Python project with pyproject.toml
   - Task 1.1.4: Add .gitignore for Python projects
3. **In Progress**: (empty initially)
4. **Review**: (empty initially)
5. **Done**: (empty initially)

## Working with the Board

### Starting Work
1. Move issue from "Ready" to "In Progress"
2. Assign issue to yourself
3. Create a feature branch
4. Work on the issue

### Completing Work
1. Create PR that references the issue (use "Closes #123")
2. Issue automatically moves to "Review"
3. After PR is merged and issue is closed, it moves to "Done"

### Adding New Issues
1. Create issue with appropriate labels
2. It auto-adds to "Backlog"
3. Set Epic, Priority, Effort, and Component fields
4. Move to "Ready" when dependencies are met

## Kanban Workflow

Since this is a Kanban project (no milestones), use these principles:

1. **WIP Limits**: Try to limit "In Progress" to 2-3 items
2. **Pull System**: Pull from "Ready" when capacity available
3. **Continuous Flow**: No sprint boundaries
4. **Priority-Based**: Always work highest priority items first
5. **Iterative**: Focus on MVP, then iteratively polish

## MVP Priority

Focus on these features first:
- F1.1: Python Project Structure
- F1.2: Development Environment
- F2.2: PDF Upload Handler (Tasks 1-2 only)
- F3.1: PDF Text Extraction (Tasks 1-2)
- F3.2: LLM Schema Design (Tasks 1-2)
- F3.3: OpenAI Integration (Tasks 1-3)
- F5.1: FHIR Library Integration (Tasks 1-2)
- F5.2: Observation Generation (Tasks 1-2)
- F5.5: Bundle Creation (Tasks 1-2)

These will give you an end-to-end working prototype.
