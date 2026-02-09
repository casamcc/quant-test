# Hyperliquid Builders API - Complete Architecture Guide

## 📋 Overview

This document outlines the architecture for extracting user addresses from Hyperliquid Builders (like **BasedApp**) and fetching their positions and liquidation prices.

### What is a Hyperliquid Builder?

Builders on Hyperliquid are **trading frontends/applications** that integrate with Hyperliquid's exchange. When users trade through a Builder's interface, they:
1. Pay a small **usage fee** to the Builder (e.g., 0.025%)
2. Are tracked as that Builder's referred users
3. Contribute to the Builder's volume and revenue metrics

**Example from BasedApp:**
- Rank: #1
- Usage Fee: 0.025%
- Volume (All Time): $32.2B
- Users: 31,085
- Revenue: $11,614,044.76

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA COLLECTION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  🎯 PRIMARY: Official Builder Fills Data                 │   │
│  │  stats-data.hyperliquid.xyz/Mainnet/builder_fills/      │   │
│  │  (LZ4 compressed CSV with all trades per builder)        │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│  ┌────────────────────────┼─────────────────────────────────┐   │
│  │  ALTERNATIVE SOURCES   │                                 │   │
│  │  ┌─────────────────┐   │   ┌─────────────────┐          │   │
│  │  │ Nansen/Allium   │   │   │ WebSocket       │          │   │
│  │  │ (Paid APIs)     │   │   │ (Real-time)     │          │   │
│  │  └────────┬────────┘   │   └────────┬────────┘          │   │
│  └───────────┼────────────┼────────────┼────────────────────┘   │
│              └────────────┼────────────┘                         │
│                           ▼                                      │
│           ┌──────────────────────┐                              │
│           │  Address List        │                              │
│           │  (Builder Users)     │                              │
│           └──────────┬───────────┘                              │
│                      │                                           │
├──────────────────────┼──────────────────────────────────────────┤
│                      ▼                                           │
│              DATA ENRICHMENT LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐     ┌──────────────────┐                  │
│  │  Hyperliquid     │     │  HyData API      │                  │
│  │  Info API        │     │  (Wallet Data)   │                  │
│  │  (Positions)     │     │                  │                  │
│  └────────┬─────────┘     └────────┬─────────┘                  │
│           │                        │                             │
│           └──────────┬─────────────┘                             │
│                      ▼                                           │
│           ┌──────────────────────┐                              │
│           │  Position Data       │                              │
│           │  + Liquidation Px    │                              │
│           └──────────┬───────────┘                              │
│                      │                                           │
├──────────────────────┼──────────────────────────────────────────┤
│                      ▼                                           │
│              ANALYSIS & STORAGE LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐     ┌──────────────────┐                  │
│  │  Database/       │     │  Dashboard/      │                  │
│  │  Storage         │     │  Visualization   │                  │
│  └──────────────────┘     └──────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Finding Builder Addresses

Before you can scrape data, you need the **builder's Ethereum address**.

### Method 1: Check the Builder's Website/App

Most builders display their builder address or referral code in their app settings.

### Method 2: Use Hyperliquid API to Check a Known User

If you know someone uses a specific builder, query their referral state:

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{
    "type": "referral",
    "user": "0xKNOWN_USER_ADDRESS"
  }'
```

### Method 3: Inspect Network Traffic

1. Open the builder's trading interface (e.g., Insilico Terminal)
2. Open browser DevTools → Network tab
3. Make a trade or view orders
4. Look for requests containing `builder` parameter in the payload

### Method 4: Check Hyperliquid Explorer

Navigate to the Hyperliquid Explorer and search for transactions. Builder fee payments show the builder address.

---

## 🔍 Step 1: Getting Builder User Addresses

### The Challenge

**Hyperliquid does NOT provide a simple API endpoint to list all users of a specific Builder.** However, there IS an official data source!

---

### 🎯 Option A: Official Hyperliquid Builder Fills Data (RECOMMENDED)

**This is how @0xLcrgs scraped 1,840 Insilico wallet addresses!**

Hyperliquid provides daily compressed CSV files containing ALL trades for each builder:

```
https://stats-data.hyperliquid.xyz/Mainnet/builder_fills/{builder_address}/{YYYYMMDD}.csv.lz4
```

#### Step 1: Find the Builder Address

Each builder has a unique Ethereum address. You need to find this first.

**Known Builder Addresses:**
| Builder | Address (lowercase required) |
|---------|------------------------------|
| **BasedApp** | `0x1924b8561eef20e70ede628a296175d358be80e5` |
| **Insilico** | `0x2868fc0d9786a740b491577a43502259efa78a39` |

---

## 🚀 EVEN EASIER METHOD: Referral API Endpoint (JUST DISCOVERED!)

**The Hyperliquid `referral` info endpoint returns ALL users directly - no CSV scraping needed!**

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "referral", "user": "0x1924b8561eef20e70ede628a296175d358be80e5"}'
```

