# Code Quality Check Command

Run comprehensive code quality checks including linting, formatting, type checking, and complexity analysis following the SPARC-V-L³ protocol.

## SPARC Phase 1: Specification - Understand Quality Standards

First, read project quality requirements:
- Read CLAUDE.md for code style and quality rules
- Read docs/DEVELOPMENT_GUIDE.md for coding standards
- Read .eslintrc/.prettierrc/pyproject.toml (configuration files)
- Check pre-commit hooks configuration
- Review recent FEEDBACK_LOG.md for quality issues

Identify available quality tools:
- Linters (ESLint, Pylint, Golint, etc.)
- Formatters (Prettier, Black, gofmt, etc.)
- Type checkers (TypeScript, mypy, etc.)
- Complexity analyzers (Sonarqube, CodeClimate)
- Security scanners (Snyk, Bandit, etc.)

## SPARC Phase 2: Plan - Create Quality Check Strategy

Plan comprehensive quality checks:

### 2.1 Static Analysis
- Syntax errors
- Code style violations
- Best practice violations
- Security vulnerabilities
- Dead code detection

### 2.2 Code Formatting
- Consistent indentation
- Line length limits
- Import organization
- Whitespace consistency

### 2.3 Type Safety
- Type annotations coverage
- Type errors
- Implicit any usage
- Unsafe operations

### 2.4 Code Complexity
- Cyclomatic complexity
- Cognitive complexity
- File length limits
- Function length limits
- Duplicate code detection

### 2.5 Documentation Quality
- Missing documentation
- Outdated comments
- README completeness
- API documentation

## SPARC Phase 3: Architecture - Verify Quality Tools Setup

Ensure all quality tools are properly configured:
- Verify linter configurations align with project standards
- Check formatter settings match team preferences
- Validate type checker strictness levels
- Ensure CI/CD runs all quality checks
- Verify pre-commit hooks are installed

Read ARCHITECTURE.md to understand quality requirements for different components.

## SPARC Phase 4: Refine - Execute Quality Checks

### 4.1 Run Linting Checks

Execute linters and capture results:
```bash
# JavaScript/TypeScript
npm run lint -- --format json > lint-report.json
npm run lint

# Python
pylint src --output-format=json > lint-report.json
pylint src

# Go
golangci-lint run ./... --out-format json > lint-report.json
golangci-lint run ./...
```

### 4.2 Auto-fix Safe Issues

Apply automatic fixes where safe:
```bash
# JavaScript/TypeScript
npm run lint -- --fix

# Python
autopep8 --in-place --recursive src/
black src/

# Go
gofmt -w .
```

### 4.3 Run Type Checking

Verify type safety:
```bash
# TypeScript
npx tsc --noEmit

# Python
mypy src --strict

# Go (built-in)
go build ./...
```

### 4.4 Check Code Formatting

Ensure consistent formatting:
```bash
# JavaScript/TypeScript
npm run format:check
# Or
npx prettier --check .

# Python
black --check src/
isort --check-only src/

# Go
gofmt -l .
```

### 4.5 Analyze Code Complexity

Check for overly complex code:
```bash
# JavaScript
npx eslint . --rule 'complexity: ["error", 10]'

# Python
radon cc src -s -n C

# General
# Use SonarQube, CodeClimate, or similar
```

### 4.6 Security Scanning

Check for security issues:
```bash
# JavaScript
npm audit
npx snyk test

# Python
bandit -r src/
safety check

# General
# Run SAST tools
```

### 4.7 Documentation Checks

Verify documentation quality:
```bash
# Check for missing JSDoc/docstrings
# Verify README has all sections
# Ensure API docs are generated
# Check for outdated examples
```

## SPARC Phase 5: Complete - Fix and Document

### 5.1 Prioritize Issues

Categorize issues by severity:
1. **Critical**: Security vulnerabilities, type errors
2. **High**: Logic errors, complexity violations
3. **Medium**: Style violations, missing docs
4. **Low**: Formatting issues, minor suggestions

### 5.2 Fix Issues Systematically

