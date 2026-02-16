"""
Liquidity Metrics Module.

This module provides functions to calculate various liquidity metrics
commonly used in electronic trading and market microstructure analysis.
"""

import numpy as np
import pandas as pd
from typing import Optional


def calculate_bid_ask_spread(
    bid_price: pd.Series,
    ask_price: pd.Series,
    spread_type: str = 'absolute'
) -> pd.Series:
    """
    Calculate bid-ask spread.
    
    Parameters
    ----------
    bid_price : pd.Series
        Bid prices
    ask_price : pd.Series
        Ask prices
    spread_type : str
        Type of spread: 'absolute', 'percentage', or 'bps' (basis points)
        
    Returns
    -------
    pd.Series
        Bid-ask spread
    """
    spread = ask_price - bid_price
    
    if spread_type == 'absolute':
        return spread
    elif spread_type == 'percentage':
        mid_price = (bid_price + ask_price) / 2
        return (spread / mid_price) * 100
    elif spread_type == 'bps':
        mid_price = (bid_price + ask_price) / 2
        return (spread / mid_price) * 10000
    else:
        raise ValueError(f"Unknown spread_type: {spread_type}")


def calculate_effective_spread(
    trade_price: pd.Series,
    mid_price: pd.Series,
    direction: pd.Series
) -> pd.Series:
    """
    Calculate effective spread (actual execution cost).
    
    Parameters
    ----------
    trade_price : pd.Series
        Actual trade execution prices
    mid_price : pd.Series
        Mid-market prices at time of trade
    direction : pd.Series
        Trade direction (1 for buy, -1 for sell)
        
    Returns
    -------
    pd.Series
        Effective spread in absolute terms
    """
    return 2 * direction * (trade_price - mid_price)


def calculate_realized_spread(
    trade_price: pd.Series,
    future_mid_price: pd.Series,
    direction: pd.Series
) -> pd.Series:
    """
    Calculate realized spread (profit from liquidity provision).
    
    Parameters
    ----------
    trade_price : pd.Series
        Trade execution prices
    future_mid_price : pd.Series
        Mid prices at a future time point
    direction : pd.Series
        Trade direction (1 for buy, -1 for sell)
        
    Returns
    -------
    pd.Series
        Realized spread
    """
    return 2 * direction * (trade_price - future_mid_price)


def calculate_price_impact(
    trade_price: pd.Series,
    pre_trade_mid: pd.Series,
    post_trade_mid: pd.Series,
    direction: pd.Series
) -> pd.Series:
    """
    Calculate price impact of trades.
    
    Parameters
    ----------
    trade_price : pd.Series
        Trade execution prices
    pre_trade_mid : pd.Series
        Mid prices before trade
    post_trade_mid : pd.Series
        Mid prices after trade
    direction : pd.Series
        Trade direction (1 for buy, -1 for sell)
        
    Returns
    -------
    pd.Series
        Price impact
    """
    return direction * (post_trade_mid - pre_trade_mid)


def calculate_market_depth(
    bid_sizes: pd.DataFrame,
    ask_sizes: pd.DataFrame,
    levels: int = 5
) -> pd.Series:
    """
    Calculate total market depth across multiple levels.
    
    Parameters
    ----------
    bid_sizes : pd.DataFrame
        Bid sizes at different levels
    ask_sizes : pd.DataFrame
        Ask sizes at different levels
    levels : int
        Number of levels to include
        
    Returns
    -------
    pd.Series
        Total market depth
    """
    total_bid = bid_sizes.iloc[:, :levels].sum(axis=1)
    total_ask = ask_sizes.iloc[:, :levels].sum(axis=1)
    return total_bid + total_ask


def calculate_quote_slope(
    prices: pd.DataFrame,
    sizes: pd.DataFrame,
    side: str = 'bid'
) -> pd.Series:
    """
    Calculate the slope of the order book (price vs cumulative size).
    
    Parameters
    ----------
    prices : pd.DataFrame
        Price levels
    sizes : pd.DataFrame
        Size at each price level
    side : str
        'bid' or 'ask'
        
    Returns
    -------
    pd.Series
        Order book slope (steeper = less liquid)
    """
    slopes = []
    
    for idx in prices.index:
        price_levels = prices.loc[idx].values
        size_levels = sizes.loc[idx].values
        
        # Calculate cumulative sizes
        cum_sizes = np.cumsum(size_levels)
        
        # Fit linear regression: price = slope * cum_size + intercept
        if len(price_levels) > 1:
            slope = np.polyfit(cum_sizes, price_levels, 1)[0]
            slopes.append(abs(slope))
        else:
            slopes.append(np.nan)
    
    return pd.Series(slopes, index=prices.index)