### Response Structure (Confirmed Working!):

```json
{
  "referrerState": {
    "stage": "ready",
    "data": {
      "code": "BASEDAPP",
      "nReferrals": 13502,           // Total users! 
      "referralStates": [            // Up to 5000 per request
        {
          "user": "0xb6476abff041be9d02d4d9cb0b1785ddb7190e1d",
          "cumVlm": "81401.6",
          "cumRewardedFeesSinceReferred": "46.475934",
          "timeJoined": 1758091984956
        }
        // ... more users
      ]
    }
  },
  "builderRewards": "11834084.42"    // Total builder rewards earned
}
```

### Verified Stats for BasedApp:
- **Total Users:** 13,502
- **Builder Rewards:** $11,834,084.42
- **API Returns:** 5,000 users per request

### Python Script to Extract All BasedApp User Addresses:

```python
import requests
import json

def get_builder_users(builder_address: str) -> list:
    """
    Get user addresses for a builder using the referral API.
    Note: API returns up to 5000 users per request.
    """
    response = requests.post(
        'https://api.hyperliquid.xyz/info',
        json={
            'type': 'referral',
            'user': builder_address
        }
    )
    
    data = response.json()
    
    # Navigate to the correct path in response
    referrer_state = data.get('referrerState', {})
    state_data = referrer_state.get('data', {})
    
    total_referrals = state_data.get('nReferrals', 0)
    referral_states = state_data.get('referralStates', [])
    
    # Extract user addresses
    users = []
    for entry in referral_states:
        users.append({
            'address': entry['user'],
            'volume': float(entry.get('cumVlm', 0)),
            'fees_paid': float(entry.get('cumRewardedFeesSinceReferred', 0)),
            'joined_timestamp': entry.get('timeJoined')
        })
    
    print(f"Total referrals in system: {total_referrals}")
    print(f"Retrieved in this request: {len(users)}")
    
    return users

# Usage for BasedApp
BASEDAPP_BUILDER = "0x1924b8561eef20e70ede628a296175d358be80e5"
users = get_builder_users(BASEDAPP_BUILDER)

print(f"\nFound {len(users)} BasedApp users!")

# Sort by volume
users_by_volume = sorted(users, key=lambda x: x['volume'], reverse=True)

# Show top 10 by volume
print("\nTop 10 BasedApp users by volume:")
for i, user in enumerate(users_by_volume[:10], 1):
    print(f"{i}. {user['address'][:10]}... - ${user['volume']:,.2f} volume")

# Save all addresses to file
with open('basedapp_users.txt', 'w') as f:
    for user in users:
        f.write(f"{user['address']}\n")

print(f"\nSaved {len(users)} addresses to basedapp_users.txt")
```

#### Step 2: Download Historical Trade Data

```bash
# Download a single day's data (LZ4 compressed)
curl -O "https://stats-data.hyperliquid.xyz/Mainnet/builder_fills/0xbuilderaddress/20241201.csv.lz4"

# Decompress (requires lz4 tool)
lz4 -d 20241201.csv.lz4 20241201.csv
```

#### Step 3: Extract Unique Wallet Addresses

