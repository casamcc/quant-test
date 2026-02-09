"""
Configuration for Hyperliquid Builder Analysis
"""

# Builder addresses (lowercase required for CSV URLs)
BUILDERS = {
    'insilico': '0x2868fc0d9786a740b491577a43502259efa78a39',
    'basedapp': '0x1924b8561eef20e70ede628a296175d358be80e5'
}

# API endpoints
HYPERLIQUID_INFO_API = 'https://api.hyperliquid.xyz/info'
BUILDER_FILLS_BASE_URL = 'https://stats-data.hyperliquid.xyz/Mainnet/builder_fills'

# Rate limiting
REQUEST_DELAY = 0.1  # seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30  # seconds

# Data paths
DATA_DIR = 'data'
RAW_DIR = f'{DATA_DIR}/raw'
PROCESSED_DIR = f'{DATA_DIR}/processed'
CACHE_DIR = f'{DATA_DIR}/cache'

# CSV scraping settings
DAYS_TO_FETCH = 50  # Fetch last 50 days (back to ~Oct 12)

