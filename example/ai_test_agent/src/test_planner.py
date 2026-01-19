"""
Test Plan Generator
Uses LLM to analyze code changes and generate comprehensive test plans.
"""

import json
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TestItem:
    """Represents a single test item in the test plan."""
    id: str
    objective: str
    test_type: str  # unit, integration, e2e, exception, concurrency, stress, leak, benchmark
    scope: List[str]  # packages or files
    prerequisites: List[str]
    metrics: List[str]
    pass_criteria: str
    estimated_duration: str
    priority: int  # 1-5, 1 being highest


@dataclass
class TestPlan:
    """Comprehensive test plan for code changes."""
    plan_id: str
    created_at: str
    commit_sha: Optional[str]
    branch: str
    changes_summary: str
    test_items: List[TestItem]
    stopping_criteria: List[str]
    resource_limits: Dict[str, str]
    iterations: int = 3


class TestPlanner:
    """Generates test plans using LLM analysis."""

    def __init__(self, llm_client, model: str = "gpt-4"):
        """
        Initialize TestPlanner.

        Args:
            llm_client: LLM client (OpenAI or Anthropic)
            model: Model name to use
        """
        self.llm_client = llm_client
        self.model = model
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load the test engineer system prompt."""
        return """You are an autonomous AI Test Engineer for Golang services.
Your goal: autonomously plan, generate, execute, diagnose, and iterate on test suites that cover functional, exception, stress, memory-leak, goroutine-leak, and performance bottleneck detection for a given Go application repository or artifact.

You MUST follow the Observe → Plan → Act → Monitor → Analyze → Learn loop until stopping criteria are met, while obeying the safety rules and resource limits below.

CAPABILITIES:
- Inspect repository files, run shell commands, run `go test`, run benchmarks
- Start and stop test harnesses (docker / k8s), collect and analyze profiling data (pprof, trace)
- Run stress/load tools, parse logs, create/patch test files
- Produce runnable Go unit tests, integration tests, `testing.B` benchmarks
- Instrument code and tests for `pprof` (cpu/heap/block/mutex/goroutine)
- Use standard Go tools: go test, go test -bench, benchstat, pprof, go tool trace, go test -race

ANALYSIS APPROACH:
1. Observe: Analyze code changes and existing test coverage
2. Plan: Create prioritized test strategy based on risk and change impact
3. Identify test types needed: unit, integration, exception, concurrency, stress, leak detection
4. Consider Go-specific concerns: goroutine leaks, race conditions, memory management

OUTPUT REQUIREMENTS:
- Return a structured JSON test plan
- Include specific test objectives, scope, prerequisites, metrics, and pass criteria
- Prioritize tests based on code change risk and impact
- Consider resource constraints and iteration limits"""

    def generate_test_plan(
        self,
        changes: List,  # List of CodeChange objects
        repo_context: Dict[str, any],
        commit_sha: Optional[str] = None,
        branch: str = "unknown"
    ) -> TestPlan:
        """
        Generate a comprehensive test plan based on code changes.

        Args:
            changes: List of CodeChange objects
            repo_context: Repository context (structure, dependencies, etc.)
            commit_sha: Optional commit SHA
            branch: Current branch name

        Returns:
            TestPlan object
        """
        logger.info(f"Generating test plan for {len(changes)} changes")

        # Prepare changes summary
        changes_summary = self._summarize_changes(changes)

        # Prepare analysis prompt
        analysis_prompt = self._create_analysis_prompt(changes, repo_context)

        # Call LLM to generate test plan
        response = self._call_llm(analysis_prompt)

        # Parse response into structured test plan
        test_items = self._parse_test_items(response)

        # Create test plan
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_plan = TestPlan(
            plan_id=plan_id,
            created_at=datetime.now().isoformat(),
            commit_sha=commit_sha,
            branch=branch,
            changes_summary=changes_summary,
            test_items=test_items,
            stopping_criteria=[
                "All tests pass and no regression or leak is detected",
                "Maximum iterations (3) reached",
                "Resource budget exceeded",
                "Human operator issues stop command"
            ],
            resource_limits={
                "cpu": "4 cores",
                "memory": "8GB",
                "disk": "10GB",
                "per_run_timeout": "30m",
                "soak_duration": "30m"
            },
            iterations=3
        )

        return test_plan

    def _summarize_changes(self, changes: List) -> str:
        """Create a summary of code changes."""
        summary_parts = []

        file_count = len(changes)
        total_additions = sum(c.additions for c in changes)
        total_deletions = sum(c.deletions for c in changes)

        summary_parts.append(
            f"Changes: {file_count} files, +{total_additions}/-{total_deletions} lines"
        )

        # Group by change type
        by_type = {}
        for change in changes:
            by_type.setdefault(change.change_type, []).append(change.file_path)

        for change_type, files in by_type.items():
            summary_parts.append(f"  {change_type}: {len(files)} files")

        return "\n".join(summary_parts)

    def _create_analysis_prompt(self, changes: List, repo_context: Dict) -> str:
        """Create the analysis prompt for the LLM."""
        prompt_parts = [
            "# Code Change Analysis Request\n",
            "## Repository Context",
            f"Language: {repo_context.get('language', 'Go')}",
            f"Module: {repo_context.get('module', 'unknown')}",
            f"Test Framework: {repo_context.get('test_framework', 'Go testing')}",
            "\n## Code Changes\n"
        ]

        for change in changes:
            prompt_parts.append(f"\n### {change.file_path} ({change.change_type})")
            prompt_parts.append(f"Lines: +{change.additions}/-{change.deletions}")
            prompt_parts.append("\n```diff")
            prompt_parts.append(change.diff_content)
            prompt_parts.append("```\n")

        prompt_parts.append("\n## Task")
        prompt_parts.append("""
