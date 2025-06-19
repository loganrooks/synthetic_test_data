# Context Sync Command

Analyze the current codebase and update all context files (CLAUDE.md, PROJECT_STATUS.md, ARCHITECTURE.md, etc.) to reflect the actual state of the project.

## SPARC Phase 1: Specification - Analyze Current State

First, understand what needs syncing:
- Analyze current codebase structure and patterns
- Read all existing context files to identify gaps
- Check git history for recent changes not reflected in docs
- Identify new technologies, dependencies, or patterns in use
- Review recent logs for decisions not yet documented

Context files to analyze and update:
- CLAUDE.md - Current directives and rules
- PROJECT_STATUS.md - Actual project progress
- ARCHITECTURE.md - Current system design
- DEVELOPMENT_GUIDE.md - Patterns and practices in use
- CHANGELOG.md - Recent changes
- All logs for patterns and decisions

## SPARC Phase 2: Plan - Create Sync Strategy

### 2.1 Codebase Analysis Plan
1. Scan for technology stack changes
2. Identify architectural patterns in use
3. Detect testing methodologies actually employed
4. Find workflow patterns from git history
5. Extract coding standards from actual code

### 2.2 Update Priority
1. PROJECT_STATUS.md - Most likely to be stale
2. ARCHITECTURE.md - May not reflect refactoring
3. CLAUDE.md - Update directives based on learnings
4. DEVELOPMENT_GUIDE.md - Capture new patterns
5. Other context files as needed

## SPARC Phase 3: Architecture - Deep System Analysis

### 3.1 Technology Stack Discovery
```bash
# Detect package managers and dependencies
find . -name "package.json" -o -name "requirements.txt" -o -name "go.mod" -o -name "Cargo.toml" | head -5

# Analyze main languages
find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.go" \) | head -20

# Check for framework-specific files
find . -name "next.config.js" -o -name "vue.config.js" -o -name "angular.json" -o -name "django-admin.py"
```

### 3.2 Architecture Pattern Detection
Analyze directory structure to infer architecture:
- Look for MVC patterns (models/, views/, controllers/)
- Check for layered architecture (domain/, infrastructure/, application/)
- Identify microservices (separate service directories)
- Detect frontend/backend separation

### 3.3 Testing Methodology Detection
```bash
# Find test files and frameworks
find . -name "*test*" -o -name "*spec*" | grep -E "\.(js|ts|py|go)$" | head -10

# Check for TDD evidence (tests alongside source)
# Check for BDD evidence (feature files)
# Identify test coverage tools
```

## SPARC Phase 4: Refine - Update Context Files

### 4.1 Update PROJECT_STATUS.md

Analyze and update based on:
```bash
# Recent commits to understand progress
git log --oneline -20

# Open issues and PRs
gh issue list --limit 10
gh pr list --limit 10

# Recent feature branches
git branch -r | grep feature/ | tail -10

# TODO comments in code
grep -r "TODO\|FIXME\|HACK" --include="*.js" --include="*.ts" --include="*.py" . | wc -l
```

Generate updated content:
```markdown
# Project Status - [PROJECT_NAME]

**Current Sprint/Phase:** [Inferred from recent branches/commits]
**Last Updated:** $(date +%Y-%m-%d)
**Version:** [From package.json/setup.py] → [Next version] (in progress)

## Active Development

### Recently Completed (last 2 weeks)
[Analyze git log for completed features]

### In Progress
[Based on open PRs and recent commits]

### Upcoming
[Based on TODO comments and issues]

## Technical Health
- Test Coverage: [Run coverage command]
- Build Status: [Check CI status]
- Open Issues: [Count]
- Technical Debt Items: [TODO/FIXME count]

## Team Activity
- Active Contributors: [git shortlog -sn --since=2.weeks]
- Recent PRs: [List]
```

### 4.2 Update ARCHITECTURE.md

Analyze actual code structure:
```bash
# Generate directory tree
tree -d -L 3 -I 'node_modules|__pycache__|.git'

# Find main entry points
find . -name "index.js" -o -name "main.py" -o -name "app.js" -o -name "main.go"

# Detect design patterns in code
# - Singleton patterns
# - Factory patterns
# - Repository patterns
# - Service layers
```

Update architecture documentation to reflect:
- Actual directory structure
- Real component relationships
- Current design patterns
- Active integrations
- Data flow patterns observed

