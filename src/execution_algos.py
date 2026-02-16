"""
Execution Algorithms Module.

This module implements common execution algorithms used in electronic trading:
- TWAP (Time-Weighted Average Price)
- VWAP (Volume-Weighted Average Price)
- POV (Percentage of Volume)
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple


class ExecutionAlgorithm:
    """Base class for execution algorithms."""
    
    def __init__(self, total_quantity: int, start_time: pd.Timestamp, end_time: pd.Timestamp):
        """
        Initialize execution algorithm.
        
        Parameters
        ----------
        total_quantity : int
            Total quantity to execute
        start_time : pd.Timestamp
            Start time for execution
        end_time : pd.Timestamp
            End time for execution
        """
        self.total_quantity = total_quantity
        self.start_time = start_time
        self.end_time = end_time
        self.executed_quantity = 0
        self.execution_schedule = []
    
    def generate_schedule(self) -> pd.DataFrame:
        """Generate execution schedule. To be implemented by subclasses."""
        raise NotImplementedError
    
    def execute(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """Execute algorithm on market data. To be implemented by subclasses."""
        raise NotImplementedError


class TWAPAlgorithm(ExecutionAlgorithm):
    """
    Time-Weighted Average Price (TWAP) Algorithm.
    
    Splits order into equal slices and executes uniformly over time.
    """
    
    def __init__(
        self,
        total_quantity: int,
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
        num_slices: Optional[int] = None,
        slice_interval: Optional[str] = '1min'
    ):
        """
        Initialize TWAP algorithm.
        
        Parameters
        ----------
        total_quantity : int
            Total quantity to execute
        start_time : pd.Timestamp
            Start time for execution
        end_time : pd.Timestamp
            End time for execution
        num_slices : int, optional
            Number of slices. If None, determined by slice_interval
        slice_interval : str, optional
            Time interval between slices (e.g., '1min', '5min')
        """
        super().__init__(total_quantity, start_time, end_time)
        self.num_slices = num_slices
        self.slice_interval = slice_interval
    
    def generate_schedule(self) -> pd.DataFrame:
        """
        Generate TWAP execution schedule.
        
        Returns
        -------
        pd.DataFrame
            Schedule with timestamps and quantities
        """
        if self.num_slices is not None:
            # Use specified number of slices
            times = pd.date_range(self.start_time, self.end_time, periods=self.num_slices)
        else:
            # Use time interval
            times = pd.date_range(self.start_time, self.end_time, freq=self.slice_interval)
        
        # Equal quantity per slice
        quantity_per_slice = self.total_quantity / len(times)
        quantities = [quantity_per_slice] * len(times)
        
        # Adjust last slice for rounding
        quantities[-1] = self.total_quantity - sum(quantities[:-1])
        
        schedule = pd.DataFrame({
            'timestamp': times,
            'quantity': quantities,
            'cumulative_quantity': np.cumsum(quantities)
        })
        
        self.execution_schedule = schedule
        return schedule
    
    def execute(self, market_data: pd.DataFrame, price_col: str = 'price') -> pd.DataFrame:
        """
        Execute TWAP algorithm on market data.
        
        Parameters
        ----------
        market_data : pd.DataFrame
            Market data with prices
        price_col : str
            Name of price column
            
        Returns
        -------
        pd.DataFrame
            Execution results with prices and quantities
        """
        if len(self.execution_schedule) == 0:
            self.generate_schedule()
        
        executions = []
        
        for _, row in self.execution_schedule.iterrows():
            exec_time = row['timestamp']
            exec_qty = row['quantity']
            
            # Find nearest market price
            if exec_time in market_data.index:
                exec_price = market_data.loc[exec_time, price_col]
            else:
                # Use nearest available price
                idx = market_data.index.get_indexer([exec_time], method='nearest')[0]
                exec_price = market_data.iloc[idx][price_col]
            
            executions.append({
                'timestamp': exec_time,
                'quantity': exec_qty,
                'price': exec_price,
                'value': exec_qty * exec_price
            })
        
        return pd.DataFrame(executions)


class VWAPAlgorithm(ExecutionAlgorithm):
    """
    Volume-Weighted Average Price (VWAP) Algorithm.
    
    Executes in proportion to historical volume patterns.
    """
    
    def __init__(
        self,
        total_quantity: int,
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
        volume_profile: Optional[pd.Series] = None
    ):
        """
        Initialize VWAP algorithm.
        
        Parameters
        ----------
        total_quantity : int
            Total quantity to execute
        start_time : pd.Timestamp
            Start time for execution
        end_time : pd.Timestamp
            End time for execution
        volume_profile : pd.Series, optional
            Historical volume profile. If None, uses uniform distribution
        """
        super().__init__(total_quantity, start_time, end_time)
        self.volume_profile = volume_profile
    
    def generate_schedule(self, time_index: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Generate VWAP execution schedule based on volume profile.
        
        Parameters
        ----------
        time_index : pd.DatetimeIndex
            Time periods for execution
            
        Returns
        -------
        pd.DataFrame
            Schedule with timestamps and quantities
        """
        if self.volume_profile is None:
            # Uniform distribution if no profile provided
            weights = np.ones(len(time_index))
        else:
            # Use provided volume profile
            weights = self.volume_profile.reindex(time_index, method='nearest').fillna(1).values
        
        # Normalize weights
        weights = weights / weights.sum()
        
        # Calculate quantities
        quantities = weights * self.total_quantity
        
        schedule = pd.DataFrame({
            'timestamp': time_index,
            'quantity': quantities,
            'weight': weights,
            'cumulative_quantity': np.cumsum(quantities)
        })
        
        self.execution_schedule = schedule
        return schedule
    
    def execute(self, market_data: pd.DataFrame, price_col: str = 'price', volume_col: str = 'volume') -> pd.DataFrame:
        """
        Execute VWAP algorithm on market data.
        
        Parameters
        ----------
        market_data : pd.DataFrame
            Market data with prices and volumes
        price_col : str
            Name of price column
        volume_col : str
            Name of volume column
            
        Returns
        -------
        pd.DataFrame
            Execution results
        """
        # Generate schedule based on market data times
        time_index = market_data.index
        self.generate_schedule(time_index)
        
        executions = []
        
        for _, row in self.execution_schedule.iterrows():
            exec_time = row['timestamp']
            exec_qty = row['quantity']
            
            if exec_time in market_data.index:
                exec_price = market_data.loc[exec_time, price_col]
            else:
                idx = market_data.index.get_indexer([exec_time], method='nearest')[0]
                exec_price = market_data.iloc[idx][price_col]
            
            executions.append({
                'timestamp': exec_time,
                'quantity': exec_qty,
                'price': exec_price,
                'value': exec_qty * exec_price
            })
        
        return pd.DataFrame(executions)


