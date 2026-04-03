"""Link checker module — verifies probe material links"""

import subprocess
import requests
import json

class LinkChecker:
    def verify_links(self, links):
        """Verify all links return HTTP 200"""
        results = {
            'timestamp': str(subprocess.run(['date', '-u'], capture_output=True, text=True).stdout.strip()),
            'links_checked': len(links),
            'all_200': True,
            'details': {}
        }
        
        for idx, link in enumerate(links, 1):
            status = self._check_link(link)
            results['details'][f'link_{idx}'] = {
                'url': link,
                'status_code': status,
                'accessible': status == 200
            }
            if status != 200:
                results['all_200'] = False
        
        return results
    
    def _check_link(self, url):
        """Check single link status code"""
        try:
            # Use gh CLI to check if file exists in repo
            if 'github.com' in url:
                # Extract repo and path from URL
                # For now, use curl as fallback
                result = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', url],
                    capture_output=True, text=True, timeout=10
                )
                return int(result.stdout.strip())
        except Exception as e:
            print(f"  ⚠️  Error checking {url}: {e}")
            return 0
        return 0
