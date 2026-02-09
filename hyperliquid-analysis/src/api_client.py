"""
Hyperliquid API Client
Wrapper for making requests to Hyperliquid's Info API
"""
import requests
import time
import json
from typing import Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class HyperliquidClient:
    """Client for interacting with Hyperliquid API"""
    
    def __init__(self):
        self.api_url = config.HYPERLIQUID_INFO_API
        self.request_delay = config.REQUEST_DELAY
        self.max_retries = config.MAX_RETRIES
        self.timeout = config.TIMEOUT
        
    def _make_request(self, payload: Dict[str, Any]) -> Optional[Dict]:
        """
        Make a POST request to Hyperliquid Info API with retries
        
        Args:
            payload: Request payload
            
        Returns:
            Response JSON or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    time.sleep(self.request_delay)  # Rate limiting
                    return response.json()
                elif response.status_code == 403:
                    print(f"  ⚠️  Access denied (403) for request")
                    return None
                else:
                    print(f"  ⚠️  Request failed with status {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"  ⚠️  Request timeout (attempt {attempt + 1}/{self.max_retries})")
            except requests.exceptions.RequestException as e:
                print(f"  ⚠️  Request error: {e}")
                
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
                
        return None
    
    def get_referral_data(self, builder_address: str, **kwargs) -> Optional[Dict]:
        """
        Get referral data for a builder address
        
        Args:
            builder_address: Builder's wallet address
            **kwargs: Additional parameters to test (offset, page, etc.)
            
        Returns:
            Referral data or None
        """
        payload = {
            'type': 'referral',
            'user': builder_address,
            **kwargs
        }
        
        return self._make_request(payload)
    
    def get_clearinghouse_state(self, user_address: str, dex: Optional[str] = None) -> Optional[Dict]:
        """
        Get user's positions (clearinghouse state)
        
        Args:
            user_address: User's wallet address
            dex: Optional DEX name for HIP-3 positions (e.g., 'xyz')
            
        Returns:
            Position data or None
        """
        payload = {
            'type': 'clearinghouseState',
            'user': user_address
        }
        
        if dex:
            payload['dex'] = dex
            
        return self._make_request(payload)











