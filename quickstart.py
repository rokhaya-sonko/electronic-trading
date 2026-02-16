#!/usr/bin/env python3
"""
Quick start script for the Electronic Trading Lab.

This script demonstrates basic usage of the library modules.
"""

import sys
sys.path.append('src')

import numpy as np
import pandas as pd

# Import our modules
from utils import generate_price_series, generate_order_book, generate_trade_data
from liquidity import calculate_bid_ask_spread, calculate_liquidity_score
from execution_algos import TWAPAlgorithm
from risk import calculate_var, calculate_sharpe_ratio


def main():
    """Run quick demonstration of library features."""
    
    print("=" * 70)
    print("Electronic Trading Lab - Quick Start Demo")
    print("=" * 70)
    
    # 1. Generate synthetic data
    print("\n1. Generating synthetic market data...")
    np.random.seed(42)
    
    prices = generate_price_series(
        n_periods=500,
        initial_price=100.0,
        mu=0.0001,
        sigma=0.02,
        seed=42
    )
    
    order_book = generate_order_book(prices, spread_bps=5.0)
    trades = generate_trade_data(prices, seed=42)
    
    print(f"   ✓ Generated {len(prices)} price points")
    print(f"   ✓ Price range: ${prices.min():.2f} - ${prices.max():.2f}")
    
    # 2. Calculate liquidity metrics
    print("\n2. Calculating liquidity metrics...")
    
    spread_bps = calculate_bid_ask_spread(
        order_book['bid_price'],
        order_book['ask_price'],
        spread_type='bps'
    )
    
    total_depth = order_book['bid_size'] + order_book['ask_size']
    
    liquidity_score = calculate_liquidity_score(
        bid_ask_spread=spread_bps,
        depth=total_depth,
        volume=trades['volume'].reindex(order_book.index, method='nearest').fillna(method='ffill'),
        normalize=True
    )
    
    print(f"   ✓ Average Spread: {spread_bps.mean():.2f} bps")
    print(f"   ✓ Average Depth: {total_depth.mean():,.0f} shares")
    print(f"   ✓ Liquidity Score: {liquidity_score.mean():.2f}/100")
    
    # 3. Execute TWAP algorithm
    print("\n3. Executing TWAP algorithm...")
    
    twap = TWAPAlgorithm(
        total_quantity=10000,
        start_time=prices.index[0],
        end_time=prices.index[100],
        num_slices=10
    )
    
    market_data = pd.DataFrame({'price': prices.values}, index=prices.index)
    executions = twap.execute(market_data)
    
    avg_exec_price = (executions['price'] * executions['quantity']).sum() / executions['quantity'].sum()
    
    print(f"   ✓ Executed {executions['quantity'].sum():,.0f} shares")
    print(f"   ✓ Number of fills: {len(executions)}")
    print(f"   ✓ Average execution price: ${avg_exec_price:.2f}")
    
    # 4. Calculate risk metrics
    print("\n4. Calculating risk metrics...")
    
    returns = prices.pct_change().dropna()
    
    var_95 = calculate_var(returns, confidence_level=0.95, method='historical')
    sharpe = calculate_sharpe_ratio(returns, risk_free_rate=0.0)
    volatility = returns.std() * np.sqrt(252) * 100
    
    print(f"   ✓ 95% VaR: {var_95:.4f} ({var_95*100:.2f}%)")
    print(f"   ✓ Sharpe Ratio: {sharpe:.3f}")
    print(f"   ✓ Annualized Volatility: {volatility:.2f}%")
    
    # Summary
    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Explore the notebooks in notebooks/ directory")
    print("  2. Read the documentation in docs/")
    print("  3. Run tests with: pytest tests/")
    print("  4. Check the API documentation for more features")
    print("\nFor detailed examples, start with:")
    print("  jupyter notebook notebooks/01_liquidity_analysis.ipynb")
    print("=" * 70)


if __name__ == '__main__':
    main()
