#!/usr/bin/env python3
"""
Generate BasedApp Position Summary for Webapp
Processes positions_summary_hypercore JSON and generates webapp-ready summary
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


def generate_summary(json_file_path, output_path=None):
    """
    Generate webapp-ready summary from positions summary JSON
    
    Args:
        json_file_path: Path to positions_summary_hypercore JSON file
        output_path: Optional output path (defaults to app/data/basedapp_positions_summary.json)
    """
    json_path = Path(json_file_path)
    
    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        return
    
    print(f"📂 Loading JSON from: {json_path.name}")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    users = data.get('users', [])
    fetch_date = data.get('fetch_date', '')
    fetched_at = data.get('fetched_at', '')
    
    print(f"✅ Processing {len(users)} users...")
    
    # Aggregate statistics
    total_users = len(users)
    users_with_positions = sum(1 for u in users if u.get('has_positions', False))
    total_positions = sum(u.get('num_positions', 0) for u in users)
    
    # Aggregate by coin
    coin_stats = defaultdict(lambda: {
        'count': 0,
        'total_value': 0,
        'longs': 0,
        'shorts': 0,
        'longs_total_size': 0,
        'shorts_total_size': 0,
        'longs_unrealized_pnl': 0,
        'shorts_unrealized_pnl': 0,
        'total_unrealized_pnl': 0,
        'total_margin_used': 0
    })
    
    # Risk distribution
    risk_distribution = defaultdict(int)
    
    # Collect all positions for top positions
    all_positions = []
    
    for user in users:
        if not user.get('has_positions', False):
            continue
        
        for position in user.get('positions', []):
            coin = position.get('coin', '')
            direction = position.get('direction', '')
            position_value = position.get('position_value', 0)
            position_size = position.get('size', 0)
            unrealized_pnl = position.get('unrealized_pnl', 0)
            margin_used = position.get('margin_used', 0)
            risk_level = position.get('risk_level', 'UNKNOWN')
            
            # Update coin stats
            coin_stats[coin]['count'] += 1
            coin_stats[coin]['total_value'] += position_value
            coin_stats[coin]['total_unrealized_pnl'] += unrealized_pnl
            coin_stats[coin]['total_margin_used'] += margin_used
            
            if direction == 'LONG':
                coin_stats[coin]['longs'] += 1
                coin_stats[coin]['longs_total_size'] += position_size
                coin_stats[coin]['longs_unrealized_pnl'] += unrealized_pnl
            elif direction == 'SHORT':
                coin_stats[coin]['shorts'] += 1
                coin_stats[coin]['shorts_total_size'] += position_size
                coin_stats[coin]['shorts_unrealized_pnl'] += unrealized_pnl
            
            # Risk distribution
            risk_distribution[risk_level] += 1
            
            # Collect for top positions
            all_positions.append({
                'user_address': user['address'],
                'coin': coin,
                'direction': direction,
                'size': position.get('size', 0),
                'position_value': position_value,
                'unrealized_pnl': unrealized_pnl,
                'entry_price': position.get('entry_price', 0),
                'risk_level': risk_level,
                'margin_used': margin_used
            })
    
    # Calculate long/short ratios
    by_coin = []
    for coin, stats in sorted(coin_stats.items(), key=lambda x: x[1]['total_value'], reverse=True):
        longs = stats['longs']
        shorts = stats['shorts']
        longs_size = stats['longs_total_size']
        shorts_size = stats['shorts_total_size']
        
        # User count based ratio
        long_short_ratio = longs / shorts if shorts > 0 else (longs if longs > 0 else 0)
        
        # Size based ratio
        long_short_size_ratio = longs_size / shorts_size if shorts_size > 0 else (longs_size if longs_size > 0 else 0)
        
        by_coin.append({
            'coin': coin,
            'count': stats['count'],
            'total_value': round(stats['total_value'], 2),
            'longs': longs,
            'shorts': shorts,
            'long_short_ratio': round(long_short_ratio, 2),
            'longs_total_size': round(stats['longs_total_size'], 4),
            'shorts_total_size': round(stats['shorts_total_size'], 4),
            'long_short_size_ratio': round(long_short_size_ratio, 2),
            'longs_unrealized_pnl': round(stats['longs_unrealized_pnl'], 2),
            'shorts_unrealized_pnl': round(stats['shorts_unrealized_pnl'], 2),
            'total_unrealized_pnl': round(stats['total_unrealized_pnl'], 2),
            'total_margin_used': round(stats['total_margin_used'], 2)
        })
    
    # Calculate total position value
    total_position_value = sum(coin['total_value'] for coin in by_coin)
    
    # Top positions (by position value)
    top_positions = sorted(
        all_positions,
        key=lambda x: abs(x['position_value']),
        reverse=True
    )[:50]  # Top 50
    
    # Format top positions
    formatted_top_positions = []
    for pos in top_positions:
        formatted_top_positions.append({
            'user_address': pos['user_address'],
            'coin': pos['coin'],
            'direction': pos['direction'],
            'size': round(pos['size'], 4),
            'position_value': round(pos['position_value'], 2),
            'unrealized_pnl': round(pos['unrealized_pnl'], 2),
            'entry_price': round(pos['entry_price'], 2),
            'risk_level': pos['risk_level'],
            'margin_used': round(pos['margin_used'], 2)
        })
    
    # Build summary object
    summary_data = {
        'generated_at': datetime.utcnow().isoformat(),
        'fetch_date': fetch_date,
        'fetched_at': fetched_at,
        'summary': {
            'total_users': total_users,
            'users_with_positions': users_with_positions,
            'users_without_positions': total_users - users_with_positions,
            'total_positions': total_positions,
            'total_position_value': round(total_position_value, 2),
            'avg_positions_per_user': round(total_positions / users_with_positions, 2) if users_with_positions > 0 else 0
        },
        'by_coin': by_coin,
        'risk_distribution': dict(risk_distribution),
        'top_positions': formatted_top_positions
    }
    
    # Determine output path
    if output_path:
        output_file = Path(output_path)
    else:
        # Default to app/data directory
        workspace_root = Path(__file__).parent.parent.parent
        output_file = workspace_root / 'app' / 'data' / 'basedapp_positions_summary.json'
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    with open(output_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"✅ Summary generated successfully!")
    print(f"📁 Output: {output_file}")
    print()
    print("Summary Statistics:")
    print(f"  Total users: {total_users:,}")
    print(f"  Users with positions: {users_with_positions:,}")
    print(f"  Total positions: {total_positions:,}")
    print(f"  Total position value: ${total_position_value:,.2f}")
    print(f"  Coins tracked: {len(by_coin)}")
    print()


def main():
    parser = argparse.ArgumentParser(description='Generate BasedApp position summary for webapp')
    parser.add_argument(
        'json_file',
        type=str,
        help='Path to positions_summary_hypercore JSON file'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output path for summary JSON (default: app/data/basedapp_positions_summary.json)'
    )
    
    args = parser.parse_args()
    
    generate_summary(args.json_file, args.output)


if __name__ == '__main__':
    main()