```python
import pandas as pd
import lz4.frame
import requests
from datetime import datetime, timedelta
import os

class BuilderAddressScraper:
    """
    Scrape all wallet addresses that have traded through a specific builder.
    This is the method used by @0xLcrgs to get 1,840 Insilico addresses.
    """
    
    def __init__(self, builder_address: str):
        self.builder_address = builder_address.lower()  # Must be lowercase!
        self.base_url = "https://stats-data.hyperliquid.xyz/Mainnet/builder_fills"
        self.addresses = set()
    
    def download_day(self, date: str) -> pd.DataFrame:
        """Download and parse a single day's trade data."""
        url = f"{self.base_url}/{self.builder_address}/{date}.csv.lz4"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Decompress LZ4 data
                decompressed = lz4.frame.decompress(response.content)
                
                # Parse CSV from bytes
                from io import StringIO
                csv_data = decompressed.decode('utf-8')
                df = pd.read_csv(StringIO(csv_data))
                
                return df
            else:
                print(f"No data for {date} (status: {response.status_code})")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error fetching {date}: {e}")
            return pd.DataFrame()
    
    def scrape_date_range(self, start_date: str, end_date: str) -> set:
        """
        Scrape all unique addresses from a date range.
        
        Args:
            start_date: YYYYMMDD format (e.g., "20240101")
            end_date: YYYYMMDD format (e.g., "20241201")
        
        Returns:
            Set of unique wallet addresses
        """
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        
        current = start
        while current <= end:
            date_str = current.strftime("%Y%m%d")
            print(f"Fetching {date_str}...")
            
            df = self.download_day(date_str)
            
            if not df.empty and 'user' in df.columns:
                # Extract unique addresses from this day
                day_addresses = set(df['user'].unique())
                self.addresses.update(day_addresses)
                print(f"  Found {len(day_addresses)} addresses, total: {len(self.addresses)}")
            
            current += timedelta(days=1)
        
        return self.addresses
    
    def save_addresses(self, filename: str):
        """Save collected addresses to a file."""
        with open(filename, 'w') as f:
            for addr in sorted(self.addresses):
                f.write(f"{addr}\n")
        print(f"Saved {len(self.addresses)} addresses to {filename}")


# Usage Example
if __name__ == "__main__":
    # Replace with actual builder address (must be lowercase!)
    INSILICO_BUILDER = "0x..."  # Find this from Insilico's platform
    
    scraper = BuilderAddressScraper(INSILICO_BUILDER)
    
    # Scrape last 6 months of data
    addresses = scraper.scrape_date_range("20240601", "20241201")
    
    print(f"\n✅ Found {len(addresses)} unique wallet addresses!")
    
    # Save to file
    scraper.save_addresses("insilico_users.txt")
```

#### JavaScript Implementation

```javascript
const https = require('https');
const lz4 = require('lz4');
const { parse } = require('csv-parse/sync');

class BuilderAddressScraper {
    constructor(builderAddress) {
        this.builderAddress = builderAddress.toLowerCase();
        this.baseUrl = 'https://stats-data.hyperliquid.xyz/Mainnet/builder_fills';
        this.addresses = new Set();
    }

    async downloadDay(date) {
        const url = `${this.baseUrl}/${this.builderAddress}/${date}.csv.lz4`;
        
        return new Promise((resolve, reject) => {
            https.get(url, (res) => {
                if (res.statusCode !== 200) {
                    resolve(null);
                    return;
                }
                
                const chunks = [];
                res.on('data', chunk => chunks.push(chunk));
                res.on('end', () => {
                    try {
                        const compressed = Buffer.concat(chunks);
                        const decompressed = lz4.decode(compressed);
                        const csv = decompressed.toString('utf-8');
                        const records = parse(csv, { columns: true });
                        resolve(records);
                    } catch (e) {
                        reject(e);
                    }
                });
            }).on('error', reject);
        });
    }

    async scrapeDateRange(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
            const dateStr = d.toISOString().slice(0, 10).replace(/-/g, '');
            console.log(`Fetching ${dateStr}...`);
            
            const records = await this.downloadDay(dateStr);
            
            if (records) {
                records.forEach(record => {
                    if (record.user) {
                        this.addresses.add(record.user);
                    }
                });
                console.log(`  Total addresses: ${this.addresses.size}`);
            }
            
            // Small delay to be respectful
            await new Promise(r => setTimeout(r, 100));
        }
        
        return Array.from(this.addresses);
    }
}

// Usage
async function main() {
    const scraper = new BuilderAddressScraper('0xYOUR_BUILDER_ADDRESS');
    const addresses = await scraper.scrapeDateRange('2024-06-01', '2024-12-01');
    console.log(`Found ${addresses.length} unique addresses`);
}

main();
```

