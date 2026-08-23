"""
FastAPI API for code file risk prediction.
S5 ML Service - Prediction API with SHAP explainability.
"""
import os
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Eureka Client
try:
    import py_eureka_client.eureka_client as eureka_client
    EUREKA_ENABLED = os.getenv("EUREKA_ENABLED", "true").lower() == "true"
except ImportError:
    EUREKA_ENABLED = False

# Global model and metadata
MODEL_PATH = os.environ.get("MODEL_PATH", "/app/models")
model = None
feature_names = None
shap_explainer = None


def load_model_sync():
    """Load the trained model and feature names."""
    global model, feature_names, shap_explainer
    
    model_file = os.path.join(MODEL_PATH, "model.pkl")
    feature_file = os.path.join(MODEL_PATH, "feature_names.pkl")
    explainer_file = os.path.join(MODEL_PATH, "shap_explainer.pkl")
    
    if not os.path.exists(model_file):
        logger.warning(f"Model not found at {model_file}. Run training first via /api/v1/train")
        return
    
    model = joblib.load(model_file)
    logger.info(f"Model loaded from {model_file}")
    
    if os.path.exists(feature_file):
        feature_names = joblib.load(feature_file)
        logger.info(f"Loaded {len(feature_names)} feature names")
    
    if os.path.exists(explainer_file):
        try:
            shap_explainer = joblib.load(explainer_file)
            logger.info("SHAP explainer loaded")
        except:
            logger.warning("Could not load SHAP explainer")


async def register_eureka():
    """Register service with Eureka server."""
    if not EUREKA_ENABLED:
        logger.info("Eureka registration disabled")
        return
    
    eureka_server = os.getenv("EUREKA_URI", "http://eureka:eureka123@localhost:8761/eureka/")
    service_name = "ML-SERVICE"
    instance_port = int(os.getenv("PORT", "8001"))
    instance_host = os.getenv("HOSTNAME", "localhost")
    
    try:
        await eureka_client.init_async(
            eureka_server=eureka_server,
            app_name=service_name,
            instance_port=instance_port,
            instance_host=instance_host,
            renewal_interval_in_secs=30,
            duration_in_secs=90
        )
        logger.info(f"Registered {service_name} with Eureka at {eureka_server}")
    except Exception as e:
        logger.warning(f"Failed to register with Eureka: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    load_model_sync()
    await register_eureka()
    yield
    if EUREKA_ENABLED:
        try:
            await eureka_client.stop_async()
            logger.info("Unregistered from Eureka")
        except Exception as e:
            logger.warning(f"Error stopping Eureka client: {e}")


# Initialize FastAPI app
app = FastAPI(
    title="S5 ML Service - Code Risk Prediction",
    description="Predict code file risk based on software metrics from S4",
    version="2.0.0",
    lifespan=lifespan
)


# Pydantic models
class PredictionInput(BaseModel):
    """Input for single prediction - accepts feature dict."""
    class_name: Optional[str] = "unknown"
    repository_id: Optional[str] = None
    features: Dict[str, float]


class BatchPredictionInput(BaseModel):
    """Input for batch predictions."""
    items: List[PredictionInput]


class PredictionOutput(BaseModel):
    """Output of prediction."""
    class_name: str
    risk_score: float
    risk_level: str
    prediction: int
    uncertainty: Optional[float] = None
    shap_values: Optional[Dict[str, float]] = None
    explanation: Optional[str] = None


class BatchPredictionOutput(BaseModel):
    """Output for batch predictions."""
    predictions: List[PredictionOutput]
    top_k: Optional[List[PredictionOutput]] = None


class TrainResponse(BaseModel):
    """Response from training endpoint."""
    status: str
    message: str
    accuracy: Optional[float] = None
    num_features: Optional[int] = None


@app.get("/")
def root():
    """Root endpoint."""
    return {"status": "healthy", "service": "S5 ML Service"}


@app.get("/health")
def health():
    """Health check endpoint."""
    model_loaded = model is not None
    return {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "num_features": len(feature_names) if feature_names else 0
    }


@app.get("/api/v1/features")
def get_features():
    """Get list of expected feature names."""
    if feature_names is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"features": feature_names, "count": len(feature_names)}


