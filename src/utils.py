"""
Utility functions for the Electronic Trading Lab.

This module provides helper functions for generating synthetic market data,
data preprocessing, and common calculations used across the library.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional


def generate_price_series(
    n_periods: int = 1000,
    initial_price: float = 100.0,
    mu: float = 0.0001,
    sigma: float = 0.02,
    seed: Optional[int] = None
) -> pd.Series:
    """
    Generate a synthetic price series using geometric Brownian motion.
    
    Parameters
    ----------
    n_periods : int
        Number of time periods to generate
    initial_price : float
        Starting price
    mu : float
        Drift parameter (expected return per period)
    sigma : float
        Volatility parameter (standard deviation of returns)
    seed : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    pd.Series
        Price series with datetime index
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate returns using geometric Brownian motion
    dt = 1.0
    returns = np.random.normal(mu * dt, sigma * np.sqrt(dt), n_periods)
    
    # Calculate price path
    price_path = initial_price * np.exp(np.cumsum(returns))
    
    # Create series with datetime index
    dates = pd.date_range(start='2024-01-01', periods=n_periods, freq='1min')
    prices = pd.Series(price_path, index=dates, name='price')
    
    return prices


def generate_order_book(
    prices: pd.Series,
    spread_bps: float = 5.0,
    depth_shares: int = 10000,
    levels: int = 5
) -> pd.DataFrame:
    """
    Generate synthetic order book data with bid-ask spreads and depth.
    
    Parameters
    ----------
    prices : pd.Series
        Mid-price series
    spread_bps : float
        Bid-ask spread in basis points
    depth_shares : int
        Number of shares at each level
    levels : int
        Number of price levels on each side
        
    Returns
    -------
    pd.DataFrame
        Order book with bid/ask prices and sizes
    """
    n = len(prices)
    half_spread = prices * (spread_bps / 10000) / 2
    
    data = {
        'mid_price': prices.values,
        'bid_price': (prices - half_spread).values,
        'ask_price': (prices + half_spread).values,
        'bid_size': np.random.randint(depth_shares // 2, depth_shares * 2, n),
        'ask_size': np.random.randint(depth_shares // 2, depth_shares * 2, n),
    }
    
    # Add additional levels
    for i in range(2, levels + 1):
        spread_multiplier = i
        data[f'bid_price_{i}'] = (prices - half_spread * spread_multiplier).values
        data[f'ask_price_{i}'] = (prices + half_spread * spread_multiplier).values
        data[f'bid_size_{i}'] = np.random.randint(depth_shares // 2, depth_shares * 2, n)
        data[f'ask_size_{i}'] = np.random.randint(depth_shares // 2, depth_shares * 2, n)
    
    df = pd.DataFrame(data, index=prices.index)
    return df


def generate_trade_data(
    prices: pd.Series,
    avg_volume: int = 1000,
    volume_std: int = 500,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Generate synthetic trade data with volume and direction.
    
    Parameters
    ----------
    prices : pd.Series
        Price series
    avg_volume : int
        Average trade volume
    volume_std : int
        Standard deviation of trade volume
    seed : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    pd.DataFrame
        Trade data with price, volume, and direction
    """
    if seed is not None:
        np.random.seed(seed)
    
    n = len(prices)
    
    # Generate volumes (ensure positive)
    volumes = np.abs(np.random.normal(avg_volume, volume_std, n)).astype(int)
    volumes = np.maximum(volumes, 1)
    
    # Generate buy/sell direction (1 for buy, -1 for sell)
    directions = np.random.choice([1, -1], size=n)
    
    # Add some noise to trade prices
    noise = np.random.normal(0, prices.std() * 0.001, n)
    trade_prices = prices.values + noise
    
    df = pd.DataFrame({
        'price': trade_prices,
        'volume': volumes,
        'direction': directions,
        'value': trade_prices * volumes
    }, index=prices.index)
    
    return df


def calculate_returns(prices: pd.Series, periods: int = 1) -> pd.Series:
    """
    Calculate returns from a price series.
    
    Parameters
    ----------
    prices : pd.Series
        Price series
    periods : int
        Number of periods for return calculation
        
    Returns
    -------
    pd.Series
        Returns series
    """
    return prices.pct_change(periods=periods)


def calculate_volatility(
    returns: pd.Series,
    window: Optional[int] = None,
    annualization_factor: float = 252.0
) -> float:
    """
    Calculate volatility from returns.
    
    Parameters
    ----------
    returns : pd.Series
        Returns series
    window : int, optional
        Rolling window size. If None, calculates overall volatility
    annualization_factor : float
        Factor to annualize volatility (252 for daily, 252*390 for minute)
        
    Returns
    -------
    float or pd.Series
        Annualized volatility
    """
    if window is None:
        return returns.std() * np.sqrt(annualization_factor)
    else:
        return returns.rolling(window=window).std() * np.sqrt(annualization_factor)


def resample_data(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    """
    Resample high-frequency data to lower frequency.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with datetime index
    freq : str
        Resampling frequency (e.g., '5min', '1H', '1D')
        
    Returns
    -------
    pd.DataFrame
        Resampled data
    """
    # Use appropriate aggregation for different columns
    agg_dict = {}
    for col in df.columns:
        if 'price' in col.lower():
            agg_dict[col] = 'last'
        elif 'volume' in col.lower() or 'size' in col.lower():
            agg_dict[col] = 'sum'
        else:
            agg_dict[col] = 'last'
    
    return df.resample(freq).agg(agg_dict).dropna()


def add_microstructure_noise(
    prices: pd.Series,
    noise_level: float = 0.0001
) -> pd.Series:
    """
    Add microstructure noise to prices to simulate market frictions.
    
    Parameters
    ----------
    prices : pd.Series
        Clean price series
    noise_level : float
        Noise level as fraction of price
        
    Returns
    -------
    pd.Series
        Noisy price series
    """
    noise = np.random.normal(0, prices.std() * noise_level, len(prices))
    return prices + noise


def split_train_test(
    data: pd.DataFrame,
    train_size: float = 0.8
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data into training and testing sets.
    
    Parameters
    ----------
    data : pd.DataFrame
        Data to split
    train_size : float
        Proportion of data for training
        
    Returns
    -------
    tuple
        (train_data, test_data)
    """
    split_idx = int(len(data) * train_size)
    return data.iloc[:split_idx], data.iloc[split_idx:]
