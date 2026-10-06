---
description: 'Track and append conversation history, prompts, and decisions to a chat-history folder in the codebase'
agent: 'agent'
---

# Chat History Tracker

## Mission

Maintain a running log of all conversations, prompts, decisions, and work performed in a `chat-history/` folder within the codebase. This creates a persistent record of what was discussed, what was done, and what decisions were made.

## Scope & Preconditions

- You must first understand the full codebase before logging anything
- The `chat-history/` folder is created at the project root if it does not exist
- Each session gets its own timestamped log file
- Logs capture: prompts given, actions taken, decisions made, files changed
- This is an ongoing task. Append new conversations to the existing log or create a new file per session

## Workflow

### Step 1: Setup

1. Check if `chat-history/` folder exists in the project root
2. If not, create it
3. Create a new log file named `YYYY-MM-DD-session.md` (use today's date)
4. If a log for today already exists, append to it instead of creating a new one

### Step 2: Understand the Codebase

1. Scan the full project structure
2. Read key files to understand the architecture, features, and current state
3. Note this understanding in the session log under a "Context" section

### Step 3: Log the Conversation

For each interaction in the session, append:

```markdown
## [HH:MM] Topic/Action

**Prompt**: What the user asked or instructed
**Action**: What was done in response
**Files Changed**: List of files created, modified, or deleted
**Decisions**: Any architectural or design decisions made
**Notes**: Relevant context or follow-up items
```

### Step 4: Maintain Continuously

- After every significant action, append the details to the current session log
- At the end of a session, add a "Summary" section with key outcomes
- Keep logs concise but complete enough to understand what happened without re-reading the full conversation

## Output Expectations

- `chat-history/` folder exists with timestamped session logs
- Each log file captures prompts, actions, file changes, and decisions
- Logs are written in clean Markdown, easy to scan
- New conversations are appended, not overwritten

## Quality Assurance

- [ ] chat-history/ folder exists at project root
- [ ] Log file uses correct date-based naming
- [ ] Every significant action is recorded
- [ ] File changes are listed accurately
- [ ] Decisions and reasoning are captured
