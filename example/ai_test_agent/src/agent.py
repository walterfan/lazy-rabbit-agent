"""
AI Test Agent
Autonomous test planning and generation agent for Golang services.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

from git_analyzer import GitAnalyzer, CodeChange
from test_planner import TestPlanner, TestPlan

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AITestAgent:
    """
    Autonomous AI Test Engineer Agent.

    Follows the Observe → Plan → Act → Monitor → Analyze → Learn loop.
    """

    def __init__(
        self,
        repo_path: str = ".",
        llm_provider: str = "openai",
        model: str = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize AI Test Agent.

        Args:
            repo_path: Path to git repository
            llm_provider: LLM provider ('openai' or 'anthropic')
            model: Model name (defaults based on provider)
            api_key: API key for LLM provider
        """
        self.repo_path = Path(repo_path).resolve()
        self.git_analyzer = GitAnalyzer(str(self.repo_path))
        self.llm_provider = llm_provider

        # Initialize LLM client
        self.llm_client = self._init_llm_client(llm_provider, api_key)

        # Set default model if not provided
        if model is None:
            model = "gpt-4" if llm_provider == "openai" else "claude-3-5-sonnet-20241022"

        self.test_planner = TestPlanner(self.llm_client, model)

        # Create output directories
        self.reports_dir = self.repo_path / "reports"
        self.artifacts_dir = self.repo_path / "artifacts"
        self.reports_dir.mkdir(exist_ok=True)
        self.artifacts_dir.mkdir(exist_ok=True)

        logger.info(f"AI Test Agent initialized for {self.repo_path}")
        logger.info(f"LLM Provider: {llm_provider}, Model: {model}")

    def _init_llm_client(self, provider: str, api_key: Optional[str]):
        """Initialize LLM client based on provider."""
        if provider == "openai":
            try:
                from openai import OpenAI
                api_key = api_key or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OpenAI API key not provided")
                return OpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")

        elif provider == "anthropic":
            try:
                from anthropic import Anthropic
                api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("Anthropic API key not provided")
                return Anthropic(api_key=api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")

        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def observe(self, mode: str = "uncommitted", **kwargs) -> Dict:
        """
        OBSERVE phase: Discover and analyze code changes.

        Args:
            mode: Change detection mode ('uncommitted', 'branch', 'commit')
            **kwargs: Additional arguments based on mode
                - branch mode: base_branch, compare_branch
                - commit mode: commit_sha

        Returns:
            Dictionary with observation results
        """
        logger.info(f"=== OBSERVE Phase (mode: {mode}) ===")

        # Get code changes based on mode
        if mode == "uncommitted":
            changes = self.git_analyzer.get_uncommitted_changes()
        elif mode == "branch":
            base_branch = kwargs.get("base_branch", "master")
            compare_branch = kwargs.get("compare_branch") or self.git_analyzer.get_current_branch()
            changes = self.git_analyzer.compare_branches(base_branch, compare_branch)
        elif mode == "commit":
            commit_sha = kwargs.get("commit_sha", "HEAD")
            changes = self.git_analyzer.get_commit_changes(commit_sha)
        else:
            raise ValueError(f"Invalid mode: {mode}")

        logger.info(f"Found {len(changes)} changed files")

        # Analyze repository structure
        repo_context = self._analyze_repo_structure()

        # Get current branch and commit info
        current_branch = self.git_analyzer.get_current_branch()
        commit_sha = kwargs.get("commit_sha") if mode == "commit" else None

        observation = {
            "mode": mode,
            "changes": changes,
            "change_count": len(changes),
            "repo_context": repo_context,
            "branch": current_branch,
            "commit_sha": commit_sha,
            "timestamp": datetime.now().isoformat()
        }

        return observation

    def plan(self, observation: Dict) -> TestPlan:
        """
        PLAN phase: Generate comprehensive test strategy.

        Args:
            observation: Results from observe phase

        Returns:
            TestPlan object
        """
        logger.info("=== PLAN Phase ===")

        test_plan = self.test_planner.generate_test_plan(
            changes=observation["changes"],
            repo_context=observation["repo_context"],
            commit_sha=observation.get("commit_sha"),
            branch=observation["branch"]
        )

        logger.info(f"Generated test plan with {len(test_plan.test_items)} test items")

        # Save test plan
        plan_file = self.reports_dir / f"{test_plan.plan_id}.json"
        self.test_planner.save_test_plan(test_plan, plan_file)

        # Generate and save human-readable report
        report = self.test_planner.generate_human_report(test_plan)
        report_file = self.reports_dir / f"{test_plan.plan_id}.md"
        report_file.write_text(report)

        logger.info(f"Test plan saved to {plan_file}")
        logger.info(f"Human report saved to {report_file}")

        return test_plan

    def act(self, test_plan: TestPlan) -> Dict:
        """
        ACT phase: Generate test code based on plan.

        Args:
            test_plan: Test plan to execute

        Returns:
            Dictionary with generated artifacts
        """
        logger.info("=== ACT Phase ===")
        logger.info("Test code generation will be implemented in future iterations")

        # TODO: Implement test code generation
        # - Generate Go test files based on test items
        # - Create test fixtures and mocks
        # - Generate benchmark tests
        # - Create stress test scripts

        artifacts = {
            "test_files": [],
            "benchmark_files": [],
            "stress_scripts": [],
            "status": "planned"
        }

        return artifacts

    def run(
        self,
        mode: str = "uncommitted",
        auto_generate: bool = False,
        **kwargs
    ) -> Dict:
        """
        Run the complete agent workflow.

        Args:
            mode: Change detection mode
            auto_generate: Whether to automatically generate test code
            **kwargs: Additional arguments for observe phase

        Returns:
            Dictionary with all results
        """
        logger.info("=== AI Test Agent Starting ===")

        try:
            # Phase 1: Observe
            observation = self.observe(mode=mode, **kwargs)

            if observation["change_count"] == 0:
                logger.warning("No changes detected. Nothing to test.")
                return {
                    "status": "no_changes",
                    "observation": observation
                }

            # Phase 2: Plan
            test_plan = self.plan(observation)

            # Phase 3: Act (if auto_generate enabled)
            artifacts = None
            if auto_generate:
                artifacts = self.act(test_plan)

            result = {
                "status": "success",
                "observation": observation,
                "test_plan": test_plan,
                "artifacts": artifacts,
                "reports": {
                    "plan_json": str(self.reports_dir / f"{test_plan.plan_id}.json"),
                    "plan_markdown": str(self.reports_dir / f"{test_plan.plan_id}.md")
                }
            }

            logger.info("=== AI Test Agent Completed Successfully ===")
            return result

        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }

    def _analyze_repo_structure(self) -> Dict:
        """
        Analyze repository structure and dependencies.

        Returns:
            Dictionary with repository context
        """
        context = {
            "language": "Go",
            "test_framework": "Go testing"
        }

        # Check for go.mod
        go_mod = self.repo_path / "go.mod"
        if go_mod.exists():
            try:
                content = go_mod.read_text()
                # Extract module name
                for line in content.split('\n'):
                    if line.startswith('module '):
                        context["module"] = line.split()[1]
                        break
            except Exception as e:
                logger.warning(f"Error reading go.mod: {e}")

        # Check for common test patterns
        test_files = list(self.repo_path.rglob("*_test.go"))
        context["existing_tests"] = len(test_files)

        # Check for benchmark files
        benchmark_files = []
        for test_file in test_files:
            content = test_file.read_text()
            if "Benchmark" in content:
                benchmark_files.append(str(test_file))
        context["existing_benchmarks"] = len(benchmark_files)

        return context