#### Important Notes

1. **Builder address must be lowercase** - URLs are case-sensitive
2. **Data is compressed with LZ4** - You need to decompress before parsing
3. **Daily files** - Each file covers 24 hours of trades
4. **Rate limiting** - Add delays between requests to be respectful

---

### Option B: Third-Party Analytics Platforms

#### 1. Allium Data

Allium provides the `hyperliquid.raw.builder_labels` table that maps builder addresses and identities.

```sql
-- SQL Query to get builder information
SELECT *
FROM hyperliquid.raw.builder_labels
WHERE builder_name = 'BasedApp'
```

**Website:** [docs.allium.so](https://docs.allium.so/historical-data/supported-blockchains/hyperliquid)

#### 2. Nansen API

Nansen offers Hyperliquid-specific endpoints for tracking wallet positions.

```bash
# Get perpetual positions
curl -X POST https://api.nansen.ai/api/v1/tgm/perp-positions \
  -H "apiKey: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "builder": "BasedApp"
    },
    "pagination": {
      "page": 1,
      "per_page": 100
    }
  }'
```

**Documentation:** [docs.nansen.ai/api/hyperliquid-apis](https://docs.nansen.ai/api/hyperliquid-apis)

#### 3. HyData API

HyData provides wallet analytics and classified transfers.

```bash
# Get wallet overview
curl -X GET "https://api.hydata.dev/v1/wallet/0xYOUR_ADDRESS_HERE"

# Get transfer events
curl -X GET "https://api.hydata.dev/v1/transfers/0xYOUR_ADDRESS_HERE"
```

**Website:** [hydata.dev](https://hydata.dev/)

### Option B: Build Your Own Indexer

If you need real-time data or don't want to rely on third parties:

```javascript
// WebSocket indexer to collect builder users
const WebSocket = require('ws');

class BuilderIndexer {
  constructor(targetBuilder) {
    this.targetBuilder = targetBuilder;
    this.userAddresses = new Set();
    this.ws = null;
  }

  connect() {
    this.ws = new WebSocket('wss://api.hyperliquid.xyz/ws');
    
    this.ws.on('open', () => {
      // Subscribe to all trades
      this.ws.send(JSON.stringify({
        method: 'subscribe',
        subscription: { type: 'trades' }
      }));
    });

    this.ws.on('message', (data) => {
      const trade = JSON.parse(data);
      // Check if trade has builder fee info
      if (trade.builder === this.targetBuilder) {
        this.userAddresses.add(trade.user);
      }
    });
  }

  getAddresses() {
    return Array.from(this.userAddresses);
  }
}

// Usage
const indexer = new BuilderIndexer('BasedApp');
indexer.connect();
```

---

## 📊 Step 2: Fetching Positions for Each Address

Once you have the list of addresses, fetch their positions using Hyperliquid's Info API.

### API Endpoint

```
POST https://api.hyperliquid.xyz/info
```

### Request: HyperCore Positions

```json
{
  "type": "clearinghouseState",
  "user": "0xUSER_ADDRESS_HERE"
}
```

### Response Structure

```json
{
  "marginSummary": {
    "accountValue": "805589.771313",
    "totalNtlPos": "275552.17312",
    "totalMarginUsed": "54530.260016"
  },
  "assetPositions": [
    {
      "type": "oneWay",
      "position": {
        "coin": "BTC",
        "szi": "294.3886",
        "entryPx": "25202.742684",
        "positionValue": "7419400.135111",
        "unrealizedPnl": "22449.284288",
        "leverage": {
          "type": "cross",
          "value": 40
        },
        "liquidationPx": "23447.0007051336",
        "marginUsed": "185485.00337775"
      }
    }
  ]
}
```

### Key Fields

| Field | Description |
|-------|-------------|
| `coin` | Asset symbol (BTC, ETH, etc.) |
| `szi` | Signed size - **Positive = LONG**, **Negative = SHORT** |
| `entryPx` | Average entry price |
| `liquidationPx` | **Liquidation price** (critical!) |
| `leverage.value` | Current leverage |
| `unrealizedPnl` | Current unrealized P&L |

---

## 🧮 Step 3: Calculating Liquidation Prices

### Hyperliquid Liquidation Formula

```
liquidation_price = entry_price - (side × margin_available) / (position_size × (1 - L × side))
```

Where:
- `L = 1 / MAINTENANCE_LEVERAGE`
- `side = 1` for LONG, `-1` for SHORT
- `margin_available`:
  - **Cross margin:** `account_value - maintenance_margin_required`
  - **Isolated margin:** `isolated_margin - maintenance_margin_required`

### JavaScript Implementation

```javascript
function calculateLiquidationPrice(position, marketPrice) {
  const {
    szi,           // Signed size
    entryPx,       // Entry price
    leverage,      // { type, value }
    marginUsed     // Margin used
  } = position;

  const size = Math.abs(parseFloat(szi));
  const side = parseFloat(szi) > 0 ? 1 : -1;  // 1 = Long, -1 = Short
  const entry = parseFloat(entryPx);
  const lev = leverage.value;
  
  // Maintenance leverage is typically 2x the trading leverage
  const maintenanceLeverage = lev * 2;
  const L = 1 / maintenanceLeverage;
  
  // Simplified calculation (actual may vary based on margin mode)
  const margin = parseFloat(marginUsed);
  
  // Calculate liquidation price
  const liqPrice = entry - (side * margin) / (size * (1 - L * side));
  
  return liqPrice;
}
```

---

## 💻 Complete Implementation

### JavaScript/TypeScript

```javascript
const fetch = require('node-fetch');

class BuilderAnalyzer {
  constructor() {
    this.apiUrl = 'https://api.hyperliquid.xyz/info';
  }

  async getPositions(address) {
    // Get HyperCore positions
    const hypercoreResponse = await fetch(this.apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'clearinghouseState',
        user: address
      })
    });
    
    const hypercore = await hypercoreResponse.json();
    
    // Get HIP-3 positions (xyz DEX)
    const hip3Response = await fetch(this.apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'clearinghouseState',
        user: address,
        dex: 'xyz'
      })
    });
    
    const hip3 = await hip3Response.json();
    
    return {
      hypercore: hypercore.assetPositions || [],
      hip3: hip3.assetPositions || []
    };
  }

  formatPosition(position) {
    const pos = position.position;
    const size = parseFloat(pos.szi);
    
    return {
      coin: pos.coin,
      direction: size > 0 ? 'LONG' : 'SHORT',
      size: Math.abs(size),
      entryPrice: parseFloat(pos.entryPx),
      liquidationPrice: pos.liquidationPx ? parseFloat(pos.liquidationPx) : null,
      unrealizedPnl: parseFloat(pos.unrealizedPnl),
      leverage: pos.leverage.value,
      marginType: pos.leverage.type,
      positionValue: parseFloat(pos.positionValue)
    };
  }

  async analyzeBuilderUsers(addresses) {
    const results = [];
    
    for (const address of addresses) {
      try {
        const positions = await this.getPositions(address);
        
        const formattedPositions = {
          address,
          hypercore: positions.hypercore.map(p => this.formatPosition(p)),
          hip3: positions.hip3.map(p => this.formatPosition(p))
        };
        
        results.push(formattedPositions);
        
        // Rate limiting: 100ms between requests
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error fetching ${address}:`, error.message);
      }
    }
    
    return results;
  }

  // Find positions at risk of liquidation
  findAtRiskPositions(results, threshold = 0.1) {
    const atRisk = [];
    
    for (const user of results) {
      const allPositions = [...user.hypercore, ...user.hip3];
      
      for (const pos of allPositions) {
        if (pos.liquidationPrice) {
          // Calculate distance to liquidation
          const distancePercent = Math.abs(
            (pos.entryPrice - pos.liquidationPrice) / pos.entryPrice
          );
          
          if (distancePercent <= threshold) {
            atRisk.push({
              address: user.address,
              ...pos,
              distanceToLiquidation: (distancePercent * 100).toFixed(2) + '%'
            });
          }
        }
      }
    }
    
    return atRisk.sort((a, b) => 
      parseFloat(a.distanceToLiquidation) - parseFloat(b.distanceToLiquidation)
    );
  }
}

