"""
Position Fetcher for Hyperliquid Users
Fetches current positions and calculates risk metrics
"""

import time
from typing import Dict, List, Optional
from .api_client import HyperliquidClient
from datetime import datetime
from tqdm import tqdm


class PositionFetcher:
    """Fetches and processes user positions from Hyperliquid"""
    
    def __init__(self, delay: float = 1.0):
        self.client = HyperliquidClient()
        self.delay = delay
        
    def fetch_user_positions(self, address: str) -> Dict:
        """
        Fetch both HyperCore and HIP-3 positions for a single user
        
        Args:
            address: User wallet address
            
        Returns:
            Dict with hypercore and hip3 positions
        """
        result = {
            'address': address,
            'fetched_at': datetime.utcnow().isoformat(),
            'hypercore': None,
            'hip3_xyz': None,
            'error': None
        }
        
        try:
            # Fetch HyperCore positions (BTC, ETH, SOL, etc.)
            hypercore_data = self.client.get_clearinghouse_state(address)
            result['hypercore'] = hypercore_data
            
            time.sleep(self.delay)
            
            # Fetch HIP-3 positions (xyz perps)
            hip3_data = self.client.get_clearinghouse_state(address, dex='xyz')
            result['hip3_xyz'] = hip3_data
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def fetch_all_positions(
        self, 
        addresses: List[str],
        progress_bar: bool = True
    ) -> List[Dict]:
        """
        Fetch positions for all users with rate limiting
        
        Args:
            addresses: List of wallet addresses
            progress_bar: Show progress bar
            
        Returns:
            List of position data for each user
        """
        results = []
        
        iterator = tqdm(addresses, desc="Fetching positions") if progress_bar else addresses
        
        for address in iterator:
            position_data = self.fetch_user_positions(address)
            results.append(position_data)
            
            # Rate limiting delay (already includes one delay from fetch_user_positions)
            time.sleep(self.delay)
            
        return results
    
    def calculate_risk_metrics(
        self, 
        position: Dict, 
        current_price: float
    ) -> Dict:
        """
        Calculate risk metrics for a position
        
        Args:
            position: Position data from API
            current_price: Current market price
            
        Returns:
            Dict with risk metrics
        """
        entry_price = float(position.get('entryPx', 0))
        liquidation_price = position.get('liquidationPx')
        szi = float(position.get('szi', 0))
        
        if liquidation_price is None:
            return {
                'distance_to_liq_usd': None,
                'distance_to_liq_pct': None,
                'risk_level': 'UNKNOWN'
            }
        
        liquidation_price = float(liquidation_price)
        
        # Calculate distance to liquidation
        if szi > 0:  # LONG position
            distance_usd = current_price - liquidation_price
            distance_pct = (distance_usd / current_price) * 100 if current_price > 0 else 0
        else:  # SHORT position
            distance_usd = liquidation_price - current_price
            distance_pct = (distance_usd / current_price) * 100 if current_price > 0 else 0
        
        # Risk level categorization
        if distance_pct < 3:
            risk_level = 'CRITICAL'
        elif distance_pct < 7:
            risk_level = 'HIGH'
        elif distance_pct < 15:
            risk_level = 'MODERATE'
        else:
            risk_level = 'LOW'
        
        return {
            'distance_to_liq_usd': round(distance_usd, 2),
            'distance_to_liq_pct': round(distance_pct, 2),
            'risk_level': risk_level
        }
    
    def extract_positions_from_response(
        self, 
        response: Dict,
        market_type: str = 'HyperCore'
    ) -> List[Dict]:
        """
        Extract position data from API response
        
        Args:
            response: API response from clearinghouseState
            market_type: 'HyperCore' or 'HIP-3'
            
        Returns:
            List of positions
        """
        if not response or 'assetPositions' not in response:
            return []
        
        positions = []
        for asset in response['assetPositions']:
            if 'position' in asset:
                pos = asset['position'].copy()
                pos['market_type'] = market_type
                pos['margin_summary'] = response.get('marginSummary', {})
                positions.append(pos)
        
        return positions











