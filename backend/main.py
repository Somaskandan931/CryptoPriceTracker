from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging
import traceback

from services.predictor import predict_price, get_prediction_confidence
from services.coins import get_all_coins, is_coin_available
from services.retrain import retrain_coin, retrain_all_coins
from services.live_price import get_live_price, get_multiple_prices
from services.risk_metrics import calculate_all_risk_metrics
from explainability.shap_explainer import explain_prediction, get_feature_importance
import pandas as pd
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger( __name__ )

# Initialize FastAPI app
app = FastAPI(
    title="Indian Market Prediction API",
    description="AI-powered Indian stock market, indices, and commodity price prediction with quantile regression",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get( "/" )
def root () :
    """API health check endpoint."""
    return {
        "status" : "online",
        "message" : "🇮🇳 Indian Market Prediction API",
        "version" : "1.0.0",
        "features" : [
            "Multi-day predictions (1-30 days)",
            "Quantile regression (Q10, Q50, Q90)",
            "INR currency support",
            "50+ Indian stocks, indices & commodities"
        ],
        "markets" : [
            "Nifty 50 & Bank Nifty",
            "BSE Sensex",
            "Top Indian stocks (IT, Banking, Energy, Auto, Pharma, FMCG)",
            "Commodities (Gold, Silver, Crude Oil)",
            "Currency pairs (USD/INR, EUR/INR, GBP/INR)"
        ]
    }


@app.get( "/assets" )
def list_assets () :
    """Get list of all available Indian market assets."""
    try :
        assets = get_all_coins()
        logger.info( f"📋 Retrieved {len( assets )} assets" )

        # Categorize assets for better organization
        categories = {
            "indices" : ["nifty50", "banknifty", "sensex"],
            "it" : ["tcs", "infosys", "wipro", "hcltech", "techm"],
            "banking" : ["hdfcbank", "icicibank", "sbi", "kotakbank", "axisbank", "bajajfinance"],
            "energy" : ["reliance", "ongc", "bpcl", "ioc", "adanigreen"],
            "automobile" : ["maruti", "tatamotors", "mahindra", "bajajauto", "heromotoco"],
            "pharma" : ["sunpharma", "drreddy", "cipla", "divislab"],
            "fmcg" : ["hul", "itc", "nestle", "britannia"],
            "metals" : ["tatasteel", "hindalco", "coalindia", "vedanta"],
            "commodities" : ["gold", "silver", "crudeoil"],
            "currency" : ["usdinr", "gbpinr", "eurinr"]
        }

        # Create detailed asset list
        asset_list = []
        for asset in assets :
            asset_info = {
                "id" : asset,
                "name" : asset.replace( "-", " " ).title(),
                "symbol" : asset.upper()
            }

            # Add category
            for cat, items in categories.items() :
                if asset in items :
                    asset_info["category"] = cat
                    break

            asset_list.append( asset_info )

        return {
            "assets" : assets,
            "detailed" : asset_list,
            "categories" : categories,
            "count" : len( assets )
        }
    except Exception as e :
        logger.error( f"❌ Error fetching assets: {e}" )
        logger.error( traceback.format_exc() )
        raise HTTPException( status_code=500, detail=str( e ) )


@app.get( "/predict/{asset}" )
def predict (
        asset: str,
        days_ahead: int = Query(
            default=1,
            ge=1,
            le=30,
            description="Number of days ahead to predict (1-30)"
        )
) :
    """
    Get price predictions for an Indian market asset.

    Parameters:
    - asset: Asset identifier (e.g., 'nifty50', 'reliance', 'gold', 'usdinr')
    - days_ahead: Days into the future to predict (1-30, default: 1)

    Returns quantile predictions (q10, q50, q90) representing
    conservative, expected, and optimistic scenarios.
    """
    try :
        logger.info( f"🔮 Prediction requested for: {asset}, days_ahead: {days_ahead}" )

        # Check if asset is available
        if not is_coin_available( asset ) :
            logger.warning( f"⚠️ Asset '{asset}' not found" )
            raise HTTPException(
                status_code=404,
                detail=f"Asset '{asset}' not found. Use /assets to see available assets."
            )

        logger.info( f"✅ Asset '{asset}' is available, generating prediction..." )

        # Get prediction
        prediction = predict_price( asset, days_ahead=days_ahead )
        logger.info( f"✅ Prediction successful for {asset} ({days_ahead} days ahead)" )

        # Get confidence metrics
        try :
            confidence = get_prediction_confidence( asset )
            if confidence :
                prediction["confidence"] = confidence
                logger.info( f"✅ Confidence metrics added for {asset}" )
        except Exception as conf_error :
            logger.warning( f"⚠️ Could not get confidence for {asset}: {conf_error}" )

        # Add metadata
        prediction["prediction_metadata"] = {
            "days_ahead" : days_ahead,
            "model_version" : "1.0.0",
            "prediction_type" : "quantile_regression",
            "currency" : "INR" if asset not in ['gold', 'silver', 'crudeoil'] else "USD"
        }

        return prediction

    except ValueError as e :
        error_msg = str( e )
        logger.error( f"❌ ValueError for {asset}: {error_msg}" )
        raise HTTPException( status_code=400, detail=error_msg )

    except FileNotFoundError as e :
        error_msg = str( e )
        logger.error( f"❌ FileNotFoundError for {asset}: {error_msg}" )
        raise HTTPException( status_code=404, detail=f"Required file not found for {asset}: {error_msg}" )

    except Exception as e :
        error_msg = str( e )
        logger.error( f"❌ Unexpected error for {asset}: {error_msg}" )
        logger.error( f"Full traceback:\n{traceback.format_exc()}" )
        raise HTTPException( status_code=500, detail=error_msg )


@app.get( "/live/{asset}" )
def live_price ( asset: str ) :
    """Get current live price for an Indian market asset."""
    try :
        logger.info( f"💰 Live price requested for: {asset}" )
        price = get_live_price( asset )

        # Determine currency
        currency = "INR"
        if asset in ['gold', 'silver', 'crudeoil'] :
            currency = "USD"
        elif asset in ['usdinr', 'gbpinr', 'eurinr'] :
            currency = "INR per foreign unit"

        return {
            "asset" : asset,
            "price" : price,
            "currency" : currency
        }
    except Exception as e :
        logger.error( f"❌ Live price error for {asset}: {e}" )
        logger.error( traceback.format_exc() )
        raise HTTPException( status_code=500, detail=str( e ) )


@app.get( "/risk/{asset}" )
def risk_analysis ( asset: str ) :
    """Get risk metrics for an Indian market asset."""
    try :
        logger.info( f"📊 Risk analysis requested for: {asset}" )
        data_path = os.path.join(
            "C:/Users/somas/PycharmProjects/Crypto Price Tracker/backend/data",
            asset,
            f"{asset}.csv"
        )

        if not os.path.exists( data_path ) :
            logger.warning( f"⚠️ Data file not found: {data_path}" )
            raise HTTPException(
                status_code=404,
                detail=f"Data not found for '{asset}'"
            )

        df = pd.read_csv( data_path )
        prices = df["Close"].values

        metrics = calculate_all_risk_metrics( prices )
        metrics["asset"] = asset

        logger.info( f"✅ Risk analysis complete for {asset}" )
        return metrics

    except Exception as e :
        logger.error( f"❌ Risk analysis error for {asset}: {e}" )
        logger.error( traceback.format_exc() )
        raise HTTPException( status_code=500, detail=str( e ) )


@app.get( "/category/{category}" )
def get_category_assets ( category: str ) :
    """Get all assets in a specific category."""
    categories = {
        "indices" : ["nifty50", "banknifty", "sensex"],
        "it" : ["tcs", "infosys", "wipro", "hcltech", "techm"],
        "banking" : ["hdfcbank", "icicibank", "sbi", "kotakbank", "axisbank", "bajajfinance"],
        "energy" : ["reliance", "ongc", "bpcl", "ioc", "adanigreen"],
        "automobile" : ["maruti", "tatamotors", "mahindra", "bajajauto", "heromotoco"],
        "pharma" : ["sunpharma", "drreddy", "cipla", "divislab"],
        "fmcg" : ["hul", "itc", "nestle", "britannia"],
        "metals" : ["tatasteel", "hindalco", "coalindia", "vedanta"],
        "commodities" : ["gold", "silver", "crudeoil"],
        "currency" : ["usdinr", "gbpinr", "eurinr"]
    }

    if category.lower() not in categories :
        raise HTTPException(
            status_code=404,
            detail=f"Category '{category}' not found. Available: {list( categories.keys() )}"
        )

    return {
        "category" : category,
        "assets" : categories[category.lower()],
        "count" : len( categories[category.lower()] )
    }


@app.get( "/health" )
def health_check () :
    """Comprehensive health check endpoint."""
    try :
        from services.coins import coin_encoder

        health_status = {
            "status" : "healthy",
            "api_version" : "1.0.0",
            "model_loaded" : coin_encoder is not None,
            "available_assets" : len( get_all_coins() ) if coin_encoder else 0,
            "market" : "🇮🇳 Indian Markets",
            "features" : {
                "multi_day_predictions" : True,
                "max_days_ahead" : 30,
                "quantile_regression" : True,
                "risk_analysis" : True,
                "explainability" : True,
                "inr_currency" : True
            }
        }
        return health_status
    except Exception as e :
        logger.error( f"❌ Health check error: {e}" )
        return {
            "status" : "unhealthy",
            "error" : str( e )
        }


if __name__ == "__main__" :
    import uvicorn

    logger.info( "🚀 Starting Indian Market Prediction API..." )
    logger.info( "🇮🇳 Supporting Indian stocks, indices, commodities & currencies" )
    logger.info( "📅 Multi-day prediction support: 1-30 days" )
    logger.info( "💱 Currency: INR" )
    uvicorn.run( app, host="0.0.0.0", port=8000 )