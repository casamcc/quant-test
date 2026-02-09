"""
CSV Scraper
Download and parse historical trade data from builder_fills CSV files
"""
import requests
import lz4.frame
import json
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set
from io import StringIO
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class CSVScraper:
    """Scrape user addresses from historical CSV files"""
    
    def __init__(self, builder_address: str, builder_name: str = "unknown"):
        self.builder_address = builder_address.lower()  # Must be lowercase for URLs
        self.builder_name = builder_name
        self.base_url = config.BUILDER_FILLS_BASE_URL
        self.users_data = {}
        
    def _download_day(self, date_str: str) -> pd.DataFrame:
        """
        Download and decompress a single day's CSV file
        
        Args:
            date_str: Date in YYYYMMDD format
            
        Returns:
            DataFrame with trade data or empty DataFrame
        """
        url = f"{self.base_url}/{self.builder_address}/{date_str}.csv.lz4"
        
        try:
            response = requests.get(url, timeout=config.TIMEOUT)
            
            if response.status_code == 200:
                # Decompress LZ4
                decompressed = lz4.frame.decompress(response.content)
                csv_data = decompressed.decode('utf-8')
                
                # Parse CSV
                df = pd.read_csv(StringIO(csv_data))
                return df
            elif response.status_code == 404:
                # No data for this day (expected for recent dates)
                return pd.DataFrame()
            elif response.status_code == 403:
                print(f"    ⚠️  Access denied for {date_str}")
                return pd.DataFrame()
            else:
                print(f"    ⚠️  Failed to fetch {date_str}: Status {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"    ⚠️  Error fetching {date_str}: {e}")
            return pd.DataFrame()
    
    def fetch_historical_users(self, days_back: int = None) -> List[Dict[str, Any]]:
        """
        Fetch all unique users from historical CSV files
        
        Args:
            days_back: Number of days to go back (default from config)
            
        Returns:
            List of user dicts with aggregated statistics
        """
        if days_back is None:
            days_back = config.DAYS_TO_FETCH
        
        print(f"\n📥 Fetching historical CSV data for {self.builder_name}...")
        print(f"  Looking back {days_back} days")
        
        # Generate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        user_addresses = set()
        user_stats = {}  # Track stats per user
        
        # Iterate through dates
        current_date = start_date
        successful_days = 0
        
        with tqdm(total=days_back, desc="Downloading CSV files") as pbar:
            while current_date <= end_date:
                date_str = current_date.strftime("%Y%m%d")
                
                df = self._download_day(date_str)
                
                if not df.empty and 'user' in df.columns:
                    # Extract unique users from this day
                    day_users = set(df['user'].unique())
                    user_addresses.update(day_users)
                    
                    # Aggregate stats per user
                    for user in day_users:
                        user_trades = df[df['user'] == user]
                        
                        if user not in user_stats:
                            user_stats[user] = {
                                'address': user,
                                'total_trades': 0,
                                'first_trade_date': date_str,
                                'last_trade_date': date_str,
                                'total_volume': 0.0
                            }
                        
                        user_stats[user]['total_trades'] += len(user_trades)
                        user_stats[user]['last_trade_date'] = date_str
                        
                        # Sum volume if available
                        if 'size' in df.columns and 'px' in df.columns:
                            volume = (user_trades['size'].abs() * user_trades['px']).sum()
                            user_stats[user]['total_volume'] += float(volume)
                    
                    successful_days += 1
                
                current_date += timedelta(days=1)
                pbar.update(1)
        
        print(f"\n  ✅ Successfully processed {successful_days}/{days_back} days")
        print(f"  ✅ Found {len(user_addresses)} unique user addresses")
        
        # Convert to list
        users_list = list(user_stats.values())
        self.users_data = user_stats
        
        return users_list
    
    def save_to_file(self, filepath: str):
        """Save users to JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        output = {
            'builder': self.builder_name,
            'builder_address': self.builder_address,
            'extracted_at': datetime.now().isoformat(),
            'method': 'historical_csv',
            'days_fetched': config.DAYS_TO_FETCH,
            'total_users': len(self.users_data),
            'users': list(self.users_data.values())
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"💾 Saved to {filepath}")











