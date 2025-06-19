# Knowledge Extraction Command

Mine insights from logs, commit history, code patterns, and team interactions to extract valuable learnings and update the project's knowledge base.

## SPARC Phase 1: Specification - Define Knowledge Sources

Knowledge sources to mine:
1. **Logs**: ACTIVITY_LOG, FEEDBACK_LOG, SELF_ANALYSIS_LOG
2. **Git History**: Commit messages, PR descriptions, code changes
3. **Code Comments**: TODOs, FIXMEs, explanatory comments
4. **Issue Tracking**: GitHub issues, bug reports, feature requests
5. **Code Patterns**: Recurring solutions, common abstractions
6. **Test Failures**: Error patterns, flaky tests, edge cases

Knowledge types to extract:
- **Technical Patterns**: Recurring solutions, best practices
- **Process Insights**: Workflow improvements, bottlenecks
- **Domain Knowledge**: Business rules, edge cases
- **Team Wisdom**: Conventions, preferences, decisions
- **Failure Patterns**: Common mistakes, anti-patterns

## SPARC Phase 2: Plan - Knowledge Mining Strategy

### 2.1 Historical Analysis
- Last 30-90 days of activity
- Focus on patterns, not individual events
- Weight recent insights higher
- Cross-reference multiple sources

### 2.2 Pattern Recognition
- Identify recurring themes
- Find solution patterns
- Detect problem areas
- Discover workflow optimizations

### 2.3 Knowledge Synthesis
- Consolidate similar insights
- Resolve contradictions
- Prioritize by impact
- Generate actionable recommendations

## SPARC Phase 3: Architecture - Mining Implementation

### 3.1 Mine Log Files
```bash
echo "📚 Mining knowledge from logs..."

# Extract patterns from FEEDBACK_LOG
echo -e "\n🔍 Analyzing FEEDBACK_LOG patterns..."
if [ -f "logs/FEEDBACK_LOG.md" ]; then
  # Find recurring issues
  echo "Common issues:"
  grep -i "issue\|error\|problem" logs/FEEDBACK_LOG.md | 
    sed 's/.*: //' | sort | uniq -c | sort -nr | head -10
  
  # Find lessons learned
  echo -e "\nLessons learned:"
  grep -i "lesson\|learned\|should\|must" logs/FEEDBACK_LOG.md |
    grep -v "^#" | head -10
fi

# Extract insights from SELF_ANALYSIS_LOG
echo -e "\n🔍 Analyzing SELF_ANALYSIS_LOG insights..."
if [ -f "logs/SELF_ANALYSIS_LOG.md" ]; then
  # Find improvement suggestions
  echo "Improvement patterns:"
  grep -i "improve\|better\|optimize\|should" logs/SELF_ANALYSIS_LOG.md |
    grep -v "^#" | head -10
  
  # Find recognized patterns
  echo -e "\nRecognized patterns:"
  grep -i "pattern\|always\|often\|frequently" logs/SELF_ANALYSIS_LOG.md |
    grep -v "^#" | head -10
fi
```

### 3.2 Analyze Git History
```bash
echo -e "\n📊 Mining git history for patterns..."

# Analyze commit patterns
echo "Commit type distribution:"
git log --pretty=format:"%s" -200 | 
  grep -oE "^(feat|fix|docs|style|refactor|test|chore)" | 
  sort | uniq -c | sort -nr

# Find files that change together
echo -e "\nFiles that often change together:"
git log --pretty=format: --name-only -100 | 
  sort | uniq -c | sort -nr | 
  grep -v "^$" | head -20 |
  awk '$1 > 5 {print}'

# Identify hot spots (frequently modified files)
echo -e "\nCode hot spots:"
git log --pretty=format: --name-only -200 |
  grep -E "\.(js|ts|py|go)$" |
  sort | uniq -c | sort -nr | head -10

# Extract improvement commits
echo -e "\nRefactoring patterns:"
git log --grep="refactor\|improve\|optimize" --oneline -50
```

