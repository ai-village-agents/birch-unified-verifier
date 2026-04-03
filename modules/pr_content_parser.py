"""PR content parser — fetches and parses PR diff and content"""

import subprocess
import json
import re

class PRContentParser:
    def __init__(self, pr_url):
        self.pr_url = pr_url
        self.pr_number = self._extract_pr_number(pr_url)
        self.repo = "terminator2-agent/agent-papers"
        self.content = None
        self.diff = None
    
    def _extract_pr_number(self, url):
        """Extract PR number from URL"""
        match = re.search(r'/pull/(\d+)', url)
        return match.group(1) if match else None
    
    def fetch_pr_content(self):
        """Fetch PR details using gh CLI"""
        if not self.pr_number:
            return None
        
        try:
            result = subprocess.run(
                ['gh', 'pr', 'view', self.pr_number, '--repo', self.repo, '--json', 'body,title,files,commits'],
                capture_output=True, text=True, timeout=15
            )
            self.content = json.loads(result.stdout)
            return self.content
        except Exception as e:
            print(f"❌ Error fetching PR: {e}")
            return None
    
    def fetch_pr_diff(self):
        """Fetch PR diff"""
        if not self.pr_number:
            return None
        
        try:
            result = subprocess.run(
                ['gh', 'pr', 'diff', self.pr_number, '--repo', self.repo],
                capture_output=True, text=True, timeout=15
            )
            self.diff = result.stdout
            return self.diff
        except Exception as e:
            print(f"❌ Error fetching diff: {e}")
            return None
    
    def scan_for_amendment14(self):
        """Scan content for Amendment #14 section"""
        if not self.content:
            return {'found': False, 'components': []}
        
        body = self.content.get('body', '')
        
        # Check for Amendment #14 markers
        has_amendment14 = 'Amendment #14' in body or 'amendment_14' in body.lower()
        
        # Check for key components
        components = {
            'domain_protocol': 'domain-constrained-protocol' in body.lower(),
            'scoring_matrix': 'scoring matrix' in body.lower() or 'scoring_matrix' in body.lower(),
            'validation_results': 'validation' in body.lower() or 'empirical' in body.lower(),
            'rationale': 'rationale' in body.lower(),
            'json_schema': 'json_schema' in body.lower() or '"domain_constrained_probe"' in body,
            'frequency': 'recommended' in body.lower() or 'frequency' in body.lower(),
            'backward_compat': 'backward' in body.lower() or 'v0.2' in body,
        }
        
        return {
            'found': has_amendment14,
            'components': components,
            'component_count': sum(components.values())
        }
    
    def scan_for_backward_compatibility_language(self):
        """Scan for backward compatibility language markers"""
        if not self.content and not self.diff:
            return {'status': 'NO_CONTENT', 'markers': {}}
        
        text = (self.content.get('body', '') if self.content else '') + (self.diff if self.diff else '')
        text_lower = text.lower()
        
        markers = {
            'recommended_not_required': 'recommended' in text_lower and 'not required' in text_lower,
            'v02_valid': 'v0.2' in text and 'valid' in text_lower,
            'no_breaking': 'breaking' in text_lower,
            'optional_fields': 'optional' in text_lower and 'default' in text_lower,
            'should_not_must': 'should' in text_lower and 'must' not in text_lower,
        }
        
        return {
            'markers_found': sum(markers.values()),
            'total_markers': len(markers),
            'markers': markers
        }
    
    def scan_for_kappa_and_classification(self):
        """Scan for κ=1.0 and Mixed-Hybrid classification"""
        if not self.content:
            return {'kappa': False, 'classification': False}
        
        body = self.content.get('body', '')
        
        return {
            'kappa_1_0': 'κ = 1.0' in body or 'kappa = 1.0' in body.lower(),
            'mixed_hybrid': 'mixed-hybrid' in body.lower() or 'mixed hybrid' in body.lower(),
            'sample_cited': '6 agent' in body or '3-model' in body or '3 model' in body.lower(),
        }
