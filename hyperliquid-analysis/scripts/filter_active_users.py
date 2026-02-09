#!/usr/bin/env python3
"""
Filter BasedApp users by activity recency
Shows distribution of users by last trade date
"""
import json
from datetime import datetime, timedelta
from collections import Counter

# Load BasedApp users
with open('data/processed/basedapp/basedapp_users_final.json', 'r') as f:
    data = json.load(f)

users = data['users']
print(f"Total users: {len(users)}")
print()

# Filter users with CSV data (have last_trade_date)
csv_users = [u for u in users if 'last_trade_date' in u]
print(f"Users with trade history: {len(csv_users)}")
print()

# Analyze last trade dates
last_trade_dates = [u['last_trade_date'] for u in csv_users]
date_counter = Counter(last_trade_dates)

# Show distribution by date
print("Last Trade Date Distribution (last 10 days):")
print("-" * 50)
sorted_dates = sorted(date_counter.keys(), reverse=True)[:10]
for date in sorted_dates:
    count = date_counter[date]
    # Convert YYYYMMDD to readable format
    readable = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
    print(f"{readable}: {count:4d} users")

print()

# Filter by recency
def filter_by_days(users, days):
    """Filter users who traded in last N days"""
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    return [u for u in users if u.get('last_trade_date', '0') >= cutoff_date]

# Show counts for different time windows
print("Active User Counts by Time Window:")
print("-" * 50)
for days in [1, 3, 7, 14, 30]:
    active = filter_by_days(csv_users, days)
    pct = len(active) / len(users) * 100
    print(f"Last {days:2d} days: {len(active):5d} users ({pct:5.1f}% of total)")

print()

# Recommended filter
recommended_days = 7
active_users = filter_by_days(csv_users, recommended_days)
print(f"✅ Recommended: Filter for last {recommended_days} days")
print(f"   Active users: {len(active_users)}")
print(f"   Reduction: {len(users) - len(active_users)} users ({(1 - len(active_users)/len(users))*100:.1f}% reduction)")
print()

# Save filtered addresses
output_file = 'data/processed/basedapp/active_users_7days.json'
active_addresses = [u['address'] for u in active_users]

with open(output_file, 'w') as f:
    json.dump({
        'filtered_at': datetime.now().isoformat(),
        'filter_criteria': f'last_trade_date >= {recommended_days} days ago',
        'total_active_users': len(active_addresses),
        'addresses': active_addresses
    }, f, indent=2)

print(f"💾 Saved active user addresses to: {output_file}")
