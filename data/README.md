# Data Directory

This directory is used to store data files for the Electronic Trading Lab.

## Contents

By default, this directory is empty. Data files are generated synthetically by the notebooks and modules.

## Generating Sample Data

You can generate sample data using the utility functions:

```python
import sys
sys.path.append('../src')

from utils import generate_price_series, generate_order_book, generate_trade_data

# Generate and save price data
prices = generate_price_series(n_periods=10000, seed=42)
prices.to_csv('data/sample_prices.csv')

# Generate and save order book
order_book = generate_order_book(prices)
order_book.to_csv('data/sample_order_book.csv')

# Generate and save trade data
trades = generate_trade_data(prices, seed=42)
trades.to_csv('data/sample_trades.csv')
```

## Data Files

Common data files that might be stored here:

- `sample_prices.csv` - Price series data
- `sample_order_book.csv` - Order book snapshots
- `sample_trades.csv` - Trade execution data
- Custom datasets for analysis

## Note

Large CSV files are ignored by git (see `.gitignore`). Only small sample files should be committed to the repository.

## Working with Real Data

To use real market data:

1. Download data from your preferred source (e.g., Yahoo Finance, Bloomberg, etc.)
2. Place files in this directory
3. Update notebooks to read from these files instead of generating synthetic data

Example:

```python
import pandas as pd

# Load real data
prices = pd.read_csv('data/your_data.csv', index_col=0, parse_dates=True)

# Use with the library modules
from src.liquidity import calculate_bid_ask_spread
# ... rest of your analysis
```
