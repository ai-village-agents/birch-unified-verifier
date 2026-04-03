"""PR Monitor module — checks for new v0.3 spec PR"""

import subprocess
import json
import time
from datetime import datetime

class PRMonitor:
    def __init__(self, repo="terminator2-agent/agent-papers"):
        self.repo = repo
        self.baseline_count = None
    
    def get_pr_count(self):
        """Get current open PR count using gh CLI"""
        try:
            result = subprocess.run(
                ['gh', 'pr', 'list', '--repo', self.repo, '--state', 'open', '--json', 'number'],
                capture_output=True, text=True, timeout=10
            )
            data = json.loads(result.stdout)
            return len(data)
        except Exception as e:
            print(f"❌ Error checking PR count: {e}")
            return None
    
    def get_latest_pr(self):
        """Get details of latest PR"""
        try:
            result = subprocess.run(
                ['gh', 'pr', 'list', '--repo', self.repo, '--state', 'all', '--limit', '1', '--json', 'number,title,url,createdAt'],
                capture_output=True, text=True, timeout=10
            )
            data = json.loads(result.stdout)
            return data[0] if data else None
        except Exception as e:
            print(f"❌ Error fetching PR: {e}")
            return None
    
    def monitor(self, repo, interval=30, max_duration=3600):
        """Monitor for new PR with timeout"""
        self.repo = repo
        self.baseline_count = self.get_pr_count()
        print(f"📊 Baseline: {self.baseline_count} open PRs at {datetime.now().strftime('%H:%M:%S')}")
        
        start_time = time.time()
        checks = 0
        
        while (time.time() - start_time) < max_duration:
            checks += 1
            current_count = self.get_pr_count()
            
            if current_count is None:
                time.sleep(interval)
                continue
            
            if current_count > self.baseline_count:
                print(f"🔔 NEW PR DETECTED! Count: {self.baseline_count} → {current_count}")
                pr_info = self.get_latest_pr()
                if pr_info:
                    print(f"   Title: {pr_info.get('title')}")
                    print(f"   URL: {pr_info.get('url')}")
                    print(f"   Created: {pr_info.get('createdAt')}")
                return pr_info
            
            elapsed = int(time.time() - start_time)
            print(f"[{elapsed}s, check #{checks}] {current_count} open PRs — next check in {interval}s...")
            time.sleep(interval)
        
        print("⏱️  Monitor timeout reached. No new PR detected.")
        return None
