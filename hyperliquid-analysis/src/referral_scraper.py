"""
Referral API Scraper
Extract user addresses using Hyperliquid's referral endpoint
"""
import json
import sys
import os
from typing import List, Dict, Any
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.api_client import HyperliquidClient


class ReferralScraper:
    """Scrape user addresses from referral API"""
    
    def __init__(self, builder_address: str, builder_name: str = "unknown"):
        self.client = HyperliquidClient()
        self.builder_address = builder_address
        self.builder_name = builder_name
        self.users = []
        
    def test_pagination(self) -> Dict[str, Any]:
        """
        Test various pagination approaches to see which work
        
        Returns:
            Dict with test results
        """
        print("🔍 Testing pagination methods...\n")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'builder': self.builder_name,
            'tests': []
        }
        
        # Test 1: Standard request (baseline)
        print("Test 1: Standard request (no pagination params)")
        data = self.client.get_referral_data(self.builder_address)
        if data:
            referrer_state = data.get('referrerState', {}).get('data', {})
            total = referrer_state.get('nReferrals', 0)
            returned = len(referrer_state.get('referralStates', []))
            print(f"  ✅ Total users: {total}")
            print(f"  ✅ Returned: {returned}")
            results['tests'].append({
                'method': 'standard',
                'success': True,
                'total_users': total,
                'returned_users': returned
            })
        else:
            print("  ❌ Failed")
            results['tests'].append({'method': 'standard', 'success': False})
        
        # Test 2: Offset parameter
        print("\nTest 2: Offset parameter (offset=5000)")
        data = self.client.get_referral_data(self.builder_address, offset=5000)
        if data:
            referrer_state = data.get('referrerState', {}).get('data', {})
            returned = len(referrer_state.get('referralStates', []))
            print(f"  ✅ Returned: {returned} users")
            results['tests'].append({
                'method': 'offset',
                'success': True,
                'returned_users': returned
            })
        else:
            print("  ❌ Failed or no additional data")
            results['tests'].append({'method': 'offset', 'success': False})
        
        # Test 3: Limit + Offset
        print("\nTest 3: Limit + Offset (limit=1000, offset=0)")
        data = self.client.get_referral_data(self.builder_address, limit=1000, offset=0)
        if data:
            referrer_state = data.get('referrerState', {}).get('data', {})
            returned = len(referrer_state.get('referralStates', []))
            print(f"  ✅ Returned: {returned} users")
            results['tests'].append({
                'method': 'limit_offset',
                'success': True,
                'returned_users': returned
            })
        else:
            print("  ❌ Failed")
            results['tests'].append({'method': 'limit_offset', 'success': False})
        
        # Test 4: Page parameter
        print("\nTest 4: Page parameter (page=2)")
        data = self.client.get_referral_data(self.builder_address, page=2)
        if data:
            referrer_state = data.get('referrerState', {}).get('data', {})
            returned = len(referrer_state.get('referralStates', []))
            print(f"  ✅ Returned: {returned} users")
            results['tests'].append({
                'method': 'page',
                'success': True,
                'returned_users': returned
            })
        else:
            print("  ❌ Failed")
            results['tests'].append({'method': 'page', 'success': False})
        
        return results
    
    def fetch_all_users(self) -> List[Dict[str, Any]]:
        """
        Fetch all users from referral API
        Tries pagination if available, otherwise returns available users
        
        Returns:
            List of user dicts with address, volume, fees, timestamp
        """
        print(f"\n📥 Fetching users for {self.builder_name}...")
        
        # Get initial data
        data = self.client.get_referral_data(self.builder_address)
        if not data:
            print("❌ Failed to fetch referral data")
            return []
        
        referrer_state = data.get('referrerState', {}).get('data', {})
        total_referrals = referrer_state.get('nReferrals', 0)
        referral_states = referrer_state.get('referralStates', [])
        
        print(f"  Total users in system: {total_referrals}")
        print(f"  Users in response: {len(referral_states)}")
        
        # Extract user data
        users = []
        for entry in referral_states:
            users.append({
                'address': entry['user'],
                'volume': float(entry.get('cumVlm', 0)),
                'fees_paid': float(entry.get('cumRewardedFeesSinceReferred', 0)),
                'joined_timestamp': entry.get('timeJoined'),
                'joined_date': datetime.fromtimestamp(entry.get('timeJoined', 0) / 1000).isoformat() if entry.get('timeJoined') else None
            })
        
        # TODO: If pagination works, fetch additional pages here
        # For now, we work with what we got
        
        self.users = users
        print(f"✅ Extracted {len(users)} user addresses")
        
        return users
    
    def save_to_file(self, filepath: str):
        """Save users to JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        output = {
            'builder': self.builder_name,
            'builder_address': self.builder_address,
            'extracted_at': datetime.now().isoformat(),
            'total_users': len(self.users),
            'users': self.users
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"💾 Saved to {filepath}")











