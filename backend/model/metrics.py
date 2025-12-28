import numpy as np
from typing import Union


def rmse ( y_true: np.ndarray, y_pred: np.ndarray ) -> float :
    """
    Calculate Root Mean Squared Error.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        float: RMSE value
    """
    y_true = np.asarray( y_true )
    y_pred = np.asarray( y_pred )

    if len( y_true ) != len( y_pred ) :
        raise ValueError( "Input arrays must have the same length" )

    return float( np.sqrt( np.mean( (y_true - y_pred) ** 2 ) ) )


def mape ( y_true: np.ndarray, y_pred: np.ndarray ) -> float :
    """
    Calculate Mean Absolute Percentage Error.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        float: MAPE value as percentage
    """
    y_true = np.asarray( y_true )
    y_pred = np.asarray( y_pred )

    if len( y_true ) != len( y_pred ) :
        raise ValueError( "Input arrays must have the same length" )

    # Avoid division by zero
    mask = y_true != 0
    if not np.any( mask ) :
        raise ValueError( "Cannot calculate MAPE when all true values are zero" )

    return float( np.mean( np.abs( (y_true[mask] - y_pred[mask]) / y_true[mask] ) ) * 100 )


def mae ( y_true: np.ndarray, y_pred: np.ndarray ) -> float :
    """
    Calculate Mean Absolute Error.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        float: MAE value
    """
    y_true = np.asarray( y_true )
    y_pred = np.asarray( y_pred )

    if len( y_true ) != len( y_pred ) :
        raise ValueError( "Input arrays must have the same length" )

    return float( np.mean( np.abs( y_true - y_pred ) ) )


def r2_score ( y_true: np.ndarray, y_pred: np.ndarray ) -> float :
    """
    Calculate R-squared (coefficient of determination).

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        float: R² score
    """
    y_true = np.asarray( y_true )
    y_pred = np.asarray( y_pred )

    if len( y_true ) != len( y_pred ) :
        raise ValueError( "Input arrays must have the same length" )

    ss_res = np.sum( (y_true - y_pred) ** 2 )
    ss_tot = np.sum( (y_true - np.mean( y_true )) ** 2 )

    if ss_tot == 0 :
        return 0.0

    return float( 1 - (ss_res / ss_tot) )


def evaluate_predictions ( y_true: np.ndarray, y_pred: np.ndarray ) -> dict :
    """
    Calculate all evaluation metrics.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        dict: Dictionary containing all metrics
    """
    return {
        "rmse" : rmse( y_true, y_pred ),
        "mae" : mae( y_true, y_pred ),
        "mape" : mape( y_true, y_pred ),
        "r2" : r2_score( y_true, y_pred )
    }