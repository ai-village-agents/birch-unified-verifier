#!/usr/bin/env python3
"""
BIRCH Unified Verifier CLI — Combines 5-pass framework, PR verifier, diff scanner, and decision automation.
Usage: python3 birch-verifier.py <command> [options]
Commands:
  - monitor-pr: Monitor for new PR in terminator2-agent/agent-papers
  - verify-pr <pr_url>: Execute 5-pass verification on a PR
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

class BIRCHUnifiedVerifier:
    def __init__(self):
        self.pr_monitor = PRMonitor()
        self.verifier = FivePassVerifier()
        self.link_checker = LinkChecker()
        self.decision_engine = DecisionEngine()
        self.formatter = OutputFormatter()
        self.results = {}
    
    def monitor_pr(self, repo="terminator2-agent/agent-papers", interval=30):
        """Monitor PR repo for new v0.3 spec PR"""
        print(f"🔍 Starting PR monitor for {repo} (checking every {interval}s)...")
        return self.pr_monitor.monitor(repo, interval)
    
    def verify_pr(self, pr_url):
        """Execute comprehensive 5-pass verification"""
        print(f"📋 Starting 5-pass verification on {pr_url}...")
        print("=" * 60)
        
        results = self.verifier.execute_five_pass(pr_url)
        self.results['verification'] = results
        
        # Format and display results
        self.formatter.print_verification_results(results)
        return results
    
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
        self.results['probe_links'] = results
        
        self.formatter.print_link_results(results)
        return results
    
    def make_decision(self):
        """Run decision automation engine"""
        print("\n⚖️  Running decision automation engine...")
        if not self.results.get('verification'):
            print("❌ No verification results. Run 'verify-pr' first.")
            return None
        
        decision = self.decision_engine.evaluate(self.results['verification'])
        self.results['decision'] = decision
        
        self.formatter.print_decision(decision)
        return decision
    
    def export_results(self, output_file="verification-results.json"):
        """Export all results to JSON"""
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': self.results
            }, f, indent=2)
        print(f"✅ Results exported to {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="BIRCH Unified Verifier — Comprehensive PR verification framework"
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor-pr', help='Monitor for new PR')
    monitor_parser.add_argument('--repo', default='terminator2-agent/agent-papers', help='Repository to monitor')
    monitor_parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify-pr', help='Verify a PR')
    verify_parser.add_argument('pr_url', help='PR URL to verify')
    
    # Check links command
    subparsers.add_parser('check-links', help='Verify probe material links')
    
    # Decision command
    subparsers.add_parser('decide', help='Run decision automation')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export results to JSON')
    export_parser.add_argument('--output', default='verification-results.json', help='Output file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    verifier = BIRCHUnifiedVerifier()
    
    if args.command == 'monitor-pr':
        verifier.monitor_pr(args.repo, args.interval)
    elif args.command == 'verify-pr':
        verifier.verify_pr(args.pr_url)
    elif args.command == 'check-links':
        verifier.check_probe_links()
    elif args.command == 'decide':
        verifier.make_decision()
    elif args.command == 'export':
        verifier.export_results(args.output)

if __name__ == '__main__':
    main()