### 3.3 Mine Code Patterns
```bash
echo -e "\n💡 Extracting code patterns..."

# Find TODO patterns
echo "TODO/FIXME analysis:"
grep -r "TODO\|FIXME\|HACK\|XXX" --include="*.js" --include="*.ts" --include="*.py" . |
  grep -oE "TODO.*|FIXME.*|HACK.*" |
  sed 's/.*: //' |
  sort | uniq -c | sort -nr | head -10

# Find common imports/dependencies
echo -e "\nMost used dependencies:"
if [ -f "package.json" ]; then
  # For JS/TS projects
  find src -name "*.js" -o -name "*.ts" |
    xargs grep -h "^import.*from" |
    grep -oE "from ['\"][^'\"]+['\"]" |
    sort | uniq -c | sort -nr | head -15
fi

# Find error handling patterns
echo -e "\nError handling patterns:"
grep -r "catch\|except\|error" --include="*.js" --include="*.ts" --include="*.py" . |
  grep -v node_modules |
  wc -l
```

### 3.4 Analyze Issue Patterns
```bash
echo -e "\n🐛 Mining issue tracking data..."

# If GitHub CLI available
if command -v gh &> /dev/null; then
  echo "Recent issue themes:"
  gh issue list --limit 50 --state all --json title,labels |
    jq -r '.[] | .title' |
    grep -oE "\b\w{4,}\b" |
    sort | uniq -c | sort -nr | head -20
  
  echo -e "\nCommon labels:"
  gh issue list --limit 50 --state all --json labels |
    jq -r '.[] | .labels[] | .name' |
    sort | uniq -c | sort -nr
fi
```

## SPARC Phase 4: Refine - Synthesize Knowledge

### 4.1 Generate Pattern Catalog
Create `docs/analysis/patterns-$(date +%Y%m%d).md`:
```markdown
# Extracted Knowledge Patterns

Generated: $(date)
Analysis Period: Last 90 days

## 🏗️ Architectural Patterns

### Successful Patterns
1. **[Pattern Name]**
   - Used in: [Files/Components]
   - Benefits: [Observed benefits]
   - Example: [Code snippet or reference]

### Anti-patterns to Avoid
1. **[Anti-pattern Name]**
   - Found in: [Locations]
   - Problems: [Issues caused]
   - Better approach: [Recommendation]

## 🔄 Process Patterns

### Effective Workflows
1. **[Workflow Name]**
   - Frequency: [How often used]
   - Success rate: [Estimated]
   - Key steps: [List]

### Bottlenecks Identified
1. **[Bottleneck]**
   - Impact: [Time/effort wasted]
   - Root cause: [Analysis]
   - Solution: [Recommendation]

## 🧪 Testing Insights

### Common Test Failures
1. **[Failure Type]**
   - Frequency: [X times in period]
   - Root cause: [Analysis]
   - Prevention: [Strategy]

### Testing Best Practices
1. **[Practice]**
   - Benefit: [Measured impact]
   - Implementation: [How to]

## 🐛 Bug Patterns

### Recurring Issues
1. **[Issue Type]**
   - Occurrences: [Count]
   - Common cause: [Analysis]
   - Prevention: [Strategy]

## 📚 Domain Knowledge

### Business Rules Discovered
1. **[Rule/Constraint]**
   - Source: [Where found]
   - Importance: [Critical/Important/Nice]
   - Documentation: [Where to document]

### Edge Cases
1. **[Edge Case]**
   - Discovery: [How found]
   - Handling: [Solution]
```

### 4.2 Update Knowledge Base
Based on extracted patterns:

Update DEVELOPMENT_GUIDE.md with:
- New best practices discovered
- Coding patterns that work well
- Anti-patterns to avoid
- Testing strategies that prevent bugs

