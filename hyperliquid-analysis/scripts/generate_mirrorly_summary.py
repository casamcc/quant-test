#!/usr/bin/env python3
"""
Generate Mirrorly Trader Summary for Webapp
Merges CSV trader metadata with current position data
"""

import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


def parse_categories(category_string):
    """Parse comma-separated category string into list"""
    if not category_string or category_string.strip() == '':
        return []
    return [cat.strip() for cat in category_string.split(',')]


def parse_number(value_string):
    """Parse number from string, handling commas and empty values"""
    if not value_string or value_string.strip() == '':
        return None
    try:
        # Remove commas and convert to float
        cleaned = value_string.replace(',', '')
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def classify_performance_tier(trader_data):
    """
    Classify trader into performance tier based on scratchpad insights
    
    Strong: Win Rate > 50% + Positive Profit + positive tags
    Avoid: Negative Pnl tag or Bad KOL
    Watch: Everything else (Heavy Drawdown, mixed signals, etc.)
    """
    categories = trader_data.get('categories', [])
    win_rate = trader_data.get('win_rate')
    total_profit = trader_data.get('total_profit')
    
    # Avoid tier - clear negative signals
    negative_tags = ['Negative Pnl', 'Bad KOL']
    if any(tag in categories for tag in negative_tags):
        return 'avoid'
    
    # Strong tier - positive indicators
    positive_tags = ['God Tier', 'Consistent Winner', 'Winning Streak']
    has_positive_tags = any(tag in categories for tag in positive_tags)
    
    if (win_rate and win_rate > 50 and 
        total_profit and total_profit > 0 and 
        has_positive_tags):
        return 'strong'
    
    # Watch tier - everything else
    return 'watch'


