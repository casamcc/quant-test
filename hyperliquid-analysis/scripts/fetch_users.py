#!/usr/bin/env python3
"""
Unified User Fetching Script
Fetches users for a given builder using both Referral API and CSV methods
Supports: insilico, basedapp
"""

import sys
import os
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.referral_scraper import ReferralScraper
from src.csv_scraper import CSVScraper
from src.data_validator import DataValidator


def main():
    parser = argparse.ArgumentParser(description='Fetch users for a builder')
    parser.add_argument(
        'builder',
        choices=list(config.BUILDERS.keys()),
        help='Builder name (insilico or basedapp)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Days to fetch for CSV method (default: 30)'
    )
    
    args = parser.parse_args()
    
    builder_name = args.builder
    builder_address = config.BUILDERS[builder_name]
    days_to_fetch = args.days
    
    # Generate date string for filenames
    date_str = datetime.utcnow().strftime('%Y%m%d')
    
    print("=" * 60)
    print(f"USER EXTRACTION - {builder_name.upper()}")
    print("=" * 60)
    
    print(f"\nBuilder: {builder_name}")
    print(f"Address: {builder_address}")
    print(f"Time window: {days_to_fetch} days")
    print(f"Date: {date_str}\n")
    
    # Create output directory structure
    output_dir = os.path.join(config.PROCESSED_DIR, builder_name, 'source', 'users')
    os.makedirs(output_dir, exist_ok=True)
    
    # ========================================
    # METHOD 1: Referral API
    # ========================================
    print("\n" + "=" * 60)
    print("METHOD 1: Referral API")
    print("=" * 60)
    
    referral_scraper = ReferralScraper(builder_address, builder_name)
    referral_users = referral_scraper.fetch_all_users()
    
    referral_file = os.path.join(output_dir, f"{builder_name}_users_referral_{date_str}.json")
    referral_scraper.save_to_file(referral_file)
    
    print(f"\n✅ Referral API: {len(referral_users)} users")
    
    # ========================================
    # METHOD 2: Historical CSV
    # ========================================
    print("\n" + "=" * 60)
    print("METHOD 2: Historical CSV")
    print("=" * 60)
    
    csv_scraper = CSVScraper(builder_address, builder_name)
    csv_users = csv_scraper.fetch_historical_users(days_back=days_to_fetch)
    
    csv_file = os.path.join(output_dir, f"{builder_name}_users_csv_{date_str}.json")
    csv_scraper.save_to_file(csv_file)
    
    print(f"\n✅ CSV Method: {len(csv_users)} users")
    
    # ========================================
    # VALIDATION & MERGE
    # ========================================
    print("\n" + "=" * 60)
    print("VALIDATION & MERGE")
    print("=" * 60)
    
    validator = DataValidator()
    
    # Load both datasets
    validator.load_referral_data(referral_file)
    validator.load_csv_data(csv_file)
    
    # Compare datasets
    validator.compare_datasets()
    
    # Merge datasets
    merged_users = validator.merge_datasets()
    
    # Save final dataset with date
    final_file = os.path.join(output_dir, f"{builder_name}_users_final_{date_str}.json")
    validator.save_merged_data(final_file, merged_users)
    
    # Save validation report with date
    report_file = os.path.join(output_dir, f"validation_report_{date_str}.json")
    validator.save_report(report_file)
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    summary = validator.validation_report.get('counts', {})
    
    print(f"\n📊 Data Sources:")
    print(f"  Referral API: {summary.get('referral_api', 0)} users")
    print(f"  CSV Method: {summary.get('csv_method', 0)} users")
    print(f"  Intersection: {summary.get('intersection', 0)} users")
    print(f"  Only in Referral: {summary.get('only_in_referral', 0)} users")
    print(f"  Only in CSV: {summary.get('only_in_csv', 0)} users")
    print(f"\n✅ Total Unique Users: {summary.get('total_unique', 0)}")
    
    if merged_users:
        # Show top 5 by trade count
        sorted_users = sorted(
            [u for u in merged_users if 'total_trades' in u],
            key=lambda x: x.get('total_trades', 0),
            reverse=True
        )
        if sorted_users:
            print(f"\n🏆 Top 5 Most Active Users:")
            for i, user in enumerate(sorted_users[:5], 1):
                trades = user.get('total_trades', 0)
                print(f"  {i}. {user['address'][:10]}... - {trades:,} trades")
    
    print(f"\n📁 Output Files:")
    print(f"  {referral_file}")
    print(f"  {csv_file}")
    print(f"  {final_file}")
    print(f"  {report_file}")
    
    print(f"\n✅ Done! {builder_name} user extraction complete.")


if __name__ == "__main__":
    main()

