# Electronic Trading Lab - Documentation

## Overview

The Electronic Trading Lab is a comprehensive Python library for analyzing and implementing electronic trading strategies. This documentation provides detailed information about the modules and their usage.

## Modules

### 1. Utils Module (`src/utils.py`)

Utility functions for data generation and preprocessing.

#### Key Functions:

- **`generate_price_series()`**: Generate synthetic price series using geometric Brownian motion
- **`generate_order_book()`**: Create synthetic order book data with bid-ask spreads
- **`generate_trade_data()`**: Generate synthetic trade data with volume and direction
- **`calculate_returns()`**: Calculate returns from price series
- **`calculate_volatility()`**: Calculate historical volatility
- **`resample_data()`**: Resample high-frequency data to lower frequencies

#### Example:

```python
from src.utils import generate_price_series, generate_order_book

# Generate price series
prices = generate_price_series(
    n_periods=1000,
    initial_price=100.0,
    mu=0.0001,
    sigma=0.02,
    seed=42
)

# Generate order book
order_book = generate_order_book(
    prices=prices,
    spread_bps=5.0,
    depth_shares=10000
)
```

### 2. Liquidity Module (`src/liquidity.py`)

Functions for calculating market liquidity metrics.

#### Key Functions:

- **`calculate_bid_ask_spread()`**: Calculate bid-ask spreads (absolute, percentage, or bps)
- **`calculate_effective_spread()`**: Measure actual execution costs
- **`calculate_market_depth()`**: Calculate total market depth
- **`calculate_amihud_illiquidity()`**: Compute Amihud illiquidity measure
- **`calculate_liquidity_score()`**: Composite liquidity score

#### Example:

```python
from src.liquidity import calculate_bid_ask_spread, calculate_liquidity_score

# Calculate spread in basis points
spread_bps = calculate_bid_ask_spread(
    bid_price=order_book['bid_price'],
    ask_price=order_book['ask_price'],
    spread_type='bps'
)

# Calculate composite liquidity score
score = calculate_liquidity_score(
    bid_ask_spread=spread_absolute,
    depth=total_depth,
    volume=trading_volume,
    normalize=True
)
```

### 3. TCA Module (`src/tca.py`)

Transaction Cost Analysis tools.

#### Key Functions:

- **`calculate_implementation_shortfall()`**: Measure implementation shortfall
- **`calculate_vwap_performance()`**: Analyze VWAP performance
- **`calculate_slippage()`**: Calculate trade slippage
- **`calculate_market_impact()`**: Measure market impact
- **`calculate_execution_quality_score()`**: Composite execution quality metric

#### Example:

```python
from src.tca import calculate_implementation_shortfall, calculate_vwap_performance

# Calculate implementation shortfall
is_results = calculate_implementation_shortfall(
    decision_price=100.0,
    execution_prices=exec_prices,
    execution_volumes=exec_volumes,
    final_price=100.5,
    side='buy'
)

# Analyze VWAP performance
vwap_results = calculate_vwap_performance(
    execution_prices=exec_prices,
    execution_volumes=exec_volumes,
    market_prices=market_prices,
    market_volumes=market_volumes,
    side='buy'
)
```

### 4. Execution Algorithms Module (`src/execution_algos.py`)

Implementation of common execution algorithms.

#### Classes:

- **`TWAPAlgorithm`**: Time-Weighted Average Price
- **`VWAPAlgorithm`**: Volume-Weighted Average Price
- **`POVAlgorithm`**: Percentage of Volume

#### Example:

```python
from src.execution_algos import TWAPAlgorithm, VWAPAlgorithm, POVAlgorithm

# TWAP execution
twap = TWAPAlgorithm(
    total_quantity=100000,
    start_time=start_time,
    end_time=end_time,
    num_slices=20
)
executions = twap.execute(market_data)

# VWAP execution
vwap = VWAPAlgorithm(
    total_quantity=100000,
    start_time=start_time,
    end_time=end_time
)
executions = vwap.execute(market_data)

# POV execution
pov = POVAlgorithm(
    total_quantity=100000,
    start_time=start_time,
    end_time=end_time,
    target_pov=0.10  # 10% of volume
)
executions = pov.execute(market_data)
```

