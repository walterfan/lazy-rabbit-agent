# AI Test Agent

An autonomous AI agent for generating comprehensive test plans and test cases for Golang services. The agent analyzes code changes via Git and generates test strategies covering functional, stress, memory leak, goroutine leak, and performance testing.

## Features

- **Autonomous Test Planning**: Follows Observe → Plan → Act → Monitor → Analyze → Learn loop
- **Git Integration**: Analyzes uncommitted changes, branch differences, or specific commits
- **LLM-Powered Analysis**: Uses OpenAI GPT-4 or Anthropic Claude for intelligent test planning
- **Comprehensive Coverage**: Generates plans for:
  - Unit tests
  - Integration tests
  - Concurrency tests (race conditions, goroutine leaks)
  - Stress/load tests
  - Memory leak detection
  - Performance benchmarks
- **Go-Specific Focus**: Understands Go idioms, goroutines, channels, and common pitfalls
- **Rich Reporting**: Generates both JSON and human-readable Markdown reports

## Architecture

```
ai_test_agent/
├── src/
│   ├── agent.py          # Main agent orchestrator
│   ├── git_analyzer.py   # Git change detection
│   ├── test_planner.py   # Test plan generation
│   └── cli.py            # Command-line interface
├── config/
│   └── prompts.yaml      # Test strategy prompts
├── reports/              # Generated test plans
└── artifacts/            # Test execution artifacts
```

## Installation

### Prerequisites

- Python 3.8+
- Git
- OpenAI API key or Anthropic API key

### Setup

1. Clone the repository or navigate to the example directory:

```bash
cd example/ai_test_agent
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure API keys:

```bash
cp .env.example .env
# Edit .env and add your API key
```

Or set environment variables:

```bash
export OPENAI_API_KEY="sk-your-key-here"
# OR
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

## Usage

### Command-Line Interface

The agent provides three main commands for different analysis modes:

#### 1. Analyze Uncommitted Changes

Analyze all staged and unstaged changes in your repository:

```bash
python src/cli.py analyze-uncommitted --repo-path /path/to/go/repo
```

With custom LLM provider:

```bash
# Using OpenAI (default)
python src/cli.py analyze-uncommitted \
  --repo-path /path/to/go/repo \
  --llm-provider openai \
  --model gpt-4

# Using Anthropic Claude
python src/cli.py analyze-uncommitted \
  --repo-path /path/to/go/repo \
  --llm-provider anthropic \
  --model claude-3-5-sonnet-20241022
```

#### 2. Compare Branches

Compare two branches and generate test plan for the differences:

```bash
python src/cli.py compare-branches \
  --repo-path /path/to/go/repo \
  --base-branch master \
  --compare-branch feature/new-api
```

#### 3. Analyze Specific Commit

Analyze changes in a specific commit:

```bash
python src/cli.py analyze-commit \
  --repo-path /path/to/go/repo \
  --commit-sha abc123def
```

### Programmatic Usage

```python
from agent import AITestAgent

# Initialize agent
agent = AITestAgent(
    repo_path="/path/to/go/repo",
    llm_provider="openai",
    model="gpt-4"
)

# Analyze uncommitted changes
result = agent.run(mode="uncommitted")

# Compare branches
result = agent.run(
    mode="branch",
    base_branch="master",
    compare_branch="feature/new-feature"
)

# Analyze specific commit
result = agent.run(
    mode="commit",
    commit_sha="abc123def"
)

# Access results
test_plan = result["test_plan"]
print(f"Generated {len(test_plan.test_items)} test items")
```

## Example Output

When you run the agent, it generates:

### 1. Console Output

