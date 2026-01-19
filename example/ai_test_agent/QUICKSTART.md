# Quick Start Guide

Get started with the AI Test Agent in 5 minutes!

## Prerequisites

- Python 3.8+
- Git repository with Go code
- OpenAI or Anthropic API key

## Installation

```bash
# Navigate to the agent directory
cd example/ai_test_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up API key
export OPENAI_API_KEY="sk-your-api-key-here"
```

## Quick Demo (No API Key Required)

Run the demo to see what the agent can do:

```bash
python demo.py
```

This shows:
- Git change detection
- Test plan structure
- Go-specific testing concerns
- Generated test commands
- Complete workflow phases

## Basic Usage

### 1. Analyze Your Current Changes

```bash
cd /path/to/your/go/project
python /path/to/example/ai_test_agent/src/cli.py analyze-uncommitted
```

This analyzes all your uncommitted changes and generates a test plan.

### 2. Compare Two Branches

```bash
python src/cli.py compare-branches \
  --base-branch master \
  --compare-branch feature/my-feature
```

Perfect for reviewing test needs before merging a PR.

### 3. Analyze a Specific Commit

```bash
python src/cli.py analyze-commit --commit-sha abc123def
```

Great for understanding what tests should have been added for a commit.

## Output Files

After running, check these directories:

```bash
reports/
  ├── plan_20240115_103000.json      # Machine-readable test plan
  └── plan_20240115_103000.md        # Human-readable report

artifacts/
  └── (test execution artifacts)      # Future: test results, profiles
```

## What You Get

The agent generates a comprehensive test plan including:

✓ **Unit Tests** - For new/modified functions
✓ **Integration Tests** - For component interactions
✓ **Concurrency Tests** - Race conditions, goroutine safety
✓ **Stress Tests** - Load and performance testing
✓ **Leak Detection** - Memory and goroutine leaks
✓ **Benchmarks** - Performance regression detection

## Example Output

```
Test Plan: plan_20240115_103000
Test Items: 12

High Priority Tests:
  [test_001] Verify goroutine handling in HandleRequest is safe
  [test_002] Test UserService.GetUser error handling
  [test_003] Detect memory leaks in long-running operations
```

## Next Steps

1. **Review the Test Plan**: Open the generated `.md` file
2. **Prioritize Tests**: Focus on Priority 1-2 items first
3. **Implement Tests**: Use the plan as a guide
4. **Run Tests**: Follow the suggested Go commands

## Programmatic Usage

```python
from agent import AITestAgent

agent = AITestAgent(
    repo_path="/path/to/repo",
    llm_provider="openai",
    model="gpt-4"
)

result = agent.run(mode="uncommitted")
test_plan = result["test_plan"]

print(f"Generated {len(test_plan.test_items)} test items")
```

## Configuration

### Use Anthropic Claude Instead

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key"

python src/cli.py analyze-uncommitted \
  --llm-provider anthropic \
  --model claude-3-5-sonnet-20241022
```

### Custom Settings

Edit `.env` file:

```bash
cp .env.example .env
# Edit .env with your preferences
```

## Troubleshooting

**"No changes detected"**
→ Make sure you have uncommitted changes: `git status`

**"API key not provided"**
→ Set environment variable: `export OPENAI_API_KEY=sk-...`

**"Not a git repository"**
→ Run from a git repository or use `--repo-path`

## Learn More

- Full documentation: [README.md](README.md)
- Prompt customization: [config/prompts.yaml](config/prompts.yaml)
- Example workflow: Run `python demo.py`

## Support

For issues or questions:
- Check the full [README.md](README.md)
- Review the demo: `python demo.py`
- Check example outputs in `reports/`

---

**Happy Testing!** 🚀
