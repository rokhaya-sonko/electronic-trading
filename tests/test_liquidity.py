"""
Unit tests for the liquidity module.
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from liquidity import (
    calculate_bid_ask_spread,
    calculate_effective_spread,
    calculate_market_depth,
    calculate_amihud_illiquidity,
    calculate_liquidity_score,
    calculate_relative_spread
)


class TestLiquidityMetrics:
    """Test suite for liquidity metrics."""
    
    def setup_method(self):
        """Set up test data."""
        # Create sample data
        dates = pd.date_range('2024-01-01', periods=100, freq='1min')
        self.bid_prices = pd.Series(np.linspace(99, 101, 100), index=dates)
        self.ask_prices = pd.Series(np.linspace(99.05, 101.05, 100), index=dates)
        self.volumes = pd.Series(np.random.randint(100, 1000, 100), index=dates)
    
    def test_bid_ask_spread_absolute(self):
        """Test absolute bid-ask spread calculation."""
        spread = calculate_bid_ask_spread(
            self.bid_prices,
            self.ask_prices,
            spread_type='absolute'
        )
        
        assert len(spread) == len(self.bid_prices)
        assert all(spread >= 0), "Spread should be non-negative"
        assert np.allclose(spread, 0.05), "Spread should be constant at 0.05"
    
    def test_bid_ask_spread_bps(self):
        """Test basis points spread calculation."""
        spread_bps = calculate_bid_ask_spread(
            self.bid_prices,
            self.ask_prices,
            spread_type='bps'
        )
        
        assert len(spread_bps) == len(self.bid_prices)
        assert all(spread_bps >= 0), "Spread in bps should be non-negative"
    
    def test_relative_spread(self):
        """Test relative spread calculation."""
        rel_spread = calculate_relative_spread(
            self.bid_prices,
            self.ask_prices
        )
        
        assert len(rel_spread) == len(self.bid_prices)
        assert all(rel_spread >= 0), "Relative spread should be non-negative"
    
    def test_effective_spread(self):
        """Test effective spread calculation."""
        trade_prices = (self.bid_prices + self.ask_prices) / 2 + 0.01
        mid_prices = (self.bid_prices + self.ask_prices) / 2
        directions = pd.Series([1] * len(self.bid_prices), index=self.bid_prices.index)
        
        eff_spread = calculate_effective_spread(
            trade_prices,
            mid_prices,
            directions
        )
        
        assert len(eff_spread) == len(trade_prices)
        assert all(eff_spread >= 0), "Effective spread should be non-negative for buys"
    
    def test_amihud_illiquidity(self):
        """Test Amihud illiquidity measure."""
        returns = self.bid_prices.pct_change().dropna()
        volumes = self.volumes[1:]
        
        amihud = calculate_amihud_illiquidity(
            returns,
            volumes,
            window=None
        )
        
        assert isinstance(amihud, float)
        assert amihud >= 0, "Amihud measure should be non-negative"
    
    def test_liquidity_score(self):
        """Test composite liquidity score."""
        spreads = calculate_bid_ask_spread(
            self.bid_prices,
            self.ask_prices,
            spread_type='absolute'
        )
        depths = self.volumes  # Simplified depth
        
        score = calculate_liquidity_score(
            spreads,
            depths,
            self.volumes,
            normalize=True
        )
        
        assert len(score) == len(spreads)
        assert all(score >= 0) and all(score <= 100), "Score should be between 0 and 100"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
