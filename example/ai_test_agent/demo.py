#!/usr/bin/env python3
"""
Demo script showing how to use the AI Test Agent programmatically.

This demonstrates the core workflow without requiring actual API keys
(uses mock mode for demonstration).
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from git_analyzer import GitAnalyzer, CodeChange
from test_planner import TestPlan, TestItem


def demo_git_analysis():
    """Demonstrate git change detection."""
    print("=" * 80)
    print("DEMO: Git Change Analysis")
    print("=" * 80)

    # This would normally analyze your actual repo
    # For demo, we'll create sample changes
    sample_changes = [
        CodeChange(
            file_path="pkg/api/handler.go",
            change_type="modified",
            diff_content="""
@@ -10,6 +10,12 @@
 func HandleRequest(w http.ResponseWriter, r *http.Request) {
+    // Added concurrency handling
+    var wg sync.WaitGroup
+    wg.Add(1)
+    go func() {
+        defer wg.Done()
+        processRequest(r)
+    }()
+    wg.Wait()
 }
""",
            additions=7,
            deletions=0
        ),
        CodeChange(
            file_path="pkg/service/user.go",
            change_type="added",
            diff_content="""
+package service
+
+type UserService struct {
+    db *sql.DB
+}
+
+func (s *UserService) GetUser(id int) (*User, error) {
+    // TODO: Add caching
+    return s.db.QueryUser(id)
+}
""",
            additions=10,
            deletions=0
        )
    ]

    print(f"\nDetected {len(sample_changes)} code changes:\n")

    for change in sample_changes:
        print(f"  [{change.change_type.upper()}] {change.file_path}")
        print(f"    Lines: +{change.additions}/-{change.deletions}")

    return sample_changes


def demo_test_plan_structure():
    """Demonstrate test plan structure."""
    print("\n" + "=" * 80)
    print("DEMO: Test Plan Structure")
    print("=" * 80)

    # Create sample test plan
    test_items = [
        TestItem(
            id="test_001",
            objective="Verify goroutine handling in HandleRequest is safe",
            test_type="concurrency",
            scope=["pkg/api"],
            prerequisites=["mock server", "test data"],
            metrics=["race conditions", "goroutine count", "deadlock detection"],
            pass_criteria="No race conditions detected, all goroutines properly terminated",
            estimated_duration="5m",
            priority=1
        ),
        TestItem(
            id="test_002",
            objective="Test UserService.GetUser error handling",
            test_type="unit",
            scope=["pkg/service"],
            prerequisites=["mock database"],
            metrics=["code coverage", "error scenarios covered"],
            pass_criteria="All error paths tested, coverage > 80%",
            estimated_duration="3m",
            priority=2
        ),
        TestItem(
            id="test_003",
            objective="Detect memory leaks in long-running UserService operations",
            test_type="leak",
            scope=["pkg/service"],
            prerequisites=["test harness", "pprof enabled"],
            metrics=["heap growth", "goroutine count", "connection pool usage"],
            pass_criteria="No sustained heap growth, stable goroutine count",
            estimated_duration="30m",
            priority=2
        ),
        TestItem(
            id="test_004",
            objective="Stress test API endpoint under high load",
            test_type="stress",
            scope=["pkg/api"],
            prerequisites=["load generator", "monitoring"],
            metrics=["RPS", "p95 latency", "error rate"],
            pass_criteria="Handle 1000 RPS with p95 < 100ms, error rate < 0.1%",
            estimated_duration="10m",
            priority=3
        ),
        TestItem(
            id="test_005",
            objective="Benchmark UserService.GetUser performance",
            test_type="benchmark",
            scope=["pkg/service"],
            prerequisites=["test data", "benchstat"],
            metrics=["ops/sec", "allocs/op", "bytes/op"],
            pass_criteria="No significant regression vs baseline",
            estimated_duration="5m",
            priority=3
        )
    ]

    print("\nGenerated Test Plan with 5 test items:\n")

    # Group by type
    by_type = {}
    for item in test_items:
        by_type.setdefault(item.test_type, []).append(item)

    for test_type, items in sorted(by_type.items()):
        print(f"\n{test_type.upper()} TESTS ({len(items)}):")
        for item in items:
            print(f"  [{item.id}] {item.objective}")
            print(f"    Priority: {item.priority}, Duration: {item.estimated_duration}")
            print(f"    Pass Criteria: {item.pass_criteria}")

    return test_items


def demo_go_specific_concerns():
    """Demonstrate Go-specific testing concerns."""
    print("\n" + "=" * 80)
    print("DEMO: Go-Specific Testing Concerns")
    print("=" * 80)

    concerns = {
        "Goroutine Leaks": {
            "detection": "Monitor runtime.NumGoroutine() before/after test",
            "tools": ["pprof goroutine profile", "goleak library"],
            "example_test": "TestNoGoroutineLeak"
        },
        "Race Conditions": {
            "detection": "Run tests with -race flag",
            "tools": ["go test -race", "ThreadSanitizer"],
            "example_test": "TestConcurrentAccess"
        },
        "Memory Leaks": {
            "detection": "Compare heap profiles over time",
            "tools": ["pprof heap", "runtime.ReadMemStats"],
            "example_test": "TestMemoryUsage"
        },
        "Channel Deadlocks": {
            "detection": "Test timeout, static analysis",
            "tools": ["deadlock detector", "go vet"],
            "example_test": "TestChannelOperations"
        },
        "Context Cancellation": {
            "detection": "Verify context.Done() is checked",
            "tools": ["context inspection", "timeout tests"],
            "example_test": "TestContextCancellation"
        }
    }

    for concern, details in concerns.items():
        print(f"\n{concern}:")
        print(f"  Detection: {details['detection']}")
        print(f"  Tools: {', '.join(details['tools'])}")
        print(f"  Example: {details['example_test']}")


def demo_test_commands():
    """Demonstrate Go test commands."""
    print("\n" + "=" * 80)
    print("DEMO: Go Test Commands Generated")
    print("=" * 80)

    commands = {
        "Unit Tests with Coverage": "go test ./... -v -race -coverprofile=coverage.out",
        "View Coverage Report": "go tool cover -html=coverage.out",
        "Run Benchmarks": "go test -bench . -benchmem -benchtimeout 5m",
        "Compare Benchmarks": "benchstat old.txt new.txt",
        "Race Detection": "go test ./... -race -count=100",
        "CPU Profile": "go test -cpuprofile cpu.prof -bench .",
        "Heap Profile": "go test -memprofile mem.prof -bench .",
        "Analyze Profile": "go tool pprof -http=:6060 cpu.prof",
        "Goroutine Profile": "curl http://localhost:6060/debug/pprof/goroutine?debug=2",
        "Integration Tests": "go test ./... -tags=integration -v",
    }

    print("\nTest commands that would be generated:\n")
    for name, cmd in commands.items():
        print(f"{name}:")
        print(f"  $ {cmd}\n")


def demo_full_workflow():
    """Demonstrate the full agent workflow."""
    print("\n" + "=" * 80)
    print("DEMO: Complete Agent Workflow")
    print("=" * 80)

    phases = [
        ("1. OBSERVE", [
            "Detect code changes via git",
            "Analyze repository structure",
            "Identify affected components",
            "Assess change complexity and risk"
        ]),
        ("2. PLAN", [
            "Analyze change impact",
            "Generate test strategy",
            "Prioritize test items",
            "Estimate resource requirements",
            "Create stopping criteria"
        ]),
        ("3. ACT (Future)", [
            "Generate Go test files",
            "Create test fixtures and mocks",
            "Set up benchmark tests",
            "Configure profiling",
            "Prepare test harnesses"
        ]),
        ("4. MONITOR (Future)", [
            "Execute test suites",
            "Collect metrics and profiles",
            "Capture artifacts",
            "Track resource usage"
        ]),
        ("5. ANALYZE (Future)", [
            "Parse test results",
            "Detect regressions",
            "Identify memory/goroutine leaks",
            "Find performance bottlenecks",
            "Generate diagnostic reports"
        ]),
        ("6. LEARN (Future)", [
            "Iterate on failures",
            "Refine test strategies",
            "Update test documentation",
            "Improve test coverage"
        ])
    ]

    for phase, steps in phases:
        print(f"\n{phase}")
        for step in steps:
            status = "✓" if "Future" not in phase else "○"
            print(f"  {status} {step}")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print(" AI TEST AGENT - DEMONSTRATION")
    print("=" * 80)
    print("\nThis demo shows the capabilities of the AI Test Agent POC.")
    print("Note: This runs without requiring API keys.\n")

    try:
        # Demo 1: Git Analysis
        changes = demo_git_analysis()

        # Demo 2: Test Plan Structure
        test_items = demo_test_plan_structure()

        # Demo 3: Go-Specific Concerns
        demo_go_specific_concerns()

        # Demo 4: Test Commands
        demo_test_commands()

        # Demo 5: Full Workflow
        demo_full_workflow()

        print("\n" + "=" * 80)
        print("DEMO COMPLETE")
        print("=" * 80)
        print("\nTo use the real agent:")
        print("  1. Set up your API key: export OPENAI_API_KEY=sk-...")
        print("  2. Run: python src/cli.py analyze-uncommitted")
        print("\nFor more information, see README.md")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\nError running demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
