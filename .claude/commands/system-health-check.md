# System Health Check Command

Verify that the SPARC-V-L³ development system is properly configured and all components are functioning correctly.

## SPARC Phase 1: Specification - Define Health Criteria

Health check covers:
1. **File Structure**: All required files and directories exist
2. **Content Validity**: Files contain required sections
3. **System Integrity**: No broken references or missing components
4. **Process Compliance**: Logs show SPARC-V-L³ protocol usage
5. **Tool Configuration**: Development tools properly configured

## SPARC Phase 2: Plan - Health Check Strategy

### 2.1 Core System Files
Check existence and validity:
- CLAUDE.md
- DEVELOPMENT_GUIDE.md
- PROJECT_STATUS.md
- ARCHITECTURE.md
- CHANGELOG.md
- All log files

### 2.2 Directory Structure
Verify standard directories:
- docs/{decisions,analysis,planning}
- archive/
- logs/
- src/ or equivalent
- tests/ or equivalent

### 2.3 Process Indicators
Evidence of SPARC-V-L³ compliance:
- Activity logs show structured entries
- Feedback logs capture learnings
- Self-analysis logs show reflection
- Git commits follow conventions

## SPARC Phase 3: Architecture - System Verification

### 3.1 Check File System Structure
```bash
echo "🏗️  Checking directory structure..."

# Required directories
REQUIRED_DIRS=(
  "docs"
  "docs/decisions"
  "docs/analysis" 
  "docs/planning"
  "archive"
  "logs"
)

MISSING_DIRS=()
for dir in "${REQUIRED_DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    MISSING_DIRS+=("$dir")
    echo "❌ Missing: $dir"
  else
    echo "✅ Found: $dir"
  fi
done
```

### 3.2 Verify Core Files
```bash
echo -e "\n📄 Checking core files..."

# Required files
REQUIRED_FILES=(
  "CLAUDE.md"
  "docs/DEVELOPMENT_GUIDE.md"
  "PROJECT_STATUS.md"
  "docs/ARCHITECTURE.md"
  "CHANGELOG.md"
  "logs/ACTIVITY_LOG.md"
  "logs/FEEDBACK_LOG.md"
  "logs/SELF_ANALYSIS_LOG.md"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    MISSING_FILES+=("$file")
    echo "❌ Missing: $file"
  else
    echo "✅ Found: $file"
  fi
done
```

## SPARC Phase 4: Refine - Deep Health Analysis

### 4.1 Validate File Contents

Check CLAUDE.md has required sections:
```bash
echo -e "\n🔍 Validating CLAUDE.md structure..."
if [ -f "CLAUDE.md" ]; then
  REQUIRED_SECTIONS=(
    "CURRENT TASK"
    "CORE DIRECTIVES"
    "CONTEXT INITIALIZATION PROTOCOL"
    "KNOWLEDGE BASE INTERACTION"
  )
  
  for section in "${REQUIRED_SECTIONS[@]}"; do
    if grep -q "$section" CLAUDE.md; then
      echo "✅ Section found: $section"
    else
      echo "⚠️  Missing section: $section"
    fi
  done
fi
```

### 4.2 Check Log Quality

Analyze log entries for SPARC-V-L³ compliance:
```bash
echo -e "\n📊 Analyzing log quality..."

# Check ACTIVITY_LOG.md for recent entries
if [ -f "logs/ACTIVITY_LOG.md" ]; then
  RECENT_ENTRIES=$(grep -c "^##" logs/ACTIVITY_LOG.md || echo "0")
  echo "Activity log entries: $RECENT_ENTRIES"
  
  # Check for SPARC phases mentioned
  SPARC_MENTIONS=$(grep -ci "SPARC\|Specification\|Plan\|Architecture\|Refine\|Complete\|Verify" logs/ACTIVITY_LOG.md || echo "0")
  echo "SPARC protocol mentions: $SPARC_MENTIONS"
fi

# Check for learning capture
if [ -f "logs/FEEDBACK_LOG.md" ]; then
  FEEDBACK_ENTRIES=$(grep -c "^##" logs/FEEDBACK_LOG.md || echo "0")
  echo "Feedback entries: $FEEDBACK_ENTRIES"
fi

if [ -f "logs/SELF_ANALYSIS_LOG.md" ]; then
  ANALYSIS_ENTRIES=$(grep -c "^##" logs/SELF_ANALYSIS_LOG.md || echo "0")
  echo "Self-analysis entries: $ANALYSIS_ENTRIES"
fi
```

