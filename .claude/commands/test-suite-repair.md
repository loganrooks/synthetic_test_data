# Test Suite Repair Command

Systematically identify, analyze, and repair broken tests following the SPARC-V-L³ protocol and TDD principles.

## SPARC Phase 1: Specification - Understand Test State

First, read the testing methodology and requirements:
- Read CLAUDE.md for project-specific testing requirements
- Read docs/DEVELOPMENT_GUIDE.md for testing methodology (TDD requirements)
- Read docs/TEST_SUITE_REPAIR_PLAN.md if it exists
- Read FEEDBACK_LOG.md for recent test-related issues

Analyze current test suite state:
- Run all tests and capture output
- Identify failing tests by category (unit, integration, e2e)
- Check test coverage metrics
- Review test file organization and naming conventions
- Identify flaky or intermittent test failures

## SPARC Phase 2: Plan - Create Repair Strategy

Based on analysis, create a repair plan that addresses:
1. **Critical failures**: Tests blocking deployment or development
2. **Flaky tests**: Intermittent failures causing CI issues
3. **Coverage gaps**: Areas lacking adequate test coverage
4. **Technical debt**: Outdated test patterns or deprecated assertions
5. **Performance**: Slow tests impacting developer productivity

Document the plan in `docs/planning/test-repair-$(date +%Y%m%d).md`

## SPARC Phase 3: Architecture - Verify Test Structure

Ensure test architecture aligns with project structure:
- Verify test file locations match source file structure
- Check test naming conventions are consistent
- Validate test utilities and helpers are properly organized
- Ensure test data/fixtures are managed appropriately
- Verify CI/CD test configuration is optimal

Read ARCHITECTURE.md to ensure tests align with system design.

## SPARC Phase 4: Refine - Execute Repairs

### 4.1 Fix Critical Test Failures

For each failing test:
1. Run the specific test in isolation to confirm failure
2. Read the test to understand expected behavior
3. Read the source code being tested
4. Identify root cause (implementation bug vs test bug)
5. Fix the issue following TDD principles:
   - If implementation bug: Fix code, ensure test passes
   - If test bug: Fix test to match intended behavior
6. Run test again to confirm fix
7. Run related tests to ensure no regression

### 4.2 Stabilize Flaky Tests

For intermittent failures:
1. Identify sources of non-determinism:
   - Timing/race conditions
   - External dependencies
   - Random data generation
   - System state dependencies
2. Apply fixes:
   - Add proper wait conditions
   - Mock external dependencies
   - Use fixed seed for random data
   - Ensure proper test isolation
3. Run test multiple times to verify stability

### 4.3 Improve Test Coverage

Identify and fill coverage gaps:
1. Generate coverage report
2. Identify critical uncovered code paths
3. Write tests for uncovered functionality following TDD:
   - Write failing test first
   - Implement minimal code to pass
   - Refactor if needed
4. Aim for project-specific coverage targets

### 4.4 Refactor Test Technical Debt

Modernize outdated test patterns:
- Update deprecated assertion methods
- Replace obsolete test utilities
- Improve test descriptions and organization
- Extract common test setup to helpers
- Remove duplicate test logic

## SPARC Phase 5: Complete - Verify and Document

### 5.1 Run Complete Test Suite

Execute full test suite to ensure:
- All tests pass consistently
- No new failures introduced
- Performance is acceptable
- Coverage meets requirements

### 5.2 Update Documentation

Update relevant documentation:
- Test suite README with any new patterns
- CI/CD configuration if needed
- Testing guidelines in DEVELOPMENT_GUIDE.md

### 5.3 Commit Changes

Create organized commits:
```bash
# Start from develop
git checkout develop

# Create test repair branch
git checkout -b feature/test-suite-repair-$(date +%Y%m%d)

# Commit by logical groups
git add tests/unit/*
git commit -m "test: Fix failing unit tests

- Fixed UserService authentication tests
- Stabilized flaky database connection tests
- Updated deprecated assertions"

git add tests/integration/*
git commit -m "test: Repair integration test suite

- Fixed API endpoint test failures
- Added proper async handling
- Improved test isolation"

git add src/* tests/*
git commit -m "fix: Resolve bugs found during test repair

- Fixed null pointer in user validation
- Corrected date parsing logic
- Updated error handling"

# Merge to develop
git checkout develop
git merge --no-ff feature/test-suite-repair-$(date +%Y%m%d)
```

## SPARC Phase 6: Verify - Confirm Success

Generate comprehensive test report:
```bash
# Run tests with coverage
npm test -- --coverage

# Run tests multiple times to verify stability
for i in {1..5}; do npm test || break; done

# Generate test timing report
npm test -- --verbose --timer
```

## SPARC Phases 7-9: L³ - Log, Learn, Level Up

### Update ACTIVITY_LOG.md
Record all test repairs with:
- Number of tests fixed
- Coverage improvement metrics
- Performance improvements
- Time spent on repairs

### Update FEEDBACK_LOG.md
Document:
- Root causes of test failures
- Patterns in test breakage
- Preventive measures identified

### Update SELF_ANALYSIS_LOG.md
Analyze the repair process:
- What caused the test failures?
- How can we prevent similar issues?
- What testing patterns need improvement?
- Should we update our TDD practices?

### Update DEVELOPMENT_GUIDE.md
If systematic improvements identified:
- New testing best practices
- Updated TDD workflow
- Enhanced test organization patterns

## Success Criteria

The test repair is complete when:
- ✓ All tests pass consistently
- ✓ No flaky tests remain
- ✓ Coverage meets project requirements
- ✓ Test execution time is reasonable
- ✓ All changes are documented
- ✓ Logs are updated
- ✓ Team is notified of significant changes

## Emergency Situations

If unable to fix a test:
1. Document the issue thoroughly in FEEDBACK_LOG.md
2. Create a GitHub issue with reproduction steps
3. Temporarily skip the test with a clear comment:
   ```javascript
   test.skip('TEMPORARY: Skipped due to issue #123 - [brief description]', () => {
     // Test implementation
   });
   ```
4. Add to PROJECT_STATUS.md critical issues section

$ARGUMENTS