class POVAlgorithm(ExecutionAlgorithm):
    """
    Percentage of Volume (POV) Algorithm.
    
    Executes as a target percentage of market volume.
    """
    
    def __init__(
        self,
        total_quantity: int,
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
        target_pov: float = 0.1,
        min_quantity: int = 100,
        max_quantity: Optional[int] = None
    ):
        """
        Initialize POV algorithm.
        
        Parameters
        ----------
        total_quantity : int
            Total quantity to execute
        start_time : pd.Timestamp
            Start time for execution
        end_time : pd.Timestamp
            End time for execution
        target_pov : float
            Target participation rate (e.g., 0.1 = 10% of volume)
        min_quantity : int
            Minimum quantity per slice
        max_quantity : int, optional
            Maximum quantity per slice
        """
        super().__init__(total_quantity, start_time, end_time)
        self.target_pov = target_pov
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
    
    def execute(self, market_data: pd.DataFrame, price_col: str = 'price', volume_col: str = 'volume') -> pd.DataFrame:
        """
        Execute POV algorithm on market data.
        
        Parameters
        ----------
        market_data : pd.DataFrame
            Market data with prices and volumes
        price_col : str
            Name of price column
        volume_col : str
            Name of volume column
            
        Returns
        -------
        pd.DataFrame
            Execution results
        """
        executions = []
        remaining_qty = self.total_quantity
        
        # Filter to execution window
        mask = (market_data.index >= self.start_time) & (market_data.index <= self.end_time)
        execution_data = market_data[mask]
        
        for timestamp, row in execution_data.iterrows():
            if remaining_qty <= 0:
                break
            
            market_volume = row[volume_col]
            exec_price = row[price_col]
            
            # Calculate target quantity based on market volume
            target_qty = market_volume * self.target_pov
            
            # Apply constraints
            exec_qty = max(self.min_quantity, target_qty)
            if self.max_quantity is not None:
                exec_qty = min(self.max_quantity, exec_qty)
            
            # Don't exceed remaining quantity
            exec_qty = min(exec_qty, remaining_qty)
            
            if exec_qty > 0:
                executions.append({
                    'timestamp': timestamp,
                    'quantity': exec_qty,
                    'price': exec_price,
                    'market_volume': market_volume,
                    'participation_rate': exec_qty / market_volume if market_volume > 0 else 0,
                    'value': exec_qty * exec_price
                })
                
                remaining_qty -= exec_qty
        
        return pd.DataFrame(executions)


def compare_algorithms(
    market_data: pd.DataFrame,
    total_quantity: int,
    start_time: pd.Timestamp,
    end_time: pd.Timestamp,
    side: str = 'buy'
) -> Dict[str, pd.DataFrame]:
    """
    Compare performance of different execution algorithms.
    
    Parameters
    ----------
    market_data : pd.DataFrame
        Market data with prices and volumes
    total_quantity : int
        Total quantity to execute
    start_time : pd.Timestamp
        Start time for execution
    end_time : pd.Timestamp
        End time for execution
    side : str
        'buy' or 'sell'
        
    Returns
    -------
    dict
        Dictionary with execution results for each algorithm
    """
    results = {}
    
    # TWAP
    twap = TWAPAlgorithm(total_quantity, start_time, end_time)
    results['TWAP'] = twap.execute(market_data)
    
    # VWAP
    vwap = VWAPAlgorithm(total_quantity, start_time, end_time)
    results['VWAP'] = vwap.execute(market_data)
    
    # POV
    pov = POVAlgorithm(total_quantity, start_time, end_time, target_pov=0.1)
    results['POV'] = pov.execute(market_data)
    
    return results


def calculate_algorithm_performance(
    executions: pd.DataFrame,
    benchmark_price: float,
    side: str = 'buy'
) -> Dict[str, float]:
    """
    Calculate performance metrics for execution algorithm.
    
    Parameters
    ----------
    executions : pd.DataFrame
        Execution results with price and quantity
    benchmark_price : float
        Benchmark price (e.g., arrival price, VWAP)
    side : str
        'buy' or 'sell'
        
    Returns
    -------
    dict
        Performance metrics
    """
    total_qty = executions['quantity'].sum()
    avg_price = (executions['price'] * executions['quantity']).sum() / total_qty
    
    if side == 'buy':
        cost_bps = (avg_price - benchmark_price) / benchmark_price * 10000
    else:
        cost_bps = (benchmark_price - avg_price) / benchmark_price * 10000
    
    return {
        'avg_execution_price': avg_price,
        'total_quantity': total_qty,
        'num_executions': len(executions),
        'cost_vs_benchmark_bps': cost_bps,
        'price_std': executions['price'].std(),
        'quantity_std': executions['quantity'].std()
    }
