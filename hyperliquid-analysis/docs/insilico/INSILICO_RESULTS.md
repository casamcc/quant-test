# Insilico Trading - User Extraction Results

## Summary

**✅ Successfully extracted 996 unique Insilico users from 50 days of historical data**

---

## Extraction Details

| Metric | Value |
|--------|-------|
| **Total Users Found** | 996 |
| **Date Range** | Oct 13 - Dec 2, 2024 (50 days) |
| **Days Processed** | 49/50 (2 recent days unavailable) |
| **Method Used** | Historical CSV parsing |
| **Builder Address** | `0x2868fc0d9786a740b491577a43502259efa78a39` |
| **Builder Rewards** | $2,536,003.71 |

---

## Most Active Traders (Top 10)

| Rank | Address | Total Trades |
|------|---------|-------------|
| 1 | `0x57fc5d08...` | 87,662 |
| 2 | `0x6c8031a9...` | 57,696 |
| 3 | `0x2669f508...` | 52,712 |
| 4 | `0x5aa13316...` | 50,885 |
| 5 | `0xe927f4a3...` | 45,729 |
| 6 | `0x97fec1cd...` | 34,649 |
| 7 | `0x97bff6e4...` | 30,905 |
| 8 | `0x908cba90...` | 30,641 |
| 9 | `0xcc5b1fef...` | 29,776 |
| 10 | `0x8dbfd29a...` | 29,252 |

---

## Key Discovery

### Insilico Does NOT Use Referral System

The referral API returned **0 users** despite Insilico earning $2.5M in builder rewards. This means:

- Insilico uses **builder fee codes** directly
- No referral tracking in Hyperliquid's system
- **CSV method is the ONLY way** to extract their user list

---

## Generated Files

| File | Description | Users |
|------|-------------|-------|
| `insilico_users_csv.json` | Full dataset with trade stats | 996 |
| `insilico_users_final.json` | Validated & merged dataset | 996 |
| `insilico_addresses_only.txt` | Plain text address list | 996 |
| `validation_report.json` | Data quality metrics | - |

---

## Comparison: Expected vs Actual

| Source | Count | Notes |
|--------|-------|-------|
| @0xLcrgs Tweet | ~1,840 users | Likely ALL historical data |
| Our 50-day scan | 996 users | Oct 13 - Dec 2, 2024 |
| **Difference** | -844 users | Need longer lookback |

### To Get All ~1,840 Users

```python
# Edit config.py
DAYS_TO_FETCH = 180  # 6 months
# or
DAYS_TO_FETCH = 365  # 1 year

# Re-run
python3 scripts/02_fetch_csv_users.py
```

---

## Next Steps: Position & Liquidation Analysis

### Step 1: Sample Position Fetch (Test with 10 users)

```python
from src.api_client import HyperliquidClient
import json

client = HyperliquidClient()

with open('data/processed/insilico_addresses_only.txt', 'r') as f:
    addresses = [line.strip() for line in f.readlines()]

# Test with first 10 users
for address in addresses[:10]:
    print(f"\nFetching positions for {address[:10]}...")
    
    # HyperCore positions
    positions = client.get_clearinghouse_state(address)
    if positions and positions.get('assetPositions'):
        for asset in positions['assetPositions']:
            pos = asset['position']
            direction = 'LONG' if float(pos['szi']) > 0 else 'SHORT'
            print(f"  {pos['coin']}: {direction}")
            print(f"    Entry: ${pos['entryPx']}")
            print(f"    Liquidation: ${pos.get('liquidationPx', 'N/A')}")
```

### Step 2: Bulk Position Analysis

Create a new script to:
1. Fetch positions for all 996 users (with rate limiting)
2. Extract liquidation prices
3. Calculate risk metrics
4. Generate liquidation proximity report

---

## Success Criteria Met ✅

- [x] Created Python analysis infrastructure
- [x] Tested both extraction methods (Referral API + CSV)
- [x] Validated data quality (0 invalid addresses, 0 duplicates)
- [x] Generated clean user lists ready for analysis
- [x] Documented findings and next steps