### 4.3 Verify Git Configuration

Check git workflow compliance:
```bash
echo -e "\n🔀 Checking git configuration..."

# Check branch structure
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Check for required branches
for branch in "main" "develop"; do
  if git show-ref --verify --quiet "refs/heads/$branch"; then
    echo "✅ Branch exists: $branch"
  else
    echo "⚠️  Missing branch: $branch"
  fi
done

# Analyze commit message compliance
echo -e "\n📝 Recent commit compliance:"
git log --pretty=format:"%s" -10 | while read commit; do
  if [[ $commit =~ ^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?: ]]; then
    echo "✅ $commit"
  else
    echo "⚠️  Non-conventional: $commit"
  fi
done
```

### 4.4 Check Tool Configuration

Verify development tools:
```bash
echo -e "\n🛠️  Checking tool configuration..."

# Check for configuration files
CONFIG_FILES=(
  ".eslintrc*"
  ".prettierrc*"
  "tsconfig.json"
  ".gitignore"
  ".editorconfig"
)

for pattern in "${CONFIG_FILES[@]}"; do
  if ls $pattern 2>/dev/null | grep -q .; then
    echo "✅ Found: $pattern"
  else
    echo "ℹ️  Not found: $pattern (may not be required)"
  fi
done

# Check for test configuration
if [ -f "package.json" ]; then
  if grep -q '"test"' package.json; then
    echo "✅ Test script configured"
  else
    echo "⚠️  No test script in package.json"
  fi
fi
```

## SPARC Phase 5: Complete - Generate Health Report

Create comprehensive health report:
```markdown
# System Health Check Report
Generated: $(date +"%Y-%m-%d %H:%M:%S")

## Overall Health Score: [SCORE]/100

### ✅ Healthy Components
- [List all passing checks]

### ⚠️  Warnings
- [List non-critical issues]

### ❌ Critical Issues
- [List missing required components]

## Detailed Analysis

### File System Integrity
- Required directories: X/Y present
- Core files: X/Y present
- Archive organization: [Status]

### Process Compliance
- SPARC-V-L³ adoption: X%
- Conventional commits: X%
- Log completeness: X%

### Documentation Quality
- Context files up-to-date: [Yes/No]
- Template variables resolved: X%
- Cross-references valid: X%

## Recommendations

### Immediate Actions
1. [Critical fixes needed]

### Short-term Improvements
1. [Important but not urgent]

### Long-term Enhancements
1. [Nice to have improvements]
```

## SPARC Phase 6: Verify - Auto-Repair Options

Offer to fix common issues:
```bash
echo -e "\n🔧 Auto-repair available for:"

# Create missing directories
if [ ${#MISSING_DIRS[@]} -gt 0 ]; then
  echo "- Create missing directories"
fi

# Initialize missing files
if [ ${#MISSING_FILES[@]} -gt 0 ]; then
  echo "- Initialize missing files from templates"
fi

# Fix file permissions
echo "- Correct file permissions"

# Update git hooks
echo "- Install/update git hooks"
```

## SPARC Phases 7-9: L³ - Log, Learn, Level Up

### Update Logs
Record health check results in ACTIVITY_LOG.md:
- Health score
- Issues found
- Repairs performed
- Recommendations made

### Document Patterns
If recurring issues found, update FEEDBACK_LOG.md with:
- Common configuration drift
- Frequent missing components
- Process compliance gaps

### Improve System
Based on findings, consider:
- Automating health checks in CI
- Creating setup scripts
- Improving documentation
- Adding validation hooks

## Health Score Calculation

```
Score = (
  File System: 30 points
  + Process Compliance: 25 points  
  + Documentation: 20 points
  + Git Workflow: 15 points
  + Tool Configuration: 10 points
)

Grading:
- 90-100: Excellent ✅
- 70-89: Good 👍
- 50-69: Fair ⚠️
- Below 50: Needs Attention ❌
```

## Quick Fixes

Provide commands to fix common issues:
```bash
# Initialize missing structure
./scripts/bootstrap-system.sh

# Update all context files
/project:context-sync

# Fix git workflow
git checkout -b develop
git push -u origin develop

# Install pre-commit hooks
pre-commit install
```

$ARGUMENTS