Analyze the code changes above and generate a comprehensive test plan.

For each code change, determine:
1. What functionality is affected?
2. What are the risk areas (race conditions, memory leaks, error handling)?
3. What test types are needed (unit, integration, stress, leak detection)?
4. What specific test scenarios should be covered?
5. What metrics should be collected?

Return a JSON array of test items with this structure:
[
  {
    "id": "test_001",
    "objective": "Verify new function handles concurrent requests safely",
    "test_type": "concurrency",
    "scope": ["pkg/handler"],
    "prerequisites": ["mock database", "test server"],
    "metrics": ["race conditions", "goroutine count", "response time"],
    "pass_criteria": "No race conditions, goroutines properly cleaned up",
    "estimated_duration": "5m",
    "priority": 1
  }
]

Focus on Go-specific concerns:
- Goroutine leaks
- Race conditions (-race flag)
- Memory management (pprof)
- Channel deadlocks
- Context cancellation
- Error handling
""")

        return "\n".join(prompt_parts)

    def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM with the analysis prompt.

        Args:
            prompt: Analysis prompt

        Returns:
            LLM response text
        """
        try:
            # This is a generic interface - actual implementation depends on the LLM client
            if hasattr(self.llm_client, 'chat'):
                # OpenAI-style client
                response = self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
                return response.choices[0].message.content
            elif hasattr(self.llm_client, 'messages'):
                # Anthropic-style client
                response = self.llm_client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    system=self.system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            else:
                raise ValueError("Unsupported LLM client")

        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            raise

    def _parse_test_items(self, response: str) -> List[TestItem]:
        """
        Parse LLM response into TestItem objects.

        Args:
            response: LLM response text

        Returns:
            List of TestItem objects
        """
        # Extract JSON from response (might be wrapped in markdown code blocks)
        json_start = response.find('[')
        json_end = response.rfind(']') + 1

        if json_start == -1 or json_end == 0:
            logger.warning("No JSON array found in response, creating default test items")
            return self._create_default_test_items()

        json_str = response[json_start:json_end]

        try:
            items_data = json.loads(json_str)
            test_items = []

            for item in items_data:
                test_item = TestItem(
                    id=item.get('id', f'test_{len(test_items) + 1:03d}'),
                    objective=item.get('objective', ''),
                    test_type=item.get('test_type', 'unit'),
                    scope=item.get('scope', []),
                    prerequisites=item.get('prerequisites', []),
                    metrics=item.get('metrics', []),
                    pass_criteria=item.get('pass_criteria', ''),
                    estimated_duration=item.get('estimated_duration', '5m'),
                    priority=item.get('priority', 3)
                )
                test_items.append(test_item)

            return test_items

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            return self._create_default_test_items()

    def _create_default_test_items(self) -> List[TestItem]:
        """Create default test items if parsing fails."""
        return [
            TestItem(
                id="test_001",
                objective="Run baseline unit tests",
                test_type="unit",
                scope=["./..."],
                prerequisites=["Go toolchain"],
                metrics=["test coverage", "pass rate"],
                pass_criteria="All tests pass",
                estimated_duration="5m",
                priority=1
            )
        ]

    def save_test_plan(self, test_plan: TestPlan, output_path: Path):
        """
        Save test plan to JSON file.

        Args:
            test_plan: TestPlan object
            output_path: Path to save the plan
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        plan_dict = asdict(test_plan)

        with open(output_path, 'w') as f:
            json.dump(plan_dict, f, indent=2)

        logger.info(f"Test plan saved to {output_path}")

    def generate_human_report(self, test_plan: TestPlan) -> str:
        """
        Generate a human-readable report from test plan.

        Args:
            test_plan: TestPlan object

        Returns:
            Markdown formatted report
        """
        lines = [
            f"# Test Plan: {test_plan.plan_id}\n",
            f"**Created:** {test_plan.created_at}",
            f"**Branch:** {test_plan.branch}",
            f"**Commit:** {test_plan.commit_sha or 'N/A'}",
            f"\n## Changes Summary\n",
            test_plan.changes_summary,
            f"\n## Test Strategy\n",
            f"**Iterations:** {test_plan.iterations}",
            f"\n### Resource Limits",
        ]

        for key, value in test_plan.resource_limits.items():
            lines.append(f"- **{key}:** {value}")

        lines.append("\n## Test Items\n")

        # Group by priority
        by_priority = {}
        for item in test_plan.test_items:
            by_priority.setdefault(item.priority, []).append(item)

        for priority in sorted(by_priority.keys()):
            items = by_priority[priority]
            lines.append(f"\n### Priority {priority} ({len(items)} tests)\n")

            for item in items:
                lines.append(f"\n#### {item.id}: {item.objective}")
                lines.append(f"- **Type:** {item.test_type}")
                lines.append(f"- **Scope:** {', '.join(item.scope)}")
                lines.append(f"- **Duration:** {item.estimated_duration}")
                lines.append(f"- **Pass Criteria:** {item.pass_criteria}")

                if item.prerequisites:
                    lines.append(f"- **Prerequisites:** {', '.join(item.prerequisites)}")

                if item.metrics:
                    lines.append(f"- **Metrics:** {', '.join(item.metrics)}")

        lines.append("\n## Stopping Criteria\n")
        for criterion in test_plan.stopping_criteria:
            lines.append(f"- {criterion}")

        return "\n".join(lines)