### 4.3 Update CLAUDE.md

Based on patterns found in logs and code:
```bash
# Analyze FEEDBACK_LOG.md for recurring issues
grep -E "ERROR|ISSUE|PROBLEM" logs/FEEDBACK_LOG.md | tail -20

# Check SELF_ANALYSIS_LOG.md for patterns
grep -E "Pattern|Lesson|Should" logs/SELF_ANALYSIS_LOG.md | tail -20

# Find workflow decisions in git commits
git log --grep="workflow\|process\|decision" --oneline | tail -10
```

Update CLAUDE.md with:
- New verification requirements discovered
- Updated workflow decisions
- Technology-specific guidelines found
- Testing requirements actually in use
- Context initialization triggers identified

### 4.4 Update DEVELOPMENT_GUIDE.md

Extract actual practices from code:
```bash
# Analyze commit message patterns
git log --pretty=format:"%s" -50 | grep -E "^(feat|fix|docs|style|refactor|test|chore)"

# Find coding patterns
# - Naming conventions in use
# - File organization patterns
# - Import structures
# - Error handling patterns
```

## SPARC Phase 5: Complete - Validate Updates

### 5.1 Cross-Reference Validation
Ensure all context files are consistent:
- Technology stack mentioned consistently
- Architecture patterns align
- Testing methodology matches across files
- No contradicting instructions

### 5.2 Fill Template Variables
Replace all placeholder variables with actual values:
```bash
# Find remaining template variables
grep -r "{{.*}}" docs/ *.md | grep -v node_modules

# Common replacements:
# {{PROJECT_NAME}} -> Actual project name
# {{TESTING_METHODOLOGY}} -> TDD/BDD/etc
# {{ARCHITECTURE_PATTERN}} -> MVC/Microservices/etc
# {{MAIN_BRANCH}} -> main/master
# {{PACKAGE_MANAGER}} -> npm/yarn/pip/etc
```

### 5.3 Commit Context Updates
```bash
git checkout develop
git checkout -b feature/context-sync-$(date +%Y%m%d)

# Commit each context file separately
git add PROJECT_STATUS.md
git commit -m "docs: Sync PROJECT_STATUS.md with current development

- Updated active development based on recent commits
- Reflected actual test coverage and build status
- Added current technical debt metrics"

git add docs/ARCHITECTURE.md
git commit -m "docs: Update ARCHITECTURE.md to reflect current structure

- Aligned with actual directory structure
- Documented discovered design patterns
- Updated component relationships"

git add CLAUDE.md
git commit -m "docs: Update CLAUDE.md with discovered patterns

- Added verification requirements from FEEDBACK_LOG
- Updated context initialization triggers
- Included new workflow decisions"
```

## SPARC Phase 6: Verify - Ensure Accuracy

Run verification checks:
```bash
# Verify all mentioned files exist
grep -h "\.md\|\.js\|\.py" *.md docs/*.md | grep -oE "[a-zA-Z0-9_/-]+\.[a-zA-Z]+" | while read file; do
  [ -f "$file" ] || echo "Missing referenced file: $file"
done

# Check for outdated information
# - Version numbers match package files
# - Directory structures are current
# - Commands actually work
```

## SPARC Phases 7-9: L³ - Log, Learn, Level Up

### Update ACTIVITY_LOG.md
Record context sync details:
- Files analyzed
- Patterns discovered
- Updates made
- Inconsistencies resolved

### Update FEEDBACK_LOG.md
Document sync challenges:
- Information that was hard to extract
- Patterns that weren't clear
- Areas needing manual review

### Update SELF_ANALYSIS_LOG.md
Analyze the sync process:
- How out of sync were the files?
- What caused the drift?
- How can we keep them synced?
- Should this run automatically?

## Success Criteria

Context sync is complete when:
- ✓ All context files reflect actual state
- ✓ No template variables remain
- ✓ Cross-references are valid
- ✓ Instructions match actual workflows
- ✓ Architecture diagrams match code
- ✓ Status reflects current progress
- ✓ All patterns are documented

## Automation Suggestions

Consider setting up:
1. Weekly context sync runs
2. Pre-commit hooks to update status
3. CI job to verify context accuracy
4. Automated architecture diagram generation
5. Status dashboard generation

$ARGUMENTS