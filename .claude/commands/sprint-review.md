# Sprint Review Command

Conduct a comprehensive sprint/iteration review following SPARC-V-L³ protocol, updating all documentation, capturing learnings, and preparing for the next iteration.

## SPARC Phase 1: Specification - Define Review Scope

Sprint review encompasses:
1. **Deliverables**: What was completed vs planned
2. **Metrics**: Velocity, quality, performance
3. **Learnings**: What worked, what didn't
4. **Team Health**: Morale, collaboration, blockers
5. **Technical Debt**: Added vs addressed
6. **Next Sprint**: Planning and preparation

Time period to analyze:
- Default: Last 2 weeks
- Configurable: Via $ARGUMENTS (e.g., "1-week" or "2025-03-01:2025-03-14")

## SPARC Phase 2: Plan - Review Strategy

### 2.1 Data Collection
- Git commits and PR merges
- Issue/ticket completion
- Test results and coverage
- Performance metrics
- Team feedback

### 2.2 Analysis Approach
- Quantitative: Numbers and metrics
- Qualitative: Patterns and feedback
- Comparative: vs previous sprints
- Predictive: Trends and forecasts

### 2.3 Documentation Updates
- CHANGELOG.md: User-facing changes
- PROJECT_STATUS.md: Progress update
- FEEDBACK_LOG.md: Sprint learnings
- Team retrospective notes

## SPARC Phase 3: Architecture - Gather Sprint Data

### 3.1 Development Metrics
```bash
echo "📊 Gathering sprint metrics..."

# Define sprint period (last 2 weeks by default)
SPRINT_START=$(date -d "2 weeks ago" +%Y-%m-%d)
SPRINT_END=$(date +%Y-%m-%d)

echo "Sprint Period: $SPRINT_START to $SPRINT_END"

# Commit statistics
echo -e "\n📈 Development Activity:"
TOTAL_COMMITS=$(git log --since="$SPRINT_START" --until="$SPRINT_END" --oneline | wc -l)
echo "Total commits: $TOTAL_COMMITS"

# Contributor statistics
echo -e "\n👥 Team Contributions:"
git shortlog -sn --since="$SPRINT_START" --until="$SPRINT_END"

# Feature vs fix ratio
echo -e "\n🔧 Work Type Distribution:"
git log --since="$SPRINT_START" --until="$SPRINT_END" --pretty=format:"%s" |
  grep -oE "^(feat|fix|docs|test|refactor|chore)" |
  sort | uniq -c | sort -nr

# Files changed
echo -e "\n📝 Files Modified:"
git log --since="$SPRINT_START" --until="$SPRINT_END" --name-only --pretty=format: |
  sort | uniq -c | sort -nr | head -20
```

### 3.2 Issue/Ticket Analysis
```bash
echo -e "\n🎯 Issue Tracking Analysis..."

if command -v gh &> /dev/null; then
  # Closed issues
  echo "Issues closed this sprint:"
  gh issue list --state closed --limit 100 --json number,title,closedAt |
    jq --arg start "$SPRINT_START" --arg end "$SPRINT_END" \
    '.[] | select(.closedAt >= $start and .closedAt <= $end) | "\(.number): \(.title)"'
  
  # Created vs closed
  CREATED=$(gh issue list --limit 100 --json createdAt |
    jq --arg start "$SPRINT_START" --arg end "$SPRINT_END" \
    '[.[] | select(.createdAt >= $start and .createdAt <= $end)] | length')
  
  CLOSED=$(gh issue list --state closed --limit 100 --json closedAt |
    jq --arg start "$SPRINT_START" --arg end "$SPRINT_END" \
    '[.[] | select(.closedAt >= $start and .closedAt <= $end)] | length')
  
  echo -e "\nIssue Flow:"
  echo "Created: $CREATED"
  echo "Closed: $CLOSED"
  echo "Net change: $((CREATED - CLOSED))"
fi
```

