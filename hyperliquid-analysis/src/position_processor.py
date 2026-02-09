"""
Position Processor
Processes raw position data and generates structured outputs
"""

from typing import Dict, List
from datetime import datetime


class PositionProcessor:
    """Processes and analyzes position data"""
    
    def __init__(self):
        # Market prices cache (would ideally fetch from API)
        self.market_prices = {}
    
    def process_user_positions(self, raw_data: Dict) -> Dict:
        """
        Process raw position data for a single user
        
        Args:
            raw_data: Raw response from position fetcher
            
        Returns:
            Processed position data
        """
        address = raw_data['address']
        
        # Extract positions from both markets
        all_positions = []
        
        # HyperCore positions
        if raw_data.get('hypercore'):
            hypercore_positions = self._extract_positions(
                raw_data['hypercore'], 
                'HyperCore'
            )
            all_positions.extend(hypercore_positions)
        
        # HIP-3 positions
        if raw_data.get('hip3_xyz'):
            hip3_positions = self._extract_positions(
                raw_data['hip3_xyz'],
                'HIP-3'
            )
            all_positions.extend(hip3_positions)
        
        # Calculate account summary
        account_summary = self._calculate_account_summary(raw_data)
        
        return {
            'address': address,
            'fetched_at': raw_data['fetched_at'],
            'has_positions': len(all_positions) > 0,
            'num_positions': len(all_positions),
            'account_summary': account_summary,
            'positions': all_positions,
            'error': raw_data.get('error')
        }
    
    def _extract_positions(self, response: Dict, market_type: str) -> List[Dict]:
        """Extract positions from API response"""
        if not response or 'assetPositions' not in response:
            return []
        
        positions = []
        for asset in response['assetPositions']:
            if 'position' in asset:
                pos = asset['position']
                
                # Parse position data
                szi = float(pos.get('szi', 0))
                entry_px = float(pos.get('entryPx', 0))
                position_value = float(pos.get('positionValue', 0))
                unrealized_pnl = float(pos.get('unrealizedPnl', 0))
                liquidation_px = pos.get('liquidationPx')
                
                # Determine direction
                direction = 'LONG' if szi > 0 else 'SHORT'
                size = abs(szi)
                
                # Build position dict
                position_data = {
                    'coin': pos.get('coin'),
                    'market_type': market_type,
                    'direction': direction,
                    'size': size,
                    'entry_price': entry_px,
                    'liquidation_price': float(liquidation_px) if liquidation_px else None,
                    'position_value': position_value,
                    'unrealized_pnl': unrealized_pnl,
                    'pnl_percent': (unrealized_pnl / position_value * 100) if position_value > 0 else 0,
                    'leverage': pos.get('leverage', {}),
                    'margin_used': float(pos.get('marginUsed', 0))
                }
                
                # Add risk metrics if liquidation price exists
                if liquidation_px:
                    # Estimate current price from position value and size
                    current_price = position_value / size if size > 0 else entry_px
                    
                    if direction == 'LONG':
                        distance_usd = current_price - float(liquidation_px)
                        distance_pct = (distance_usd / current_price) * 100
                    else:
                        distance_usd = float(liquidation_px) - current_price
                        distance_pct = (distance_usd / current_price) * 100
                    
                    # Risk level
                    if distance_pct < 3:
                        risk_level = 'CRITICAL'
                    elif distance_pct < 7:
                        risk_level = 'HIGH'
                    elif distance_pct < 15:
                        risk_level = 'MODERATE'
                    else:
                        risk_level = 'LOW'
                    
                    position_data['distance_to_liq_pct'] = round(distance_pct, 2)
                    position_data['distance_to_liq_usd'] = round(distance_usd, 2)
                    position_data['risk_level'] = risk_level
                else:
                    position_data['distance_to_liq_pct'] = None
                    position_data['distance_to_liq_usd'] = None
                    position_data['risk_level'] = 'UNKNOWN'
                
                positions.append(position_data)
        
        return positions
    
    def _calculate_account_summary(self, raw_data: Dict) -> Dict:
        """Calculate account-level summary metrics"""
        summary = {
            'account_value': 0,
            'total_margin_used': 0,
            'total_unrealized_pnl': 0,
            'total_position_value': 0
        }
        
        # Get from HyperCore margin summary (most complete)
        if raw_data.get('hypercore') and 'marginSummary' in raw_data['hypercore']:
            margin = raw_data['hypercore']['marginSummary']
            summary['account_value'] = float(margin.get('accountValue', 0))
            summary['total_margin_used'] = float(margin.get('totalMarginUsed', 0))
        
        return summary
    
    def filter_btc_positions(self, processed_data: List[Dict]) -> List[Dict]:
        """
        Filter and extract BTC positions only
        
        Args:
            processed_data: List of processed user position data
            
        Returns:
            List of BTC position records (one per position)
        """
        btc_positions = []
        
        for user_data in processed_data:
            address = user_data['address']
            account_summary = user_data.get('account_summary', {})
            
            for position in user_data.get('positions', []):
                if position['coin'] == 'BTC':
                    # Flatten for CSV export
                    btc_record = {
                        'address': address,
                        'account_value': account_summary.get('account_value', 0),
                        **position
                    }
                    btc_positions.append(btc_record)
        
        return btc_positions
    
    def sort_btc_positions(self, btc_positions: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Sort BTC positions by direction and size
        
        Args:
            btc_positions: List of BTC position records
            
        Returns:
            Dict with 'longs' and 'shorts' sorted by size descending
        """
        longs = [p for p in btc_positions if p['direction'] == 'LONG']
        shorts = [p for p in btc_positions if p['direction'] == 'SHORT']
        
        # Sort by position value (largest first)
        longs.sort(key=lambda x: x['position_value'], reverse=True)
        shorts.sort(key=lambda x: x['position_value'], reverse=True)
        
        return {
            'longs': longs,
            'shorts': shorts,
            'summary': {
                'total_longs': len(longs),
                'total_shorts': len(shorts),
                'total_long_value': sum(p['position_value'] for p in longs),
                'total_short_value': sum(p['position_value'] for p in shorts),
                'long_short_ratio': len(longs) / len(shorts) if shorts else float('inf')
            }
        }
    
    def generate_at_risk_report(self, processed_data: List[Dict]) -> List[Dict]:
        """
        Generate report of positions at high risk of liquidation
        
        Args:
            processed_data: List of processed user position data
            
        Returns:
            List of at-risk positions sorted by risk level
        """
        at_risk = []
        
        for user_data in processed_data:
            for position in user_data.get('positions', []):
                risk_level = position.get('risk_level')
                if risk_level in ['CRITICAL', 'HIGH']:
                    at_risk.append({
                        'address': user_data['address'],
                        'account_value': user_data.get('account_summary', {}).get('account_value', 0),
                        **position
                    })
        
        # Sort by distance to liquidation (most at risk first)
        at_risk.sort(key=lambda x: x.get('distance_to_liq_pct', 100))
        
        return at_risk











