"""
Unit tests for the execution algorithms module.
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from execution_algos import TWAPAlgorithm, VWAPAlgorithm, POVAlgorithm


class TestExecutionAlgorithms:
    """Test suite for execution algorithms."""
    
    def setup_method(self):
        """Set up test data."""
        self.total_quantity = 10000
        self.start_time = pd.Timestamp('2024-01-01 09:30:00')
        self.end_time = pd.Timestamp('2024-01-01 16:00:00')
        
        # Create market data
        dates = pd.date_range(self.start_time, self.end_time, freq='1min')
        self.market_data = pd.DataFrame({
            'price': np.random.uniform(99, 101, len(dates)),
            'volume': np.random.randint(1000, 5000, len(dates))
        }, index=dates)
    
    def test_twap_schedule_generation(self):
        """Test TWAP schedule generation."""
        twap = TWAPAlgorithm(
            self.total_quantity,
            self.start_time,
            self.end_time,
            num_slices=10
        )
        
        schedule = twap.generate_schedule()
        
        assert len(schedule) == 10
        assert np.isclose(schedule['quantity'].sum(), self.total_quantity)
        assert schedule['cumulative_quantity'].iloc[-1] == self.total_quantity
    
    def test_twap_execution(self):
        """Test TWAP execution on market data."""
        twap = TWAPAlgorithm(
            self.total_quantity,
            self.start_time,
            self.end_time,
            num_slices=10
        )
        
        executions = twap.execute(self.market_data)
        
        assert len(executions) == 10
        assert np.isclose(executions['quantity'].sum(), self.total_quantity)
        assert all(executions['price'] > 0)
        assert all(executions['value'] > 0)
    
    def test_vwap_schedule_generation(self):
        """Test VWAP schedule generation."""
        vwap = VWAPAlgorithm(
            self.total_quantity,
            self.start_time,
            self.end_time
        )
        
        time_index = self.market_data.index[:10]
        schedule = vwap.generate_schedule(time_index)
        
        assert len(schedule) == 10
        assert np.isclose(schedule['quantity'].sum(), self.total_quantity)
        assert np.isclose(schedule['weight'].sum(), 1.0)
    
    def test_vwap_execution(self):
        """Test VWAP execution on market data."""
        vwap = VWAPAlgorithm(
            self.total_quantity,
            self.start_time,
            self.end_time
        )
        
        executions = vwap.execute(self.market_data.head(50))
        
        assert len(executions) > 0
        assert executions['quantity'].sum() <= self.total_quantity + 1  # Allow for rounding
        assert all(executions['price'] > 0)
    
    def test_pov_execution(self):
        """Test POV execution on market data."""
        pov = POVAlgorithm(
            self.total_quantity,
            self.start_time,
            self.end_time,
            target_pov=0.1
        )
        
        executions = pov.execute(self.market_data.head(200))
        
        assert len(executions) > 0
        # POV may not execute entire order if market volume is low
        assert executions['quantity'].sum() <= self.total_quantity
        assert all(executions['participation_rate'] <= 1.0)
        assert all(executions['price'] > 0)
    
    def test_pov_participation_rate(self):
        """Test POV participation rate constraint."""
        target_pov = 0.15
        pov = POVAlgorithm(
            self.total_quantity,
            self.start_time,
            self.end_time,
            target_pov=target_pov
        )
        
        executions = pov.execute(self.market_data.head(100))
        
        # Check that participation rate is close to target
        avg_participation = (
            executions['quantity'].sum() / 
            executions['market_volume'].sum()
        )
        # May not exactly match due to min/max constraints
        assert avg_participation <= target_pov * 2  # Reasonable bound


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
