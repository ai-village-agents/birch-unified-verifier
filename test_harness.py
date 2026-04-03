#!/usr/bin/env python3
"""Test harness for BIRCH unified verifier — allows dry-run with mock PR data"""

import json
import sys
from datetime import datetime
from modules.five_pass_verifier import FivePassVerifier
from modules.link_checker import LinkChecker
from modules.decision_engine import DecisionEngine
from modules.output_formatter import OutputFormatter

class TestHarness:
    def __init__(self):
        self.formatter = OutputFormatter()
        self.verifier = FivePassVerifier()
        self.link_checker = LinkChecker()
        self.decision_engine = DecisionEngine()
    
    def run_mock_verification(self):
        """Run a mock verification with realistic mock PR content"""
        print("🧪 Running MOCK BIRCH v0.3 PR Verification")
        print("=" * 60)
        
        # Create mock results as if a real PR was processed
        mock_results = {
            'timestamp': datetime.now().isoformat(),
            'pr_url': 'https://github.com/terminator2-agent/agent-papers/pull/MOCK-001',
            'passes': {
                'pass_1': {
                    'pass_num': 1,
                    'status': 'SUCCESS',
                    'duration': '5 min',
                    'details': [
                        '✓ Amendment #14 found with 7/7 components',
                        '✓ Domain-Constrained Protocol Design present',
                        '✓ Scoring Matrix (4-Level Scale) present',
                        '✓ Empirical Validation Results present',
                        '✓ Load-Bearing Rationale present',
                        '✓ Data Submission Format (JSON Schema) present',
                        '✓ Submission Frequency present',
                        '✓ Backward Compatibility Statement present',
                    ]
                },
                'pass_2': {
                    'pass_num': 2,
                    'status': 'SUCCESS',
                    'duration': '10 min',
                    'details': [
                        '✓ All 5 probe material links verified',
                        '✓ Link 1 (Rubric): HTTP 200',
                        '✓ Link 2 (Responses): HTTP 200',
                        '✓ Link 3 (Analysis): HTTP 200',
                        '✓ Link 4 (Methodology): HTTP 200',
                        '✓ Link 5 (Summary): HTTP 200',
                    ]
                },
                'pass_3': {
                    'pass_num': 3,
                    'status': 'SUCCESS',
                    'duration': '15 min',
                    'details': [
                        '✓ Domain constraint isolation verified',
                        '✓ Scoring matrix κ=1.0 application confirmed',
                        '✓ JSON schema matches 6-agent empirical data',
                        '✓ Load-bearing rationale validated',
                    ]
                },
                'pass_4': {
                    'pass_num': 4,
                    'status': 'SUCCESS',
                    'duration': '10 min',
                    'details': [
                        '✓ Found "RECOMMENDED not REQUIRED" language',
                        '✓ v0.2 submissions remain valid',
                        '✓ No breaking changes to v0.2',
                        '✓ All fields optional with defaults',
                    ]
                },
                'pass_5': {
                    'pass_num': 5,
                    'status': 'SUCCESS',
                    'duration': '5 min',
                    'details': [
                        '✓ κ = 1.0 inter-rater reliability cited',
                        '✓ Mixed-Hybrid classification stated',
                        '✓ 6-agent, 3-model-family sample documented',
                    ]
                }
            },
            'red_flags': []
        }
        
        # Display results
        self.formatter.print_verification_results(mock_results)
        
        # Make decision
        print("\n" + "=" * 60)
        decision = self.decision_engine.evaluate(mock_results)
        self.formatter.print_decision(decision)
        
        return {'verification': mock_results, 'decision': decision}
    
    def test_link_checker(self):
        """Test link checker against actual probe material URLs"""
        print("🔗 Testing Link Checker Against Actual URLs")
        print("=" * 60)
        
        probe_links = [
            "https://github.com/ai-village-agents/framework-reflections-2026/blob/main/analysis/pre-registered-scoring-rubric-structural-determinism-probe.md",
            "https://github.com/ai-village-agents/framework-reflections-2026/blob/main/analysis/structural-determinism-probe-results/all-responses.md",
            "https://github.com/ai-village-agents/framework-reflections-2026/blob/main/analysis/structural-determinism-probe/final-analysis-report.md",
            "https://github.com/ai-village-agents/framework-reflections-2026/blob/main/papers/domain-constrained-metaphor-probe-methodology.md",
            "https://github.com/ai-village-agents/framework-reflections-2026/blob/main/analysis/probe-summary-for-birch-v0.3.md",
        ]
        
        results = self.link_checker.verify_links(probe_links)
        self.formatter.print_link_results(results)
        
        return results

def main():
    harness = TestHarness()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--links':
        harness.test_link_checker()
    else:
        harness.run_mock_verification()

if __name__ == '__main__':
    main()
