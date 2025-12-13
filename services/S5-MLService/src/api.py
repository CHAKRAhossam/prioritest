"""
FastAPI API for code file risk prediction.
MTP-37: Production API with POST /api/v1/predict endpoint.
"""
import os
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

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
    """
    Input features for prediction aligned with architecture specification.
    
    Format from architecture spec:
    {
      "class_name": "com.example.UserService",
      "repository_id": "repo_12345",
      "features": {
        "loc": 150,
        "cyclomatic_complexity": 12,
        "churn": 0.15,
        "num_authors": 3,
        "bug_fix_proximity": 0.8,
        "current_line_coverage": 0.85,
        "test_debt_score": 0.2
      }
    }
    """
    class_name: Optional[str] = None
    repository_id: Optional[str] = None
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
    """
    Output of prediction aligned with architecture specification.
    
    Format from architecture spec:
    {
      "class_name": "com.example.UserService",
      "risk_score": 0.75,
      "risk_level": "high",
      "uncertainty": 0.12,
      "top_k_recommendations": [...],
      "shap_values": {...},
      "explanation": "..."
    }
    """
    class_name: str
    risk_score: float
    risk_level: str
    uncertainty: Optional[float] = None
    top_k_recommendations: Optional[List[dict]] = None
    shap_values: Optional[dict] = None
    explanation: Optional[str] = None


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
    
    # Class name (use actual class name if provided, otherwise "risky"/"safe")
    class_name = getattr(input_data, 'class_name', None) or ("risky" if prediction == 1 else "safe")
    
    # Calculate uncertainty (simplified: based on probability distribution)
    uncertainty = abs(probabilities[0] - probabilities[1]) / 2.0 if len(probabilities) == 2 else 0.0
    
    # Generate explanation
    explanation = _generate_explanation(risk_score, risk_level, input_data)
    
    # SHAP values (placeholder - would need actual SHAP calculation)
    shap_values = _calculate_shap_values(input_data, risk_score)
    
    # Top K recommendations (simplified - would come from batch prediction)
    top_k_recommendations = [{
        "class_name": class_name,
        "risk_score": risk_score,
        "priority": 1
    }]
    
    return PredictionOutput(
        class_name=class_name,
        risk_score=risk_score,
        risk_level=risk_level,
        uncertainty=uncertainty,
        top_k_recommendations=top_k_recommendations,
        shap_values=shap_values,
        explanation=explanation
    )


def _generate_explanation(risk_score: float, risk_level: str, input_data: PredictionInput) -> str:
    """Generate human-readable explanation for the prediction."""
    factors = []
    
    if input_data.complexity > 10:
        factors.append(f"High complexity ({input_data.complexity:.1f})")
    if input_data.bug_fix_proximity > 0.7:
        factors.append("High proximity to bug-fix commits")
    if input_data.churn > 50:
        factors.append(f"High code churn ({input_data.churn:.0f})")
    
    if factors:
        return f"High risk due to: {', '.join(factors)}"
    else:
        return f"Risk level: {risk_level} (score: {risk_score:.2f})"


def _calculate_shap_values(input_data: PredictionInput, risk_score: float) -> dict:
    """
    Calculate SHAP values for feature contributions.
    Placeholder implementation - would need actual SHAP library integration.
    """
    # Simplified: proportional contribution based on feature values
    total_impact = abs(input_data.complexity) + abs(input_data.churn) + abs(input_data.bug_fix_proximity)
    
    if total_impact > 0:
        return {
            "loc": round(input_data.lines_modified / max(total_impact, 1) * risk_score, 3),
            "cyclomatic_complexity": round(input_data.complexity / max(total_impact, 1) * risk_score, 3),
            "churn": round(input_data.churn / max(total_impact, 1) * risk_score, 3),
            "bug_fix_proximity": round(input_data.bug_fix_proximity / max(total_impact, 1) * risk_score, 3)
        }
    return {}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
