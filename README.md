# Electronic Trading Lab

A comprehensive Python library for electronic trading analysis, featuring liquidity metrics, transaction cost analysis (TCA), execution algorithms, and risk management tools.

## 🎯 Overview

This repository provides a production-ready framework for analyzing and implementing electronic trading strategies. It includes:

- **Liquidity Metrics**: Bid-ask spread, market depth, price impact analysis
- **Transaction Cost Analysis (TCA)**: Implementation shortfall, VWAP analysis, slippage metrics
- **Execution Algorithms**: TWAP, VWAP, and POV (Percentage of Volume) implementations
- **Risk Management**: Portfolio risk metrics, VaR calculations, exposure analysis
- **Market Microstructure Models**: Price impact models, optimal execution strategies

## 📁 Project Structure

```
electronic-trading-lab/
├── data/                  # Synthetic and sample market data
├── notebooks/            # Jupyter notebooks for analysis
│   ├── 01_liquidity_analysis.ipynb
│   ├── 02_tca_analysis.ipynb
│   ├── 03_execution_algorithms.ipynb
│   ├── 04_feature_engineering.ipynb
│   ├── 05_risk_analysis.ipynb
│   └── 06_optimal_execution.ipynb
├── src/                  # Core Python modules
│   ├── liquidity.py      # Liquidity metrics
│   ├── tca.py           # Transaction cost analysis
│   ├── execution_algos.py # Execution algorithms
│   ├── risk.py          # Risk management
│   ├── models.py        # Market microstructure models
│   └── utils.py         # Utilities and data generation
├── tests/               # Unit tests
├── docs/                # Documentation
└── requirements.txt     # Python dependencies
```

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/rokhaya-sonko/eTrading.git
cd eTrading
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running Notebooks

Launch Jupyter:
```bash
jupyter notebook notebooks/
```

Navigate to any notebook to explore:
- **01_liquidity_analysis.ipynb**: Analyze market liquidity metrics
- **02_tca_analysis.ipynb**: Perform transaction cost analysis
- **03_execution_algorithms.ipynb**: Compare TWAP, VWAP, and POV algorithms
- **04_feature_engineering.ipynb**: Build features for trading models
- **05_risk_analysis.ipynb**: Calculate portfolio risk metrics
- **06_optimal_execution.ipynb**: Implement optimal execution strategies

## 📊 Features

### Liquidity Metrics
- Bid-ask spread analysis
- Market depth calculations
- Volume-weighted metrics
- Price impact estimation

### Transaction Cost Analysis
- Implementation shortfall
- VWAP benchmarking
- Slippage analysis
- Execution quality metrics

### Execution Algorithms
- **TWAP (Time-Weighted Average Price)**: Spreads orders evenly over time
- **VWAP (Volume-Weighted Average Price)**: Matches historical volume patterns
- **POV (Percentage of Volume)**: Targets a percentage of market volume

### Risk Management
- Value at Risk (VaR)
- Expected Shortfall (ES)
- Portfolio volatility
- Greeks calculations

## 🧪 Testing

Run tests with pytest:
```bash
pytest tests/
```

With coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## 📖 Documentation

Detailed documentation is available in the `docs/` directory. Each module is well-documented with docstrings and examples.

## 🔬 Synthetic Data

All notebooks use synthetic market data generated with realistic properties:
- Price processes with drift and volatility
- Microstructure noise
- Bid-ask spreads
- Volume patterns

This ensures reproducibility and allows experimentation without real market data.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This is an educational and research tool. Not intended for production trading without proper validation and risk management.