# Insilico Trading Data

**Builder:** Insilico  
**Builder Address:** `0x2868fc0d9786a740b491577a43502259efa78a39`  
**Data Collected:** December 2, 2024  
**Lookback Period:** 50 days (October 13 - December 2, 2024)

---

## 📁 Directory Structure

### ✅ **Source Data** (`source/`)
Primary datasets - **DO NOT DELETE** - all analyses depend on these:

#### `source/users/`
User extraction data:
- **`insilico_users_final.json`** (226 KB) - All 996 unique Insilico users (merged dataset) ⭐
- `insilico_users_csv.json` (203 KB) - Users from historical CSV method
- `insilico_users_referral.json` (177 B) - Users from referral API (0 results)

#### `source/positions/`
Position data from API:
- **`positions_raw.json`** (2.0 MB) - Raw API responses for all 996 users ⭐
- **`positions_summary.json`** (1.0 MB) - Processed position data ⭐
  - 278 users with positions (27.9%)
  - 718 users with no positions (72.1%)
  - 1,110 total positions found

### 📊 **Analysis Outputs** (`analysis/`)
Derived analyses - can be regenerated from source data:

#### `analysis/btc/`
- `btc_positions.json` - All 116 BTC positions with metadata
- `btc_positions.csv` - BTC positions in spreadsheet format
  - 80 LONG positions ($81.2M)
  - 36 SHORT positions ($2.3M)
  - Long/Short ratio: 2.22:1

#### `analysis/smart_money/`
- `smart_longs_post_pump.json` - Traders who profited from BTC/HYPE pump
- `dumb_shorts_post_pump.json` - Traders who lost fighting the pump
- `true_smart_money.json` - Actually profitable positions (good entries)
- `true_dumb_money.json` - Actually losing positions (bad entries)

#### `analysis/no_positions/`
- `insilico_no_positions.csv` - 718 users with NO current positions

#### `analysis/exports/`
- `insilico_addresses_only.txt` - Plain text list of all addresses

---

## 📊 Key Statistics

| Metric | Value |
|--------|-------|
| Total Users | 996 |
| Users with Positions | 278 (27.9%) |
| Users with NO Positions | 718 (72.1%) |
| Total Positions | 1,110 |
| BTC Positions | 116 |
| Data Freshness | December 2, 2024 |

---

## 🔍 Notable Findings

1. **Low Position Rate** - Only 27.9% of users have open positions
2. **BTC Bias** - 97.3% of BTC exposure is LONG (bullish)
3. **Mega Whale** - Single $58M LONG position dominates
4. **Referral Method Failed** - Insilico doesn't use referral tracking
5. **CSV Method Success** - Historical trade data was the only reliable source

---

## 📖 Documentation

See `docs/insilico/` for detailed analysis:
- `INSILICO_RESULTS.md` - User extraction process & findings
- `POSITION_ANALYSIS.md` - Complete position analysis report

---

## 🔄 Next Steps

This folder contains complete Insilico data. Future builder analyses (BasedApp, etc.) will have similar folder structures.











