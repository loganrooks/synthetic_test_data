# Onboarding Command

Initialize Claude Code for a new project or team member by analyzing the codebase, setting up the development environment, and providing a comprehensive orientation.

## SPARC Phase 1: Specification - Understand Project Context

First-time setup detection:
- Check if CLAUDE.md exists and is populated
- Verify if this is a fresh clone
- Determine if switching from another project
- Identify what type of onboarding is needed

Onboarding scenarios:
1. **New Project**: No SPARC-V-L³ system exists
2. **New Team Member**: System exists, needs orientation
3. **Project Switch**: Refresh context from different project
4. **Recovery**: System exists but is incomplete

## SPARC Phase 2: Plan - Create Onboarding Strategy

### 2.1 Project Analysis
1. Detect technology stack
2. Identify project type (web app, CLI, library, etc.)
3. Find existing documentation
4. Analyze code structure
5. Discover workflow patterns

### 2.2 Environment Setup
1. Install dependencies
2. Configure development tools
3. Set up git hooks
4. Initialize SPARC-V-L³ system
5. Create missing structure

### 2.3 Knowledge Transfer
1. Generate project overview
2. Explain architecture
3. Document key workflows
4. Highlight important patterns
5. List common tasks

## SPARC Phase 3: Architecture - Deep Project Analysis

### 3.1 Technology Stack Detection
```bash
echo "🔍 Analyzing technology stack..."

# Detect primary language
PRIMARY_LANG="unknown"
if [ -f "package.json" ]; then
  PRIMARY_LANG="JavaScript/TypeScript"
  echo "📦 Found: Node.js project"
  
  # Check for frameworks
  if grep -q "next" package.json; then echo "  - Next.js detected"; fi
  if grep -q "react" package.json; then echo "  - React detected"; fi
  if grep -q "vue" package.json; then echo "  - Vue detected"; fi
  if grep -q "express" package.json; then echo "  - Express detected"; fi
  
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
  PRIMARY_LANG="Python"
  echo "🐍 Found: Python project"
  
  # Check for frameworks
  if grep -qi "django" requirements.txt 2>/dev/null; then echo "  - Django detected"; fi
  if grep -qi "flask" requirements.txt 2>/dev/null; then echo "  - Flask detected"; fi
  if grep -qi "fastapi" requirements.txt 2>/dev/null; then echo "  - FastAPI detected"; fi
  
elif [ -f "go.mod" ]; then
  PRIMARY_LANG="Go"
  echo "🐹 Found: Go project"
  
elif [ -f "Cargo.toml" ]; then
  PRIMARY_LANG="Rust"
  echo "🦀 Found: Rust project"
fi

# Detect testing framework
echo -e "\n🧪 Detecting testing setup..."
if [ -f "package.json" ]; then
  if grep -q "jest" package.json; then echo "  - Jest testing framework"; fi
  if grep -q "mocha" package.json; then echo "  - Mocha testing framework"; fi
  if grep -q "vitest" package.json; then echo "  - Vitest testing framework"; fi
fi
```

### 3.2 Project Structure Analysis
```bash
echo -e "\n📁 Analyzing project structure..."

# Generate structure overview
tree -d -L 2 -I 'node_modules|__pycache__|.git|dist|build' > /tmp/structure.txt

# Identify architecture pattern
if [ -d "src/controllers" ] && [ -d "src/models" ] && [ -d "src/views" ]; then
  echo "  - MVC architecture detected"
elif [ -d "src/components" ] && [ -d "src/pages" ]; then
  echo "  - Component-based architecture detected"
elif [ -d "src/domain" ] && [ -d "src/infrastructure" ]; then
  echo "  - Clean/Hexagonal architecture detected"
fi
```

## SPARC Phase 4: Refine - Initialize System

### 4.1 Create SPARC-V-L³ Structure
```bash
echo -e "\n🏗️  Setting up SPARC-V-L³ system..."

# Create required directories
mkdir -p docs/{decisions,analysis,planning}
mkdir -p archive/$(date +%Y-%m)
mkdir -p logs
mkdir -p .claude/commands

echo "✅ Directory structure created"
```

