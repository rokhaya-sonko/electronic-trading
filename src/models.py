"""
Market Microstructure Models Module.

This module implements models for optimal execution, price impact,
and market microstructure analysis.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Optional, Dict, Tuple


class AlmgrenChrissModel:
    """
    Almgren-Chriss optimal execution model.
    
    Optimal execution strategy that balances market impact and timing risk.
    Reference: Almgren & Chriss (2000) "Optimal execution of portfolio transactions"
    """
    
    def __init__(
        self,
        total_quantity: int,
        total_time: float,
        volatility: float,
        permanent_impact: float = 0.1,
        temporary_impact: float = 0.1,
        risk_aversion: float = 1e-6
    ):
        """
        Initialize Almgren-Chriss model.
        
        Parameters
        ----------
        total_quantity : int
            Total quantity to execute
        total_time : float
            Total time horizon (in same units as volatility)
        volatility : float
            Price volatility
        permanent_impact : float
            Permanent market impact parameter
        temporary_impact : float
            Temporary market impact parameter
        risk_aversion : float
            Risk aversion parameter (lambda)
        """
        self.X = total_quantity
        self.T = total_time
        self.sigma = volatility
        self.gamma = permanent_impact
        self.eta = temporary_impact
        self.lambda_risk = risk_aversion
    
    def calculate_optimal_trajectory(self, num_periods: int) -> pd.DataFrame:
        """
        Calculate optimal execution trajectory.
        
        Parameters
        ----------
        num_periods : int
            Number of time periods to split execution
            
        Returns
        -------
        pd.DataFrame
            Optimal trajectory with holdings and trade rates
        """
        tau = self.T / num_periods  # Time per period
        
        # Calculate kappa (combination of temporary and permanent impact)
        kappa_tilde = np.sqrt(self.lambda_risk * self.sigma**2 / self.eta)
        kappa_hat = np.sqrt(self.eta * kappa_tilde**2 + self.gamma**2 / 4) - self.gamma / 2
        
        # Calculate optimal trajectory
        times = np.linspace(0, self.T, num_periods + 1)
        
        holdings = []
        trade_rates = []
        
        for t in times[:-1]:
            # Optimal holdings at time t
            remaining_time = self.T - t
            x_t = self.X * np.sinh(kappa_hat * remaining_time) / np.sinh(kappa_hat * self.T)
            holdings.append(x_t)
            
            # Trade rate (negative of derivative)
            n_t = self.X * kappa_hat * np.cosh(kappa_hat * remaining_time) / np.sinh(kappa_hat * self.T)
            trade_rates.append(n_t * tau)
        
        # Final holding should be zero
        holdings.append(0)
        trade_rates.append(0)
        
        trajectory = pd.DataFrame({
            'time': times,
            'holdings': holdings,
            'trade_size': trade_rates,
            'cumulative_traded': self.X - np.array(holdings)
        })
        
        return trajectory
    
    def calculate_expected_cost(self, trajectory: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate expected execution cost for a trajectory.
        
        Parameters
        ----------
        trajectory : pd.DataFrame
            Execution trajectory
            
        Returns
        -------
        dict
            Cost components
        """
        trade_sizes = trajectory['trade_size'].values[:-1]
        holdings = trajectory['holdings'].values[:-1]
        tau = self.T / (len(trajectory) - 1)
        
        # Permanent impact cost
        permanent_cost = self.gamma * np.sum(trade_sizes)**2 / 2
        
        # Temporary impact cost
        temporary_cost = self.eta * np.sum(trade_sizes**2)
        
        # Timing risk (variance)
        timing_risk = self.sigma**2 * tau * np.sum(holdings**2)
        
        # Total expected cost
        total_cost = permanent_cost + temporary_cost + self.lambda_risk * timing_risk
        
        return {
            'permanent_cost': permanent_cost,
            'temporary_cost': temporary_cost,
            'timing_risk': timing_risk,
            'total_expected_cost': total_cost
        }


