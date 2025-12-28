import subprocess
import os
from typing import Dict


def retrain_coin ( coin: str ) -> Dict[str, str] :
    """
    Trigger retraining for a specific cryptocurrency.

    This spawns a background process to retrain the model without blocking
    the API response.

    Args:
        coin: Cryptocurrency identifier

    Returns:
        dict: Status message
    """
    script_path = "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/model/train_model.py"

    if not os.path.exists( script_path ) :
        return {
            "status" : "error",
            "message" : f"Training script not found at {script_path}"
        }

    try :
        # Start training process in background
        process = subprocess.Popen(
            ["python", script_path, coin],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True  # Detach from parent process
        )

        return {
            "status" : "started",
            "message" : f"Retraining started for {coin}",
            "process_id" : process.pid
        }

    except Exception as e :
        return {
            "status" : "error",
            "message" : f"Failed to start retraining: {str( e )}"
        }


def retrain_all_coins () -> Dict[str, str] :
    """
    Trigger retraining for all cryptocurrencies.

    Returns:
        dict: Status message
    """
    script_path = "backend/model/train_model.py"

    if not os.path.exists( script_path ) :
        return {
            "status" : "error",
            "message" : f"Training script not found at {script_path}"
        }

    try :
        # Start full retraining process in background
        process = subprocess.Popen(
            ["python", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )

        return {
            "status" : "started",
            "message" : "Full model retraining started",
            "process_id" : process.pid
        }

    except Exception as e :
        return {
            "status" : "error",
            "message" : f"Failed to start retraining: {str( e )}"
        }


def check_training_status ( process_id: int ) -> Dict[str, str] :
    """
    Check if a training process is still running.

    Args:
        process_id: Process ID to check

    Returns:
        dict: Training status
    """
    try :
        # Check if process exists
        os.kill( process_id, 0 )
        return {
            "status" : "running",
            "process_id" : process_id
        }
    except OSError :
        return {
            "status" : "completed",
            "process_id" : process_id
        }