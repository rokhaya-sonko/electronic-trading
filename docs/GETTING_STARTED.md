# Getting Started with Electronic Trading Lab

This guide will help you get started with the Electronic Trading Lab.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/rokhaya-sonko/eTrading.git
cd eTrading
```

### 2. Set Up Virtual Environment

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- NumPy and Pandas for data manipulation
- Matplotlib and Seaborn for visualization
- SciPy for statistical functions
- Jupyter for notebooks
- pytest for testing

## Quick Start

### Running Your First Analysis

1. **Start Jupyter Notebook:**

```bash
jupyter notebook notebooks/
```

2. **Open a notebook:**
   - Start with `01_liquidity_analysis.ipynb` for liquidity metrics
   - Or `02_tca_analysis.ipynb` for transaction cost analysis

3. **Run the cells:**
   - Execute cells in order (Shift + Enter)
   - All notebooks use synthetic data, so they run independently

### Using the Library in Python

Create a new Python script or notebook:

```python
import sys
sys.path.append('src')

from utils import generate_price_series, generate_order_book
from liquidity import calculate_bid_ask_spread, calculate_liquidity_score

# Generate synthetic data
prices = generate_price_series(n_periods=1000, initial_price=100.0, seed=42)
order_book = generate_order_book(prices, spread_bps=5.0)

# Calculate metrics
spread = calculate_bid_ask_spread(
    order_book['bid_price'],
    order_book['ask_price'],
    spread_type='bps'
)

print(f"Average spread: {spread.mean():.2f} bps")
```

## Notebook Overview

### 1. Liquidity Analysis (`01_liquidity_analysis.ipynb`)

Learn about market liquidity metrics:
- Bid-ask spreads
- Market depth
- Amihud illiquidity
- Composite liquidity scores

**Use this when:** You want to assess market quality or compare liquidity across assets.

### 2. Transaction Cost Analysis (`02_tca_analysis.ipynb`)

Analyze execution costs:
- Implementation shortfall
- VWAP performance
- Slippage analysis
- Execution quality scoring

**Use this when:** You need to evaluate trading performance or optimize execution.

### 3. Execution Algorithms (`03_execution_algorithms.ipynb`)

Compare execution strategies:
- TWAP (Time-Weighted Average Price)
- VWAP (Volume-Weighted Average Price)
- POV (Percentage of Volume)

**Use this when:** You're deciding which execution algorithm to use.

### 4. Feature Engineering (`04_feature_engineering.ipynb`)

Build features for trading models:
- Technical indicators
- Liquidity features
- Microstructure features
- Volume profiles

**Use this when:** You're building predictive models for trading.

### 5. Risk Analysis (`05_risk_analysis.ipynb`)

Assess portfolio risk:
- Value at Risk (VaR)
- Expected Shortfall
- Sharpe ratios
- Stress testing

**Use this when:** You need to understand and manage portfolio risk.

### 6. Optimal Execution (`06_optimal_execution.ipynb`)

Implement optimal execution strategies:
- Almgren-Chriss model
- Price impact estimation
- Strategy comparison

**Use this when:** You want to minimize execution costs under constraints.

## Common Tasks

### Task 1: Calculate Liquidity Metrics

```python
from src.liquidity import calculate_bid_ask_spread, calculate_amihud_illiquidity
from src.utils import generate_price_series, generate_order_book, generate_trade_data

# Generate data
prices = generate_price_series(n_periods=500, seed=42)
order_book = generate_order_book(prices)
trades = generate_trade_data(prices, seed=42)

# Calculate spread
spread = calculate_bid_ask_spread(
    order_book['bid_price'],
    order_book['ask_price'],
    spread_type='bps'
)

# Calculate Amihud
returns = prices.pct_change().dropna()
amihud = calculate_amihud_illiquidity(
    returns.reindex(trades.index, method='nearest'),
    trades['volume'],
    window=20
)

print(f"Average spread: {spread.mean():.2f} bps")
print(f"Amihud illiquidity: {amihud.mean():.8f}")
```

### Task 2: Execute TWAP Order

```python
from src.execution_algos import TWAPAlgorithm
from src.utils import generate_price_series
import pandas as pd

# Generate market data
market_data = generate_price_series(n_periods=100, seed=42).to_frame('price')

# Define order
total_quantity = 10000
start_time = market_data.index[0]
end_time = market_data.index[-1]

# Execute TWAP
twap = TWAPAlgorithm(total_quantity, start_time, end_time, num_slices=10)
executions = twap.execute(market_data)

print(f"Executed {executions['quantity'].sum():,.0f} shares")
print(f"Average price: ${executions['price'].mean():.2f}")
```

### Task 3: Calculate Portfolio VaR

```python
from src.risk import calculate_var, calculate_expected_shortfall
import numpy as np
import pandas as pd

# Generate returns
np.random.seed(42)
returns = pd.Series(np.random.normal(0.001, 0.02, 252))

# Calculate risk metrics
var_95 = calculate_var(returns, confidence_level=0.95, method='historical')
var_99 = calculate_var(returns, confidence_level=0.99, method='historical')
es_95 = calculate_expected_shortfall(returns, confidence_level=0.95)

print(f"95% VaR: {var_95:.4f}")
print(f"99% VaR: {var_99:.4f}")
print(f"95% Expected Shortfall: {es_95:.4f}")
```

## Running Tests

Ensure everything is working correctly:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_liquidity.py

# Generate coverage report
pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### Issue: Module not found

**Solution:** Make sure you've added the src directory to your path:

```python
import sys
sys.path.append('src')  # or '../src' from notebooks
```

### Issue: Jupyter notebook not starting

**Solution:** Ensure Jupyter is installed:

```bash
pip install jupyter notebook
jupyter notebook --version
```

### Issue: Import errors

**Solution:** Install all dependencies:

```bash
pip install -r requirements.txt
```

### Issue: Tests failing

**Solution:** Check that pytest is installed and you're in the project root:

```bash
pip install pytest
cd /path/to/eTrading
pytest tests/
```

## Next Steps

1. **Explore the notebooks** - Run through each notebook to understand the capabilities
2. **Modify parameters** - Change inputs to see how results vary
3. **Use real data** - Replace synthetic data with actual market data
4. **Build models** - Use the features from notebook 04 to build predictive models
5. **Customize** - Extend the modules with your own metrics and algorithms

## Additional Resources

- **Documentation:** See `docs/API_DOCUMENTATION.md` for detailed API reference
- **Examples:** All notebooks contain working examples
- **Tests:** Check `tests/` directory for usage patterns
- **Source Code:** Browse `src/` for implementation details

## Getting Help

- Check existing notebook examples
- Review the API documentation
- Look at test files for usage patterns
- Open an issue on GitHub for bugs or questions

## Best Practices

1. **Always use seed values** for reproducible results with synthetic data
2. **Start with small datasets** to test your code quickly
3. **Validate metrics** against known benchmarks when possible
4. **Document your analysis** using markdown cells in notebooks
5. **Version control** your notebooks and scripts

Happy Trading! 📈