class LinearPriceImpactModel:
    """
    Linear price impact model.
    
    Models price impact as linear function of trade size.
    """
    
    def __init__(self, permanent_coef: float = 0.1, temporary_coef: float = 0.05):
        """
        Initialize linear price impact model.
        
        Parameters
        ----------
        permanent_coef : float
            Permanent impact coefficient
        temporary_coef : float
            Temporary impact coefficient
        """
        self.gamma = permanent_coef
        self.eta = temporary_coef
    
    def calculate_impact(self, trade_size: float, direction: int = 1) -> Dict[str, float]:
        """
        Calculate price impact of a trade.
        
        Parameters
        ----------
        trade_size : float
            Size of trade
        direction : int
            1 for buy, -1 for sell
            
        Returns
        -------
        dict
            Impact components
        """
        permanent_impact = direction * self.gamma * trade_size
        temporary_impact = direction * self.eta * trade_size
        
        return {
            'permanent_impact': permanent_impact,
            'temporary_impact': temporary_impact,
            'total_impact': permanent_impact + temporary_impact
        }
    
    def estimate_from_data(
        self,
        trade_sizes: pd.Series,
        price_changes: pd.Series,
        temporary_horizon: int = 5
    ) -> Dict[str, float]:
        """
        Estimate impact parameters from historical data.
        
        Parameters
        ----------
        trade_sizes : pd.Series
            Historical trade sizes
        price_changes : pd.Series
            Corresponding price changes
        temporary_horizon : int
            Periods to measure temporary impact reversal
            
        Returns
        -------
        dict
            Estimated parameters
        """
        # Permanent impact: long-term price change per unit traded
        long_term_changes = price_changes.rolling(window=temporary_horizon).mean()
        self.gamma = (long_term_changes / trade_sizes).mean()
        
        # Temporary impact: short-term deviation from permanent
        immediate_changes = price_changes
        self.eta = ((immediate_changes - long_term_changes) / trade_sizes).mean()
        
        return {
            'permanent_coef': self.gamma,
            'temporary_coef': self.eta
        }


class KyleModel:
    """
    Kyle's lambda model for market impact.
    
    Models price impact based on order flow and liquidity.
    Reference: Kyle (1985)
    """
    
    def __init__(self, kyle_lambda: Optional[float] = None):
        """
        Initialize Kyle model.
        
        Parameters
        ----------
        kyle_lambda : float, optional
            Kyle's lambda (price impact coefficient)
        """
        self.lambda_kyle = kyle_lambda
    
    def estimate_lambda(
        self,
        order_flow: pd.Series,
        price_changes: pd.Series
    ) -> float:
        """
        Estimate Kyle's lambda from data.
        
        Parameters
        ----------
        order_flow : pd.Series
            Signed order flow (positive for buys)
        price_changes : pd.Series
            Corresponding price changes
            
        Returns
        -------
        float
            Estimated lambda
        """
        # Kyle's lambda: E[Δp | q] = lambda * q
        # Estimate via regression
        from scipy.stats import linregress
        
        slope, _, _, _, _ = linregress(order_flow, price_changes)
        self.lambda_kyle = slope
        
        return self.lambda_kyle
    
    def calculate_price_impact(self, order_flow: float) -> float:
        """
        Calculate price impact for given order flow.
        
        Parameters
        ----------
        order_flow : float
            Signed order flow
            
        Returns
        -------
        float
            Expected price impact
        """
        if self.lambda_kyle is None:
            raise ValueError("Kyle's lambda not set. Call estimate_lambda first.")
        
        return self.lambda_kyle * order_flow


class OptimalExecutionSolver:
    """
    General optimal execution solver using numerical optimization.
    """
    
    def __init__(
        self,
        total_quantity: int,
        num_periods: int,
        price_impact_fn,
        risk_aversion: float = 1.0,
        volatility: float = 0.02
    ):
        """
        Initialize optimal execution solver.
        
        Parameters
        ----------
        total_quantity : int
            Total quantity to execute
        num_periods : int
            Number of periods
        price_impact_fn : callable
            Function that calculates price impact given trade size
        risk_aversion : float
            Risk aversion parameter
        volatility : float
            Price volatility per period
        """
        self.X = total_quantity
        self.N = num_periods
        self.impact_fn = price_impact_fn
        self.lambda_risk = risk_aversion
        self.sigma = volatility
    
    def objective(self, trade_schedule: np.ndarray) -> float:
        """
        Objective function: minimize cost + risk penalty.
        
        Parameters
        ----------
        trade_schedule : np.ndarray
            Trade sizes for each period
            
        Returns
        -------
        float
            Total cost
        """
        # Calculate impact costs
        impact_cost = sum([self.impact_fn(q) for q in trade_schedule])
        
        # Calculate holdings over time
        holdings = self.X - np.cumsum(trade_schedule)
        
        # Timing risk
        timing_risk = self.sigma**2 * np.sum(holdings**2)
        
        # Total cost
        total_cost = impact_cost + self.lambda_risk * timing_risk
        
        return total_cost
    
    def solve(self) -> pd.DataFrame:
        """
        Solve for optimal execution schedule.
        
        Returns
        -------
        pd.DataFrame
            Optimal execution schedule
        """
        # Initial guess: uniform trading
        x0 = np.ones(self.N) * self.X / self.N
        
        # Constraint: sum of trades = total quantity
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - self.X}
        
        # Bounds: non-negative trades
        bounds = [(0, self.X) for _ in range(self.N)]
        
        # Optimize
        result = minimize(
            self.objective,
            x0,
            method='SLSQP',
            constraints=constraints,
            bounds=bounds
        )
        
        if not result.success:
            print(f"Optimization warning: {result.message}")
        
        # Create schedule DataFrame
        schedule = pd.DataFrame({
            'period': range(self.N),
            'trade_size': result.x,
            'cumulative_traded': np.cumsum(result.x),
            'remaining': self.X - np.cumsum(result.x)
        })
        
        return schedule


