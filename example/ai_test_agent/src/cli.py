#!/usr/bin/env python3
"""
AI Test Agent CLI
Command-line interface for the autonomous test agent.
"""

import sys
import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from agent import AITestAgent

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    AI Test Agent - Autonomous test planning for Golang services.

    Analyzes code changes and generates comprehensive test plans covering
    functional, stress, memory leak, goroutine leak, and performance tests.
    """
    pass


@cli.command()
@click.option(
    "--repo-path",
    type=click.Path(exists=True),
    default=".",
    help="Path to git repository"
)
@click.option(
    "--llm-provider",
    type=click.Choice(["openai", "anthropic"]),
    default="openai",
    help="LLM provider to use"
)
@click.option(
    "--model",
    type=str,
    help="Model name (defaults based on provider)"
)
@click.option(
    "--api-key",
    type=str,
    help="API key for LLM provider (or set OPENAI_API_KEY/ANTHROPIC_API_KEY env var)"
)
def analyze_uncommitted(repo_path, llm_provider, model, api_key):
    """
    Analyze uncommitted changes and generate test plan.

    Detects all staged and unstaged changes in the repository.
    """
    console.print("[bold cyan]AI Test Agent - Analyzing Uncommitted Changes[/bold cyan]\n")

    try:
        agent = AITestAgent(
            repo_path=repo_path,
            llm_provider=llm_provider,
            model=model,
            api_key=api_key
        )

        result = agent.run(mode="uncommitted")

        if result["status"] == "no_changes":
            console.print("[yellow]No changes detected in repository.[/yellow]")
            return

        if result["status"] == "error":
            console.print(f"[red]Error: {result['error']}[/red]")
            sys.exit(1)

        _display_results(result)

    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--repo-path",
    type=click.Path(exists=True),
    default=".",
    help="Path to git repository"
)
@click.option(
    "--base-branch",
    type=str,
    default="master",
    help="Base branch to compare against"
)
@click.option(
    "--compare-branch",
    type=str,
    help="Branch to compare (defaults to current branch)"
)
@click.option(
    "--llm-provider",
    type=click.Choice(["openai", "anthropic"]),
    default="openai",
    help="LLM provider to use"
)
@click.option(
    "--model",
    type=str,
    help="Model name (defaults based on provider)"
)
@click.option(
    "--api-key",
    type=str,
    help="API key for LLM provider"
)
def compare_branches(repo_path, base_branch, compare_branch, llm_provider, model, api_key):
    """
    Compare two branches and generate test plan.

    Detects all differences between base and compare branches.
    """
    console.print(f"[bold cyan]AI Test Agent - Comparing Branches[/bold cyan]\n")

    try:
        agent = AITestAgent(
            repo_path=repo_path,
            llm_provider=llm_provider,
            model=model,
            api_key=api_key
        )

        result = agent.run(
            mode="branch",
            base_branch=base_branch,
            compare_branch=compare_branch
        )

        if result["status"] == "no_changes":
            console.print(f"[yellow]No changes between {base_branch} and {compare_branch}.[/yellow]")
            return

        if result["status"] == "error":
            console.print(f"[red]Error: {result['error']}[/red]")
            sys.exit(1)

        _display_results(result)

    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--repo-path",
    type=click.Path(exists=True),
    default=".",
    help="Path to git repository"
)
@click.option(
    "--commit-sha",
    type=str,
    required=True,
    help="Git commit SHA to analyze"
)
@click.option(
    "--llm-provider",
    type=click.Choice(["openai", "anthropic"]),
    default="openai",
    help="LLM provider to use"
)
@click.option(
    "--model",
    type=str,
    help="Model name (defaults based on provider)"
)
@click.option(
    "--api-key",
    type=str,
    help="API key for LLM provider"
)
def analyze_commit(repo_path, commit_sha, llm_provider, model, api_key):
    """
    Analyze a specific commit and generate test plan.

    Detects all changes in the specified commit.
    """
    console.print(f"[bold cyan]AI Test Agent - Analyzing Commit {commit_sha}[/bold cyan]\n")

    try:
        agent = AITestAgent(
            repo_path=repo_path,
            llm_provider=llm_provider,
            model=model,
            api_key=api_key
        )

        result = agent.run(
            mode="commit",
            commit_sha=commit_sha
        )

        if result["status"] == "no_changes":
            console.print(f"[yellow]No changes in commit {commit_sha}.[/yellow]")
            return

        if result["status"] == "error":
            console.print(f"[red]Error: {result['error']}[/red]")
            sys.exit(1)

        _display_results(result)

    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)


def _display_results(result: dict):
    """Display agent execution results."""
    observation = result["observation"]
    test_plan = result["test_plan"]

    # Display observation summary
    console.print(Panel.fit(
        f"[bold]Repository:[/bold] {observation['branch']}\n"
        f"[bold]Changes:[/bold] {observation['change_count']} files\n"
        f"[bold]Timestamp:[/bold] {observation['timestamp']}",
        title="Observation",
        border_style="cyan"
    ))

    # Display changed files
    if observation["changes"]:
        console.print("\n[bold]Changed Files:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File")
        table.add_column("Type")
        table.add_column("Changes")

        for change in observation["changes"]:
            table.add_row(
                change.file_path,
                change.change_type,
                f"+{change.additions}/-{change.deletions}"
            )

        console.print(table)

    # Display test plan summary
    console.print(f"\n[bold]Test Plan:[/bold] {test_plan.plan_id}")
    console.print(f"[bold]Test Items:[/bold] {len(test_plan.test_items)}")

    # Group test items by type
    by_type = {}
    for item in test_plan.test_items:
        by_type.setdefault(item.test_type, []).append(item)

    console.print("\n[bold]Test Breakdown by Type:[/bold]")
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Test Type")
    table.add_column("Count")
    table.add_column("Priority Range")

    for test_type, items in sorted(by_type.items()):
        priorities = [item.priority for item in items]
        table.add_row(
            test_type,
            str(len(items)),
            f"{min(priorities)}-{max(priorities)}"
        )

    console.print(table)

    # Display top priority tests
    console.print("\n[bold]High Priority Tests (Priority 1-2):[/bold]")
    high_priority = [item for item in test_plan.test_items if item.priority <= 2]

    if high_priority:
        table = Table(show_header=True, header_style="bold yellow")
        table.add_column("ID")
        table.add_column("Objective")
        table.add_column("Type")
        table.add_column("Duration")

        for item in sorted(high_priority, key=lambda x: x.priority):
            table.add_row(
                item.id,
                item.objective[:50] + "..." if len(item.objective) > 50 else item.objective,
                item.test_type,
                item.estimated_duration
            )

        console.print(table)
    else:
        console.print("[dim]No high priority tests[/dim]")

    # Display report locations
    console.print("\n[bold green]Reports Generated:[/bold green]")
    console.print(f"  JSON: {result['reports']['plan_json']}")
    console.print(f"  Markdown: {result['reports']['plan_markdown']}")

    # Display markdown preview
    report_path = Path(result['reports']['plan_markdown'])
    if report_path.exists():
        console.print("\n[bold]Test Plan Preview:[/bold]")
        markdown_content = report_path.read_text()
        # Show first 1500 characters
        preview = markdown_content[:1500]
        if len(markdown_content) > 1500:
            preview += "\n\n... (see full report in file)"
        console.print(Markdown(preview))


if __name__ == "__main__":
    cli()
