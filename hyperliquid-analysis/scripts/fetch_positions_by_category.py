#!/usr/bin/env python3
"""
Fetch Positions by Category
Reads a CSV of addresses with categories and fetches their Hyperliquid positions
Groups results by category for sentiment analysis
"""

import sys
import csv
import json
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from tqdm import tqdm
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.api_client import HyperliquidClient
from src.position_processor import PositionProcessor


def load_addresses_from_csv(csv_path):
    """Load addresses from CSV with Name, Address, Category columns"""
    addresses = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            addresses.append({
                'name': row.get('Name', '').strip(),
                'address': row.get('Address', '').strip(),
                'category': row.get('Category', 'Unknown').strip()
            })
    return addresses


def fetch_position(client, address_info, delay=0.1):
    """Fetch position for a single address"""
    result = {
        'name': address_info['name'],
        'address': address_info['address'],
        'category': address_info['category'],
        'fetched_at': datetime.utcnow().isoformat(),
        'hypercore': None,
        'error': None
    }
    
    try:
        hypercore_data = client.get_clearinghouse_state(address_info['address'])
        result['hypercore'] = hypercore_data
        time.sleep(delay)
    except Exception as e:
        result['error'] = str(e)
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Fetch positions by category from CSV')
    parser.add_argument(
        'csv_file',
        type=str,
        help='Path to CSV file with Name, Address, Category columns'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file path (default: positions_by_category_YYYYMMDD.json)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=5,
        help='Number of parallel workers (default: 5)'
    )
    
    args = parser.parse_args()
    
    date_str = datetime.utcnow().strftime('%Y%m%d')
    
    print("=" * 60)
    print("FETCH POSITIONS BY CATEGORY")
    print("=" * 60)
    print()
    
    # Load addresses from CSV
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    addresses = load_addresses_from_csv(csv_path)
    print(f"📂 Loaded {len(addresses)} addresses from {csv_path.name}")
    
    # Show category breakdown
    categories = defaultdict(list)
    for addr in addresses:
        categories[addr['category']].append(addr['name'])
    
    print(f"\n📊 Categories:")
    for cat, names in sorted(categories.items()):
        print(f"   {cat}: {len(names)} traders")
    print()
    
    # Initialize client and processor
    client = HyperliquidClient()
    processor = PositionProcessor()
    
    # Fetch positions
    print("🔄 Fetching positions...")
    start_time = time.time()
    
    raw_results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(fetch_position, client, addr, 0.15): addr 
            for addr in addresses
        }
        
        for future in tqdm(as_completed(futures), total=len(addresses), desc="Fetching"):
            try:
                result = future.result()
                raw_results.append(result)
            except Exception as e:
                print(f"Error: {e}")
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ Fetching complete in {elapsed_time:.1f} seconds")
    
    # Process positions
    print("\n📊 Processing positions...")
    
    traders = []
    by_category = defaultdict(lambda: {
        'traders': 0,
        'traders_with_positions': 0,
        'total_positions': 0,
        'longs': 0,
        'shorts': 0,
        'total_long_value': 0,
        'total_short_value': 0,
        'by_coin': defaultdict(lambda: {'longs': 0, 'shorts': 0, 'long_value': 0, 'short_value': 0})
    })
    
    for raw_data in raw_results:
        processed = processor.process_user_positions(raw_data)
        
        category = raw_data['category']
        by_category[category]['traders'] += 1
        
        trader_data = {
            'name': raw_data['name'],
            'address': raw_data['address'],
            'category': category,
            'has_positions': processed['has_positions'],
            'num_positions': processed['num_positions'],
            'account_value': processed['account_summary'].get('account_value', 0),
            'positions': []
        }
        
        if processed['has_positions']:
            by_category[category]['traders_with_positions'] += 1
            by_category[category]['total_positions'] += processed['num_positions']
            
            for pos in processed['positions']:
                direction = pos['direction']
                coin = pos['coin']
                value = pos['position_value']
                
                if direction == 'LONG':
                    by_category[category]['longs'] += 1
                    by_category[category]['total_long_value'] += value
                    by_category[category]['by_coin'][coin]['longs'] += 1
                    by_category[category]['by_coin'][coin]['long_value'] += value
                else:
                    by_category[category]['shorts'] += 1
                    by_category[category]['total_short_value'] += value
                    by_category[category]['by_coin'][coin]['shorts'] += 1
                    by_category[category]['by_coin'][coin]['short_value'] += value
                
                trader_data['positions'].append({
                    'coin': coin,
                    'direction': direction,
                    'size': pos['size'],
                    'position_value': round(pos['position_value'], 2),
                    'unrealized_pnl': round(pos['unrealized_pnl'], 2),
                    'entry_price': pos['entry_price'],
                    'risk_level': pos.get('risk_level', 'UNKNOWN')
                })
        
        traders.append(trader_data)
    
    # Convert defaultdicts to regular dicts and calculate ratios
    by_category_output = {}
    for cat, stats in by_category.items():
        longs = stats['longs']
        shorts = stats['shorts']
        long_short_ratio = longs / shorts if shorts > 0 else (longs if longs > 0 else 0)
        
        by_coin_output = {}
        for coin, coin_stats in stats['by_coin'].items():
            coin_longs = coin_stats['longs']
            coin_shorts = coin_stats['shorts']
            by_coin_output[coin] = {
                'longs': coin_longs,
                'shorts': coin_shorts,
                'long_value': round(coin_stats['long_value'], 2),
                'short_value': round(coin_stats['short_value'], 2),
                'ratio': round(coin_longs / coin_shorts, 2) if coin_shorts > 0 else coin_longs
            }
        
        by_category_output[cat] = {
            'traders': stats['traders'],
            'traders_with_positions': stats['traders_with_positions'],
            'total_positions': stats['total_positions'],
            'longs': longs,
            'shorts': shorts,
            'long_short_ratio': round(long_short_ratio, 2),
            'total_long_value': round(stats['total_long_value'], 2),
            'total_short_value': round(stats['total_short_value'], 2),
            'by_coin': by_coin_output
        }
    
    # Sort traders by category then by account value
    traders.sort(key=lambda x: (x['category'], -x['account_value']))
    
    # Build output
    output = {
        'generated_at': datetime.utcnow().isoformat(),
        'source_file': csv_path.name,
        'total_traders': len(traders),
        'traders_with_positions': sum(1 for t in traders if t['has_positions']),
        'by_category': by_category_output,
        'traders': traders
    }
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path(__file__).parent.parent / 'data' / 'processed' / 'custom'
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f'positions_by_category_{date_str}.json'
    
    # Save output
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    # Print summary
    print()
    print("=" * 60)
    print("SENTIMENT SUMMARY BY CATEGORY")
    print("=" * 60)
    
    for cat in sorted(by_category_output.keys()):
        stats = by_category_output[cat]
        print(f"\n📊 {cat}:")
        print(f"   Traders: {stats['traders']} ({stats['traders_with_positions']} with positions)")
        print(f"   Positions: {stats['total_positions']} ({stats['longs']} long, {stats['shorts']} short)")
        print(f"   Long/Short Ratio: {stats['long_short_ratio']}")
        print(f"   Long Value: ${stats['total_long_value']:,.2f}")
        print(f"   Short Value: ${stats['total_short_value']:,.2f}")
        
        if stats['by_coin']:
            print(f"   By Coin:")
            for coin, coin_stats in sorted(stats['by_coin'].items(), key=lambda x: -(x[1]['long_value'] + x[1]['short_value'])):
                print(f"      {coin}: {coin_stats['longs']}L / {coin_stats['shorts']}S (ratio: {coin_stats['ratio']})")
    
    print()
    print("=" * 60)
    print(f"✅ Results saved to: {output_path}")
    print("=" * 60)


if __name__ == '__main__':
    main()
