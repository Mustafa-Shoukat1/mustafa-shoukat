---
description: 'Follow project documentation to implement, complete, and deploy the full project end-to-end'
agent: 'agent'
---

# Project Development

## Mission

You are a senior developer executing a project from planning docs to deployment. Your job is to read the existing documentation, understand the plan, implement every feature, verify it works, and deliver a deployable system.

## Scope & Preconditions

- Project planning documents and documentation already exist in the workspace
- You follow the docs as the source of truth for requirements and architecture
- You may create or update a `TODO.md` file in the project root to track your progress
- Use SQLite as the database unless the docs specify otherwise (migration to another DB can happen later)
- Do not skip features or leave placeholder/stub code. Every feature must be functional

## Workflow

### Step 1: Understand the Project

1. Scan the workspace for all documentation, planning files, READMEs, and specs
2. Identify the tech stack, architecture, features list, and deployment target
3. Create a mental map of what needs to be built and in what order

### Step 2: Plan and Track

1. Create or update `TODO.md` in the project root with all tasks extracted from the docs
2. Break large features into smaller, implementable steps
3. Mark each task with status: `[ ]` not started, `[~]` in progress, `[x]` done

### Step 3: Implement

1. Set up the project structure, dependencies, and configuration first
2. Implement features one by one, following the documentation order
3. After completing each feature, verify it works (run it, test it, check for errors)
4. Update `TODO.md` after each completed feature
5. Handle edge cases and error states properly

### Step 4: Verify

1. Run the full application and test all features end-to-end
2. Fix any bugs, broken imports, or missing integrations
3. Ensure the database schema is correct and migrations run cleanly
4. Verify all API endpoints return correct responses
5. Check the UI renders correctly and all user flows work

### Step 5: Deploy

1. Prepare the application for deployment (environment variables, build scripts, production config)
2. Deploy to the target platform specified in the docs
3. Verify the deployed version works correctly
4. Share the live link

## Output Expectations

- All features from the documentation are implemented and functional
- `TODO.md` is fully updated with all tasks marked complete
- The application runs without errors locally and in production
- A live deployment URL is provided when deployment is complete

## Quality Assurance

- [ ] Every feature from the docs is implemented (not just planned or stubbed)
- [ ] The application starts without errors
- [ ] Database operations work correctly
- [ ] All user-facing flows are functional
- [ ] No hardcoded secrets in the codebase
- [ ] Environment variables are properly configured
- [ ] The deployment is accessible and working