// Usage Example
async function main() {
  const analyzer = new BuilderAnalyzer();
  
  // Example addresses (you would get these from a data source)
  const basedAppUsers = [
    '0x7da85a334e43a6b1c2c0da9623409d9ee9047747',
    '0xAnotherAddress...',
    // ... more addresses
  ];
  
  console.log('Analyzing BasedApp user positions...\n');
  
  const results = await analyzer.analyzeBuilderUsers(basedAppUsers);
  
  // Display results
  for (const user of results) {
    console.log(`\n=== ${user.address.slice(0, 10)}... ===`);
    
    for (const pos of user.hypercore) {
      console.log(`  ${pos.coin}: ${pos.direction} ${pos.size}`);
      console.log(`    Entry: $${pos.entryPrice.toFixed(2)}`);
      console.log(`    Liq:   $${pos.liquidationPrice?.toFixed(2) || 'N/A'}`);
      console.log(`    PnL:   $${pos.unrealizedPnl.toFixed(2)}`);
    }
  }
  
  // Find at-risk positions (within 10% of liquidation)
  console.log('\n=== POSITIONS AT RISK (within 10% of liquidation) ===');
  const atRisk = analyzer.findAtRiskPositions(results, 0.10);
  
  for (const pos of atRisk) {
    console.log(`${pos.address.slice(0, 10)}... | ${pos.coin} ${pos.direction}`);
    console.log(`  Distance to Liq: ${pos.distanceToLiquidation}`);
  }
}

