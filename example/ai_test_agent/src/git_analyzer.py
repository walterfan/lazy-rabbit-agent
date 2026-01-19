"""
Git Change Analyzer
Detects and analyzes code changes using git commands.
"""

import subprocess
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodeChange:
    """Represents a code change detected by git."""
    file_path: str
    change_type: str  # added, modified, deleted
    diff_content: str
    additions: int
    deletions: int


class GitAnalyzer:
    """Analyzes git repository changes for test generation."""

    def __init__(self, repo_path: str = "."):
        """
        Initialize GitAnalyzer.

        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = Path(repo_path).resolve()
        self._validate_git_repo()

    def _validate_git_repo(self):
        """Validate that the path is a git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            raise ValueError(f"{self.repo_path} is not a git repository")

    def get_uncommitted_changes(self) -> List[CodeChange]:
        """
        Get uncommitted changes (staged and unstaged).

        Returns:
            List of CodeChange objects
        """
        logger.info("Detecting uncommitted changes...")

        # Get list of changed files
        result = subprocess.run(
            ["git", "diff", "HEAD", "--name-status"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        changes = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) < 2:
                continue

            status, file_path = parts[0], parts[1]

            # Get diff for this file
            diff = self._get_file_diff(file_path)
            stats = self._get_diff_stats(file_path)

            change_type = self._map_status_to_type(status)

            changes.append(CodeChange(
                file_path=file_path,
                change_type=change_type,
                diff_content=diff,
                additions=stats['additions'],
                deletions=stats['deletions']
            ))

        return changes

    def compare_branches(self, base_branch: str, compare_branch: str) -> List[CodeChange]:
        """
        Compare two branches and get the differences.

        Args:
            base_branch: Base branch name (e.g., 'main', 'master')
            compare_branch: Branch to compare (e.g., 'feature/new-feature')

        Returns:
            List of CodeChange objects
        """
        logger.info(f"Comparing {base_branch}...{compare_branch}")

        # Get list of changed files between branches
        result = subprocess.run(
            ["git", "diff", f"{base_branch}...{compare_branch}", "--name-status"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        changes = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) < 2:
                continue

            status, file_path = parts[0], parts[1]

            # Get diff for this file
            diff = self._get_file_diff(file_path, f"{base_branch}...{compare_branch}")
            stats = self._get_diff_stats(file_path, f"{base_branch}...{compare_branch}")

            change_type = self._map_status_to_type(status)

            changes.append(CodeChange(
                file_path=file_path,
                change_type=change_type,
                diff_content=diff,
                additions=stats['additions'],
                deletions=stats['deletions']
            ))

        return changes

    def get_commit_changes(self, commit_sha: str) -> List[CodeChange]:
        """
        Get changes from a specific commit.

        Args:
            commit_sha: Git commit SHA

        Returns:
            List of CodeChange objects
        """
        logger.info(f"Analyzing commit {commit_sha}")

        # Get list of changed files in commit
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-status", "-r", commit_sha],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        changes = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) < 2:
                continue

            status, file_path = parts[0], parts[1]

            # Get diff for this file
            diff = self._get_commit_file_diff(commit_sha, file_path)
            stats = self._get_commit_diff_stats(commit_sha, file_path)

            change_type = self._map_status_to_type(status)

            changes.append(CodeChange(
                file_path=file_path,
                change_type=change_type,
                diff_content=diff,
                additions=stats['additions'],
                deletions=stats['deletions']
            ))

        return changes

    def _get_file_diff(self, file_path: str, ref: Optional[str] = None) -> str:
        """Get diff content for a specific file."""
        cmd = ["git", "diff"]
        if ref:
            cmd.append(ref)
        else:
            cmd.append("HEAD")
        cmd.extend(["--", file_path])

        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout

    def _get_commit_file_diff(self, commit_sha: str, file_path: str) -> str:
        """Get diff content for a file in a specific commit."""
        result = subprocess.run(
            ["git", "show", f"{commit_sha}:{file_path}"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout

    def _get_diff_stats(self, file_path: str, ref: Optional[str] = None) -> Dict[str, int]:
        """Get statistics for file changes."""
        cmd = ["git", "diff", "--numstat"]
        if ref:
            cmd.append(ref)
        else:
            cmd.append("HEAD")
        cmd.extend(["--", file_path])

        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            parts = result.stdout.strip().split('\t')
            return {
                'additions': int(parts[0]) if parts[0] != '-' else 0,
                'deletions': int(parts[1]) if parts[1] != '-' else 0
            }
        return {'additions': 0, 'deletions': 0}

    def _get_commit_diff_stats(self, commit_sha: str, file_path: str) -> Dict[str, int]:
        """Get statistics for file changes in a commit."""
        result = subprocess.run(
            ["git", "show", "--numstat", commit_sha, "--", file_path],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            parts = result.stdout.strip().split('\t')
            return {
                'additions': int(parts[0]) if parts[0] != '-' else 0,
                'deletions': int(parts[1]) if parts[1] != '-' else 0
            }
        return {'additions': 0, 'deletions': 0}

    def _map_status_to_type(self, status: str) -> str:
        """Map git status code to change type."""
        if status.startswith('A'):
            return 'added'
        elif status.startswith('M'):
            return 'modified'
        elif status.startswith('D'):
            return 'deleted'
        elif status.startswith('R'):
            return 'renamed'
        else:
            return 'unknown'

    def get_current_branch(self) -> str:
        """Get the current branch name."""
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    def get_commit_message(self, commit_sha: str = "HEAD") -> str:
        """Get commit message for a specific commit."""
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B", commit_sha],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