### 3.3 Quality Metrics
```bash
echo -e "\n✅ Quality Metrics..."

# Test results
if [ -f "package.json" ] && grep -q '"test"' package.json; then
  echo "Running test coverage analysis..."
  npm test -- --coverage --silent 2>/dev/null || echo "Tests not available"
fi

# Code quality trends
echo -e "\nCode quality indicators:"
# Count of TODO/FIXME
TODO_COUNT=$(grep -r "TODO\|FIXME" --include="*.js" --include="*.ts" --include="*.py" . 2>/dev/null | wc -l)
echo "Technical debt markers (TODO/FIXME): $TODO_COUNT"

# Linting issues
if [ -f "package.json" ] && grep -q '"lint"' package.json; then
  LINT_ISSUES=$(npm run lint 2>&1 | grep -c "error\|warning" || echo "0")
  echo "Linting issues: $LINT_ISSUES"
fi
```

## SPARC Phase 4: Refine - Generate Review

### 4.1 Create Sprint Summary
Generate `docs/planning/sprint-review-$(date +%Y%m%d).md`:
```markdown
# Sprint Review: $(date +%Y-%m-%d)

**Sprint Period:** $SPRINT_START to $SPRINT_END
**Team Size:** [Active contributors count]
**Sprint Goal:** [From PROJECT_STATUS.md or manual input]

## 📊 Sprint Metrics

### Velocity
- **Commits:** $TOTAL_COMMITS
- **Issues Closed:** $CLOSED
- **PRs Merged:** [Count]
- **Story Points:** [If tracked]

### Quality
- **Test Coverage:** [X]%
- **Build Success Rate:** [X]%
- **Bug Fix Rate:** [fixes/total commits]
- **Technical Debt:** $TODO_COUNT markers

### Work Distribution
- Features: [X]%
- Bug Fixes: [X]%
- Documentation: [X]%
- Refactoring: [X]%
- Other: [X]%

## ✅ Completed Work

### Major Features
1. **[Feature Name]** (#[Issue])
   - Description: [What was delivered]
   - Impact: [User value]
   - Contributors: [Who worked on it]

### Bug Fixes
1. **[Bug Description]** (#[Issue])
   - Root cause: [Brief explanation]
   - Solution: [How fixed]

### Improvements
1. **[Improvement]**
   - Before: [Previous state]
   - After: [Current state]
   - Benefit: [Why it matters]

## 📚 Key Learnings

### What Went Well
- [Success 1]
- [Success 2]
- [Success 3]

### Challenges Faced
- [Challenge 1]: [How addressed]
- [Challenge 2]: [How addressed]

### Process Improvements
- [Improvement 1]
- [Improvement 2]

## 🔄 Carryover Items

### Incomplete Tasks
1. **[Task]** - [X]% complete
   - Blocker: [If any]
   - Plan: [Next steps]

### Technical Debt
1. **[Debt Item]**
   - Impact: [High/Medium/Low]
   - Effort: [Estimate]
   - Priority: [When to address]

## 👥 Team Health

### Highlights
- [Positive team dynamic]
- [Good collaboration example]

### Concerns
- [Any team issues]
- [Resource constraints]

## 📈 Trends

### Positive Trends
- [Metric] improving by [X]%
- [Area] showing consistency

### Concerning Trends
- [Metric] declining
- [Area] needs attention

## 🎯 Next Sprint Planning

### Priorities
1. [Top priority]
2. [Second priority]
3. [Third priority]

### Capacity Planning
- Team availability: [Any planned absences]
- External dependencies: [Any blockers]

### Goals
- Velocity target: [Based on average]
- Quality target: [Specific metrics]
- Delivery target: [What to ship]
```

### 4.2 Update CHANGELOG.md
Add sprint deliverables:
```markdown
## [Version] - $(date +%Y-%m-%d)

### Added
- [New features from sprint]

### Changed
- [Modifications and improvements]

### Fixed
- [Bug fixes]

### Security
- [Security updates if any]

### Deprecated
- [Features being phased out]

### Removed
- [Deleted features/code]
```

### 4.3 Update PROJECT_STATUS.md
Reflect current state:
```markdown
# Project Status - [PROJECT_NAME]

**Last Sprint:** $SPRINT_START to $SPRINT_END
**Sprint Velocity:** $TOTAL_COMMITS commits, $CLOSED issues closed
**Next Sprint Starts:** $(date -d "monday" +%Y-%m-%d)

## Current Focus
[Updated based on sprint results and next priorities]

## Recent Achievements ✅
[List completed items from sprint]

## In Progress 🚧
[List carried over items]

## Upcoming 📅
[List next sprint priorities]

## Health Indicators
- Build: [Status]
- Tests: [Coverage]%
- Team: [Morale indicator]
- Technical Debt: [Trend]
```

