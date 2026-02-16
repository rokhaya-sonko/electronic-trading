"""
Risk Management Module.

This module provides risk metrics and tools for portfolio risk analysis,
including VaR, Expected Shortfall, and position monitoring.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Optional, Dict, List


def calculate_var(
    returns: pd.Series,
    confidence_level: float = 0.95,
    method: str = 'historical'
) -> float:
    """
    Calculate Value at Risk (VaR).
    
    Parameters
    ----------
    returns : pd.Series
        Returns series
    confidence_level : float
        Confidence level (e.g., 0.95 for 95%)
    method : str
        Method: 'historical', 'parametric', or 'cornish_fisher'
        
    Returns
    -------
    float
        VaR (positive number represents potential loss)
    """
    if method == 'historical':
        # Historical VaR
        var = -np.percentile(returns, (1 - confidence_level) * 100)
    
    elif method == 'parametric':
        # Parametric VaR (assumes normal distribution)
        mu = returns.mean()
        sigma = returns.std()
        z_score = stats.norm.ppf(1 - confidence_level)
        var = -(mu + z_score * sigma)
    
    elif method == 'cornish_fisher':
        # Cornish-Fisher VaR (accounts for skewness and kurtosis)
        mu = returns.mean()
        sigma = returns.std()
        skew = returns.skew()
        kurt = returns.kurtosis()
        
        z = stats.norm.ppf(1 - confidence_level)
        z_cf = z + (z**2 - 1) * skew / 6 + (z**3 - 3*z) * kurt / 24 - (2*z**3 - 5*z) * skew**2 / 36
        
        var = -(mu + z_cf * sigma)
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return var


def calculate_expected_shortfall(
    returns: pd.Series,
    confidence_level: float = 0.95
) -> float:
    """
    Calculate Expected Shortfall (Conditional VaR).
    
    ES is the expected loss given that VaR has been exceeded.
    
    Parameters
    ----------
    returns : pd.Series
        Returns series
    confidence_level : float
        Confidence level
        
    Returns
    -------
    float
        Expected Shortfall
    """
    var = calculate_var(returns, confidence_level, method='historical')
    # ES is the mean of returns worse than VaR
    es = -returns[returns <= -var].mean()
    return es


def calculate_portfolio_var(
    returns: pd.DataFrame,
    weights: np.ndarray,
    confidence_level: float = 0.95,
    method: str = 'parametric'
) -> float:
    """
    Calculate portfolio VaR considering correlations.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Returns for multiple assets
    weights : np.ndarray
        Portfolio weights
    confidence_level : float
        Confidence level
    method : str
        Calculation method
        
    Returns
    -------
    float
        Portfolio VaR
    """
    # Calculate portfolio returns
    portfolio_returns = (returns * weights).sum(axis=1)
    
    # Calculate VaR on portfolio returns
    var = calculate_var(portfolio_returns, confidence_level, method)
    
    return var


def calculate_volatility(
    returns: pd.Series,
    window: Optional[int] = None,
    annualize: bool = True,
    trading_days: int = 252
) -> pd.Series:
    """
    Calculate realized volatility.
    
    Parameters
    ----------
    returns : pd.Series
        Returns series
    window : int, optional
        Rolling window size. If None, calculates overall volatility
    annualize : bool
        Whether to annualize volatility
    trading_days : int
        Number of trading days per year
        
    Returns
    -------
    pd.Series or float
        Volatility
    """
    if window is None:
        vol = returns.std()
    else:
        vol = returns.rolling(window=window).std()
    
    if annualize:
        vol = vol * np.sqrt(trading_days)
    
    return vol


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    annualize: bool = True,
    trading_days: int = 252
) -> float:
    """
    Calculate Sharpe ratio.
    
    Parameters
    ----------
    returns : pd.Series
        Returns series
    risk_free_rate : float
        Risk-free rate (annualized)
    annualize : bool
        Whether to annualize the ratio
    trading_days : int
        Number of trading days per year
        
    Returns
    -------
    float
        Sharpe ratio
    """
    excess_returns = returns - risk_free_rate / trading_days
    
    if annualize:
        sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(trading_days)
    else:
        sharpe = excess_returns.mean() / excess_returns.std()
    
    return sharpe


def calculate_max_drawdown(prices: pd.Series) -> Dict[str, float]:
    """
    Calculate maximum drawdown and related metrics.
    
    Parameters
    ----------
    prices : pd.Series
        Price or portfolio value series
        
    Returns
    -------
    dict
        Drawdown metrics
    """
    # Calculate cumulative returns
    cumulative = (1 + prices.pct_change()).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    
    max_dd = drawdown.min()
    max_dd_date = drawdown.idxmin()
    
    # Find peak before max drawdown
    peak_date = cumulative[:max_dd_date].idxmax()
    
    # Calculate recovery time
    recovery_dates = cumulative[max_dd_date:][cumulative[max_dd_date:] >= cumulative[peak_date]]
    if len(recovery_dates) > 0:
        recovery_date = recovery_dates.index[0]
        recovery_days = (recovery_date - max_dd_date).days
    else:
        recovery_date = None
        recovery_days = None
    
    return {
        'max_drawdown': max_dd,
        'max_drawdown_date': max_dd_date,
        'peak_date': peak_date,
        'recovery_date': recovery_date,
        'recovery_days': recovery_days
    }


def calculate_beta(
    asset_returns: pd.Series,
    market_returns: pd.Series
) -> float:
    """
    Calculate beta (systematic risk).
    
    Parameters
    ----------
    asset_returns : pd.Series
        Asset returns
    market_returns : pd.Series
        Market returns
        
    Returns
    -------
    float
        Beta coefficient
    """
    covariance = asset_returns.cov(market_returns)
    market_variance = market_returns.var()
    beta = covariance / market_variance
    return beta


def calculate_tracking_error(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    annualize: bool = True,
    trading_days: int = 252
) -> float:
    """
    Calculate tracking error.
    
    Parameters
    ----------
    portfolio_returns : pd.Series
        Portfolio returns
    benchmark_returns : pd.Series
        Benchmark returns
    annualize : bool
        Whether to annualize
    trading_days : int
        Number of trading days per year
        
    Returns
    -------
    float
        Tracking error
    """
    active_returns = portfolio_returns - benchmark_returns
    te = active_returns.std()
    
    if annualize:
        te = te * np.sqrt(trading_days)
    
    return te


def calculate_information_ratio(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    annualize: bool = True,
    trading_days: int = 252
) -> float:
    """
    Calculate information ratio.
    
    Parameters
    ----------
    portfolio_returns : pd.Series
        Portfolio returns
    benchmark_returns : pd.Series
        Benchmark returns
    annualize : bool
        Whether to annualize
    trading_days : int
        Number of trading days per year
        
    Returns
    -------
    float
        Information ratio
    """
    active_returns = portfolio_returns - benchmark_returns
    
    if annualize:
        ir = active_returns.mean() / active_returns.std() * np.sqrt(trading_days)
    else:
        ir = active_returns.mean() / active_returns.std()
    
    return ir


def calculate_portfolio_risk_metrics(
    returns: pd.DataFrame,
    weights: np.ndarray,
    benchmark_returns: Optional[pd.Series] = None
) -> Dict[str, float]:
    """
    Calculate comprehensive risk metrics for a portfolio.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Asset returns
    weights : np.ndarray
        Portfolio weights
    benchmark_returns : pd.Series, optional
        Benchmark returns for relative metrics
        
    Returns
    -------
    dict
        Dictionary of risk metrics
    """
    # Calculate portfolio returns
    portfolio_returns = (returns * weights).sum(axis=1)
    
    metrics = {
        'volatility': calculate_volatility(portfolio_returns, annualize=True),
        'var_95': calculate_var(portfolio_returns, 0.95),
        'var_99': calculate_var(portfolio_returns, 0.99),
        'expected_shortfall_95': calculate_expected_shortfall(portfolio_returns, 0.95),
        'sharpe_ratio': calculate_sharpe_ratio(portfolio_returns),
        'max_drawdown': calculate_max_drawdown((1 + portfolio_returns).cumprod())['max_drawdown']
    }
    
    if benchmark_returns is not None:
        metrics['beta'] = calculate_beta(portfolio_returns, benchmark_returns)
        metrics['tracking_error'] = calculate_tracking_error(portfolio_returns, benchmark_returns)
        metrics['information_ratio'] = calculate_information_ratio(portfolio_returns, benchmark_returns)
    
    return metrics


def calculate_position_limits(
    portfolio_value: float,
    var_limit: float = 0.02,
    confidence_level: float = 0.95,
    asset_volatility: float = 0.20
) -> Dict[str, float]:
    """
    Calculate position size limits based on risk constraints.
    
    Parameters
    ----------
    portfolio_value : float
        Total portfolio value
    var_limit : float
        VaR limit as fraction of portfolio (e.g., 0.02 = 2%)
    confidence_level : float
        VaR confidence level
    asset_volatility : float
        Asset volatility (annualized)
        
    Returns
    -------
    dict
        Position limits
    """
    # Calculate z-score for confidence level
    z_score = stats.norm.ppf(confidence_level)
    
    # Maximum position size to stay within VaR limit
    max_position_value = (var_limit * portfolio_value) / (z_score * asset_volatility)
    
    return {
        'max_position_value': max_position_value,
        'max_position_pct': max_position_value / portfolio_value,
        'var_limit': var_limit * portfolio_value
    }


def stress_test_portfolio(
    returns: pd.DataFrame,
    weights: np.ndarray,
    scenarios: Dict[str, Dict[str, float]]
) -> pd.DataFrame:
    """
    Stress test portfolio under various scenarios.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Historical asset returns
    weights : np.ndarray
        Portfolio weights
    scenarios : dict
        Dictionary of scenarios with asset shocks
        Example: {'crisis': {'asset1': -0.20, 'asset2': -0.15}}
        
    Returns
    -------
    pd.DataFrame
        Scenario results
    """
    results = []
    
    for scenario_name, shocks in scenarios.items():
        scenario_returns = pd.Series(index=returns.columns, dtype=float)
        
        for asset in returns.columns:
            if asset in shocks:
                scenario_returns[asset] = shocks[asset]
            else:
                scenario_returns[asset] = 0.0
        
        portfolio_return = (scenario_returns * weights).sum()
        
        results.append({
            'scenario': scenario_name,
            'portfolio_return': portfolio_return,
            'portfolio_value_change': portfolio_return
        })
    
    return pd.DataFrame(results)


def calculate_correlation_matrix(returns: pd.DataFrame, window: Optional[int] = None) -> pd.DataFrame:
    """
    Calculate correlation matrix of returns.
    
    Parameters
    ----------
    returns : pd.DataFrame
        Returns for multiple assets
    window : int, optional
        Rolling window size
        
    Returns
    -------
    pd.DataFrame
        Correlation matrix
    """
    if window is None:
        return returns.corr()
    else:
        return returns.rolling(window=window).corr()
