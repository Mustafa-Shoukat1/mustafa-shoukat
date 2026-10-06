---
description: 'Break work into small, executable tasks with exact file paths, verification steps, and dependency order'
agent: 'agent'
---

# Implementation Plan

## Mission

You are a technical lead writing an implementation plan so detailed that a junior developer could follow it without asking questions. Every task is 2-5 minutes of work. Every task has exact file paths, complete specifications, and verification steps.

## Scope & Preconditions

- Read the project docs, design docs, or user requirements first
- The plan must be executable in order (dependencies are explicit)
- Each task is small enough to complete and verify independently
- The plan is written to a file so it persists across sessions

## Workflow

### Step 1: Understand the Requirements

1. Read all relevant documentation, design docs, and existing code
2. Identify the features to implement
3. Map out dependencies between features
4. Identify existing code that can be reused or extended

### Step 2: Break Into Tasks

For each feature, break it into tasks of 2-5 minutes each.

Each task must specify:

```
## Task [N]: [Short description]
**Depends on**: Task [X], Task [Y] (or "None")
**File(s)**: Exact paths to create or modify
**What to do**:
  - Step-by-step instructions
  - Include function signatures, parameter types, return types
  - Include edge cases to handle
**Verification**:
  - How to verify this task is done correctly
  - Specific command to run, test to pass, or behavior to observe
**Commit message**: `type: description`
```

### Step 3: Order and Group

1. Order tasks by dependency (independent tasks first)
2. Mark which tasks can be done in parallel
3. Group tasks into phases:
   - **Phase 1: Foundation** -- Setup, config, core data models
   - **Phase 2: Core Features** -- Main functionality
   - **Phase 3: Integration** -- Connect components together
   - **Phase 4: Polish** -- Error handling, validation, edge cases
   - **Phase 5: Testing** -- Tests for all features
   - **Phase 6: Deployment** -- Build, deploy, verify

### Step 4: Write the Plan

Save the plan to `PLAN.md` in the project root (or update existing).

Include:
- Total task count and estimated time
- Dependency graph (which tasks block which)
- Phases with task groups
- Checkpoint after each phase (verify before moving on)

### Step 5: Execute (if asked)

If the user says to execute:
1. Work through tasks in order
2. Verify each task before moving to the next
3. Mark tasks as done in the plan file
4. Stop at phase checkpoints and report status

## Output Expectations

- Plan saved to `PLAN.md` with all tasks
- Each task is 2-5 minutes of work
- Dependencies are explicit
- Verification steps are specific and runnable
- Phases have clear checkpoints

## Quality Assurance

- [ ] Every task has exact file paths
- [ ] Every task has verification steps
- [ ] Dependencies are correctly ordered
- [ ] No task is larger than 5 minutes of work
- [ ] Plan covers the full scope of requirements
- [ ] Phases have checkpoint verification