```
AI Test Agent - Analyzing Uncommitted Changes

╭─────────────── Observation ───────────────╮
│ Repository: feature/new-api                │
│ Changes: 5 files                           │
│ Timestamp: 2024-01-15T10:30:00            │
╰────────────────────────────────────────────╯

Changed Files:
┌────────────────────────────┬──────────┬──────────┐
│ File                       │ Type     │ Changes  │
├────────────────────────────┼──────────┼──────────┤
│ pkg/api/handler.go         │ modified │ +45/-12  │
│ pkg/api/handler_test.go    │ modified │ +30/-5   │
│ pkg/service/user.go        │ added    │ +120/-0  │
└────────────────────────────┴──────────┴──────────┘

Test Plan: plan_20240115_103000
Test Items: 12

Test Breakdown by Type:
┌───────────────┬───────┬────────────────┐
│ Test Type     │ Count │ Priority Range │
├───────────────┼───────┼────────────────┤
│ unit          │ 4     │ 1-2            │
│ integration   │ 3     │ 2-3            │
│ concurrency   │ 2     │ 1-2            │
│ stress        │ 2     │ 3-4            │
│ leak          │ 1     │ 2              │
└───────────────┴───────┴────────────────┘
```

### 2. JSON Report (`reports/plan_*.json`)

```json
{
  "plan_id": "plan_20240115_103000",
  "created_at": "2024-01-15T10:30:00",
  "branch": "feature/new-api",
  "changes_summary": "Changes: 5 files, +195/-17 lines",
  "test_items": [
    {
      "id": "test_001",
      "objective": "Verify new API handler concurrent request safety",
      "test_type": "concurrency",
      "scope": ["pkg/api"],
      "prerequisites": ["mock database", "test server"],
      "metrics": ["race conditions", "goroutine count", "response time"],
      "pass_criteria": "No race conditions, all goroutines cleaned up",
      "estimated_duration": "5m",
      "priority": 1
    }
  ],
  "stopping_criteria": [
    "All tests pass and no regression or leak is detected",
    "Maximum iterations (3) reached"
  ],
  "resource_limits": {
    "cpu": "4 cores",
    "memory": "8GB"
  }
}
```

### 3. Markdown Report (`reports/plan_*.md`)

```markdown
# Test Plan: plan_20240115_103000

**Created:** 2024-01-15T10:30:00
**Branch:** feature/new-api

## Changes Summary

Changes: 5 files, +195/-17 lines
  modified: 3 files
  added: 2 files

## Test Items

### Priority 1 (3 tests)

#### test_001: Verify new API handler concurrent request safety
- **Type:** concurrency
- **Scope:** pkg/api
- **Duration:** 5m
- **Pass Criteria:** No race conditions, all goroutines cleaned up
- **Prerequisites:** mock database, test server
- **Metrics:** race conditions, goroutine count, response time
```

## Test Plan Structure

Each test plan includes:

### Test Types

1. **Unit Tests** - Isolated function testing
   - Function inputs/outputs
   - Edge cases and boundaries
   - Error handling

2. **Integration Tests** - Component interaction testing
   - Database operations
   - External service calls
   - Message queue operations

3. **Concurrency Tests** - Race condition and goroutine safety
   - Data races (using `-race` flag)
   - Goroutine leaks
   - Channel operations
   - Mutex usage

4. **Stress Tests** - Load and performance testing
   - High throughput scenarios
   - Latency under load
   - Resource exhaustion

5. **Leak Detection** - Memory and goroutine leak detection
   - Long-running soak tests
   - Heap profiling (pprof)
   - Goroutine profiling

6. **Benchmarks** - Performance microbenchmarks
   - `testing.B` benchmarks
   - CPU profiling
   - Memory allocation analysis

### Go-Specific Focus Areas

The agent specifically looks for:

- **Goroutine leaks**: Unclosed goroutines, missing context cancellation
- **Race conditions**: Concurrent access to shared memory
- **Channel deadlocks**: Improper channel usage
- **Context handling**: Missing timeout/cancellation
- **Resource cleanup**: Deferred closes, connection management
- **Error handling**: Proper error propagation

## Configuration

### Environment Variables

```bash
# LLM Provider
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=openai
MODEL_NAME=gpt-4

# Agent Settings
MAX_ITERATIONS=3
PER_RUN_TIMEOUT=30m
SOAK_DURATION=30m

# Resource Limits
CPU_CORES=4
MEMORY_GB=8
DISK_GB=10

# Thresholds
MEMORY_GROWTH_THRESHOLD=25
GOROUTINE_GROWTH_THRESHOLD=10
```

