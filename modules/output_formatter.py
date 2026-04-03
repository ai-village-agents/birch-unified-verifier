"""Output formatter — pretty-prints verification results"""

class OutputFormatter:
    def print_verification_results(self, results):
        """Print 5-pass verification results"""
        print(f"\n📋 VERIFICATION RESULTS")
        print(f"   PR: {results.get('pr_url')}")
        print(f"   Timestamp: {results.get('timestamp')}")
        print(f"   Status: {results.get('overall_status')}")
        print()
        
        for pass_key, pass_data in results.get('passes', {}).items():
            pass_num = pass_data.get('pass_num')
            status = pass_data.get('status')
            status_icon = '✅' if status == 'SUCCESS' else '⚠️ ' if status == 'RED_FLAG' else '⏳'
            print(f"{status_icon} Pass {pass_num}: {status} ({pass_data.get('duration')})")
            
            for detail in pass_data.get('details', []):
                print(f"     {detail}")
        
        if results.get('red_flags'):
            print(f"\n🚨 RED FLAGS DETECTED:")
            for flag in results.get('red_flags'):
                print(f"   ❌ {flag}")
    
    def print_link_results(self, results):
        """Print link verification results"""
        print(f"\n🔗 LINK VERIFICATION")
        print(f"   Total checked: {results.get('links_checked')}")
        print(f"   All 200: {'✅ YES' if results.get('all_200') else '❌ NO'}")
        print()
        
        for link_key, link_data in results.get('details', {}).items():
            status = '✅' if link_data.get('accessible') else '❌'
            print(f"{status} {link_key}")
            print(f"     URL: {link_data.get('url')}")
            print(f"     HTTP: {link_data.get('status_code')}")
    
    def print_decision(self, decision):
        """Print decision engine output"""
        decision_icon = {
            'APPROVE': '✅',
            'CONDITIONAL': '⚠️ ',
            'REJECT': '❌',
            'UNDETERMINED': '❓'
        }
        
        icon = decision_icon.get(decision.get('decision'), '?')
        print(f"\n⚖️  DECISION: {icon} {decision.get('decision')}")
        print(f"   Score: {decision.get('total_score')}/{decision.get('max_score')}")
        print()
        
        for reason in decision.get('reasoning', []):
            print(f"   {reason}")