### 4.2 Generate Initial CLAUDE.md
Based on project analysis, create customized CLAUDE.md:
```markdown
# 🎯 CURRENT TASK: Project Onboarding and Setup
- **STATUS:** Initializing SPARC-V-L³ system

---

## 🧠 CORE DIRECTIVES (VERIFY ON EVERY ACTION)

1. **SPARC-V-L³ Protocol:** You MUST follow the full SPARC-V-L³ cycle for all non-trivial changes.
2. **Testing is Non-Negotiable:** [DETECTED_TEST_FRAMEWORK] tests must pass before any commit.
3. **Architecture Compliance:** Follow [DETECTED_ARCHITECTURE] patterns consistently.
4. **Verification is Mandatory:** All changes must be verified through tests and manual checks.
5. **Log All Actions:** Every response must update ACTIVITY_LOG.md.

---

## 📚 PROJECT OVERVIEW

**Project Type:** [DETECTED_PROJECT_TYPE]
**Primary Language:** [PRIMARY_LANG]
**Framework:** [DETECTED_FRAMEWORK]
**Testing:** [DETECTED_TEST_FRAMEWORK]
**Architecture:** [DETECTED_ARCHITECTURE]

---

## 🔄 CONTEXT INITIALIZATION PROTOCOL

[... rest of template with detected values filled in ...]
```

### 4.3 Initialize Log Files
Create initial log entries:
```bash
# Initialize ACTIVITY_LOG.md
cat > logs/ACTIVITY_LOG.md << EOF
# Activity Log

This log maintains an immutable record of all development actions.

## $(date "+%Y-%m-%d %H:%M:%S") - System Initialization

**Task:** SPARC-V-L³ system setup and onboarding
**Actor:** Onboarding Command
**Actions:**
- Analyzed project structure and technology stack
- Created required directory structure
- Initialized context files
- Set up development environment

**Result:** System ready for development

EOF

# Initialize other logs similarly
```

### 4.4 Environment Setup
```bash
echo -e "\n🔧 Setting up development environment..."

# Install dependencies based on detected stack
if [ -f "package.json" ]; then
  echo "Installing Node.js dependencies..."
  npm install
  
  # Install dev tools if missing
  if ! grep -q "eslint" package.json; then
    echo "Installing recommended dev tools..."
    npm install --save-dev eslint prettier
  fi
  
elif [ -f "requirements.txt" ]; then
  echo "Setting up Python virtual environment..."
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  
elif [ -f "go.mod" ]; then
  echo "Downloading Go dependencies..."
  go mod download
fi

# Set up git hooks
echo -e "\n🔗 Setting up git hooks..."
if [ -f ".pre-commit-config.yaml" ]; then
  pre-commit install
else
  echo "No pre-commit config found, creating basic hooks..."
  # Create basic pre-commit hook
fi
```

## SPARC Phase 5: Complete - Generate Orientation