def generate_summary(csv_file_path, positions_json_path, output_path=None):
    """
    Generate webapp-ready summary from CSV and positions JSON
    
    Args:
        csv_file_path: Path to Hyperliquid List CSV
        positions_json_path: Path to positions_summary_hypercore JSON
        output_path: Optional output path
    """
    csv_path = Path(csv_file_path)
    json_path = Path(positions_json_path)
    
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        return
    
    print(f"📂 Loading CSV from: {csv_path.name}")
    print(f"📂 Loading positions from: {json_path.name}")
    print()
    
    # Load CSV trader metadata
    traders_by_address = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            address = row['Address'].lower()
            traders_by_address[address] = {
                'name': row['Name'],
                'address': row['Address'],  # Keep original case
                'categories': parse_categories(row['Category']),
                'win_rate': parse_number(row['Win Rate']),
                'wins': int(row['Win']) if row['Win'] else None,
                'losses': int(row['Loss']) if row['Loss'] else None,
                'total_profit': parse_number(row['Total Profit'])
            }
    
    print(f"✅ Loaded {len(traders_by_address)} traders from CSV")
    
    # Load position data
    with open(json_path, 'r') as f:
        positions_data = json.load(f)
    
    fetch_date = positions_data.get('fetch_date', '')
    fetched_at = positions_data.get('fetched_at', '')
    users = positions_data.get('users', [])
    
    print(f"✅ Loaded position data for {len(users)} addresses")
    print()
    
    # Merge data
    merged_traders = []
    category_counts = defaultdict(int)
    
    for user in users:
        address = user['address'].lower()
        
        if address not in traders_by_address:
            print(f"⚠️  Warning: Address {user['address']} not found in CSV")
            continue
        
        trader = traders_by_address[address].copy()
        
        # Add position data
        trader['has_positions'] = user.get('has_positions', False)
        trader['num_positions'] = user.get('num_positions', 0)
        
        # Extract account summary
        account_summary = user.get('account_summary', {})
        trader['account_value'] = account_summary.get('account_value', 0)
        
        # Calculate total unrealized PnL from positions
        unrealized_pnl = 0
        top_coins = []
        if trader['has_positions']:
            positions = user.get('positions', [])
            for pos in positions:
                unrealized_pnl += pos.get('unrealized_pnl', 0)
            # Get top 3 coins by position value
            sorted_positions = sorted(
                positions,
                key=lambda p: abs(p.get('position_value', 0)),
                reverse=True
            )
            top_coins = [p['coin'] for p in sorted_positions[:3]]
        
        trader['unrealized_pnl'] = unrealized_pnl
        trader['top_coins'] = top_coins
        
        # Classify performance tier
        trader['performance_tier'] = classify_performance_tier(trader)
        
        # Count categories
        for category in trader['categories']:
            category_counts[category] += 1
        
        merged_traders.append(trader)
    
    print(f"✅ Merged {len(merged_traders)} traders with position data")
    print()
    
    # Calculate summary statistics
    total_traders = len(merged_traders)
    traders_with_positions = sum(1 for t in merged_traders if t['has_positions'])
    total_positions = sum(t['num_positions'] for t in merged_traders)
    
    # Group by performance tier
    by_performance_tier = {
        'strong': [t for t in merged_traders if t['performance_tier'] == 'strong'],
        'watch': [t for t in merged_traders if t['performance_tier'] == 'watch'],
        'avoid': [t for t in merged_traders if t['performance_tier'] == 'avoid']
    }
    
    # Sort traders by total profit (descending, nulls last)
    def sort_key(trader):
        profit = trader.get('total_profit')
        if profit is None:
            return float('-inf')
        return profit
    
    merged_traders.sort(key=sort_key, reverse=True)
    
    # Build summary object
    summary_data = {
        'generated_at': datetime.utcnow().isoformat(),
        'fetch_date': fetch_date,
        'fetched_at': fetched_at,
        'summary': {
            'total_traders': total_traders,
            'traders_with_positions': traders_with_positions,
            'total_positions': total_positions,
            'category_counts': dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))
        },
        'traders': merged_traders,
        'by_performance_tier': {
            'strong': sorted(by_performance_tier['strong'], key=sort_key, reverse=True),
            'watch': sorted(by_performance_tier['watch'], key=sort_key, reverse=True),
            'avoid': sorted(by_performance_tier['avoid'], key=sort_key, reverse=True)
        }
    }
    
    # Determine output path
    if output_path:
        output_file = Path(output_path)
    else:
        # Default to app/data directory
        workspace_root = Path(__file__).parent.parent.parent
        output_file = workspace_root / 'app' / 'data' / f'mirrorly_summary_{fetch_date}.json'
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    with open(output_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"✅ Summary generated successfully!")
    print(f"📁 Output: {output_file}")
    print()
    print("Summary Statistics:")
    print(f"  Total traders: {total_traders}")
    print(f"  Traders with positions: {traders_with_positions}")
    print(f"  Total positions: {total_positions}")
    print(f"  Category breakdown:")
    for category, count in list(category_counts.items())[:10]:
        print(f"    - {category}: {count}")
    print()
    print("Performance Tiers:")
    print(f"  Strong: {len(by_performance_tier['strong'])} traders")
    print(f"  Watch: {len(by_performance_tier['watch'])} traders")
    print(f"  Avoid: {len(by_performance_tier['avoid'])} traders")
    print()


def main():
    parser = argparse.ArgumentParser(description='Generate Mirrorly trader summary for webapp')
    parser.add_argument(
        '--csv',
        type=str,
        default='hyperliquid-analysis/data/processed/mirror/source/user/Hyperliquid List - Sheet2.csv',
        help='Path to CSV file with trader metadata'
    )
    parser.add_argument(
        '--positions',
        type=str,
        default='hyperliquid-analysis/data/processed/mirrorly/source/positions/positions_summary_hypercore_20260209.json',
        help='Path to positions summary JSON'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output path for summary JSON (default: app/data/mirrorly_summary_{date}.json)'
    )
    
    args = parser.parse_args()
    
    generate_summary(args.csv, args.positions, args.output)


if __name__ == '__main__':
    main()