### 5. Risk Module (`src/risk.py`)

Portfolio risk management tools.

#### Key Functions:

- **`calculate_var()`**: Value at Risk (Historical, Parametric, Cornish-Fisher)
- **`calculate_expected_shortfall()`**: Expected Shortfall (CVaR)
- **`calculate_volatility()`**: Historical volatility
- **`calculate_sharpe_ratio()`**: Risk-adjusted returns
- **`calculate_max_drawdown()`**: Maximum drawdown analysis
- **`calculate_beta()`**: Systematic risk
- **`stress_test_portfolio()`**: Scenario analysis

#### Example:

```python
from src.risk import calculate_var, calculate_expected_shortfall, calculate_sharpe_ratio

# Calculate VaR
var_95 = calculate_var(returns, confidence_level=0.95, method='historical')
var_99 = calculate_var(returns, confidence_level=0.99, method='parametric')

# Calculate Expected Shortfall
es = calculate_expected_shortfall(returns, confidence_level=0.95)

# Calculate Sharpe ratio
sharpe = calculate_sharpe_ratio(returns, risk_free_rate=0.02)
```

### 6. Models Module (`src/models.py`)

Market microstructure and optimal execution models.

#### Classes:

- **`AlmgrenChrissModel`**: Optimal execution with market impact
- **`LinearPriceImpactModel`**: Linear price impact estimation
- **`KyleModel`**: Kyle's lambda model
- **`OptimalExecutionSolver`**: Numerical optimization for execution

#### Example:

```python
from src.models import AlmgrenChrissModel, LinearPriceImpactModel

# Almgren-Chriss optimal execution
ac_model = AlmgrenChrissModel(
    total_quantity=100000,
    total_time=1.0,
    volatility=0.02,
    permanent_impact=0.1,
    temporary_impact=0.1,
    risk_aversion=1e-6
)
trajectory = ac_model.calculate_optimal_trajectory(num_periods=20)

# Price impact modeling
impact_model = LinearPriceImpactModel(
    permanent_coef=0.1,
    temporary_coef=0.05
)
impact = impact_model.calculate_impact(trade_size=10000, direction=1)
```

## Best Practices

### 1. Data Generation

Always use a fixed seed for reproducibility:

```python
prices = generate_price_series(n_periods=1000, seed=42)
```

### 2. Parameter Selection

- **Liquidity Analysis**: Use 5-10 bps spread for liquid stocks
- **Execution Algorithms**: Match execution window to liquidity profile
- **Risk Metrics**: Use 95% confidence for VaR, 99% for stress testing

### 3. Visualization

Use the provided notebooks as templates for creating visualizations:

```python
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style('whitegrid')
plt.figure(figsize=(12, 6))
# Your plotting code here
```

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_liquidity.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Common Workflows

### Workflow 1: Execution Quality Analysis

1. Generate or load market data
2. Execute order using an algorithm
3. Calculate TCA metrics (implementation shortfall, VWAP performance)
4. Compare against benchmarks
5. Generate execution report

### Workflow 2: Portfolio Risk Assessment

1. Load portfolio returns data
2. Calculate VaR and Expected Shortfall
3. Analyze correlation structure
4. Run stress tests
5. Generate risk report

### Workflow 3: Optimal Execution Planning

1. Estimate market impact parameters
2. Define risk aversion level
3. Calculate optimal trajectory using Almgren-Chriss
4. Compare with standard algorithms
5. Select best strategy

## References

### Academic Papers

1. Almgren, R., & Chriss, N. (2000). "Optimal execution of portfolio transactions"
2. Amihud, Y. (2002). "Illiquidity and stock returns"
3. Kyle, A. S. (1985). "Continuous auctions and insider trading"
4. Roll, R. (1984). "A simple implicit measure of the effective bid-ask spread"

### Books

1. Kissell, R. (2013). "The Science of Algorithmic Trading and Portfolio Management"
2. Hasbrouck, J. (2007). "Empirical Market Microstructure"

## Support

For questions or issues:
- Open an issue on GitHub
- Check the example notebooks in `notebooks/`
- Review the test files in `tests/` for usage examples

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is open source and available under the MIT License.
