# Hyperliquid API - Complete Guide to Fetching All Positions

## Overview

Hyperliquid has two types of perpetual markets that require separate API calls:
1. **HyperCore** - Native Hyperliquid perpetuals (BTC, ETH, SOL, etc.)
2. **HIP-3** - Multi-DEX perpetuals (xyz:XYZ100, xyz:TSLA, etc.)

You must query both separately to get a complete picture of a user's positions.

---

## API Endpoint

```
POST https://api.hyperliquid.xyz/info
```

---

## 1. Fetching HyperCore Positions (Native Markets)

### Request Format

```json
{
  "type": "clearinghouseState",
  "user": "0xUSER_ADDRESS_HERE"
}
```

### cURL Example

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{
    "type": "clearinghouseState",
    "user": "0x7da85a334e43a6b1c2c0da9623409d9ee9047747"
  }'
```

### Response Structure

```json
{
  "marginSummary": {
    "accountValue": "805589.771313",
    "totalNtlPos": "275552.17312",
    "totalMarginUsed": "54530.260016"
  },
  "crossMarginSummary": { ... },
  "assetPositions": [
    {
      "type": "oneWay",
      "position": {
        "coin": "BTC",
        "szi": "294.3886",           // Positive = LONG, Negative = SHORT
        "entryPx": "25202.742684",   // Entry price
        "positionValue": "7419400.135111",
        "unrealizedPnl": "22449.284288",
        "leverage": {
          "type": "cross",
          "value": 40
        },
        "liquidationPx": null,
        "marginUsed": "185485.00337775"
      }
    }
  ]
}
```

### Key Fields

| Field | Description |
|-------|-------------|
| `coin` | Asset symbol (BTC, ETH, SOL, etc.) |
| `szi` | Signed size - **Positive = LONG**, **Negative = SHORT** |
| `entryPx` | Average entry price |
| `unrealizedPnl` | Current unrealized profit/loss |
| `positionValue` | Total notional value in USD |
| `leverage.type` | "cross" or "isolated" |
| `leverage.value` | Leverage multiplier |

---

## 2. Fetching HIP-3 Positions (Multi-DEX Markets)

### Request Format

**The key difference:** Add `"dex"` parameter to specify which HIP-3 DEX to query.

```json
{
  "type": "clearinghouseState",
  "user": "0xUSER_ADDRESS_HERE",
  "dex": "xyz"
}
```

### Known HIP-3 DEX Identifiers

- `"xyz"` - XYZ Perps (offers XYZ100, TSLA, AAPL, etc.)
- `"unit"` - Unit Perps
- More DEXes will launch over time

### cURL Example

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{
    "type": "clearinghouseState",
    "user": "0x7da85a334e43a6b1c2c0da9623409d9ee9047747",
    "dex": "xyz"
  }'
```

### Response Structure

```json
{
  "marginSummary": {
    "accountValue": "228776.559687",
    "totalNtlPos": "2400555.0",
    "totalMarginUsed": "228776.559687"
  },
  "assetPositions": [
    {
      "type": "oneWay",
      "position": {
        "coin": "xyz:XYZ100",       // Note the "dex:market" format
        "szi": "95.0",
        "entryPx": "25696.25",
        "positionValue": "2400555.0",
        "unrealizedPnl": "-40589.663",
        "leverage": {
          "type": "isolated",
          "value": 10
        },
        "liquidationPx": "23447.0007051336",
        "cumFunding": {
          "allTime": "25702.1009"
        }
      }
    }
  ]
}
```

---

## 3. Complete Implementation Examples

### JavaScript/TypeScript

```javascript
async function getAllUserPositions(address) {
  const results = {
    hypercore: null,
    hip3: {}
  };
  
  // 1. Fetch HyperCore positions
  const hypercoreResponse = await fetch('https://api.hyperliquid.xyz/info', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      type: 'clearinghouseState',
      user: address
    })
  });
  results.hypercore = await hypercoreResponse.json();
  
  // 2. Fetch HIP-3 positions from each known DEX
  const dexes = ['xyz', 'unit'];
  
  for (const dex of dexes) {
    try {
      const hip3Response = await fetch('https://api.hyperliquid.xyz/info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'clearinghouseState',
          user: address,
          dex: dex
        })
      });
      
      const hip3Data = await hip3Response.json();
      
      // Only store if user has positions on this DEX
      if (hip3Data.assetPositions && hip3Data.assetPositions.length > 0) {
        results.hip3[dex] = hip3Data;
      }
    } catch (error) {
      console.log(`No positions on ${dex} DEX`);
    }
  }
  
  return results;
}

// Usage
const address = '0x7da85a334e43a6b1c2c0da9623409d9ee9047747';
const positions = await getAllUserPositions(address);

console.log('HyperCore positions:', positions.hypercore.assetPositions);
console.log('HIP-3 positions:', positions.hip3);
```

