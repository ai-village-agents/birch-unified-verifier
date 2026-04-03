"""DeepSeek-V3.2 PR verifier integration module.

Wraps the birch_pr_verifier.py tool and maps its results to the unified framework.
"""

import sys
import json
import subprocess
from pathlib import Path

# Import local birch_pr_verifier if available
try:
    # Add parent directory to path to import birch-tools
    sys.path.insert(0, str(Path.home() / 'birch-tools'))
    import birch_pr_verifier
    DEEPSEEK_VERIFIER_AVAILABLE = True
except ImportError:
    DEEPSEEK_VERIFIER_AVAILABLE = False


class DeepSeekVerifier:
    """Wrapper for DeepSeek-V3.2's comprehensive PR verifier."""
    
    def __init__(self):
        self.available = DEEPSEEK_VERIFIER_AVAILABLE
        self.results = {}
        
    def verify_pr(self, pr_number: int):
        """Run DeepSeek's PR verifier on a PR number."""
        if not self.available:
            return {
                'error': 'DeepSeek verifier not available',
                'available': False
            }
        
        try:
            # Call the verifier directly
            exit_code, results = birch_pr_verifier.evaluate(pr_number)
            
            # Map results to unified framework format
            mapped = self._map_to_unified_format(results, exit_code)
            self.results = mapped
            return mapped
            
        except Exception as e:
            return {
                'error': f'DeepSeek verifier execution failed: {e}',
                'available': True,
                'exception': str(e)
            }
    
    def verify_pr_from_url(self, pr_url: str):
        """Extract PR number from URL and verify."""
        import re
        
        # Extract PR number from GitHub URL
        match = re.search(r'github\.com/([^/]+/[^/]+)/pull/(\d+)', pr_url)
        if not match:
            return {
                'error': f'Could not extract PR number from URL: {pr_url}',
                'available': self.available
            }
        
        repo = match.group(1)
        pr_number = int(match.group(2))
        
        # Verify it's the expected repository
        if repo != 'terminator2-agent/agent-papers':
            return {
                'error': f'Unexpected repository: {repo}. Expected terminator2-agent/agent-papers',
                'available': self.available
            }
        
        return self.verify_pr(pr_number)
    
    def _map_to_unified_format(self, deepseek_results, exit_code):
        """Map DeepSeek's results to the unified verification format."""
        mapped = {
            'timestamp': deepseek_results.get('timestamp', ''),
            'pr_number': deepseek_results.get('pr_number'),
            'exit_code': exit_code,
            'issues': deepseek_results.get('issues', []),
            'red_flags': [],
            'checks': {},
            'details': []
        }
        
        # Extract key checks
        checks = {}
        
        # 1. Amendment fields
        key_fields = deepseek_results.get('key_amendment_fields', {})
        checks['amendment_fields'] = {
            'present': bool(key_fields),
            'fields_found': list(key_fields.keys()),
            'details': key_fields
        }
        
        # 2. Core URLs
        core_links = deepseek_results.get('core_links', {})
        expected_urls = deepseek_results.get('expected_core_urls', [])
        checks['core_urls'] = {
            'found': len([url for url, info in core_links.items() if info.get('accessible')]),
            'total_expected': len(expected_urls),
            'details': core_links
        }
        
        # 3. Backward compatibility
        bc_result = deepseek_results.get('backward_compatibility', {})
        checks['backward_compatibility'] = {
            'recommended_not_required': bc_result.get('recommended_not_required', False),
            'should_language': bc_result.get('should_language', False),
            'essential_marking': bc_result.get('essential_marking', False),
            'details': bc_result
        }
        
        # 4. Citations
        citations = deepseek_results.get('citations', {})
        checks['citations'] = {
            'kappa_1_0': citations.get('kappa_1_0', False),
            'mixed_hybrid': citations.get('mixed_hybrid', False),
            'details': citations
        }
        
        # 5. Non-ASCII hyphens
        hyphen_info = deepseek_results.get('non_ascii_hyphens', {})
        checks['non_ascii_hyphens'] = {
            'found': hyphen_info.get('found', 0),
            'details': hyphen_info
        }
        
        # 6. JSON schema
        schema_info = deepseek_results.get('schema_check', {})
        checks['json_schema'] = {
            'found': schema_info.get('found', False),
            'valid': schema_info.get('valid', False),
            'details': schema_info
        }
        
        # Map issues to red flags
        for issue in deepseek_results.get('issues', []):
            # Classify severity
            if any(keyword in issue.lower() for keyword in ['missing', '404', 'failed', 'not found', 'invalid']):
                mapped['red_flags'].append(issue)
        
        # Add critical red flags based on checks
        if not checks.get('core_urls', {}).get('found', 0) >= 5:
            mapped['red_flags'].append('Not all 5 core probe material URLs found')
        
        if not checks.get('backward_compatibility', {}).get('recommended_not_required', False):
            mapped['red_flags'].append("Missing 'RECOMMENDED not REQUIRED' language")
        
        if not checks.get('citations', {}).get('kappa_1_0', False):
            mapped['red_flags'].append('Missing κ=1.0 citation')
        
        if not checks.get('citations', {}).get('mixed_hybrid', False):
            mapped['red_flags'].append('Missing Mixed-Hybrid classification')
        
        mapped['checks'] = checks
        
        # Generate summary details
        if mapped['issues']:
            mapped['details'].append(f"Found {len(mapped['issues'])} issues")
        
        if mapped['red_flags']:
            mapped['details'].append(f"Found {len(mapped['red_flags'])} red flags")
        else:
            mapped['details'].append("No red flags detected")
        
        # Overall status
        if exit_code == 0 and not mapped['red_flags']:
            mapped['overall_status'] = 'PASS'
        elif mapped['red_flags']:
            mapped['overall_status'] = 'RED_FLAGS_DETECTED'
        else:
            mapped['overall_status'] = 'ISSUES_DETECTED'
        
        return mapped
    
    def get_decision_input(self):
        """Extract decision-relevant information from results."""
        if not self.results:
            return {}
        
        decision_input = {
            'probe_links_http200': False,
            'amendment14_complete': False,
            'backward_compat': False,
            'kappa_1_0': False,
            'mixed_hybrid': False,
            'json_schema': False,
            'sample_cited': False,  # TODO: extract from deepseek results
        }
        
        checks = self.results.get('checks', {})
        
        # Probe links
        core_urls = checks.get('core_urls', {})
        decision_input['probe_links_http200'] = core_urls.get('found', 0) >= 5
        
        # Amendment #14 - we check for key fields
        amendment_fields = checks.get('amendment_fields', {})
        decision_input['amendment14_complete'] = len(amendment_fields.get('fields_found', [])) >= 7
        
        # Backward compatibility
        bc = checks.get('backward_compatibility', {})
        decision_input['backward_compat'] = bc.get('recommended_not_required', False)
        
        # Citations
        citations = checks.get('citations', {})
        decision_input['kappa_1_0'] = citations.get('kappa_1_0', False)
        decision_input['mixed_hybrid'] = citations.get('mixed_hybrid', False)
        
        # JSON schema
        schema = checks.get('json_schema', {})
        decision_input['json_schema'] = schema.get('valid', False)
        
        return decision_input
