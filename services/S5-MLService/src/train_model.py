"""
Train XGBoost model for code file risk classification.
MTP-30 & MTP-38: Train/test split, evaluation, and model persistence.
"""
import os
import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix


def main():
    # Paths
    data_path = "../microservice-4-preprocessing/data/processed/train.csv"
    model_dir = "models"
    model_path = os.path.join(model_dir, "model.pkl")

    # Load data
    print(f"Loading data from {data_path}...")
    if not os.path.exists(data_path):
        print(f"Error: File not found at {data_path}")
        print(f"Current working directory: {os.getcwd()}")
        return

    df = pd.read_csv(data_path)
    print(f"Data loaded successfully. Shape: {df.shape}")

    # Split Features (X) and Target (y) - target is the last column
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    feature_names = list(X.columns)
    print(f"Features ({len(feature_names)}): {feature_names}")
    print(f"Target column: {df.columns[-1]}")

    # Split into train and test sets (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"\nTrain set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")

    # Initialize XGBClassifier
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss'
    )

    # Train the model
    print("\nTraining XGBoost model...")
    model.fit(X_train, y_train)

    # Evaluate on TEST set
    print("\nEvaluating model on TEST data...")
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)

    print("-" * 40)
    print(f"Accuracy on TEST set: {accuracy:.4f}")
    print("\nConfusion Matrix:")
    print(conf_matrix)
    print("-" * 40)

    # Save the model
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")

    # Also save feature names for the API
    feature_names_path = os.path.join(model_dir, "feature_names.pkl")
    joblib.dump(feature_names, feature_names_path)
    print(f"Feature names saved to: {feature_names_path}")


if __name__ == "__main__":
    main()
