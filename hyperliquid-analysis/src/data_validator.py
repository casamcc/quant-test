"""
Data Validator
Compare and validate results from different scraping methods
"""
import json
import sys
import os
from typing import Dict, List, Any, Set
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class DataValidator:
    """Validate and merge user data from multiple sources"""
    
    def __init__(self):
        self.referral_data = None
        self.csv_data = None
        self.validation_report = {}
        
    def load_referral_data(self, filepath: str):
        """Load users from referral API output"""
        with open(filepath, 'r') as f:
            self.referral_data = json.load(f)
        print(f"✅ Loaded {len(self.referral_data['users'])} users from referral API")
    
    def load_csv_data(self, filepath: str):
        """Load users from CSV scraper output"""
        with open(filepath, 'r') as f:
            self.csv_data = json.load(f)
        print(f"✅ Loaded {len(self.csv_data['users'])} users from CSV method")
    
    def validate_ethereum_address(self, address: str) -> bool:
        """Check if address is valid Ethereum format"""
        return address.startswith('0x') and len(address) == 42
    
    def compare_datasets(self) -> Dict[str, Any]:
        """
        Compare referral API and CSV datasets
        
        Returns:
            Validation report with statistics
        """
        print("\n🔍 Comparing datasets...\n")
        
        # Extract address sets
        referral_addresses = set(u['address'] for u in self.referral_data['users'])
        csv_addresses = set(u['address'] for u in self.csv_data['users'])
        
        # Calculate overlaps
        intersection = referral_addresses & csv_addresses
        only_referral = referral_addresses - csv_addresses
        only_csv = csv_addresses - referral_addresses
        total_unique = referral_addresses | csv_addresses
        
        # Data quality checks
        invalid_referral = [a for a in referral_addresses if not self.validate_ethereum_address(a)]
        invalid_csv = [a for a in csv_addresses if not self.validate_ethereum_address(a)]
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'builder': self.referral_data['builder'],
            'counts': {
                'referral_api': len(referral_addresses),
                'csv_method': len(csv_addresses),
                'intersection': len(intersection),
                'only_in_referral': len(only_referral),
                'only_in_csv': len(only_csv),
                'total_unique': len(total_unique)
            },
            'data_quality': {
                'invalid_addresses_referral': len(invalid_referral),
                'invalid_addresses_csv': len(invalid_csv),
                'duplicate_check_passed': (
                    len(referral_addresses) == len(self.referral_data['users']) and
                    len(csv_addresses) == len(self.csv_data['users'])
                )
            },
            'overlap_percentage': (len(intersection) / len(total_unique) * 100) if total_unique else 0
        }
        
        # Print summary
        print(f"📊 Validation Report")
        print(f"  Referral API users:    {report['counts']['referral_api']:,}")
        print(f"  CSV method users:      {report['counts']['csv_method']:,}")
        print(f"  Total unique users:    {report['counts']['total_unique']:,}")
        print(f"  Overlap:               {report['counts']['intersection']:,} ({report['overlap_percentage']:.1f}%)")
        print(f"  Only in Referral API:  {report['counts']['only_in_referral']:,}")
        print(f"  Only in CSV:           {report['counts']['only_in_csv']:,}")
        print(f"\n  Data quality:")
        print(f"  Invalid addresses:     {report['data_quality']['invalid_addresses_referral'] + report['data_quality']['invalid_addresses_csv']}")
        print(f"  No duplicates:         {'✅' if report['data_quality']['duplicate_check_passed'] else '❌'}")
        
        self.validation_report = report
        return report
    
    def merge_datasets(self) -> List[Dict[str, Any]]:
        """
        Merge both datasets into a single unified list
        Prioritize CSV data for completeness, enrich with referral API data
        
        Returns:
            Merged user list
        """
        print("\n🔄 Merging datasets...")
        
        # Create lookup dict from referral data
        referral_lookup = {u['address']: u for u in self.referral_data['users']}
        csv_lookup = {u['address']: u for u in self.csv_data['users']}
        
        # Merge
        all_addresses = set(referral_lookup.keys()) | set(csv_lookup.keys())
        merged_users = []
        
        for address in all_addresses:
            user = {'address': address}
            
            # Add data from CSV if available
            if address in csv_lookup:
                user.update(csv_lookup[address])
                user['source'] = 'csv'
            
            # Enrich with referral API data if available
            if address in referral_lookup:
                ref_user = referral_lookup[address]
                if 'source' in user:
                    user['source'] = 'both'
                else:
                    user['source'] = 'referral'
                
                # Add referral-specific fields
                user['api_volume'] = ref_user.get('volume')
                user['api_fees_paid'] = ref_user.get('fees_paid')
                user['api_joined_date'] = ref_user.get('joined_date')
            
            merged_users.append(user)
        
        print(f"✅ Merged {len(merged_users)} unique users")
        
        return merged_users
    
    def save_report(self, filepath: str):
        """Save validation report"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.validation_report, f, indent=2)
        
        print(f"💾 Validation report saved to {filepath}")
    
    def save_merged_data(self, filepath: str, merged_users: List[Dict]):
        """Save merged user dataset"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        output = {
            'builder': self.referral_data['builder'],
            'builder_address': self.referral_data['builder_address'],
            'merged_at': datetime.now().isoformat(),
            'total_users': len(merged_users),
            'validation_summary': self.validation_report.get('counts', {}),
            'users': merged_users
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"💾 Merged dataset saved to {filepath}")











