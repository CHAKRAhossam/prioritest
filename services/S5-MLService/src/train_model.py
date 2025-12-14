"""
Train XGBoost/LightGBM model for code risk classification.
Loads data from S4 (PretraitementFeatures) and outputs trained models.

Features:
- XGBoost and LightGBM classifiers
- SHAP for model explainability
- Model persistence to /app/models
"""
import os
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score
)
import shap
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data(data_path: str) -> tuple:
    """Load train and test data from S4 output."""
    train_path = os.path.join(data_path, "processed", "train.csv")
    test_path = os.path.join(data_path, "processed", "test.csv")
    
    if not os.path.exists(train_path):
        logger.error(f"Training data not found at {train_path}")
        raise FileNotFoundError(f"Training data not found at {train_path}")
    
    logger.info(f"Loading training data from {train_path}")
    train_df = pd.read_csv(train_path)
    
    test_df = None
    if os.path.exists(test_path):
        logger.info(f"Loading test data from {test_path}")
        test_df = pd.read_csv(test_path)
    
    return train_df, test_df


def prepare_features(df: pd.DataFrame) -> tuple:
    """Prepare features and target from dataframe."""
    # Drop non-feature columns (identifiers, timestamps, strings)
    cols_to_drop = []
    for col in df.columns:
        if df[col].dtype == 'object':
            cols_to_drop.append(col)
        elif col in ['commit_sha', 'repository_id', 'file_path', 'commit_date', 
                     'test_class', 'class_name', 'repository', 'test_name',
                     'commit_id', 'id']:
            cols_to_drop.append(col)
    
    logger.info(f"Dropping non-feature columns: {cols_to_drop}")
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
    
    if 'target' in df.columns:
        X = df.drop(columns=['target'])
        y = df['target']
    elif 'failed' in df.columns:
        X = df.drop(columns=['failed'])
        y = df['failed']
    else:
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
    
    # Ensure all features are numeric
    X = X.select_dtypes(include=[np.number])
    
    feature_names = list(X.columns)
    logger.info(f"Prepared {len(feature_names)} features: {feature_names[:10]}...")
    return X, y, feature_names

def train_xgboost(X_train, y_train) -> XGBClassifier:
    """Train XGBoost classifier."""
    logger.info("Training XGBoost model...")
    
    # Handle single class case
    unique_classes = np.unique(y_train)
    if len(unique_classes) < 2:
        logger.warning(f"Only {len(unique_classes)} class found. Adding synthetic samples.")
        minority_class = 0 if unique_classes[0] == 1 else 1
        n_synthetic = min(5, len(X_train) // 10)
        synthetic_X = X_train.sample(n=n_synthetic, replace=True).reset_index(drop=True)
        synthetic_y = pd.Series([minority_class] * n_synthetic)
        X_train = pd.concat([X_train.reset_index(drop=True), synthetic_X], ignore_index=True)
        y_train = pd.concat([y_train.reset_index(drop=True), synthetic_y], ignore_index=True)
    
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)
    logger.info("XGBoost training complete")
    return model


def train_lightgbm(X_train, y_train) -> LGBMClassifier:
    """Train LightGBM classifier."""
    logger.info("Training LightGBM model...")
    
    unique_classes = np.unique(y_train)
    if len(unique_classes) < 2:
        logger.warning(f"Only {len(unique_classes)} class found. Adding synthetic samples.")
        minority_class = 0 if unique_classes[0] == 1 else 1
        n_synthetic = min(5, len(X_train) // 10)
        synthetic_X = X_train.sample(n=n_synthetic, replace=True).reset_index(drop=True)
        synthetic_y = pd.Series([minority_class] * n_synthetic)
        X_train = pd.concat([X_train.reset_index(drop=True), synthetic_X], ignore_index=True)
        y_train = pd.concat([y_train.reset_index(drop=True), synthetic_y], ignore_index=True)
    
    model = LGBMClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        verbose=-1
    )
    model.fit(X_train, y_train)
    logger.info("LightGBM training complete")
    return model


