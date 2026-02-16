# Electronic Trading Lab - Jupyter Notebooks

This directory contains interactive Jupyter notebooks demonstrating various concepts in electronic trading and market microstructure.

## Notebooks

### 01. Liquidity Analysis
**File:** `01_liquidity_analysis.ipynb`

Analyzes market liquidity using various metrics:
- Bid-ask spreads (absolute, percentage, basis points)
- Market depth and order book analysis
- Amihud illiquidity measure
- Composite liquidity scores
- Correlation analysis between liquidity metrics

### 02. Transaction Cost Analysis (TCA)
**File:** `02_tca_analysis.ipynb`

Comprehensive transaction cost analysis:
- Implementation shortfall
- Arrival price analysis
- VWAP benchmarking
- Market impact estimation
- Slippage analysis
- Execution quality metrics

### 03. Execution Algorithms
**File:** `03_execution_algorithms.ipynb`

Common execution algorithms used in algorithmic trading:
- **TWAP** (Time-Weighted Average Price): Uniform execution over time
- **VWAP** (Volume-Weighted Average Price): Execution based on volume patterns
- **POV** (Percentage of Volume): Participation-based execution
- Algorithm comparison and performance analysis
- Execution schedule visualization
- Cost analysis in basis points

### 04. Feature Engineering
**File:** `04_feature_engineering.ipynb`

Feature engineering for quantitative trading models:
- **Technical Indicators**: RSI, MACD, Bollinger Bands
- **Liquidity Features**: Spreads, depth, Amihud illiquidity
- **Microstructure Features**: Order flow, trade imbalance, effective spread
- **Volume Features**: VWAP distance, relative volume, volume momentum
- **Time-based Features**: Lags, rolling statistics, momentum, acceleration
- Correlation analysis and feature importance

### 05. Risk Analysis
**File:** `05_risk_analysis.ipynb`

Portfolio risk analysis and management:
- **Value at Risk (VaR)**: Historical, parametric, and Cornish-Fisher methods
- **Expected Shortfall (CVaR)**: Tail risk measurement
- **Sharpe Ratio**: Risk-adjusted performance
- **Maximum Drawdown**: Peak-to-trough decline analysis
- **Correlation Analysis**: Portfolio diversification
- **Stress Testing**: Scenario-based risk assessment
- Comprehensive risk reporting

### 06. Optimal Execution
**File:** `06_optimal_execution.ipynb`

Optimal execution strategies and theory:
- **Almgren-Chriss Model**: Optimal execution balancing impact and risk
- **Price Impact Models**: Permanent and temporary impact
- **Strategy Comparison**: Uniform, front-loaded, back-loaded, optimal
- Monte Carlo simulation with price impact
- Cost analysis and trajectory optimization
- Sensitivity analysis to risk aversion parameters

## Running the Notebooks

### Prerequisites

```bash
# Install required packages
pip install -r ../requirements.txt
```

### Launching Jupyter

```bash
# From the project root directory
jupyter notebook notebooks/
```

Or from this directory:

```bash
jupyter notebook
```

### Execution Order

While each notebook is self-contained, the suggested order for learning is:

1. **01_liquidity_analysis.ipynb** - Understanding market liquidity
2. **02_tca_analysis.ipynb** - Measuring execution quality
3. **03_execution_algorithms.ipynb** - Common execution strategies
4. **04_feature_engineering.ipynb** - Building trading features
5. **05_risk_analysis.ipynb** - Portfolio risk management
6. **06_optimal_execution.ipynb** - Optimal execution theory

## Notebook Structure

Each notebook follows a consistent structure:

1. **Introduction**: Overview of concepts covered
2. **Data Generation**: Create synthetic market data for demonstrations
3. **Analysis Sections**: Multiple sections with code and visualizations
4. **Visualizations**: Comprehensive plots and charts
5. **Conclusion**: Summary of key insights and next steps

## Key Features

- ✅ **Self-contained**: Each notebook includes all necessary imports and data generation
- ✅ **Well-documented**: Extensive markdown explanations and comments
- ✅ **Visualizations**: Multiple charts and plots for better understanding
- ✅ **Synthetic Data**: Uses realistic simulated data (no external data needed)
- ✅ **Educational**: Designed for learning and teaching
- ✅ **Production-ready**: Code can be adapted for real trading applications

## Module Dependencies

All notebooks import from the `../src` directory:

- `utils.py`: Data generation and utility functions
- `liquidity.py`: Liquidity metrics
- `tca.py`: Transaction cost analysis
- `execution_algos.py`: Execution algorithms (TWAP, VWAP, POV)
- `models.py`: Market microstructure models (Almgren-Chriss, price impact)
- `risk.py`: Risk metrics and analysis

## Data

The notebooks use synthetic data generated via geometric Brownian motion and other stochastic processes. This allows them to run without requiring external data sources.

## Contributing

When adding new notebooks:
1. Follow the existing naming convention: `XX_topic_name.ipynb`
2. Include comprehensive markdown documentation
3. Use the project's existing modules from `../src`
4. Include visualizations and examples
5. Add a conclusion section with key takeaways

## License

See the main project README for license information.