For each category of issues:
```bash
# Create quality improvement branch
git checkout develop
git checkout -b feature/code-quality-$(date +%Y%m%d)

# Fix critical issues first
# Fix security vulnerabilities
# Fix type errors
git add src/
git commit -m "fix: Resolve critical type and security issues

- Fixed implicit any usage in user service
- Resolved SQL injection vulnerability
- Added proper type guards"

# Fix high-priority issues
# Reduce complexity
# Fix logic errors
git add src/
git commit -m "refactor: Reduce code complexity

- Split large functions into smaller ones
- Extracted repeated logic to utilities
- Simplified conditional statements"

# Fix medium issues
# Add missing documentation
git add src/
git commit -m "docs: Add missing documentation

- Added JSDoc to all public APIs
- Updated inline comments
- Improved variable naming"

# Fix low issues
# Format code
git add .
git commit -m "style: Apply consistent formatting

- Ran prettier on all files
- Fixed import ordering
- Normalized whitespace"
```

### 5.3 Update Quality Configurations

If needed, update tool configurations:
```bash
# Update linter rules
# Adjust formatter settings
# Modify complexity thresholds
git add .eslintrc.* .prettierrc.*
git commit -m "chore: Update code quality configurations

- Added new ESLint rules for better type safety
- Adjusted Prettier line length to 100
- Enabled additional security checks"
```

## SPARC Phase 6: Verify - Ensure All Checks Pass

Run all quality checks again:
```bash
# Create quality check script if not exists
cat > scripts/quality-check.sh << 'EOF'
#!/bin/bash
set -e

echo "🔍 Running code quality checks..."

echo "📝 Linting..."
npm run lint

echo "🎨 Formatting..."
npm run format:check

echo "🔤 Type checking..."
npm run type-check

echo "🔐 Security audit..."
npm audit

echo "🧪 Running tests..."
npm test

echo "✅ All quality checks passed!"
EOF

chmod +x scripts/quality-check.sh
./scripts/quality-check.sh
```

## SPARC Phases 7-9: L³ - Log, Learn, Level Up

### Update ACTIVITY_LOG.md
Record quality improvements:
- Number of issues fixed by category
- Tools run and results
- Configuration changes made
- Time spent on fixes

### Update FEEDBACK_LOG.md
Document patterns found:
- Common quality issues
- Root causes identified
- Areas needing attention
- Tool effectiveness

### Update SELF_ANALYSIS_LOG.md
Analyze quality trends:
- Are certain issues recurring?
- Which tools provide most value?
- Should we adjust our standards?
- How can we prevent issues earlier?

### Update DEVELOPMENT_GUIDE.md
If needed, update guidelines:
- New coding standards
- Additional pre-commit checks
- Updated complexity limits
- Enhanced review criteria

## Quality Metrics Report

Generate comprehensive quality report:
```markdown
# Code Quality Report - $(date +%Y-%m-%d)

## Summary
- Lines of Code: X
- Test Coverage: X%
- Technical Debt: X hours
- Security Issues: X critical, X high, X medium

## Linting Results
- Errors: X
- Warnings: X
- Auto-fixed: X

## Type Safety
- Type Coverage: X%
- Any usage: X instances
- Type errors: X

## Complexity
- Average Complexity: X
- High Complexity Functions: X
- Duplicate Code: X%

## Improvements Made
- [List key improvements]

## Recommendations
- [List ongoing improvements needed]
```

## Pre-commit Hook Setup

Ensure quality checks run automatically:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: lint
        name: Lint
        entry: npm run lint
        language: system
        pass_filenames: false
      
      - id: type-check
        name: Type Check
        entry: npm run type-check
        language: system
        pass_filenames: false
      
      - id: format
        name: Format
        entry: npm run format
        language: system
```

## Success Criteria

Quality check is complete when:
- ✓ All linting errors resolved
- ✓ Code is properly formatted
- ✓ No type errors exist
- ✓ Complexity is within limits
- ✓ Security vulnerabilities addressed
- ✓ Documentation is complete
- ✓ All tests still pass
- ✓ Pre-commit hooks configured

## Continuous Improvement

Set up automated quality tracking:
1. Configure CI to fail on quality violations
2. Set up quality metrics dashboard
3. Track quality trends over time
4. Regular quality review meetings
5. Celebrate quality improvements

$ARGUMENTS