Update ARCHITECTURE.md with:
- Architectural patterns that emerged
- Component relationships discovered
- Design decisions validated by usage
- Technical debt areas identified

### 4.3 Generate Recommendations
Create `docs/analysis/recommendations-$(date +%Y%m%d).md`:
```markdown
# Knowledge-Based Recommendations

## 🎯 High-Priority Actions

### 1. Code Quality Improvements
Based on pattern analysis:
- [ ] Refactor [hot spot files] - changed X times
- [ ] Extract common pattern from [files]
- [ ] Add error handling to [components]

### 2. Process Optimizations
Based on workflow analysis:
- [ ] Automate [recurring task]
- [ ] Streamline [bottleneck process]
- [ ] Document [undocumented pattern]

### 3. Testing Enhancements
Based on failure analysis:
- [ ] Add tests for [edge case]
- [ ] Stabilize [flaky test]
- [ ] Increase coverage in [area]

## 📊 Metrics and Trends

### Development Velocity
- Commits per week: [trend]
- Feature completion rate: [trend]
- Bug fix time: [average]

### Code Health
- Complexity trend: [increasing/decreasing]
- Test coverage: [trend]
- Technical debt: [estimate]

## 🔮 Predictions

Based on current patterns:
1. **[Area]** will likely need refactoring soon
2. **[Component]** is becoming a bottleneck
3. **[Pattern]** should be standardized
```

## SPARC Phase 5: Complete - Knowledge Integration

### 5.1 Create Knowledge Summary
Generate executive summary:
```markdown
# Knowledge Extraction Summary

**Extraction Date:** $(date)
**Period Analyzed:** [Date range]
**Data Sources:** Logs, Git history, Code analysis

## Key Findings

### 🌟 Top 5 Insights
1. [Most impactful finding]
2. [Second most important]
3. [Third insight]
4. [Fourth insight]
5. [Fifth insight]

### 💡 Actionable Improvements
- **Immediate:** [Quick wins]
- **Short-term:** [1-2 week improvements]
- **Long-term:** [Architectural changes]

### 📈 Positive Trends
- [What's working well]
- [Successful patterns]
- [Team strengths]

### ⚠️ Areas of Concern
- [What needs attention]
- [Recurring problems]
- [Technical debt]
```

### 5.2 Update Context Files
Integrate learnings into:
- CLAUDE.md: Add discovered patterns as rules
- PROJECT_STATUS.md: Update with trend information
- DEVELOPMENT_GUIDE.md: Add best practices
- FEEDBACK_LOG.md: Log meta-insights about learning

## SPARC Phase 6: Verify - Validate Insights

Cross-check extracted knowledge:
- Do patterns appear in multiple sources?
- Are insights actionable?
- Do recommendations align with project goals?
- Have similar patterns been tried before?

## SPARC Phases 7-9: L³ - Log, Learn, Level Up

### Update ACTIVITY_LOG.md
Record extraction process:
- Sources analyzed
- Patterns found
- Insights generated
- Recommendations made

### Update FEEDBACK_LOG.md
Meta-learning about extraction:
- Which sources were most valuable?
- What patterns were surprising?
- How can extraction improve?

### Update SELF_ANALYSIS_LOG.md
Reflect on knowledge management:
- Is knowledge being captured effectively?
- Are insights being acted upon?
- How can the team learn better?

## Automation Potential

Consider automating:
1. **Weekly Pattern Reports**: Automated extraction summaries
2. **Commit Analysis**: Real-time pattern detection
3. **Knowledge Alerts**: Notify when patterns emerge
4. **Learning Dashboard**: Visualize trends
5. **Auto-documentation**: Update guides based on patterns

## Success Metrics

Extraction is valuable when:
- ✓ Actionable insights generated
- ✓ Patterns prevent future issues
- ✓ Team velocity improves
- ✓ Technical debt decreases
- ✓ Knowledge is retained
- ✓ Onboarding accelerates

$ARGUMENTS