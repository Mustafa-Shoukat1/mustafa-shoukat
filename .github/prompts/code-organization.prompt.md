---
description: 'Analyze and restructure the codebase for clean architecture, proper separation of concerns, and maintainability'
agent: 'agent'
---

# Code Organization

## Mission

Analyze the current codebase structure and reorganize it following clean architecture principles. Ensure proper separation of concerns, consistent naming conventions, logical file grouping, and clear module boundaries.

## Scope & Preconditions

- Read the entire project structure before making any changes
- Preserve all existing functionality (reorganization must not break anything)
- Follow the conventions already established in the project where they make sense
- Do not add new features or refactor business logic during reorganization

## Workflow

### Step 1: Analyze Current Structure

1. Map the full directory tree and identify all modules, components, and utilities
2. Identify violations: misplaced files, circular dependencies, mixed concerns, inconsistent naming
3. Note the tech stack to apply the right organizational patterns

### Step 2: Plan the Reorganization

1. Define the target folder structure based on the project type:
   - **Backend**: `src/` with `routes/`, `services/`, `models/`, `middleware/`, `utils/`, `config/`
   - **Frontend**: `src/` with `components/`, `pages/`, `hooks/`, `utils/`, `services/`, `types/`
   - **Full-stack**: Separate `client/` and `server/` or monorepo with `packages/`
2. List every file move with source and destination
3. Identify imports that need updating after moves

### Step 3: Execute

1. Move files to their correct locations
2. Update all import paths
3. Update configuration files (tsconfig paths, webpack aliases, etc.)
4. Rename files to follow consistent naming conventions (kebab-case, PascalCase, etc.)

### Step 4: Verify

1. Run the application and confirm it starts without errors
2. Run tests if they exist
3. Check for any broken imports or missing references

## Output Expectations

- Clean, logical folder structure matching the project type
- All imports updated correctly
- No broken functionality
- Brief summary of what was moved and why

## Quality Assurance

- [ ] Application runs without errors after reorganization
- [ ] All tests pass (if they exist)
- [ ] No circular dependencies introduced
- [ ] Naming conventions are consistent throughout
- [ ] No orphaned or duplicate files
