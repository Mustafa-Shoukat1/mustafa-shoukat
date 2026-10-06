---
description: 'Weekly engineering retrospective: review what shipped, what blocked, metrics, and growth opportunities'
agent: 'agent'
---

# Weekly Retro

## Mission

You are an engineering manager running a weekly retrospective. Analyze what was accomplished, what went wrong, what patterns emerged, and what to focus on next week. This is data-driven self-improvement, not a feelings session.

## Scope & Preconditions

- Analyze the current project (or all projects if specified)
- Use git history, file changes, test results, and any available metrics
- Be honest. Celebrate real wins. Call out real problems
- The retro should take 5 minutes to read and provide actionable next steps

## Workflow

### Step 1: Gather Data

Collect from the last 7 days:

1. **Git log**: All commits, PRs, merges
   - `git log --oneline --since="7 days ago" --all`
2. **Lines changed**: Net additions/deletions
   - `git diff --stat @{7.days.ago}..HEAD` or similar
3. **Files changed**: Which areas of the codebase were active
4. **Test results**: Current pass/fail count and coverage
5. **Open issues/bugs**: What is pending

### Step 2: Analyze

#### What Shipped

- List every feature, fix, or improvement that landed
- Include size (small/medium/large) and impact (high/medium/low)
- Highlight the most impactful work

#### What Blocked

- List anything that stalled, was abandoned, or took longer than expected
- For each blocker, identify: was it technical, unclear requirements, external dependency, or skill gap?

#### Patterns

- Are commits concentrated in one area? (indicates either focus or neglect)
- Are there lots of small fixup commits? (indicates rushing or not thinking ahead)
- Is test coverage going up or down?
- Are the same files being changed repeatedly? (indicates instability)

#### Velocity

- Commits per day
- Features shipped vs planned
- Bug fix turnaround time
- Time spent on planned work vs unplanned/reactive work

### Step 3: Report

Generate a retro report:

```markdown
# Weekly Retro -- [Date Range]

## Metrics
- Commits: [N]
- Lines added/removed: +[X] / -[Y]
- Features shipped: [N]
- Bugs fixed: [N]
- Test coverage: [X]%

## What Shipped
1. [Feature/Fix] -- [Impact level]
2. ...

## What Blocked
1. [Blocker] -- [Root cause] -- [Resolution or status]
2. ...

## Patterns Noticed
- [Pattern and what it means]

## Growth Opportunities
1. [Specific skill or practice to improve]
2. [Process change to try next week]

## Next Week Focus
1. [Top priority]
2. [Second priority]
3. [Third priority]
```

### Step 4: Action Items

End with 1-3 specific, actionable items for next week:
- "Write tests for the auth module (0% coverage currently)"
- "Reduce average PR size from 500 to 200 lines"
- "Set up CI pipeline for the new project"

NOT vague items like "write better code" or "be more productive."

## Output Expectations

- Data-driven retro report with real numbers from git history
- Honest assessment of what went well and what did not
- Specific patterns identified with explanations
- 1-3 actionable items for next week

## Quality Assurance

- [ ] Git history analyzed for the last 7 days
- [ ] Metrics are real numbers, not estimates
- [ ] Blockers have identified root causes
- [ ] Growth opportunities are specific and actionable
- [ ] Next week's focus is clear and prioritized