def compare_execution_strategies(
    total_quantity: int,
    num_periods: int,
    volatility: float = 0.02,
    impact_params: Dict[str, float] = None
) -> pd.DataFrame:
    """
    Compare different execution strategies.
    
    Parameters
    ----------
    total_quantity : int
        Total quantity to execute
    num_periods : int
        Number of periods
    volatility : float
        Price volatility
    impact_params : dict
        Price impact parameters
        
    Returns
    -------
    pd.DataFrame
        Comparison of strategies
    """
    if impact_params is None:
        impact_params = {'permanent': 0.1, 'temporary': 0.05}
    
    results = []
    
    # Strategy 1: Uniform (TWAP-like)
    uniform_trades = np.ones(num_periods) * total_quantity / num_periods
    uniform_cost = sum([impact_params['permanent'] * q + impact_params['temporary'] * q**2 
                       for q in uniform_trades])
    results.append({'strategy': 'Uniform', 'total_cost': uniform_cost})
    
    # Strategy 2: Front-loaded
    front_loaded = np.array([total_quantity * (2 * i / (num_periods * (num_periods + 1))) 
                             for i in range(num_periods, 0, -1)])
    front_cost = sum([impact_params['permanent'] * q + impact_params['temporary'] * q**2 
                     for q in front_loaded])
    results.append({'strategy': 'Front-loaded', 'total_cost': front_cost})
    
    # Strategy 3: Back-loaded
    back_loaded = np.array([total_quantity * (2 * i / (num_periods * (num_periods + 1))) 
                           for i in range(1, num_periods + 1)])
    back_cost = sum([impact_params['permanent'] * q + impact_params['temporary'] * q**2 
                    for q in back_loaded])
    results.append({'strategy': 'Back-loaded', 'total_cost': back_cost})
    
    return pd.DataFrame(results)


def simulate_execution_with_impact(
    execution_schedule: pd.DataFrame,
    initial_price: float,
    volatility: float,
    impact_model: LinearPriceImpactModel,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Simulate execution with price impact and random price movements.
    
    Parameters
    ----------
    execution_schedule : pd.DataFrame
        Execution schedule with trade_size column
    initial_price : float
        Initial price
    volatility : float
        Price volatility per period
    impact_model : LinearPriceImpactModel
        Price impact model
    seed : int, optional
        Random seed
        
    Returns
    -------
    pd.DataFrame
        Simulation results
    """
    if seed is not None:
        np.random.seed(seed)
    
    num_periods = len(execution_schedule)
    prices = [initial_price]
    realized_costs = []
    
    current_price = initial_price
    
    for _, row in execution_schedule.iterrows():
        trade_size = row['trade_size']
        
        # Random price movement
        price_change = np.random.normal(0, volatility)
        current_price += price_change
        
        # Add impact
        impact = impact_model.calculate_impact(trade_size, direction=1)
        execution_price = current_price + impact['total_impact']
        
        # Update price with permanent impact
        current_price += impact['permanent_impact']
        
        prices.append(current_price)
        realized_costs.append((execution_price - initial_price) * trade_size)
    
    results = execution_schedule.copy()
    results['price'] = prices[:-1]
    results['realized_cost'] = realized_costs
    
    return results
