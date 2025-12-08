import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class FeatureEngineer(BaseEstimator, TransformerMixin):
    """
    A class to generate derived features for the recommendation system.
    """
    def __init__(self):
        pass

    def fit(self, X, y=None):
        """
        Fit method. Since this transformer doesn't learn parameters, it just returns self.
        
        Args:
            X (pd.DataFrame): The training data.
            y: Ignored.
            
        Returns:
            self
        """
        return self

    def transform(self, X):
        """
        Transform the data by adding derived features.
        
        Args:
            X (pd.DataFrame): The data to transform.
            
        Returns:
            pd.DataFrame: The data with new features.
        """
        # Create a copy to avoid modifying the original dataframe
        X_new = X.copy()
        
        # Apply feature engineering steps
        X_new = self.calculate_churn(X_new)
        X_new = self.count_authors(X_new)
        X_new = self.days_since_bugfix(X_new)
        
        return X_new

    def calculate_churn(self, df):
        """
        Simulates code churn score calculation.
        MTP-22: Features dérivées - Churn
        """
        # Simulating random churn score between 0 and 100
        # In a real scenario, this would calculate lines added/deleted/modified from git logs
        np.random.seed(42) # For reproducibility in this simulation
        df['churn'] = np.random.randint(0, 101, size=len(df))
        return df

    def count_authors(self, df):
        """
        Simulates author count calculation.
        MTP-23: Features dérivées - Auteurs
        """
        # Simulating random author count between 1 and 10
        # In a real scenario, this would count unique authors from git logs
        np.random.seed(43)
        df['num_authors'] = np.random.randint(1, 11, size=len(df))
        return df

    def days_since_bugfix(self, df):
        """
        Simulates days since last bug fix.
        MTP-24: Features dérivées - Bug-fix proximity
        """
        # Simulating random days since last fix between 0 and 365
        # In a real scenario, this would check jira/git history for 'fix' keywords
        np.random.seed(44)
        df['bug_fix_proximity'] = np.random.randint(0, 366, size=len(df))
        return df

if __name__ == "__main__":
    # Create dummy data
    data = {
        'file_path': ['src/main.py', 'src/utils.py', 'tests/test_main.py', 'src/api.py', 'config.yaml'],
        'lines_of_code': [120, 45, 80, 200, 15]
    }
    df = pd.DataFrame(data)

    print("Original Data:")
    print(df)
    print("\n" + "-"*30 + "\n")

    # Initialize and run FeatureEngineer
    engineer = FeatureEngineer()
    
    print("Fitting FeatureEngineer...")
    engineer.fit(df)
    
    print("Transforming Data (Generating Features)...")
    df_enriched = engineer.transform(df)

    print("Enriched Data:")
    print(df_enriched)
