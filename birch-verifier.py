#!/usr/bin/env python3
"""
BIRCH Unified Verifier CLI — Combines 5-pass framework, PR verifier, diff scanner, and decision automation.
Usage: python3 birch-verifier.py <command> [options]
Commands:
  - monitor-pr: Monitor for new PR in terminator2-agent/agent-papers
  - verify-pr <pr_url>: Execute 5-pass verification on a PR
  - deepseek-verify <pr_url>: Run DeepSeek-V3.2's comprehensive verifier
  - check-links: Verify all 5 probe material links return HTTP 200
  - decide: Run decision automation against verification results
"""

import sys
import json
import time
from datetime import datetime
import argparse
from pathlib import Path

# Import modules
from modules.pr_monitor import PRMonitor
from modules.five_pass_verifier import FivePassVerifier
from modules.link_checker import LinkChecker
from modules.decision_engine import DecisionEngine
from modules.output_formatter import OutputFormatter
from modules.deepseek_verifier import DeepSeekVerifier


class BIRCHUnifiedVerifier:
    def __init__(self):
        self.pr_monitor = PRMonitor()
        self.verifier = FivePassVerifier()
        self.link_checker = LinkChecker()
        self.decision_engine = DecisionEngine()
        self.formatter = OutputFormatter()
        self.deepseek_verifier = DeepSeekVerifier()
        self.results = {}

    def monitor_pr(self, repo="terminator2-agent/agent-papers", interval=30):
        """Monitor PR repo for new v0.3 spec PR"""
        print(f"🔍 Starting PR monitor for {repo} (checking every {interval}s)...")
        return self.pr_monitor.monitor(repo, interval)

    def verify_pr(
        self,
        pr_url: str,
        enable_external_tools: bool = False,
        spec_path: str | None = None,
    ):
        """Execute comprehensive 5-pass verification.

        If ``enable_external_tools`` is True, this also invokes optional
        sidecar tools (DeepSeek verifier, GPT-5.2 scanner, encoding
        scan) and attaches their results under an ``external_tools``
        key in the returned structure.
        """
        print(f"📋 Starting 5-pass verification on {pr_url}...")
        print("=" * 60)

        results = self.verifier.execute_five_pass(
            pr_url,
            enable_external_tools=enable_external_tools,
            spec_path=spec_path,
        )
        self.results["verification"] = results

        # Format and display results
        self.formatter.print_verification_results(results)
        return results

    def deepseek_verify(self, pr_url):
        """Run DeepSeek-V3.2's comprehensive PR verifier"""
        print(f"🔍 Running DeepSeek-V3.2 PR verifier on {pr_url}...")
        print("=" * 60)

        if not self.deepseek_verifier.available:
            print("❌ DeepSeek verifier not available")
            print("Make sure ~/birch-tools/birch_pr_verifier.py exists")
            return None

        results = self.deepseek_verifier.verify_pr_from_url(pr_url)
        self.results["deepseek_verification"] = results

        # Display results
        self._print_deepseek_results(results)
        return results

    def _print_deepseek_results(self, results):
        """Format and display DeepSeek verifier results"""
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return

        print(f"\n📊 DeepSeek-V3.2 PR Verification Results")
        print("-" * 50)
        print(f"PR #{results.get('pr_number', 'N/A')}")
        print(f"Overall Status: {results.get('overall_status', 'UNKNOWN')}")
        print(f"Exit Code: {results.get('exit_code', 'N/A')}")

        if results.get("issues"):
            print(f"\n⚠️  Issues Found ({len(results['issues'])}):")
            for issue in results["issues"][:10]:  # Show first 10 issues
                print(f"  • {issue}")
            if len(results["issues"]) > 10:
                print(f"  ... and {len(results['issues']) - 10} more issues")

        if results.get("red_flags"):
            print(f"\n🚨 RED FLAGS ({len(results['red_flags'])}):")
            for flag in results["red_flags"]:
                print(f"  ⚠️  {flag}")

        checks = results.get("checks", {})
        if checks:
            print(f"\n✅ Detailed Checks:")

            # Core URLs
            core_urls = checks.get("core_urls", {})
            if core_urls:
                found = core_urls.get("found", 0)
                total = core_urls.get("total_expected", 5)
                print(f"  • Core Probe URLs: {found}/{total} found")

            # Amendment fields
            amendment_fields = checks.get("amendment_fields", {})
            if amendment_fields and amendment_fields.get("fields_found"):
                print(
                    f"  • Amendment Fields: {len(amendment_fields['fields_found'])} key fields found",
                )

            # Backward compatibility
            bc = checks.get("backward_compatibility", {})
            if bc:
                status = []
                if bc.get("recommended_not_required"):
                    status.append("RECOMMENDED ✓")
                if bc.get("should_language"):
                    status.append("SHOULD ✓")
                if bc.get("essential_marking"):
                    status.append("Essential ✓")
                if status:
                    print(f"  • Backward Compatibility: {', '.join(status)}")

            # Citations
            citations = checks.get("citations", {})
            if citations:
                status = []
                if citations.get("kappa_1_0"):
                    status.append("κ=1.0 ✓")
                if citations.get("mixed_hybrid"):
                    status.append("Mixed-Hybrid ✓")
                if status:
                    print(f"  • Citations: {', '.join(status)}")

            # JSON Schema
            schema = checks.get("json_schema", {})
            if schema:
                if schema.get("found"):
                    print("  • JSON Schema: Found")
                if schema.get("valid"):
                    print("  • JSON Schema: Valid")

        print(f"\n📋 Details:")
        for detail in results.get("details", []):
            print(f"  • {detail}")

        # Decision input
        decision_input = self.deepseek_verifier.get_decision_input()
        if decision_input:
            print(f"\n⚖️  Decision-Relevant Checks:")
            for key, value in decision_input.items():
                status = "✓" if value else "✗"
                print(f"  {status} {key}")

    def check_probe_links(self):
        """Verify all 5 probe material links"""
        print("🔗 Checking all 5 probe material links...")
        probe_links = [
            "https://github.com/ai-village-agents/framework-reflections-2026/blob/main/analysis/pre-registered-scoring-rubric-structural-determinism-probe.md",
            "https://github.com/ai-village-agents/framework-reflections-2026/blob/main/analysis/structural-determinism-probe-results/all-responses.md",
            "https://github.com/ai-village-agents/framework-reflections-2026/blob/main/analysis/structural-determinism-probe/final-analysis-report.md",
            "https://github.com/ai-village-agents/framework-reflections-2026/blob/main/papers/domain-constrained-metaphor-probe-methodology.md",
            "https://github.com/ai-village-agents/framework-reflections-2026/blob/main/analysis/probe-summary-for-birch-v0.3.md",
        ]

        results = self.link_checker.verify_links(probe_links)
        self.results["probe_links"] = results

        self.formatter.print_link_results(results)
        return results

    def make_decision(self):
        """Run decision automation engine"""
        print("\n⚖️  Running decision automation engine...")
        if not self.results.get("verification"):
            print("❌ No verification results. Run 'verify-pr' first.")
            return None

        decision = self.decision_engine.evaluate(self.results["verification"])
        self.results["decision"] = decision

        self.formatter.print_decision(decision)
        return decision

    def export_results(self, output_file: str = "verification-results.json"):
        """Export all results to JSON"""
        with open(output_file, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "results": self.results,
                },
                f,
                indent=2,
            )
        print(f"✅ Results exported to {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="BIRCH Unified Verifier — Comprehensive PR verification framework",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Monitor command
    monitor_parser = subparsers.add_parser("monitor-pr", help="Monitor for new PR")
    monitor_parser.add_argument(
        "--repo",
        default="terminator2-agent/agent-papers",
        help="Repository to monitor",
    )
    monitor_parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Check interval in seconds",
    )

    # Verify command
    verify_parser = subparsers.add_parser(
        "verify-pr", help="Verify a PR with 5-pass framework",
    )
    verify_parser.add_argument("pr_url", help="PR URL to verify")
    verify_parser.add_argument(
        "--with-tools",
        action="store_true",
        help=(
            "Also run DeepSeek verifier, GPT-5.2 scanner, and encoding "
            "scan if available"
        ),
    )
    verify_parser.add_argument(
        "--spec-path",
        default=None,
        help="Path to unified spec file for encoding scan helper",
    )

    # DeepSeek verify command
    deepseek_parser = subparsers.add_parser(
        "deepseek-verify",
        help="Run DeepSeek-V3.2 comprehensive verifier",
    )
    deepseek_parser.add_argument("pr_url", help="PR URL to verify")

    # Check links command
    subparsers.add_parser("check-links", help="Verify probe material links")

    # Decision command
    subparsers.add_parser("decide", help="Run decision automation")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export results to JSON")
    export_parser.add_argument(
        "--output",
        default="verification-results.json",
        help="Output file",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    verifier = BIRCHUnifiedVerifier()

    if args.command == "monitor-pr":
        verifier.monitor_pr(args.repo, args.interval)
    elif args.command == "verify-pr":
        verifier.verify_pr(
            args.pr_url,
            enable_external_tools=args.with_tools,
            spec_path=args.spec_path,
        )
    elif args.command == "deepseek-verify":
        verifier.deepseek_verify(args.pr_url)
    elif args.command == "check-links":
        verifier.check_probe_links()
    elif args.command == "decide":
        verifier.make_decision()
    elif args.command == "export":
        verifier.export_results(args.output)


if __name__ == "__main__":
    main()
