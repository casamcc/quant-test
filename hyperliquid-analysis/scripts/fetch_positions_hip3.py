#!/usr/bin/env python3
"""
Fetch HIP-3 Positions for Builder Users
Fetches HIP-3/xyz dex positions only (spot markets) - no HyperCore positions
Supports: insilico, basedapp
"""

import sys
import json
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.api_client import HyperliquidClient
from src.position_processor import PositionProcessor


def fetch_hip3_only(client, address, delay=0.1):
    """Fetch only HIP-3 positions (xyz dex)"""
    result = {
        'address': address,
        'fetched_at': datetime.utcnow().isoformat(),
        'hip3_xyz': None,
        'error': None
    }
    
    try:
        # Fetch HIP-3 positions only (xyz dex)
        hip3_data = client.get_clearinghouse_state(address, dex='xyz')
        result['hip3_xyz'] = hip3_data
        time.sleep(delay)
    except Exception as e:
        result['error'] = str(e)
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Fetch HIP-3 positions for a builder')
    parser.add_argument(
        'builder',
        choices=['insilico', 'basedapp'],
        help='Builder name'
    )
    parser.add_argument(
        '--input-file',
        type=str,
        help='Path to user addresses JSON file (default: auto-detect from builder)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=10,
        choices=[1, 10, 20],
        help='Number of parallel workers (default: 10)'
    )
    
    args = parser.parse_args()
    builder_name = args.builder
    
    # Generate date string for filenames
    date_str = datetime.utcnow().strftime('%Y%m%d')
    
    print("=" * 60)
    print(f"POSITION FETCHING - {builder_name.upper()} (HIP-3/xyz DEX Only)")
    print("=" * 60)
    print()
    
    # Determine input file
    if args.input_file:
        input_file = Path(args.input_file)
    else:
        # Auto-detect: try active users first, then fall back to final users
        active_file = Path(__file__).parent.parent / 'data' / 'processed' / builder_name / 'active_users_7days.json'
        
        if active_file.exists():
            input_file = active_file
            print(f"📂 Using active users file")
        else:
            # Find most recent final users file
            final_files = list(Path(__file__).parent.parent / 'data' / 'processed' / builder_name / 'source' / 'users').glob(f'{builder_name}_users_final_*.json')
            if final_files:
                input_file = max(final_files, key=lambda p: p.stat().st_mtime)
                print(f"📂 Using most recent users file: {input_file.name}")
            else:
                print(f"❌ No user files found. Please run fetch_users.py first or specify --input-file")
                return
    
    print(f"📂 Loading user addresses from: {input_file.name}")
    
    with open(input_file, 'r') as f:
        data = json.load(f)
        # Handle different file structures
        if 'addresses' in data:
            addresses = data['addresses']
        elif 'users' in data:
            addresses = [user['address'] if isinstance(user, dict) else user for user in data['users']]
        else:
            print(f"❌ Invalid file format. Expected 'addresses' or 'users' key.")
            return
    
    print(f"✅ Loaded {len(addresses)} addresses")
    print()
    
    # Configuration
    print("⚙️  Configuration:")
    print("   Markets: HIP-3/xyz DEX only (spot markets)")
    print("   Skipping: HyperCore (perpetuals)")
    print("   API calls: 1 per user")
    print()
    
    # Worker configuration
    if args.workers == 1:
        workers = 1
        delay = 1.0
        estimated_time = len(addresses) * 1.2 / 60
    elif args.workers == 20:
        workers = 20
        delay = 0.1
        estimated_time = len(addresses) * 0.3 / 20 / 60
    else:  # default to 10
        workers = 10
        delay = 0.1
        estimated_time = len(addresses) * 0.3 / 10 / 60
    
    print(f"⚙️  Running with:")
    print(f"   Workers: {workers}")
    print(f"   Delay: {delay}s")
    print(f"   Total API calls: {len(addresses):,}")
    print(f"   Estimated time: ~{estimated_time:.1f} minutes")
    print()
    
    # Initialize client
    client = HyperliquidClient()
    
    # Fetch positions
    print("🔄 Fetching positions...")
    start_time = time.time()
    
    if workers == 1:
        # Sequential
        raw_results = []
        for address in tqdm(addresses, desc="Fetching"):
            result = fetch_hip3_only(client, address, delay)
            raw_results.append(result)
    else:
        # Parallel
        raw_results = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(fetch_hip3_only, client, addr, delay): addr 
                for addr in addresses
            }
            
            for future in tqdm(as_completed(futures), total=len(addresses), desc="Fetching"):
                try:
                    result = future.result()
                    raw_results.append(result)
                except Exception as e:
                    print(f"Error: {e}")
    
    elapsed_time = time.time() - start_time
    print()
    print(f"✅ Fetching complete in {elapsed_time/60:.1f} minutes!")
    print()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'data' / 'processed' / builder_name / 'source' / 'positions'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save raw results
    raw_output_file = output_dir / f'positions_raw_hip3_{date_str}.json'
    print(f"💾 Saving raw data to: {raw_output_file.name}")
    
    with open(raw_output_file, 'w') as f:
        json.dump({
            'fetched_at': raw_results[0]['fetched_at'] if raw_results else None,
            'fetch_date': date_str,
            'total_users': len(raw_results),
            'markets': 'HIP-3/xyz DEX only',
            'builder': builder_name,
            'users': raw_results
        }, f, indent=2)
    
    print()
    
    # Process positions
    print("📊 Processing position data...")
    processor = PositionProcessor()
    
    processed_results = []
    users_with_positions = 0
    total_positions = 0
    errors = 0
    
    for raw_data in raw_results:
        processed = processor.process_user_positions(raw_data)
        processed_results.append(processed)
        
        if processed['has_positions']:
            users_with_positions += 1
            total_positions += processed['num_positions']
        
        if processed.get('error'):
            errors += 1
    
    # Save processed results
    processed_output_file = output_dir / f'positions_summary_hip3_{date_str}.json'
    print(f"💾 Saving processed data to: {processed_output_file.name}")
    
    with open(processed_output_file, 'w') as f:
        json.dump({
            'fetched_at': raw_results[0]['fetched_at'] if raw_results else None,
            'fetch_date': date_str,
            'total_users_queried': len(addresses),
            'users_with_positions': users_with_positions,
            'total_positions': total_positions,
            'errors': errors,
            'markets': 'HIP-3/xyz DEX only',
            'builder': builder_name,
            'users': processed_results
        }, f, indent=2)
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total users queried:     {len(addresses):,}")
    print(f"Users with positions:    {users_with_positions:,} ({users_with_positions/len(addresses)*100:.1f}%)")
    print(f"Total positions found:   {total_positions:,}")
    print(f"Errors:                  {errors}")
    print(f"Time elapsed:            {elapsed_time/60:.1f} minutes")
    print()
    print("✅ Position fetching complete!")
    print()
    print("📁 Output files:")
    print(f"   - {raw_output_file}")
    print(f"   - {processed_output_file}")
    print()


if __name__ == '__main__':
    main()

