"""
FastAPI API for code file risk prediction.
MTP-37: Production API with POST /api/v1/predict endpoint.
"""
import os
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Initialize FastAPI app
app = FastAPI(
    title="ML Service - Code Risk Prediction",
    description="Predict code file risk based on software metrics",
    version="1.0.0"
)

# Load model and feature names at startup
MODEL_PATH = "models/model.pkl"
FEATURE_NAMES_PATH = "models/feature_names.pkl"

model = None
feature_names = None


@app.on_event("startup")
def load_model():
    """Load the trained model and feature names at startup."""
    global model, feature_names
    
    if not os.path.exists(MODEL_PATH):
        print(f"Warning: Model not found at {MODEL_PATH}. Run train_model.py first.")
        return
    
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")
    
    if os.path.exists(FEATURE_NAMES_PATH):
        feature_names = joblib.load(FEATURE_NAMES_PATH)
        print(f"Feature names loaded: {feature_names}")


# Pydantic models for request/response
class PredictionInput(BaseModel):
    """Input features for prediction."""
    lines_modified: float
    complexity: float
    author_type_Bot: float = 0.0
    author_type_Junior: float = 0.0
    author_type_Senior: float = 0.0
    file_type_java: float = 0.0
    file_type_py: float = 0.0
    file_type_xml: float = 0.0
    churn: float
    num_authors: float
    bug_fix_proximity: float

    class Config:
        # Allow field names with dots/underscores
        populate_by_name = True


class PredictionOutput(BaseModel):
    """Output of prediction."""
    class_name: str
    risk_score: float
    risk_level: str


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ML Service"}


@app.get("/health")
def health():
    """Health check endpoint."""
    model_loaded = model is not None
    return {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded
    }


@app.post("/api/v1/predict", response_model=PredictionOutput)
def predict(input_data: PredictionInput):
    """
    Predict code file risk.
    
    Returns:
        - class_name: "risky" or "safe"
        - risk_score: probability of being risky (0.0 to 1.0)
        - risk_level: "low", "medium", or "high" based on risk_score
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run train_model.py first."
        )
    
    # Prepare features in the correct order (must match train.csv columns)
    features = [
        input_data.lines_modified,
        input_data.complexity,
        input_data.author_type_Bot,
        input_data.author_type_Junior,
        input_data.author_type_Senior,
        input_data.file_type_java,
        input_data.file_type_py,
        input_data.file_type_xml,
        input_data.churn,
        input_data.num_authors,
        input_data.bug_fix_proximity,
    ]
    
    # Get prediction and probability
    prediction = model.predict([features])[0]
    probabilities = model.predict_proba([features])[0]
    
    # risk_score is the probability of class 1 (risky)
    risk_score = float(probabilities[1])
    
    # Determine risk level based on PDF specification (3 levels)
    if risk_score > 0.7:
        risk_level = "high"
    elif risk_score >= 0.3:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    # Class name
    class_name = "risky" if prediction == 1 else "safe"
    
    return PredictionOutput(
        class_name=class_name,
        risk_score=risk_score,
        risk_level=risk_level
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
