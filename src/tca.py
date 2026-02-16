"""
Transaction Cost Analysis (TCA) Module.

This module provides functions for analyzing transaction costs,
including implementation shortfall, VWAP analysis, and slippage metrics.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict


def calculate_implementation_shortfall(
    decision_price: float,
    execution_prices: pd.Series,
    execution_volumes: pd.Series,
    final_price: float,
    side: str = 'buy'
) -> Dict[str, float]:
    """
    Calculate implementation shortfall decomposition.
    
    Implementation shortfall = Total Cost - Opportunity Cost - Timing Cost - Fees
    
    Parameters
    ----------
    decision_price : float
        Price when decision to trade was made
    execution_prices : pd.Series
        Actual execution prices for each fill
    execution_volumes : pd.Series
        Volumes for each fill
    final_price : float
        Price at end of trading period
    side : str
        'buy' or 'sell'
        
    Returns
    -------
    dict
        Dictionary with IS components (bps)
    """
    total_volume = execution_volumes.sum()
    avg_execution_price = (execution_prices * execution_volumes).sum() / total_volume
    
    if side == 'buy':
        # For buys, higher price = higher cost
        total_cost = (avg_execution_price - decision_price) / decision_price * 10000
        opportunity_cost = (final_price - decision_price) / decision_price * 10000
        execution_cost = (avg_execution_price - decision_price) / decision_price * 10000
    else:  # sell
        # For sells, lower price = higher cost
        total_cost = (decision_price - avg_execution_price) / decision_price * 10000
        opportunity_cost = (decision_price - final_price) / decision_price * 10000
        execution_cost = (decision_price - avg_execution_price) / decision_price * 10000
    
    return {
        'decision_price': decision_price,
        'avg_execution_price': avg_execution_price,
        'final_price': final_price,
        'total_cost_bps': total_cost,
        'execution_cost_bps': execution_cost,
        'opportunity_cost_bps': opportunity_cost,
        'total_volume': total_volume
    }


def calculate_vwap_performance(
    execution_prices: pd.Series,
    execution_volumes: pd.Series,
    market_prices: pd.Series,
    market_volumes: pd.Series,
    side: str = 'buy'
) -> Dict[str, float]:
    """
    Calculate VWAP performance metrics.
    
    Parameters
    ----------
    execution_prices : pd.Series
        Actual execution prices
    execution_volumes : pd.Series
        Execution volumes
    market_prices : pd.Series
        Market prices during execution period
    market_volumes : pd.Series
        Market volumes during execution period
    side : str
        'buy' or 'sell'
        
    Returns
    -------
    dict
        VWAP performance metrics
    """
    # Calculate execution VWAP
    exec_vwap = (execution_prices * execution_volumes).sum() / execution_volumes.sum()
    
    # Calculate market VWAP
    market_vwap = (market_prices * market_volumes).sum() / market_volumes.sum()
    
    # Calculate slippage
    if side == 'buy':
        slippage_bps = (exec_vwap - market_vwap) / market_vwap * 10000
    else:  # sell
        slippage_bps = (market_vwap - exec_vwap) / market_vwap * 10000
    
    return {
        'execution_vwap': exec_vwap,
        'market_vwap': market_vwap,
        'slippage_bps': slippage_bps,
        'total_exec_volume': execution_volumes.sum(),
        'total_market_volume': market_volumes.sum(),
        'participation_rate': execution_volumes.sum() / market_volumes.sum()
    }


def calculate_slippage(
    arrival_price: pd.Series,
    execution_price: pd.Series,
    side: str = 'buy'
) -> pd.Series:
    """
    Calculate slippage for each trade.
    
    Parameters
    ----------
    arrival_price : pd.Series
        Price when order arrived
    execution_price : pd.Series
        Price when order executed
    side : str
        'buy' or 'sell'
        
    Returns
    -------
    pd.Series
        Slippage in basis points
    """
    if side == 'buy':
        slippage = (execution_price - arrival_price) / arrival_price * 10000
    else:  # sell
        slippage = (arrival_price - execution_price) / arrival_price * 10000
    
    return slippage


def calculate_market_impact(
    pre_trade_price: pd.Series,
    post_trade_price: pd.Series,
    execution_volume: pd.Series,
    market_volume: pd.Series,
    side: str = 'buy'
) -> pd.DataFrame:
    """
    Calculate market impact metrics.
    
    Parameters
    ----------
    pre_trade_price : pd.Series
        Prices before trades
    post_trade_price : pd.Series
        Prices after trades
    execution_volume : pd.Series
        Trade volumes
    market_volume : pd.Series
        Market volumes
    side : str
        'buy' or 'sell'
        
    Returns
    -------
    pd.DataFrame
        Market impact metrics
    """
    # Calculate price impact
    if side == 'buy':
        price_impact = (post_trade_price - pre_trade_price) / pre_trade_price * 10000
    else:  # sell
        price_impact = (pre_trade_price - post_trade_price) / pre_trade_price * 10000
    
    # Calculate participation rate
    participation = execution_volume / market_volume
    
    # Combine metrics
    impact_df = pd.DataFrame({
        'price_impact_bps': price_impact,
        'participation_rate': participation,
        'execution_volume': execution_volume,
        'market_volume': market_volume
    })
    
    return impact_df


def calculate_timing_cost(
    benchmark_price: float,
    execution_prices: pd.Series,
    execution_volumes: pd.Series,
    execution_times: pd.DatetimeIndex,
    side: str = 'buy'
) -> pd.DataFrame:
    """
    Calculate timing cost of executions relative to benchmark.
    
    Parameters
    ----------
    benchmark_price : float
        Benchmark price (e.g., decision price, open price)
    execution_prices : pd.Series
        Execution prices
    execution_volumes : pd.Series
        Execution volumes
    execution_times : pd.DatetimeIndex
        Execution timestamps
    side : str
        'buy' or 'sell'
        
    Returns
    -------
    pd.DataFrame
        Timing costs
    """
    if side == 'buy':
        timing_cost = (execution_prices - benchmark_price) / benchmark_price * 10000
    else:  # sell
        timing_cost = (benchmark_price - execution_prices) / benchmark_price * 10000
    
    df = pd.DataFrame({
        'execution_time': execution_times,
        'execution_price': execution_prices,
        'execution_volume': execution_volumes,
        'timing_cost_bps': timing_cost,
        'cumulative_cost_bps': (timing_cost * execution_volumes).cumsum() / execution_volumes.cumsum()
    })
    
    return df


def calculate_arrival_cost(
    arrival_price: pd.Series,
    execution_price: pd.Series,
    volume: pd.Series,
    side: str = 'buy'
) -> float:
    """
    Calculate volume-weighted arrival cost.
    
    Parameters
    ----------
    arrival_price : pd.Series
        Arrival prices
    execution_price : pd.Series
        Execution prices
    volume : pd.Series
        Trade volumes
    side : str
        'buy' or 'sell'
        
    Returns
    -------
    float
        Volume-weighted arrival cost in bps
    """
    if side == 'buy':
        cost_per_trade = (execution_price - arrival_price) / arrival_price * 10000
    else:  # sell
        cost_per_trade = (arrival_price - execution_price) / arrival_price * 10000
    
    weighted_cost = (cost_per_trade * volume).sum() / volume.sum()
    return weighted_cost


def calculate_execution_quality_score(
    slippage_bps: float,
    market_impact_bps: float,
    fill_rate: float,
    speed_score: float = 1.0
) -> float:
    """
    Calculate composite execution quality score.
    
    Parameters
    ----------
    slippage_bps : float
        Average slippage in bps (lower is better)
    market_impact_bps : float
        Average market impact in bps (lower is better)
    fill_rate : float
        Percentage of order filled (0-1, higher is better)
    speed_score : float
        Execution speed score (0-1, higher is better)
        
    Returns
    -------
    float
        Quality score (0-100, higher is better)
    """
    # Normalize costs (assuming typical ranges)
    slippage_score = max(0, 1 - abs(slippage_bps) / 50)  # 50 bps as reference
    impact_score = max(0, 1 - abs(market_impact_bps) / 30)  # 30 bps as reference
    
    # Weighted composite
    quality_score = (
        0.3 * slippage_score +
        0.3 * impact_score +
        0.3 * fill_rate +
        0.1 * speed_score
    ) * 100
    
    return quality_score


def analyze_execution_by_time(
    execution_data: pd.DataFrame,
    time_column: str = 'timestamp',
    price_column: str = 'price',
    volume_column: str = 'volume',
    freq: str = '5min'
) -> pd.DataFrame:
    """
    Analyze execution patterns by time of day.
    
    Parameters
    ----------
    execution_data : pd.DataFrame
        Execution data
    time_column : str
        Name of timestamp column
    price_column : str
        Name of price column
    volume_column : str
        Name of volume column
    freq : str
        Time frequency for grouping
        
    Returns
    -------
    pd.DataFrame
        Execution statistics by time bucket
    """
    df = execution_data.copy()
    df['time_bucket'] = df[time_column].dt.floor(freq)
    
    grouped = df.groupby('time_bucket').agg({
        price_column: ['mean', 'std', 'min', 'max'],
        volume_column: ['sum', 'mean', 'count']
    })
    
    return grouped


def calculate_price_improvement(
    limit_price: pd.Series,
    execution_price: pd.Series,
    side: str = 'buy'
) -> pd.Series:
    """
    Calculate price improvement vs. limit price.
    
    Parameters
    ----------
    limit_price : pd.Series
        Limit prices submitted
    execution_price : pd.Series
        Actual execution prices
    side : str
        'buy' or 'sell'
        
    Returns
    -------
    pd.Series
        Price improvement in bps (positive = improvement)
    """
    if side == 'buy':
        # Buy: execution below limit = improvement
        improvement = (limit_price - execution_price) / limit_price * 10000
    else:  # sell
        # Sell: execution above limit = improvement
        improvement = (execution_price - limit_price) / limit_price * 10000
    
    return improvement


def calculate_interval_vwap(
    prices: pd.Series,
    volumes: pd.Series,
    window: int = 20
) -> pd.Series:
    """
    Calculate rolling VWAP over specified window.
    
    Parameters
    ----------
    prices : pd.Series
        Price series
    volumes : pd.Series
        Volume series
    window : int
        Rolling window size
        
    Returns
    -------
    pd.Series
        Rolling VWAP
    """
    vwap = (prices * volumes).rolling(window=window).sum() / volumes.rolling(window=window).sum()
    return vwap