### 5.1 Create Project README
Generate comprehensive onboarding document:
```markdown
# 🚀 Welcome to [PROJECT_NAME]!

Generated by SPARC-V-L³ Onboarding System on $(date)

## Quick Start

1. **Environment Setup** ✅
   - Dependencies installed
   - Development tools configured
   - Git hooks active

2. **Run the Project**
   ```bash
   [DETECTED_RUN_COMMAND]
   ```

3. **Run Tests**
   ```bash
   [DETECTED_TEST_COMMAND]
   ```

## Project Overview

### Architecture
[ARCHITECTURE_DESCRIPTION]

### Key Technologies
- **Language:** [PRIMARY_LANG]
- **Framework:** [FRAMEWORK]
- **Testing:** [TEST_FRAMEWORK]
- **Database:** [DATABASE_IF_DETECTED]

### Project Structure
```
[SIMPLIFIED_TREE_OUTPUT]
```

## Development Workflow

### SPARC-V-L³ Protocol
This project follows the SPARC-V-L³ development protocol:
1. **S**pecification - Understand requirements
2. **P**lan - Create detailed approach
3. **A**rchitecture - Consider system design
4. **R**efine - Implement solution
5. **C**omplete - Finish implementation
6. **V**erify - Test thoroughly
7. **L³** - Log, Learn, Level Up

### Git Workflow
- Feature branches: `feature/description-YYYYMMDD`
- Commit format: `type(scope): description`
- Merge flow: feature → develop → main

## Common Tasks

### Add a New Feature
```bash
/project:create-feature [feature-name]
```

### Fix Issues
```bash
/project:test-suite-repair
/project:code-quality-check
```

### Update Documentation
```bash
/project:context-sync
```

## Important Files

- **CLAUDE.md** - AI assistant instructions
- **DEVELOPMENT_GUIDE.md** - Coding standards
- **ARCHITECTURE.md** - System design
- **PROJECT_STATUS.md** - Current progress

## Getting Help

1. Check existing documentation in `docs/`
2. Review recent changes in CHANGELOG.md
3. Look for patterns in similar code
4. Ask team members
5. Use `/project:help` command

## Next Steps

1. [ ] Read DEVELOPMENT_GUIDE.md
2. [ ] Review ARCHITECTURE.md
3. [ ] Run the test suite
4. [ ] Make a small contribution
5. [ ] Join team channels

Welcome aboard! 🎉
```

### 5.2 Interactive Orientation
Provide interactive guidance:
```bash
echo -e "\n🎓 ONBOARDING COMPLETE!\n"
echo "Here's what I've set up for you:"
echo "✅ SPARC-V-L³ development system"
echo "✅ Project dependencies installed"
echo "✅ Git hooks configured"
echo "✅ Context files initialized"
echo "✅ Development environment ready"

echo -e "\n📋 Recommended next steps:"
echo "1. Read the generated project overview above"
echo "2. Run the project: [COMMAND]"
echo "3. Run tests: [COMMAND]"
echo "4. Try a simple task"

echo -e "\n💡 Useful commands:"
echo "/project:help - Show all available commands"
echo "/project:context-sync - Update documentation"
echo "/project:system-health-check - Verify setup"
```

## SPARC Phase 6: Verify - Test Setup

Run verification checks:
```bash
# Test that project runs
echo -e "\n🧪 Verifying setup..."

# Run tests if available
if [ -f "package.json" ] && grep -q '"test"' package.json; then
  npm test || echo "⚠️  Tests failing - this may be expected"
fi

# Verify SPARC-V-L³ system
if [ -f "CLAUDE.md" ] && [ -d "logs" ] && [ -d "docs" ]; then
  echo "✅ SPARC-V-L³ system verified"
else
  echo "❌ System setup incomplete"
fi
```

## SPARC Phases 7-9: L³ - Log, Learn, Level Up

### Create Onboarding Record
Update logs with onboarding details:
- Technologies discovered
- Patterns identified
- Setup steps performed
- Issues encountered

### Capture Learnings
Document in FEEDBACK_LOG.md:
- Missing documentation found
- Unclear patterns
- Setup challenges
- Improvement suggestions

### Update Templates
Based on onboarding experience:
- Refine detection algorithms
- Improve templates
- Add missing patterns
- Enhance automation

## Custom Project Types

### For Web Applications
- Set up dev server proxy
- Configure hot reload
- Initialize component library
- Set up routing structure

### For CLI Tools
- Set up command structure
- Initialize help system
- Configure argument parsing
- Create example commands

### For Libraries
- Set up build system
- Configure publishing
- Initialize documentation
- Create examples

## Success Checklist

Onboarding complete when:
- ✓ Can run the project
- ✓ Can run tests
- ✓ Understand architecture
- ✓ Know development workflow
- ✓ Have made first commit
- ✓ Context files accurate
- ✓ Feel oriented

$ARGUMENTS