### Python

```python
import requests

def get_all_user_positions(address):
    """Fetch both HyperCore and HIP-3 positions"""
    results = {
        'hypercore': None,
        'hip3': {}
    }
    
    # 1. Get HyperCore positions
    response = requests.post(
        'https://api.hyperliquid.xyz/info',
        json={'type': 'clearinghouseState', 'user': address}
    )
    results['hypercore'] = response.json()
    
    # 2. Get HIP-3 positions from each DEX
    dexes = ['xyz', 'unit']
    
    for dex in dexes:
        try:
            response = requests.post(
                'https://api.hyperliquid.xyz/info',
                json={
                    'type': 'clearinghouseState',
                    'user': address,
                    'dex': dex
                }
            )
            hip3_data = response.json()
            
            # Only store if user has positions
            if hip3_data.get('assetPositions'):
                results['hip3'][dex] = hip3_data
                
        except Exception as e:
            print(f"No positions on {dex} DEX: {e}")
    
    return results

# Usage
address = '0x7da85a334e43a6b1c2c0da9623409d9ee9047747'
all_positions = get_all_user_positions(address)

# Display summary
print(f"HyperCore: {len(all_positions['hypercore']['assetPositions'])} positions")
for dex, data in all_positions['hip3'].items():
    print(f"{dex} DEX: {len(data['assetPositions'])} positions")
    for pos in data['assetPositions']:
        coin = pos['position']['coin']
        size = float(pos['position']['szi'])
        direction = 'LONG' if size > 0 else 'SHORT'
        pnl = float(pos['position']['unrealizedPnl'])
        print(f"  {coin}: {direction} {abs(size)}, PnL: ${pnl:,.2f}")
```

### Bash/cURL Script

```bash
#!/bin/bash

ADDRESS="0x7da85a334e43a6b1c2c0da9623409d9ee9047747"
API_URL="https://api.hyperliquid.xyz/info"

echo "=== HyperCore Positions ==="
curl -s -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"clearinghouseState\",\"user\":\"$ADDRESS\"}" \
  | jq '.assetPositions[] | {coin: .position.coin, size: .position.szi, pnl: .position.unrealizedPnl}'

echo ""
echo "=== HIP-3 xyz DEX Positions ==="
curl -s -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"clearinghouseState\",\"user\":\"$ADDRESS\",\"dex\":\"xyz\"}" \
  | jq '.assetPositions[] | {coin: .position.coin, size: .position.szi, pnl: .position.unrealizedPnl}'

echo ""
echo "=== HIP-3 unit DEX Positions ==="
curl -s -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"clearinghouseState\",\"user\":\"$ADDRESS\",\"dex\":\"unit\"}" \
  | jq '.assetPositions[] | {coin: .position.coin, size: .position.szi, pnl: .position.unrealizedPnl}'
```

---

## 4. Getting ALL Addresses with Positions

### Challenge

Hyperliquid API doesn't have a single endpoint to get all addresses holding positions. You need to:

### Option A: Use Third-Party Indexers (Recommended)

**Nansen API** provides aggregated position data:

```bash
curl -X POST https://api.nansen.ai/api/v1/tgm/perp-positions \
  -H "apiKey: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "token_symbol": "BTC",
    "filters": {
      "side": ["Long"]
    },
    "pagination": {
      "page": 1,
      "per_page": 100
    }
  }'
```

**Hydromancer API** for HIP-3 markets:

```bash
curl -X POST https://api.hydromancer.xyz/perpSnapshot \
  -H "Content-Type: application/json" \
  -d '{
    "markets": ["xyz:XYZ100"]
  }'
```

### Option B: Build Your Own Indexer

1. Listen to WebSocket for all trades
2. Collect unique addresses
3. Query each address individually
4. Store in your own database

```javascript
const ws = new WebSocket('wss://api.hyperliquid.xyz/ws');

ws.send(JSON.stringify({
  method: 'subscribe',
  subscription: { type: 'allMids' }
}));

const activeAddresses = new Set();
ws.on('message', (data) => {
  const trade = JSON.parse(data);
  if (trade.user) activeAddresses.add(trade.user);
});
```

