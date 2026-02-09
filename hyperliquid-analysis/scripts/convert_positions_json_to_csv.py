#!/usr/bin/env python3
"""
Convert Position JSON to CSV
Converts positions_summary JSON files to CSV format
"""

import sys
import json
import csv
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import the export function directly
import csv
from datetime import datetime


def export_to_csv(processed_results, output_dir, date_str, builder_name):
    """
    Export processed position data to CSV files
    
    Creates two CSV files:
    1. users_summary.csv - One row per user with account summary
    2. positions_detail.csv - One row per position with user address
    """
    # Prepare user-level data
    users_data = []
    positions_data = []
    
    for user in processed_results:
        # User-level row
        account_summary = user.get('account_summary', {})
        user_row = {
            'address': user['address'],
            'fetched_at': user['fetched_at'],
            'has_positions': user['has_positions'],
            'num_positions': user['num_positions'],
            'account_value': account_summary.get('account_value', 0),
            'total_margin_used': account_summary.get('total_margin_used', 0),
            'total_unrealized_pnl': account_summary.get('total_unrealized_pnl', 0),
            'total_position_value': account_summary.get('total_position_value', 0),
            'error': user.get('error') or ''
        }
        users_data.append(user_row)
        
        # Position-level rows
        for position in user.get('positions', []):
            # Flatten leverage dict if present
            leverage_type = ''
            leverage_value = ''
            if isinstance(position.get('leverage'), dict):
                leverage_type = position['leverage'].get('type', '')
                leverage_value = position['leverage'].get('value', '')
            elif position.get('leverage'):
                leverage_value = str(position['leverage'])
            
            position_row = {
                'user_address': user['address'],
                'coin': position.get('coin', ''),
                'market_type': position.get('market_type', ''),
                'direction': position.get('direction', ''),
                'size': position.get('size', 0),
                'entry_price': position.get('entry_price', 0),
                'liquidation_price': position.get('liquidation_price') or '',
                'position_value': position.get('position_value', 0),
                'unrealized_pnl': position.get('unrealized_pnl', 0),
                'pnl_percent': position.get('pnl_percent', 0),
                'leverage_type': leverage_type,
                'leverage_value': leverage_value,
                'margin_used': position.get('margin_used', 0),
                'distance_to_liq_pct': position.get('distance_to_liq_pct') or '',
                'distance_to_liq_usd': position.get('distance_to_liq_usd') or '',
                'risk_level': position.get('risk_level', '')
            }
            positions_data.append(position_row)
    
    # Write users CSV
    users_csv_file = output_dir / f'users_summary_hypercore_{date_str}.csv'
    if users_data:
        fieldnames = ['address', 'fetched_at', 'has_positions', 'num_positions',
                     'account_value', 'total_margin_used', 'total_unrealized_pnl',
                     'total_position_value', 'error']
        with open(users_csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users_data)
        print(f"💾 Saving users CSV to: {users_csv_file.name}")
    
    # Write positions CSV
    positions_csv_file = output_dir / f'positions_detail_hypercore_{date_str}.csv'
    if positions_data:
        fieldnames = ['user_address', 'coin', 'market_type', 'direction', 'size',
                     'entry_price', 'liquidation_price', 'position_value',
                     'unrealized_pnl', 'pnl_percent', 'leverage_type', 'leverage_value',
                     'margin_used', 'distance_to_liq_pct', 'distance_to_liq_usd', 'risk_level']
        with open(positions_csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(positions_data)
        print(f"💾 Saving positions CSV to: {positions_csv_file.name}")
    
    return users_csv_file, positions_csv_file


def convert_json_to_csv(json_file_path, output_dir=None):
    """
    Convert positions summary JSON to CSV files
    
    Args:
        json_file_path: Path to positions_summary JSON file
        output_dir: Optional output directory (defaults to same directory as JSON file)
    """
    json_path = Path(json_file_path)
    
    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        return
    
    print(f"📂 Loading JSON from: {json_path.name}")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Extract users data
    processed_results = data.get('users', [])
    
    if not processed_results:
        print("❌ No user data found in JSON file")
        return
    
    print(f"✅ Loaded {len(processed_results)} users")
    
    # Determine output directory
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = json_path.parent
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract date string from filename or use current date
    date_str = data.get('fetch_date', '')
    if not date_str:
        # Try to extract from filename
        filename = json_path.stem
        if 'hypercore_' in filename:
            parts = filename.split('hypercore_')
            if len(parts) > 1:
                date_str = parts[1]
    
    if not date_str:
        from datetime import datetime
        date_str = datetime.utcnow().strftime('%Y%m%d')
    
    builder_name = data.get('builder', 'unknown')
    
    print()
    print("📊 Converting to CSV...")
    
    # Use the export function from fetch_positions_hypercore
    users_csv_file, positions_csv_file = export_to_csv(
        processed_results, output_dir, date_str, builder_name
    )
    
    print()
    print("=" * 60)
    print("CONVERSION COMPLETE")
    print("=" * 60)
    print(f"Users CSV:     {users_csv_file}")
    print(f"Positions CSV: {positions_csv_file}")
    print()


def main():
    parser = argparse.ArgumentParser(description='Convert positions JSON to CSV')
    parser.add_argument(
        'json_file',
        type=str,
        help='Path to positions_summary JSON file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for CSV files (default: same as JSON file)'
    )
    
    args = parser.parse_args()
    
    convert_json_to_csv(args.json_file, args.output_dir)


if __name__ == '__main__':
    main()

