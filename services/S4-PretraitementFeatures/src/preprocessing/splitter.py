import pandas as pd
import numpy as np

class TimeAwareSplitter:
    """
    A class to split data into training and testing sets based on time,
    ensuring no data leakage from future to past.
    """
    def __init__(self, date_col, test_size=0.2):
        """
        Initialize the splitter.
        
        Args:
            date_col (str): The name of the column containing date information.
            test_size (float): The proportion of the dataset to include in the test split.
        """
        self.date_col = date_col
        self.test_size = test_size

    def split(self, df):
        """
        Split the dataframe into train and test sets respecting temporal order.
        
        Args:
            df (pd.DataFrame): The input dataframe.
            
        Returns:
            tuple: (train_df, test_df)
        """
        # Ensure the date column is in datetime format
        if not pd.api.types.is_datetime64_any_dtype(df[self.date_col]):
            df = df.copy()
            df[self.date_col] = pd.to_datetime(df[self.date_col])

        # Sort by date
        df_sorted = df.sort_values(by=self.date_col).reset_index(drop=True)
        
        # Calculate split index
        n_samples = len(df_sorted)
        split_idx = int(n_samples * (1 - self.test_size))
        
        # Split data
        train_df = df_sorted.iloc[:split_idx]
        test_df = df_sorted.iloc[split_idx:]
        
        return train_df, test_df

if __name__ == "__main__":
    # Create dummy data with dates
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    data = {
        'commit_id': range(100),
        'commit_date': dates,
        'feature_val': np.random.randn(100)
    }
    df = pd.DataFrame(data)
    
    # Shuffle data to simulate unsorted input
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    print("Original Data Sample (Unsorted):")
    print(df.head())
    print("\n" + "-"*30 + "\n")

    # Initialize and run TimeAwareSplitter
    splitter = TimeAwareSplitter(date_col='commit_date', test_size=0.2)
    
    print(f"Splitting data (Test Size: {splitter.test_size})...")
    train_df, test_df = splitter.split(df)

    print(f"Train Set Size: {len(train_df)}")
    print(f"Test Set Size: {len(test_df)}")
    print("\n" + "-"*30 + "\n")

    # Verification
    train_min = train_df['commit_date'].min()
    train_max = train_df['commit_date'].max()
    test_min = test_df['commit_date'].min()
    test_max = test_df['commit_date'].max()

    print("Verification of Temporal Split:")
    print(f"Train Date Range: {train_min.date()} to {train_max.date()}")
    print(f"Test Date Range:  {test_min.date()} to {test_max.date()}")
    
    if train_max < test_min:
        print("\nSUCCESS: No temporal overlap. Train data strictly precedes Test data.")
    else:
        print("\nFAILURE: Temporal overlap detected!")
