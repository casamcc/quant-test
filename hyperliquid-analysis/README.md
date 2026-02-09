# Hyperliquid Builder Analysis

Python-based data analysis pipeline for extracting and analyzing Hyperliquid builder users and their trading positions.

## Project Goal

Extract all user addresses from Hyperliquid builders (starting with Insilico) and analyze their:
- Current positions
- Liquidation prices
- Risk exposure
- Trading patterns

## Methods Implemented

### Method 1: Referral API
Uses Hyperliquid's referral endpoint to fetch user addresses directly.
- **Pros:** Fast, includes user metadata (volume, fees)
- **Cons:** May have pagination limits (5000 users per request)

### Method 2: Historical CSV
Downloads and parses daily trade data from Hyperliquid's S3 bucket.
- **Pros:** Complete historical data, guaranteed all users
- **Cons:** Requires downloading/processing multiple files

## Directory Structure

```
hyperliquid-analysis/
├── src/                  # Source code
├── data/                 # Data storage
│   ├── raw/             # Raw CSV downloads
│   ├── processed/       # Cleaned datasets
│   └── cache/           # API response cache
├── notebooks/           # Jupyter analysis notebooks
└── scripts/             # Executable scripts
```

## Usage

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Extract Users (Referral API)
```bash
python scripts/01_fetch_referral_users.py
```

### 3. Extract Users (CSV Method)
```bash
python scripts/02_fetch_csv_users.py
```

### 4. Validate & Compare
```bash
python scripts/03_compare_methods.py
```

## Builder Addresses

- **Insilico:** `0x2868fc0d9786a740b491577a43502259efa78a39`
- **BasedApp:** `0x1924b8561eef20e70ede628a296175d358be80e5`

## Output Files

- `data/processed/insilico_users_referral.json` - Users from API
- `data/processed/insilico_users_csv.json` - Users from CSV
- `data/processed/insilico_users_final.json` - Validated merged dataset
- `data/processed/validation_report.json` - Quality metrics