## SPARC Phase 5: Complete - Team Retrospective

### 5.1 Generate Retrospective Template
Create `docs/planning/retro-$(date +%Y%m%d).md`:
```markdown
# Sprint Retrospective

**Date:** $(date)
**Participants:** [Team members]
**Facilitator:** [Name]

## 🌟 What Went Well
- [Team member 1]: [Positive feedback]
- [Team member 2]: [Success story]
- [Process]: [What worked]

## 😟 What Could Be Improved
- [Pain point 1]
- [Process friction]
- [Communication issue]

## 💡 Ideas and Experiments
- [Idea 1]: Try for next sprint
- [Tool/Process 2]: Research this week
- [Practice 3]: Implement gradually

## 🎬 Action Items
- [ ] [Specific action] - Owner: [Name] - Due: [Date]
- [ ] [Process change] - Owner: [Team] - Due: [Next sprint]
- [ ] [Investigation] - Owner: [Name] - Due: [Date]

## 📏 Measurements
How will we know if improvements work?
- [Metric 1]: Target [X]
- [Metric 2]: Improve by [Y]%
```

### 5.2 Communication Summary
Generate stakeholder update:
```markdown
# Sprint Summary for Stakeholders

**Sprint Dates:** $SPRINT_START to $SPRINT_END

## 🎯 Sprint Goal Achievement
[Was the sprint goal met? Percentage complete]

## 🚀 Key Deliverables
- [User-facing feature 1]
- [User-facing feature 2]
- [Major fix or improvement]

## 📊 By The Numbers
- Features Delivered: [X]
- Bugs Fixed: [Y]
- Team Velocity: [Trending up/stable/down]

## 🔮 Next Sprint Preview
[What stakeholders can expect next]

## 🤝 Dependencies
Need from stakeholders:
- [Decision needed]
- [Resource required]
- [Clarification on X]
```

## SPARC Phase 6: Verify - Review Completeness

Checklist verification:
```bash
echo "✅ Sprint Review Checklist:"
echo "[ ] Git history analyzed"
echo "[ ] Metrics calculated"
echo "[ ] CHANGELOG.md updated"
echo "[ ] PROJECT_STATUS.md updated"
echo "[ ] Sprint review document created"
echo "[ ] Retrospective template ready"
echo "[ ] Stakeholder summary prepared"
echo "[ ] Next sprint priorities defined"

# Archive sprint documents
mkdir -p archive/sprints/$(date +%Y-%m)
cp docs/planning/sprint-review-*.md archive/sprints/$(date +%Y-%m)/
```

## SPARC Phases 7-9: L³ - Log, Learn, Level Up

### Update ACTIVITY_LOG.md
Record sprint review:
```markdown
## $(date "+%Y-%m-%d %H:%M:%S") - Sprint Review Completed

**Sprint Period:** $SPRINT_START to $SPRINT_END
**Key Metrics:**
- Velocity: $TOTAL_COMMITS commits
- Issues: $CLOSED closed, $CREATED created
- Quality: [Coverage]%, [Debt] items

**Major Accomplishments:**
[List top 3-5 achievements]

**Process Improvements Identified:**
[List improvements for next sprint]
```

### Update FEEDBACK_LOG.md
Capture sprint learnings:
- Process bottlenecks discovered
- Team collaboration insights
- Technical challenges faced
- Solutions that worked well

### Update SELF_ANALYSIS_LOG.md
Reflect on sprint patterns:
- Is velocity sustainable?
- Are estimates improving?
- Is technical debt managed?
- Is team morale healthy?

### Update DEVELOPMENT_GUIDE.md
If sprint revealed new best practices:
- Add successful patterns
- Update workflow documentation
- Refine estimation guidelines
- Improve team practices

## Success Indicators

Effective sprint review when:
- ✓ All work accounted for
- ✓ Metrics show trends
- ✓ Learnings captured
- ✓ Team aligned on next steps
- ✓ Stakeholders informed
- ✓ Process improvements identified
- ✓ Documentation current

## Automation Opportunities

Consider automating:
1. Metric collection scripts
2. Changelog generation
3. Status report templates
4. Velocity tracking
5. Burndown charts

$ARGUMENTS