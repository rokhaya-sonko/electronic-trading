"""
Unit tests for the risk module.
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from risk import (
    calculate_var,
    calculate_expected_shortfall,
    calculate_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown
)


class TestRiskMetrics:
    """Test suite for risk metrics."""
    
    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        # Generate returns
        self.returns = pd.Series(np.random.normal(0.001, 0.02, 1000))
        # Generate prices
        self.prices = pd.Series(100 * np.exp(np.cumsum(self.returns)))
    
    def test_var_historical(self):
        """Test historical VaR calculation."""
        var = calculate_var(self.returns, confidence_level=0.95, method='historical')
        
        assert isinstance(var, (float, np.floating))
        assert var >= 0, "VaR should be non-negative"
    
    def test_var_parametric(self):
        """Test parametric VaR calculation."""
        var = calculate_var(self.returns, confidence_level=0.95, method='parametric')
        
        assert isinstance(var, (float, np.floating))
        assert var >= 0, "VaR should be non-negative"
    
    def test_var_cornish_fisher(self):
        """Test Cornish-Fisher VaR calculation."""
        var = calculate_var(self.returns, confidence_level=0.95, method='cornish_fisher')
        
        assert isinstance(var, (float, np.floating))
        assert var >= 0, "VaR should be non-negative"
    
    def test_expected_shortfall(self):
        """Test Expected Shortfall calculation."""
        es = calculate_expected_shortfall(self.returns, confidence_level=0.95)
        
        assert isinstance(es, (float, np.floating))
        assert es >= 0, "ES should be non-negative"
        
        # ES should be >= VaR
        var = calculate_var(self.returns, confidence_level=0.95, method='historical')
        assert es >= var, "ES should be greater than or equal to VaR"
    
    def test_volatility(self):
        """Test volatility calculation."""
        vol = calculate_volatility(self.returns, window=None, annualize=True)
        
        assert isinstance(vol, (float, np.floating))
        assert vol > 0, "Volatility should be positive"
    
    def test_rolling_volatility(self):
        """Test rolling volatility calculation."""
        vol = calculate_volatility(self.returns, window=20, annualize=True)
        
        assert isinstance(vol, pd.Series)
        assert len(vol) == len(self.returns)
        assert all(vol.dropna() > 0), "Volatility should be positive"
    
    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        sharpe = calculate_sharpe_ratio(
            self.returns,
            risk_free_rate=0.0,
            annualize=True
        )
        
        assert isinstance(sharpe, (float, np.floating))
        # Sharpe can be positive or negative
    
    def test_max_drawdown(self):
        """Test maximum drawdown calculation."""
        dd_results = calculate_max_drawdown(self.prices)
        
        assert 'max_drawdown' in dd_results
        assert 'max_drawdown_date' in dd_results
        assert 'peak_date' in dd_results
        
        max_dd = dd_results['max_drawdown']
        assert max_dd <= 0, "Maximum drawdown should be non-positive"
        assert max_dd >= -1, "Maximum drawdown should be >= -100%"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