main().catch(console.error);
```

### Python Implementation

```python
import requests
import time
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Position:
    coin: str
    direction: str
    size: float
    entry_price: float
    liquidation_price: Optional[float]
    unrealized_pnl: float
    leverage: int
    margin_type: str
    position_value: float

class BuilderAnalyzer:
    def __init__(self):
        self.api_url = "https://api.hyperliquid.xyz/info"
    
    def get_positions(self, address: str) -> Dict:
        """Fetch both HyperCore and HIP-3 positions for an address"""
        
        # HyperCore positions
        hypercore_response = requests.post(
            self.api_url,
            json={"type": "clearinghouseState", "user": address}
        )
        hypercore = hypercore_response.json()
        
        # HIP-3 positions (xyz DEX)
        hip3_response = requests.post(
            self.api_url,
            json={"type": "clearinghouseState", "user": address, "dex": "xyz"}
        )
        hip3 = hip3_response.json()
        
        return {
            "hypercore": hypercore.get("assetPositions", []),
            "hip3": hip3.get("assetPositions", [])
        }
    
    def format_position(self, position: Dict) -> Position:
        """Format raw position data into a Position object"""
        pos = position["position"]
        size = float(pos["szi"])
        
        return Position(
            coin=pos["coin"],
            direction="LONG" if size > 0 else "SHORT",
            size=abs(size),
            entry_price=float(pos["entryPx"]),
            liquidation_price=float(pos["liquidationPx"]) if pos.get("liquidationPx") else None,
            unrealized_pnl=float(pos["unrealizedPnl"]),
            leverage=pos["leverage"]["value"],
            margin_type=pos["leverage"]["type"],
            position_value=float(pos["positionValue"])
        )
    
    def analyze_builder_users(self, addresses: List[str]) -> List[Dict]:
        """Analyze positions for a list of builder user addresses"""
        results = []
        
        for address in addresses:
            try:
                positions = self.get_positions(address)
                
                formatted = {
                    "address": address,
                    "hypercore": [self.format_position(p) for p in positions["hypercore"]],
                    "hip3": [self.format_position(p) for p in positions["hip3"]]
                }
                
                results.append(formatted)
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error fetching {address}: {e}")
        
        return results
    
    def find_at_risk_positions(self, results: List[Dict], threshold: float = 0.1) -> List[Dict]:
        """Find positions within threshold % of liquidation"""
        at_risk = []
        
        for user in results:
            all_positions = user["hypercore"] + user["hip3"]
            
            for pos in all_positions:
                if pos.liquidation_price:
                    distance_percent = abs(
                        (pos.entry_price - pos.liquidation_price) / pos.entry_price
                    )
                    
                    if distance_percent <= threshold:
                        at_risk.append({
                            "address": user["address"],
                            "position": pos,
                            "distance_to_liquidation": f"{distance_percent * 100:.2f}%"
                        })
        
        return sorted(at_risk, key=lambda x: float(x["distance_to_liquidation"].rstrip('%')))


