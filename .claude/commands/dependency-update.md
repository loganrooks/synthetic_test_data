# Dependency Update Command

Safely update project dependencies following the SPARC-V-L³ protocol with comprehensive testing and rollback capabilities.

## SPARC Phase 1: Specification - Analyze Dependency State

First, understand the project's dependency context:
- Read CLAUDE.md for dependency management rules
- Read docs/DEVELOPMENT_GUIDE.md for version control policies
- Read package.json/requirements.txt/go.mod (based on project type)
- Check for dependency lock files (package-lock.json, yarn.lock, etc.)
- Review CHANGELOG.md for recent dependency updates

Analyze current dependencies:
- Run dependency audit for security vulnerabilities
- Check for outdated packages
- Identify deprecated dependencies
- Review breaking changes in available updates
- Check peer dependency compatibility

## SPARC Phase 2: Plan - Create Update Strategy

Create a categorized update plan:

### 2.1 Security Updates (CRITICAL)
- Dependencies with known vulnerabilities
- Must be updated immediately
- May require code changes

### 2.2 Patch Updates (SAFE)
- Bug fixes only (x.x.PATCH)
- Backward compatible
- Low risk of breaking changes

### 2.3 Minor Updates (MODERATE)
- New features (x.MINOR.x)
- Backward compatible
- Medium risk, requires testing

### 2.4 Major Updates (RISKY)
- Breaking changes (MAJOR.x.x)
- Requires code migration
- High risk, extensive testing needed

Document plan in `docs/planning/dependency-update-$(date +%Y%m%d).md`

## SPARC Phase 3: Architecture - Impact Analysis

Analyze architectural impact of updates:
- Check ARCHITECTURE.md for dependency-specific patterns
- Identify code areas affected by major updates
- Review integration points with updated dependencies
- Verify compatibility with current architecture
- Plan necessary code refactoring

## SPARC Phase 4: Refine - Execute Updates

### 4.1 Create Safety Checkpoint

Before any updates:
```bash
# Create backup branch
git checkout -b dependency-update-backup-$(date +%Y%m%d)
git push origin dependency-update-backup-$(date +%Y%m%d)

# Save current dependency state
cp package-lock.json package-lock.json.backup
# Or equivalent for your package manager
```

### 4.2 Update Dependencies by Category

#### Security Updates First
```bash
# Example for npm
npm audit fix

# For critical vulnerabilities requiring major updates
npm audit fix --force

# Verify fixes
npm audit
```

#### Patch Updates
```bash
# Update only patch versions
npm update --save

# Or for specific packages
npm install package@latest --save-exact
```

#### Minor Updates
Update one at a time for better tracking:
```bash
# Check available updates
npm outdated

# Update specific packages
npm install package@^new.minor.version

# Run tests after each update
npm test
```

#### Major Updates
For each major update:
1. Read the migration guide/changelog
2. Update the dependency
3. Update code to match new API
4. Run all tests
5. Test manually if needed
6. Document breaking changes

### 4.3 Update Sub-dependencies

Handle transitive dependency issues:
```bash
# Deduplicate dependencies
npm dedupe

# Clean and reinstall if needed
rm -rf node_modules package-lock.json
npm install
```

### 4.4 Test Each Update Phase

After each category of updates:
1. Run unit tests
2. Run integration tests
3. Run linting/type checking
4. Build the project
5. Run smoke tests
6. Check for console warnings

## SPARC Phase 5: Complete - Verify and Document

### 5.1 Comprehensive Testing

Run full test suite:
```bash
# Full test suite with coverage
npm test -- --coverage

# Build for production
npm run build

# Run production smoke tests
npm run test:prod

# Check bundle size impact
npm run analyze
```

### 5.2 Security Verification

Final security check:
```bash
# Run security audit
npm audit

# Check for known vulnerabilities
npm ls --depth=0 | grep -E "(deprecated|security)"

# Verify licenses are acceptable
npm run license-check
```

### 5.3 Commit Updates

Organize commits by update type:
```bash
git checkout develop
git checkout -b feature/dependency-updates-$(date +%Y%m%d)

# Security updates
git add package.json package-lock.json
git commit -m "fix(deps): Security updates

- Updated vulnerable-package from 1.0.0 to 1.0.1 (CVE-2024-12345)
- Updated another-package from 2.0.0 to 2.0.1 (security fix)"

# Patch updates
git add package.json package-lock.json
git commit -m "chore(deps): Patch updates

- Updated utility-lib from 3.1.0 to 3.1.5
- Updated helper-tool from 1.2.3 to 1.2.7
- Various sub-dependency updates"

# Minor updates
git add package.json package-lock.json src/*
git commit -m "feat(deps): Minor version updates

- Updated framework from 4.1.0 to 4.3.0
- Added new optional features support
- Updated related code to use new APIs"

# Major updates (if any)
git add .
git commit -m "feat(deps)!: Major version update for big-library

BREAKING CHANGE: Updated big-library from 2.x to 3.x
- Migrated to new API structure
- Updated all imports and usage
- See migration guide in docs/"
```

## SPARC Phase 6: Verify - Rollback Plan

Ensure rollback capability:
```bash
# Document rollback procedure
echo "## Rollback Procedure
1. git checkout dependency-update-backup-$(date +%Y%m%d)
2. npm ci
3. npm test
4. Deploy previous version" > ROLLBACK.md

# Verify backup branch exists
git branch -r | grep dependency-update-backup
```

## SPARC Phases 7-9: L³ - Log, Learn, Level Up

### Update ACTIVITY_LOG.md
Record update details:
- Number of dependencies updated
- Security vulnerabilities resolved
- Performance impact (bundle size, build time)
- Breaking changes handled

### Update FEEDBACK_LOG.md
Document any issues:
- Unexpected breaking changes
- Compatibility problems
- Performance regressions
- Workarounds applied

### Update SELF_ANALYSIS_LOG.md
Analyze the update process:
- Which updates were most problematic?
- How can we improve the process?
- Should we adjust update frequency?
- Are there dependencies we should replace?

### Update PROJECT Documentation
- Update README.md with new version requirements
- Update CHANGELOG.md with dependency changes
- Update docs/ARCHITECTURE.md if patterns changed
- Create migration guide for major updates

## Dependency-Specific Strategies

### JavaScript/Node.js
```bash
# Use npm-check-updates for overview
npx npm-check-updates

# Update package.json interactively
npx npm-check-updates -i

# Use npm ci for clean installs
npm ci
```

### Python
```bash
# Use pip-review
pip-review --local --auto

# Or with poetry
poetry update
poetry show --outdated
```

### Go
```bash
# Update all dependencies
go get -u ./...

# Tidy up
go mod tidy
```

### Ruby
```bash
# Update bundler
bundle update

# Check outdated
bundle outdated
```

## Success Criteria

Update is complete when:
- ✓ No security vulnerabilities remain
- ✓ All tests pass
- ✓ Build succeeds
- ✓ No runtime errors
- ✓ Performance is acceptable
- ✓ Documentation is updated
- ✓ Rollback plan is tested
- ✓ Team is notified

## Emergency Procedures

If updates cause critical issues:
1. Immediately rollback to backup branch
2. Document issue in FEEDBACK_LOG.md
3. Create GitHub issue with details
4. Notify team via Slack/communication channel
5. Pin problematic dependency version
6. Plan targeted fix in separate branch

$ARGUMENTS