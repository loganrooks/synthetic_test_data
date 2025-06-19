# Workspace Maintenance Command

Execute comprehensive workspace organization and git debt resolution following the SPARC-V-L³ protocol.

## SPARC Phase 1: Specification - Analyze Current State

First, read and understand the workspace organization rules:
- Read CLAUDE.md for workspace-specific rules and current directives
- Read docs/DEVELOPMENT_GUIDE.md for general organization guidelines
- Read PROJECT_STATUS.md to understand current project state

Then analyze the current workspace:
- List all markdown files to identify misplaced documentation
- Check git status to identify uncommitted changes (git debt)
- Identify current branch and branching strategy
- Find potential duplicate files (patterns like .copy, .backup, .old, -v1, etc.)
- Locate outdated documents that should be archived

## SPARC Phase 2: Plan - Create Organization Strategy

Based on the analysis, create a detailed plan that includes:
1. Files to be moved to their proper directories
2. Duplicates to be verified and handled
3. Outdated documents to be archived
4. System logs that need updating
5. Git changes to be organized into logical commits

## SPARC Phase 3: Architecture - Ensure Proper Structure

Verify and create the standard directory structure:
```bash
mkdir -p docs/{decisions,analysis,planning}
mkdir -p archive/$(date +%Y-%m)
mkdir -p logs
mkdir -p src
mkdir -p tests
mkdir -p scripts
```

Check if ARCHITECTURE.md needs updates based on planned file movements.

## SPARC Phase 4: Refine - Execute Organization

### 4.1 Organize Documentation Files

Move files to appropriate locations based on type:
- **Root directory**: Keep only README.md, CLAUDE.md, PROJECT_STATUS.md, CHANGELOG.md, LICENSE.md
- **logs/**: Move all *_LOG.md files (ACTIVITY_LOG.md, FEEDBACK_LOG.md, SELF_ANALYSIS_LOG.md)
- **docs/**: Move ARCHITECTURE.md, *_GUIDE.md, *_PLAN.md, and other documentation
- **archive/**: Move outdated or obsolete files with timestamp

### 4.2 Handle Duplicates Safely

For each potential duplicate:
1. Compare file contents using `diff`
2. If identical: Remove the duplicate
3. If different: Archive the older/backup version
4. Always verify content before any deletion

### 4.3 Archive Outdated Documents

Move to timestamped archive folder:
- Planning documents older than 90 days
- Files containing "obsolete" or "deprecated" in name
- Old versions of current documents

### 4.4 Update System Logs

Update ACTIVITY_LOG.md with detailed maintenance record including:
- Timestamp
- Files moved/deleted/archived
- Rationale for each action
- Result of operations

## SPARC Phase 5: Complete - Resolve Git Debt

### 5.1 Analyze Uncommitted Changes

Group changes by logical feature/category:
- Documentation updates (docs/, *.md files)
- Source code changes (src/)
- Test updates (tests/)
- Configuration changes
- Miscellaneous updates

### 5.2 Create Feature Branches and Commit

For each logical group of changes:
1. Ensure we're on develop branch
2. Create dated feature branch: `feature/{category}-updates-{date}`
3. Stage relevant files
4. Commit with conventional commit message format
5. Return to develop branch

Example workflow:
```bash
# Start from develop
git checkout develop || git checkout -b develop

# Documentation changes
git checkout -b feature/doc-updates-$(date +%Y%m%d)
git add docs/*.md logs/*.md *.md
git commit -m "docs: Update documentation and logs

- Reorganized documentation structure
- Updated system logs with maintenance records
- Archived outdated planning documents"

# Return to develop
git checkout develop
```

### 5.3 Merge to Develop

Merge all feature branches to develop (no PR needed for feature→develop):
```bash
git merge --no-ff feature/doc-updates-$(date +%Y%m%d) -m "Merge feature/doc-updates to develop"
```

Note: PRs are only required for develop→main (deployment branch).

## SPARC Phase 6: Verify - Confirm Success

Generate verification report showing:
- Updated directory structure
- Git status (should show no uncommitted changes)
- Current branch (should be develop)
- Recent commits
- Summary of all changes made

## SPARC Phases 7-9: L³ - Log, Learn, Level Up

### Update FEEDBACK_LOG.md
Record any issues encountered, deviations from plan, or lessons learned.

### Update SELF_ANALYSIS_LOG.md
Analyze the maintenance process:
- What patterns were observed?
- What could be improved?
- What systematic issues were identified?

### Update DEVELOPMENT_GUIDE.md (if needed)
If any systemic lessons were learned that should change future maintenance procedures.

## Final Summary

Display a comprehensive summary showing:
- Number of files organized
- Duplicates handled
- Documents archived
- Git commits created
- System logs updated
- Any issues that require manual intervention

Remember to follow all workspace-specific rules from CLAUDE.md and handle all files with care, always verifying before deletion or major changes.

$ARGUMENTS