def evaluate_model(model, X_test, y_test, model_name: str = "Model"):
    """Evaluate model and print metrics."""
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{'='*50}")
    print(f"{model_name} Evaluation Results")
    print(f"{'='*50}")
    print(f"Accuracy: {accuracy:.4f}")
    
    unique_pred = np.unique(y_pred)
    unique_true = np.unique(y_test)
    
    if len(unique_true) > 1 and len(unique_pred) > 1:
        precision = precision_score(y_test, y_pred, average='binary', zero_division=0)
        recall = recall_score(y_test, y_pred, average='binary', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1 Score: {f1:.4f}")
    
    print(f"\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print(f"{'='*50}")
    
    return accuracy


def compute_shap_values(model, X_sample, feature_names: list):
    """Compute SHAP values for model explainability."""
    logger.info("Computing SHAP values...")
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
        
        if isinstance(shap_values, list):
            shap_importance = np.abs(shap_values[1]).mean(axis=0)
        else:
            shap_importance = np.abs(shap_values).mean(axis=0)
        
        importance_dict = dict(zip(feature_names, shap_importance))
        sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        
        print("\nTop 10 Most Important Features (SHAP):")
        for i, (feat, imp) in enumerate(sorted_importance[:10]):
            print(f"  {i+1}. {feat}: {imp:.4f}")
        
        return explainer, shap_values
    except Exception as e:
        logger.warning(f"Could not compute SHAP values: {e}")
        return None, None


def save_model(model, model_dir: str, model_name: str, feature_names: list):
    """Save model and metadata."""
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, f"{model_name}.pkl")
    feature_path = os.path.join(model_dir, "feature_names.pkl")
    
    joblib.dump(model, model_path)
    joblib.dump(feature_names, feature_path)
    logger.info(f"Model saved to {model_path}")
    
    # Also save as default model.pkl for API
    default_model_path = os.path.join(model_dir, "model.pkl")
    joblib.dump(model, default_model_path)


def main():
    """Main training pipeline."""
    data_path = os.environ.get("DATA_PATH", "/app/data")
    model_dir = os.environ.get("MODEL_PATH", "/app/models")
    
    print("="*60)
    print("S5 ML Service - Model Training")
    print("="*60)
    
    try:
        train_df, test_df = load_data(data_path)
    except FileNotFoundError as e:
        logger.error(str(e))
        logger.info("Please run S4 pipeline first to generate training data.")
        return
    
    print(f"\nTraining data shape: {train_df.shape}")
    if test_df is not None:
        print(f"Test data shape: {test_df.shape}")
    
    X_train, y_train, feature_names = prepare_features(train_df)
    print(f"\nNumber of features: {len(feature_names)}")
    print(f"Target distribution:\n{y_train.value_counts()}")
    
    if test_df is not None:
        X_test, y_test, _ = prepare_features(test_df)
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
    
    # Train models
    xgb_model = train_xgboost(X_train.copy(), y_train.copy())
    xgb_accuracy = evaluate_model(xgb_model, X_test, y_test, "XGBoost")
    
    lgb_model = train_lightgbm(X_train.copy(), y_train.copy())
    lgb_accuracy = evaluate_model(lgb_model, X_test, y_test, "LightGBM")
    
    # Select best model
    if xgb_accuracy >= lgb_accuracy:
        best_model = xgb_model
        print(f"\n✅ XGBoost selected as best model (accuracy: {xgb_accuracy:.4f})")
    else:
        best_model = lgb_model
        print(f"\n✅ LightGBM selected as best model (accuracy: {lgb_accuracy:.4f})")
    
    # Compute SHAP values
    X_sample = X_test.head(100) if len(X_test) > 100 else X_test
    explainer, shap_values = compute_shap_values(best_model, X_sample, feature_names)
    
    # Save models
    save_model(best_model, model_dir, "model", feature_names)
    
    if explainer is not None:
        explainer_path = os.path.join(model_dir, "shap_explainer.pkl")
        joblib.dump(explainer, explainer_path)
    
    print("\n" + "="*60)
    print("Training complete!")
    print("="*60)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
