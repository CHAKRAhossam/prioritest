import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from collections import Counter

class ClassBalancer:
    """
    A class to handle class imbalance using SMOTE (Synthetic Minority Over-sampling Technique).
    """
    def __init__(self, random_state=42):
        """
        Initialize the ClassBalancer.
        
        Args:
            random_state (int): Seed for reproducibility.
        """
        self.smote = SMOTE(random_state=random_state)

    def fit_resample(self, X, y):
        """
        Resample the dataset to balance classes.
        
        Args:
            X (pd.DataFrame or np.ndarray): Features.
            y (pd.Series or np.ndarray): Target variable.
            
        Returns:
            tuple: (X_resampled, y_resampled)
        """
        # Check if we have at least 2 classes
        unique_classes = np.unique(y)
        if len(unique_classes) < 2:
            print(f"⚠️  Only {len(unique_classes)} class(es) found. SMOTE requires at least 2 classes.")
            print("   Skipping SMOTE resampling. Returning original data.")
            return X, y
        
        # Check if minority class has enough samples for SMOTE (need at least k_neighbors+1)
        class_counts = Counter(y)
        min_samples = min(class_counts.values())
        if min_samples < 6:  # SMOTE default k_neighbors=5, needs at least 6 samples
            print(f"⚠️  Minority class has only {min_samples} samples (SMOTE needs at least 6).")
            print("   Skipping SMOTE resampling. Returning original data.")
            return X, y
        
        X_resampled, y_resampled = self.smote.fit_resample(X, y)
        return X_resampled, y_resampled

if __name__ == "__main__":
    # Create imbalanced dummy data
    # 90 samples of class 0, 10 samples of class 1
    X = np.random.rand(100, 5)
    y = np.array([0] * 90 + [1] * 10)
    
    print("Original Class Distribution:")
    print(Counter(y))
    print("\n" + "-"*30 + "\n")

    # Initialize and run ClassBalancer
    balancer = ClassBalancer()
    
    print("Applying SMOTE balancing...")
    X_resampled, y_resampled = balancer.fit_resample(X, y)

    print("Resampled Class Distribution:")
    print(Counter(y_resampled))
    
    if Counter(y_resampled)[0] == Counter(y_resampled)[1]:
        print("\nSUCCESS: Classes are perfectly balanced.")
    else:
        print("\nFAILURE: Classes are not balanced.")
