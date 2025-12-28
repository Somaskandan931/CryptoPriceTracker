import numpy as np
from typing import Tuple


def calculate_returns ( prices: np.ndarray ) -> np.ndarray :
    """
    Calculate returns from price series.

    Args:
        prices: Array of prices

    Returns:
        np.ndarray: Array of returns
    """
    prices = np.asarray( prices )
    if len( prices ) < 2 :
        raise ValueError( "Need at least 2 prices to calculate returns" )

    return np.diff( prices ) / prices[:-1]


def var_cvar ( prices: np.ndarray, confidence: float = 0.95 ) -> Tuple[float, float] :
    """
    Calculate Value at Risk (VaR) and Conditional Value at Risk (CVaR).

    VaR: Maximum expected loss at a given confidence level
    CVaR: Expected loss given that VaR threshold is breached

    Args:
        prices: Array of historical prices
        confidence: Confidence level (default: 0.95 for 95%)

    Returns:
        tuple: (VaR, CVaR) both as negative values representing losses
    """
    if not 0 < confidence < 1 :
        raise ValueError( "Confidence must be between 0 and 1" )

    prices = np.asarray( prices )
    returns = calculate_returns( prices )

    # Calculate VaR (at the specified percentile)
    var = np.percentile( returns, (1 - confidence) * 100 )

    # Calculate CVaR (average of returns below VaR)
    cvar = returns[returns <= var].mean()

    return float( var ), float( cvar )


def volatility ( prices: np.ndarray, annualize: bool = False ) -> float :
    """
    Calculate volatility (standard deviation of returns).

    Args:
        prices: Array of historical prices
        annualize: If True, annualize the volatility (assume daily data)

    Returns:
        float: Volatility value
    """
    prices = np.asarray( prices )
    returns = calculate_returns( prices )

    vol = np.std( returns )

    if annualize :
        # Assuming daily data, annualize with sqrt(365)
        vol *= np.sqrt( 365 )

    return float( vol )


def sharpe_ratio ( prices: np.ndarray, risk_free_rate: float = 0.02 ) -> float :
    """
    Calculate Sharpe Ratio (risk-adjusted return).

    Args:
        prices: Array of historical prices
        risk_free_rate: Annual risk-free rate (default: 0.02 for 2%)

    Returns:
        float: Sharpe ratio
    """
    prices = np.asarray( prices )
    returns = calculate_returns( prices )

    # Annualize returns and volatility
    annual_return = np.mean( returns ) * 365
    annual_vol = volatility( prices, annualize=True )

    if annual_vol == 0 :
        return 0.0

    return float( (annual_return - risk_free_rate) / annual_vol )


def max_drawdown ( prices: np.ndarray ) -> float :
    """
    Calculate maximum drawdown (largest peak-to-trough decline).

    Args:
        prices: Array of historical prices

    Returns:
        float: Maximum drawdown as a negative percentage
    """
    prices = np.asarray( prices )

    # Calculate cumulative maximum
    cum_max = np.maximum.accumulate( prices )

    # Calculate drawdown at each point
    drawdown = (prices - cum_max) / cum_max

    return float( np.min( drawdown ) )


def calculate_all_risk_metrics ( prices: np.ndarray, confidence: float = 0.95 ) -> dict :
    """
    Calculate comprehensive risk metrics for a price series.

    Args:
        prices: Array of historical prices
        confidence: Confidence level for VaR/CVaR

    Returns:
        dict: Dictionary containing all risk metrics
    """
    var, cvar = var_cvar( prices, confidence )

    return {
        "var" : round( var * 100, 2 ),  # As percentage
        "cvar" : round( cvar * 100, 2 ),  # As percentage
        "volatility" : round( volatility( prices, annualize=True ) * 100, 2 ),  # As percentage
        "sharpe_ratio" : round( sharpe_ratio( prices ), 2 ),
        "max_drawdown" : round( max_drawdown( prices ) * 100, 2 )  # As percentage
    }