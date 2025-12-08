import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class DataCleaner:
    """
    A class to handle data cleaning steps: missing value imputation and categorical encoding.
    """
    def __init__(self):
        self.numeric_imputer = SimpleImputer(strategy='mean')
        self.categorical_imputer = SimpleImputer(strategy='most_frequent')
        self.encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        self.preprocessor = None

    def fit(self, X):
        """
        Fit the imputers and encoder on the data.
        
        Args:
            X (pd.DataFrame): The training data.
        """
        # Identify numeric and categorical columns
        numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
        categorical_features = X.select_dtypes(include=['object', 'category']).columns

        # Create transformers
        numeric_transformer = Pipeline(steps=[
            ('imputer', self.numeric_imputer)
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', self.categorical_imputer),
            ('encoder', self.encoder)
        ])

        # Combine into a ColumnTransformer
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ],
            verbose_feature_names_out=False
        )

        self.preprocessor.fit(X)
        return self

    def transform(self, X):
        """
        Transform the data using the fitted preprocessor.
        
        Args:
            X (pd.DataFrame): The data to transform.
            
        Returns:
            pd.DataFrame: The transformed data.
        """
        if self.preprocessor is None:
            raise RuntimeError("DataCleaner has not been fitted yet.")
        
        X_transformed = self.preprocessor.transform(X)
        
        # Get feature names if possible
        try:
            feature_names = self.preprocessor.get_feature_names_out()
        except AttributeError:
            # Fallback if get_feature_names_out is not available or fails
            feature_names = [f"feature_{i}" for i in range(X_transformed.shape[1])]
        
        # Clean column names: remove dots from one-hot encoded names
        # e.g., "file_type_.java" -> "file_type_java"
        feature_names = [name.replace('.', '') for name in feature_names]
            
        return pd.DataFrame(X_transformed, columns=feature_names, index=X.index)

if __name__ == "__main__":
    # Create dummy data
    data = {
        'age': [25, 30, np.nan, 22, 35],
        'salary': [50000, 60000, 55000, np.nan, 70000],
        'city': ['Paris', 'London', 'Paris', np.nan, 'New York'],
        'purchased': ['Yes', 'No', 'Yes', 'No', 'Yes']
    }
    df = pd.DataFrame(data)

    print("Original Data:")
    print(df)
    print("\n" + "-"*30 + "\n")

    # Initialize and run DataCleaner
    cleaner = DataCleaner()
    
    print("Fitting DataCleaner...")
    cleaner.fit(df)
    
    print("Transforming Data...")
    df_cleaned = cleaner.transform(df)

    print("Cleaned Data:")
    print(df_cleaned)