### Custom Prompts

Edit `config/prompts.yaml` to customize test strategies and focus areas.

## Workflow

The agent follows the autonomous testing workflow:

```
1. OBSERVE
   ├─ Detect code changes (git)
   ├─ Analyze repository structure
   └─ Identify affected components

2. PLAN
   ├─ Analyze change impact and risk
   ├─ Generate test strategy
   ├─ Prioritize test items
   └─ Estimate resource needs

3. ACT (Future)
   ├─ Generate Go test files
   ├─ Create benchmarks
   ├─ Set up test harnesses
   └─ Configure profiling

4. MONITOR (Future)
   ├─ Execute tests
   ├─ Collect metrics
   └─ Capture artifacts

5. ANALYZE (Future)
   ├─ Parse test results
   ├─ Detect regressions
   ├─ Identify leaks
   └─ Find bottlenecks

6. LEARN (Future)
   ├─ Iterate on failures
   ├─ Refine tests
   └─ Update documentation
```

**Current POC Status**: Phases 1-2 (Observe & Plan) are implemented. Phases 3-6 are planned for future iterations.

## Advanced Usage

### Custom Analysis

```python
from agent import AITestAgent
from git_analyzer import GitAnalyzer

# Custom git analysis
git_analyzer = GitAnalyzer("/path/to/repo")
changes = git_analyzer.compare_branches("main", "feature-branch")

# Filter changes (e.g., only Go files)
go_changes = [c for c in changes if c.file_path.endswith('.go')]

# Custom test plan generation
agent = AITestAgent("/path/to/repo")
observation = {
    "changes": go_changes,
    "repo_context": {"language": "Go", "module": "myapp"},
    "branch": "feature-branch"
}
test_plan = agent.plan(observation)
```

### Integration with CI/CD

```yaml
# .github/workflows/test-planning.yml
name: AI Test Planning

on:
  pull_request:
    branches: [main, master]

jobs:
  generate-test-plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install AI Test Agent
        run: |
          cd example/ai_test_agent
          pip install -r requirements.txt

      - name: Generate Test Plan
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          cd example/ai_test_agent
          python src/cli.py compare-branches \
            --base-branch ${{ github.base_ref }} \
            --compare-branch ${{ github.head_ref }}

      - name: Upload Test Plan
        uses: actions/upload-artifact@v3
        with:
          name: test-plan
          path: example/ai_test_agent/reports/
```

## Troubleshooting

### API Key Issues

If you see `API key not provided`:

```bash
# Verify environment variable is set
echo $OPENAI_API_KEY

# Or pass directly
python src/cli.py analyze-uncommitted --api-key sk-your-key-here
```

### Git Repository Issues

If you see `not a git repository`:

```bash
# Verify you're in a git repo
git status

# Or specify path explicitly
python src/cli.py analyze-uncommitted --repo-path /path/to/repo
```

### No Changes Detected

If no changes are found:

```bash
# Check git status
git status
git diff HEAD

# For branch comparison, ensure branches exist
git branch -a
```

## Roadmap

- [x] Phase 1: Observe - Git change detection
- [x] Phase 2: Plan - Test strategy generation
- [ ] Phase 3: Act - Test code generation
- [ ] Phase 4: Monitor - Test execution and metrics collection
- [ ] Phase 5: Analyze - Result analysis and diagnostics
- [ ] Phase 6: Learn - Iterative improvement

## Contributing

This is a POC demonstrating the concept of autonomous test planning. Contributions are welcome!

## License

MIT License

## References

- [Go Testing Documentation](https://golang.org/pkg/testing/)
- [Go Race Detector](https://golang.org/doc/articles/race_detector.html)
- [pprof Profiling](https://golang.org/pkg/runtime/pprof/)
- [Benchstat](https://pkg.go.dev/golang.org/x/perf/cmd/benchstat)
