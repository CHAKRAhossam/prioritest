import pandas as pd
import numpy as np
import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.preprocessing.clean import DataCleaner
from src.preprocessing.feature_engineering import FeatureEngineer
from src.preprocessing.splitter import TimeAwareSplitter
from src.preprocessing.balancer import ClassBalancer
from src.data_loader import RealDataLoader

def generate_dummy_data(output_path, n_samples=1000):
    """Generates dummy data for the pipeline (fallback when no real data)."""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=n_samples, freq='H')
    
    data = {
        'commit_id': range(n_samples),
        'commit_date': dates,
        'lines_modified': np.random.randint(1, 500, size=n_samples),
        'complexity': np.random.rand(n_samples) * 10,
        'author_type': np.random.choice(['Senior', 'Junior', 'Bot'], size=n_samples),
        'file_type': np.random.choice(['.py', '.java', '.xml'], size=n_samples),
        'target': np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1]) # Imbalanced
    }
    
    # Add some missing values
    df = pd.DataFrame(data)
    df.loc[np.random.choice(df.index, 50), 'lines_modified'] = np.nan
    df.loc[np.random.choice(df.index, 50), 'author_type'] = np.nan
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated dummy data at {output_path}")

def main():
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_path = os.path.join(base_dir, 'data', 'raw', 'dataset.csv')
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    os.makedirs(processed_dir, exist_ok=True)

    # 1. Load Real Data
    print("=" * 60)
    print("Loading REAL data from PostgreSQL and S3...")
    print("=" * 60)
    
    data_loader = RealDataLoader()
    df = data_loader.load_real_data()
    
    # Fallback to dummy data if no real data available
    if df is None or df.empty or len(df) == 0:
        print("\n⚠️  No real data found. Generating dummy data for testing...")
        generate_dummy_data(raw_data_path)
        df = pd.read_csv(raw_data_path)
        df['commit_date'] = pd.to_datetime(df['commit_date'])
    else:
        print(f"\n✅ Loaded {len(df)} real records from database")
        # Save raw data for reference
        os.makedirs(os.path.dirname(raw_data_path), exist_ok=True)
        df.to_csv(raw_data_path, index=False)
        print(f"Saved raw data to {raw_data_path}")
    
    # Ensure commit_date is datetime
    if 'commit_date' in df.columns:
        df['commit_date'] = pd.to_datetime(df['commit_date'])
    else:
        # Fallback: create commit_date from timestamp if available
        if 'timestamp' in df.columns:
            df['commit_date'] = pd.to_datetime(df['timestamp'])
        else:
            print("⚠️  No date column found. Creating synthetic dates...")
            df['commit_date'] = pd.date_range(start='2023-01-01', periods=len(df), freq='H')
    
    # 3. Separate Metadata (to preserve from Cleaner)
    # We keep commit_date for splitting, and target for balancing/training
    # Handle case where commit_id might not exist (use index)
    meta_cols = ['commit_date', 'target']
    if 'commit_id' in df.columns:
        meta_cols.insert(0, 'commit_id')
    elif 'id' in df.columns:
        df = df.rename(columns={'id': 'commit_id'})
        meta_cols.insert(0, 'commit_id')
    else:
        df['commit_id'] = df.index
    
    # Ensure target exists (create if missing)
    if 'target' not in df.columns:
        print("⚠️  No target column found. Creating synthetic target...")
        df['target'] = np.random.choice([0, 1], size=len(df), p=[0.9, 0.1])
    
    X_meta = df[meta_cols].copy()
    X_features = df.drop(columns=meta_cols, errors='ignore')
    
    # 4. Clean Data
    print("Cleaning data...")
    cleaner = DataCleaner()
    cleaner.fit(X_features)
    X_cleaned = cleaner.transform(X_features)
    
    # Reassemble
    df_cleaned = pd.concat([X_cleaned, X_meta], axis=1)
    
    # 5. Feature Engineering
    print("Engineering features...")
    engineer = FeatureEngineer()
    df_enriched = engineer.transform(df_cleaned)
    
    # 6. Time-Aware Split
    print("Splitting data...")
    
    # Save enriched data for Feast (needs IDs and Dates)
    features_path = os.path.join(processed_dir, 'features.parquet')
    df_enriched.to_parquet(features_path, index=False)
    print(f"Saved features for Feast to {features_path}")

    splitter = TimeAwareSplitter(date_col='commit_date', test_size=0.2)
    train_df, test_df = splitter.split(df_enriched)
    
    print(f"Train size: {len(train_df)}, Test size: {len(test_df)}")
    
    # 7. Balance Classes (Train only)
    print("Balancing training data...")
    balancer = ClassBalancer()
    
    # Prepare for balancing (drop non-numeric/date cols that SMOTE can't handle)
    # We need to drop commit_date and commit_id for SMOTE
    cols_to_drop = ['commit_date', 'commit_id', 'target']
    X_train = train_df.drop(columns=cols_to_drop)
    y_train = train_df['target']
    
    X_train_resampled, y_train_resampled = balancer.fit_resample(X_train, y_train)
    
    print(f"Original Train Target Dist: {y_train.value_counts().to_dict()}")
    print(f"Resampled Train Target Dist: {y_train_resampled.value_counts().to_dict()}")
    
    # 8. Save Processed Data
    # Reassemble resampled train data
    train_processed = pd.concat([X_train_resampled, y_train_resampled], axis=1)
    
    train_path = os.path.join(processed_dir, 'train.csv')
    test_path = os.path.join(processed_dir, 'test.csv')
    
    train_processed.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    print(f"Saved processed data to {processed_dir}")

if __name__ == "__main__":
    main()
