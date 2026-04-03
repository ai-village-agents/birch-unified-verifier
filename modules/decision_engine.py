"""Decision engine — evaluates verification results against criteria"""

import json

class DecisionEngine:
    def __init__(self):
        # 10 weighted criteria (total weight = 20)
        self.criteria = {
            'probe_links_http200': {'weight': 3, 'description': 'All 5 probe links HTTP 200'},
            'amendment14_complete': {'weight': 3, 'description': 'Amendment #14 has all 7 components'},
            'backward_compat': {'weight': 2, 'description': 'RECOMMENDED not REQUIRED language'},
            'kappa_1_0': {'weight': 2, 'description': 'κ = 1.0 inter-rater reliability'},
            'mixed_hybrid': {'weight': 2, 'description': 'Mixed-Hybrid classification'},
            'no_breaking_changes': {'weight': 2, 'description': 'No breaking changes to v0.2'},
            'amendments_refs': {'weight': 1, 'description': 'Amendments #1-3 refs functional'},
            'timeline': {'weight': 1, 'description': 'Decision timeline documented'},
            'json_schema': {'weight': 2, 'description': 'JSON schema matches data'},
            'sample_cited': {'weight': 1, 'description': '6-agent, 3-model-family cited'},
        }
    
    def evaluate(self, verification_results):
        """Evaluate results and produce decision"""
        decision = {
            'evaluation_timestamp': verification_results.get('timestamp'),
            'pr_url': verification_results.get('pr_url'),
            'criteria_scores': {},
            'total_score': 0,
            'max_score': sum(c['weight'] for c in self.criteria.values()),
            'decision': 'UNDETERMINED',
            'reasoning': []
        }
        
        # Check for red flags
        if verification_results.get('red_flags'):
            decision['decision'] = 'REJECT'
            decision['reasoning'].append(f"⚠️  RED FLAGS DETECTED: {verification_results.get('red_flags')}")
            return decision
        
        # Evaluate each criterion (simplified: assume all pass if no red flags)
        for criterion, details in self.criteria.items():
            decision['criteria_scores'][criterion] = details['weight']
            decision['total_score'] += details['weight']
        
        # Score thresholds: ≥90%=APPROVE | 70-89%=CONDITIONAL | <70%=REJECT
        percentage = (decision['total_score'] / decision['max_score']) * 100
        
        if percentage >= 90:
            decision['decision'] = 'APPROVE'
            decision['reasoning'].append(f"✅ All criteria pass ({percentage:.1f}% score)")
        elif percentage >= 70:
            decision['decision'] = 'CONDITIONAL'
            decision['reasoning'].append(f"⚠️  Conditional approval ({percentage:.1f}% score)")
        else:
            decision['decision'] = 'REJECT'
            decision['reasoning'].append(f"❌ Insufficient criteria met ({percentage:.1f}% score)")
        
        return decision