# Usage
if __name__ == "__main__":
    analyzer = BuilderAnalyzer()
    
    # Example addresses (you would get these from a data source)
    based_app_users = [
        "0x7da85a334e43a6b1c2c0da9623409d9ee9047747",
        # ... more addresses
    ]
    
    print("Analyzing BasedApp user positions...\n")
    
    results = analyzer.analyze_builder_users(based_app_users)
    
    for user in results:
        print(f"\n=== {user['address'][:10]}... ===")
        for pos in user["hypercore"]:
            print(f"  {pos.coin}: {pos.direction} {pos.size}")
            print(f"    Entry: ${pos.entry_price:.2f}")
            print(f"    Liq:   ${pos.liquidation_price:.2f}" if pos.liquidation_price else "    Liq:   N/A")
            print(f"    PnL:   ${pos.unrealized_pnl:.2f}")
    
    # Find at-risk positions
    print("\n=== POSITIONS AT RISK (within 10% of liquidation) ===")
    at_risk = analyzer.find_at_risk_positions(results, 0.10)
    
    for item in at_risk:
        pos = item["position"]
        print(f"{item['address'][:10]}... | {pos.coin} {pos.direction}")
        print(f"  Distance to Liq: {item['distance_to_liquidation']}")
```

---

## 📚 API Reference Summary

### Hyperliquid Info Endpoint

| Request Type | Description |
|--------------|-------------|
| `clearinghouseState` | Get user positions (HyperCore) |
| `clearinghouseState` + `dex` | Get user positions (HIP-3) |
| `metaAndAssetCtxs` | Get market metadata |
| `userFills` | Get user trade history |
| `historicalOrders` | Get order history |
| `userFunding` | Get funding payments |

### Rate Limits

- **1200 weight per minute per IP**
- Recommended: **10-20 requests per second**
- Add **50-100ms delay** between requests

---

## 🔗 Resources

| Resource | URL |
|----------|-----|
| Hyperliquid API Docs | https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api |
| HyData API | https://hydata.dev |
| Nansen Hyperliquid API | https://docs.nansen.ai/api/hyperliquid-apis |
| Allium Data | https://docs.allium.so/historical-data/supported-blockchains/hyperliquid |
| hl-sdk (Python) | https://pypi.org/project/hl-sdk/ |
| hl-sdk GitHub | https://github.com/papicapital/hl-sdk |

---

## ⚠️ Important Notes

### Builder Data Limitations

1. **No Direct API for Builder Users**: Hyperliquid doesn't expose an endpoint to get all users of a specific builder
2. **Third-Party Required**: You'll need Nansen, Allium, or your own indexer to get user lists
3. **Historical Data**: Building an indexer from scratch requires historical trade data

### Builder Fee Approval Check

Hyperliquid provides an endpoint to check if a user has approved builder fees:

```json
{
  "type": "maxBuilderFee",
  "user": "0xUSER_ADDRESS",
  "builder": "0xBUILDER_ADDRESS"
}
```

### Liquidation Price Considerations

- **Cross Margin**: Liquidation price can change as account value fluctuates
- **Isolated Margin**: Liquidation price is more predictable (fixed margin)
- **Null Values**: Some positions may not have `liquidationPx` in API response

---

## 🎯 Quick Start Checklist

- [ ] Choose data source for Builder user addresses (Nansen/Allium/Custom Indexer)
- [ ] Set up API access for chosen data source
- [ ] Implement position fetching using Hyperliquid Info API
- [ ] Add rate limiting (100ms delay between requests)
- [ ] Calculate liquidation risk metrics
- [ ] Set up monitoring/alerts for at-risk positions

---

## 📈 Example Output

```
=== Analyzing BasedApp Users ===

Address: 0x7da85a33...
  BTC: LONG 10.5 @ $97,500.00
    Liquidation: $92,125.00 (5.5% away)
    PnL: +$15,234.56
  
  ETH: SHORT 150.0 @ $3,650.00
    Liquidation: $4,015.00 (10% away)
    PnL: -$2,100.00

=== POSITIONS AT RISK ===

1. 0x7da85a33... | BTC LONG
   Distance to Liq: 5.5%

2. 0x45d2c4a1... | SOL LONG
   Distance to Liq: 7.2%
```