---

## 5. Rate Limits

**Hyperliquid API Rate Limits:**
- 1200 weight per minute per IP address
- ~10-20 requests per second is safe
- Add 50-100ms delay between requests

```javascript
// Rate limiting helper
async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Query with rate limiting
for (const address of addresses) {
  const positions = await getUserPositions(address);
  await sleep(100); // 100ms delay
}
```

---

## 6. Other Useful Endpoints

### Get User Trade History

```json
{
  "type": "userFills",
  "user": "0xUSER_ADDRESS_HERE"
}
```

### Get Historical Orders

```json
{
  "type": "historicalOrders",
  "user": "0xUSER_ADDRESS_HERE"
}
```

### Get Funding Payments

```json
{
  "type": "userFunding",
  "user": "0xUSER_ADDRESS_HERE"
}
```

### Get Market Metadata

```json
{
  "type": "metaAndAssetCtxs"
}
```

---

## 7. Important Notes

### Position Direction
- **Positive `szi`** = LONG position
- **Negative `szi`** = SHORT position

### Market Naming
- **HyperCore:** Just asset name (e.g., `"BTC"`, `"ETH"`)
- **HIP-3:** Prefixed with DEX (e.g., `"xyz:XYZ100"`, `"xyz:TSLA"`)

### Cross vs Isolated Margin
- **Cross:** Shares margin across all positions
- **Isolated:** Each position has dedicated margin

### Funding Rates
- Perpetual contracts have funding payments
- Check `cumFunding.allTime` for total funding earned/paid
- Positive = earned funding, Negative = paid funding

---

## 8. Complete Working Example

```javascript
// Complete example that fetches and displays all positions
async function displayUserPositions(address) {
  console.log(`\n=== Fetching positions for ${address} ===\n`);
  
  // HyperCore positions
  const hypercore = await fetch('https://api.hyperliquid.xyz/info', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      type: 'clearinghouseState',
      user: address
    })
  }).then(r => r.json());
  
  console.log('HyperCore Positions:');
  console.log(`Account Value: $${parseFloat(hypercore.marginSummary.accountValue).toLocaleString()}`);
  
  for (const asset of hypercore.assetPositions || []) {
    const pos = asset.position;
    const direction = parseFloat(pos.szi) > 0 ? 'LONG' : 'SHORT';
    const size = Math.abs(parseFloat(pos.szi));
    const pnl = parseFloat(pos.unrealizedPnl);
    
    console.log(`  ${pos.coin}: ${direction} ${size} @ $${pos.entryPx}`);
    console.log(`    PnL: $${pnl.toFixed(2)} | Leverage: ${pos.leverage.value}x`);
  }
  
  // HIP-3 positions
  const dexes = ['xyz', 'unit'];
  for (const dex of dexes) {
    const hip3 = await fetch('https://api.hyperliquid.xyz/info', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'clearinghouseState',
        user: address,
        dex: dex
      })
    }).then(r => r.json());
    
    if (hip3.assetPositions && hip3.assetPositions.length > 0) {
      console.log(`\n${dex.toUpperCase()} DEX Positions:`);
      console.log(`Account Value: $${parseFloat(hip3.marginSummary.accountValue).toLocaleString()}`);
      
      for (const asset of hip3.assetPositions) {
        const pos = asset.position;
        const direction = parseFloat(pos.szi) > 0 ? 'LONG' : 'SHORT';
        const size = Math.abs(parseFloat(pos.szi));
        const pnl = parseFloat(pos.unrealizedPnl);
        
        console.log(`  ${pos.coin}: ${direction} ${size} @ $${pos.entryPx}`);
        console.log(`    PnL: $${pnl.toFixed(2)} | Leverage: ${pos.leverage.value}x`);
      }
    }
  }
}

// Run it
displayUserPositions('0x7da85a334e43a6b1c2c0da9623409d9ee9047747');
```

---

## Resources

- [Hyperliquid API Documentation](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api)
- [HIP-3 Overview](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips)
- [WebSocket API](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket)
- [Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits)

---

## Summary

**To get ALL positions for a user:**

1. ✅ Query HyperCore: `{"type": "clearinghouseState", "user": "0xADDRESS"}`
2. ✅ Query each HIP-3 DEX: `{"type": "clearinghouseState", "user": "0xADDRESS", "dex": "xyz"}`
3. ✅ Combine results for complete portfolio view

**Key Insight:** HIP-3 positions require the `"dex"` parameter - this is the critical discovery!












