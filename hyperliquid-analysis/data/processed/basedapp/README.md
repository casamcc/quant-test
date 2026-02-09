# BasedApp Trading Data

**Builder:** BasedApp  
**Builder Address:** `0x3dbbbf8a1c8164c2e812a03067b678dbbf9f67f3`  
**Data Collected:** December 3, 2024  
**Lookback Period:** 30 days (November 2 - December 2, 2024)

---

## 📁 Directory Structure

### ✅ **Source Data** (`source/`)
Primary datasets - **DO NOT DELETE** - all analyses depend on these:

#### `source/users/`
User extraction data:
- **`basedapp_users_final.json`** (3.5 MB) - All 14,496 unique BasedApp users (merged dataset) ⭐
- `basedapp_users_csv.json` (2.3 MB) - Users from historical CSV method (11,441 users)
- `basedapp_users_referral.json` (1.1 MB) - Users from referral API (5,000 users)
- `validation_report.json` (422 B) - Data quality and overlap report

#### `source/positions/`
Position data from API (HyperCore only):
- **`positions_raw_hypercore.json`** (7.5 MB) - Raw API responses for 6,289 active users ⭐
- **`positions_summary_hypercore.json`** (5.1 MB) - Processed position data ⭐
  - 2,856 users with positions (45.4%)
  - 4,200 total positions found
  - Markets: BTC, ETH, SOL, HYPE, and other perpetuals

### 📊 **Analysis Outputs** (`analysis/`)
Derived analyses - can be regenerated from source data:

#### `analysis/filtered_users/`
- `active_users_7days.json` (315 KB) - 6,289 users active in last 7 days

#### `analysis/smart_money/`
- `smart_money_addresses.json` (25 KB) - Top 20 performers by absolute PnL
- `dumb_money_addresses.json` (28 KB) - Bottom 20 performers by absolute PnL

---

## 📊 Key Statistics

| Metric | Value |
|--------|-------|
| Total Users | 14,496 |
| Active Users (7d) | 6,289 (43.4%) |
| Users with Positions | 2,856 (45.4% of active) |
| Total Positions | 4,200 |
| Top Asset | HYPE (1,741 positions, 41.5%) |
| Data Freshness | December 3, 2024 |

---

## 🔍 Notable Findings

1. **Large User Base** - 14,496 users (14.5x larger than Insilico)
2. **Active Referral System** - 5,000 users from referrals (vs 0 for Insilico)
3. **High Position Rate** - 45.4% of active users have open positions
4. **HYPE Dominance** - 41.5% of all positions are in HYPE token
5. **Long Bias** - 75.1% long vs 24.9% short across all positions
6. **HyperCore Focus** - Only perpetual positions (BTC, ETH, SOL, HYPE, etc.)

---

## 💰 Position Highlights

### Total Position Value
- **$22.6 Million** across 4,200 positions
- Average position size: $5,377

### Top Assets by Position Count
1. HYPE - 1,741 positions (41.5%)
2. BTC - 538 positions (12.8%)
3. ETH - 267 positions (6.4%)
4. SOL - 149 positions (3.5%)

### Risk Distribution
- **Critical Risk**: 134 positions (3.2%)
- **High Risk**: 152 positions (3.6%)
- **Moderate Risk**: 420 positions (10.0%)
- **Low Risk**: 2,925 positions (69.6%)

---

## 🧠 Smart Money Analysis

### Top Performers
- **Smart Money**: 60.6% short bias, 13.1x avg leverage
- **Dumb Money**: 76.3% long bias, 8.3x avg leverage

### Key Insight
Smart money is heavily SHORT while the market is heavily LONG, suggesting potential overextension.

---

## 🔄 How to Regenerate Analyses

All analysis outputs can be regenerated from source data:

```bash
# Smart money analysis
python3 scripts/smart_vs_dumb_money.py

# Filter active users
python3 scripts/filter_active_users.py

# HYPE analysis
python3 scripts/analyze_hype.py
```

---

## 📖 Related Documentation

See project root for analysis scripts:
- `scripts/06_fetch_basedapp_users.py` - User extraction
- `scripts/07_fetch_basedapp_positions.py` - Position fetching
- `scripts/smart_vs_dumb_money.py` - Smart money analysis
- `scripts/analyze_hype.py` - HYPE token deep dive

---

## 🔄 Next Steps

This folder contains complete BasedApp data. Structure matches Insilico for consistency across builders.