@app.post("/api/v1/train", response_model=TrainResponse)
def train_model():
    """Trigger model training from S4 data."""
    global model, feature_names, shap_explainer
    
    try:
        from src.train_model import main as run_training
        run_training()
        
        # Reload model after training
        model_file = os.path.join(MODEL_PATH, "model.pkl")
        feature_file = os.path.join(MODEL_PATH, "feature_names.pkl")
        
        if os.path.exists(model_file):
            model = joblib.load(model_file)
            if os.path.exists(feature_file):
                feature_names = joblib.load(feature_file)
            
            return TrainResponse(
                status="success",
                message="Model trained successfully",
                num_features=len(feature_names) if feature_names else 0
            )
        else:
            return TrainResponse(
                status="error",
                message="Training completed but model file not found"
            )
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return TrainResponse(
            status="error",
            message=str(e)
        )


@app.post("/api/v1/predict", response_model=PredictionOutput)
def predict(input_data: PredictionInput):
    """Predict risk for a single class."""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Call /api/v1/train first."
        )
    
    # Build feature vector from input
    features_dict = input_data.features
    
    # Create feature array matching expected order
    feature_vector = []
    missing_features = []
    
    for fname in feature_names:
        if fname in features_dict:
            feature_vector.append(features_dict[fname])
        else:
            feature_vector.append(0.0)  # Default to 0 for missing features
            missing_features.append(fname)
    
    if missing_features and len(missing_features) < len(feature_names) // 2:
        logger.debug(f"Missing features defaulted to 0: {missing_features[:5]}...")
    
    # Predict
    features_array = np.array([feature_vector])
    prediction = int(model.predict(features_array)[0])
    probabilities = model.predict_proba(features_array)[0]
    
    risk_score = float(probabilities[1]) if len(probabilities) > 1 else float(prediction)
    
    # Determine risk level
    if risk_score > 0.7:
        risk_level = "high"
    elif risk_score >= 0.3:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    # Calculate uncertainty
    uncertainty = 1.0 - abs(probabilities[0] - probabilities[1]) if len(probabilities) == 2 else 0.5
    
    # Compute SHAP values if explainer available
    shap_values_dict = None
    if shap_explainer is not None:
        try:
            shap_vals = shap_explainer.shap_values(features_array)
            if isinstance(shap_vals, list):
                shap_vals = shap_vals[1]  # Class 1 (risky)
            shap_values_dict = dict(zip(feature_names, shap_vals[0].tolist()))
            # Keep only top 10 by absolute value
            sorted_shap = sorted(shap_values_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
            shap_values_dict = dict(sorted_shap)
        except Exception as e:
            logger.warning(f"Could not compute SHAP: {e}")
    
    # Generate explanation
    explanation = _generate_explanation(risk_score, risk_level, features_dict, shap_values_dict)
    
    return PredictionOutput(
        class_name=input_data.class_name or "unknown",
        risk_score=risk_score,
        risk_level=risk_level,
        prediction=prediction,
        uncertainty=uncertainty,
        shap_values=shap_values_dict,
        explanation=explanation
    )


@app.post("/api/v1/predict/batch", response_model=BatchPredictionOutput)
def predict_batch(input_data: BatchPredictionInput, top_k: int = 10):
    """Predict risk for multiple classes and return top-K risky ones."""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Call /api/v1/train first."
        )
    
    predictions = []
    for item in input_data.items:
        pred = predict(item)
        predictions.append(pred)
    
    # Sort by risk score descending
    sorted_predictions = sorted(predictions, key=lambda x: x.risk_score, reverse=True)
    top_k_list = sorted_predictions[:top_k]
    
    return BatchPredictionOutput(
        predictions=predictions,
        top_k=top_k_list
    )


def _generate_explanation(
    risk_score: float, 
    risk_level: str, 
    features: Dict[str, float],
    shap_values: Optional[Dict[str, float]] = None
) -> str:
    """Generate human-readable explanation."""
    factors = []
    
    # Use SHAP values if available
    if shap_values:
        top_factors = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        for feat, val in top_factors:
            if abs(val) > 0.01:
                direction = "increases" if val > 0 else "decreases"
                factors.append(f"{feat} {direction} risk ({val:.3f})")
    
    # Fallback to feature values
    if not factors:
        if features.get('complexity', 0) > 5:
            factors.append(f"High complexity ({features.get('complexity', 0):.1f})")
        if features.get('churn', 0) > 50:
            factors.append(f"High code churn ({features.get('churn', 0):.0f})")
        if features.get('bug_fix_proximity', 0) > 200:
            factors.append("Recent bug-fix activity")
    
    if factors:
        return f"Risk factors: {', '.join(factors)}"
    return f"Overall risk: {risk_level} (score: {risk_score:.2f})"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