def calculate_amihud_illiquidity(
    returns: pd.Series,
    volumes: pd.Series,
    window: Optional[int] = None
) -> pd.Series:
    """
    Calculate Amihud illiquidity measure.
    
    Amihud (2002): average ratio of absolute return to dollar volume.
    Higher values indicate lower liquidity.
    
    Parameters
    ----------
    returns : pd.Series
        Price returns
    volumes : pd.Series
        Trading volumes
    window : int, optional
        Rolling window size. If None, calculates for entire series
        
    Returns
    -------
    pd.Series or float
        Amihud illiquidity measure
    """
    illiquidity = abs(returns) / volumes
    
    if window is None:
        return illiquidity.mean()
    else:
        return illiquidity.rolling(window=window).mean()


def calculate_roll_spread(returns: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate Roll's spread estimator from price changes.
    
    Roll (1984): Estimate spread from serial covariance of price changes.
    
    Parameters
    ----------
    returns : pd.Series
        Price returns or price changes
    window : int
        Rolling window size
        
    Returns
    -------
    pd.Series
        Estimated spread
    """
    # Calculate serial covariance
    cov = returns.rolling(window=window).cov(returns.shift(1))
    
    # Roll's estimator: spread = 2 * sqrt(-cov)
    # Set negative or zero covariances to small positive value
    cov_adj = cov.where(cov < 0, -1e-10)
    spread = 2 * np.sqrt(-cov_adj)
    
    return spread


def calculate_turnover(
    volume: pd.Series,
    shares_outstanding: float,
    window: Optional[int] = None
) -> pd.Series:
    """
    Calculate turnover ratio (volume / shares outstanding).
    
    Parameters
    ----------
    volume : pd.Series
        Trading volume
    shares_outstanding : float
        Total shares outstanding
    window : int, optional
        Rolling window for aggregation
        
    Returns
    -------
    pd.Series
        Turnover ratio
    """
    if window is not None:
        volume = volume.rolling(window=window).sum()
    
    return volume / shares_outstanding


def calculate_volume_weighted_spread(
    spreads: pd.Series,
    volumes: pd.Series,
    window: int = 20
) -> pd.Series:
    """
    Calculate volume-weighted average spread.
    
    Parameters
    ----------
    spreads : pd.Series
        Bid-ask spreads
    volumes : pd.Series
        Trading volumes
    window : int
        Rolling window size
        
    Returns
    -------
    pd.Series
        Volume-weighted spread
    """
    weighted = (spreads * volumes).rolling(window=window).sum()
    total_volume = volumes.rolling(window=window).sum()
    
    return weighted / total_volume


def calculate_liquidity_score(
    bid_ask_spread: pd.Series,
    depth: pd.Series,
    volume: pd.Series,
    normalize: bool = True
) -> pd.Series:
    """
    Calculate composite liquidity score from multiple metrics.
    
    Combines spread (cost), depth (quantity), and volume (activity).
    Higher score = more liquid.
    
    Parameters
    ----------
    bid_ask_spread : pd.Series
        Bid-ask spread (lower is better)
    depth : pd.Series
        Market depth (higher is better)
    volume : pd.Series
        Trading volume (higher is better)
    normalize : bool
        Whether to normalize to 0-100 scale
        
    Returns
    -------
    pd.Series
        Composite liquidity score
    """
    # Invert spread (so higher is better)
    spread_score = 1 / (1 + bid_ask_spread)
    
    # Normalize each component
    spread_norm = (spread_score - spread_score.min()) / (spread_score.max() - spread_score.min())
    depth_norm = (depth - depth.min()) / (depth.max() - depth.min())
    volume_norm = (volume - volume.min()) / (volume.max() - volume.min())
    
    # Equal weighted composite
    score = (spread_norm + depth_norm + volume_norm) / 3
    
    if normalize:
        score = score * 100
    
    return score


def calculate_relative_spread(
    bid_price: pd.Series,
    ask_price: pd.Series
) -> pd.Series:
    """
    Calculate relative (percentage) bid-ask spread.
    
    Parameters
    ----------
    bid_price : pd.Series
        Bid prices
    ask_price : pd.Series
        Ask prices
        
    Returns
    -------
    pd.Series
        Relative spread as percentage
    """
    mid_price = (bid_price + ask_price) / 2
    return ((ask_price - bid_price) / mid_price) * 100
