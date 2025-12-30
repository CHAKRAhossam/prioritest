"""
Tests for the FeatureEngineer class.
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from preprocessing.feature_engineering import FeatureEngineer


def test_feature_engineer_fit():
    """Test FeatureEngineer fit method."""
    data = {
        'file_path': ['src/main.py', 'src/utils.py', 'tests/test_main.py'],
        'lines_of_code': [120, 45, 80]
    }
    df = pd.DataFrame(data)
    
    engineer = FeatureEngineer()
    result = engineer.fit(df)
    
    assert result is engineer  # Should return self


def test_feature_engineer_transform():
    """Test FeatureEngineer transform method."""
    data = {
        'file_path': ['src/main.py', 'src/utils.py', 'tests/test_main.py'],
        'lines_of_code': [120, 45, 80]
    }
    df = pd.DataFrame(data)
    
    engineer = FeatureEngineer()
    engineer.fit(df)
    df_transformed = engineer.transform(df)
    
    assert df_transformed is not None
    assert isinstance(df_transformed, pd.DataFrame)
    assert len(df_transformed) == len(df)
    assert 'churn' in df_transformed.columns
    assert 'num_authors' in df_transformed.columns
    assert 'bug_fix_proximity' in df_transformed.columns


def test_feature_engineer_calculate_churn():
    """Test calculate_churn method."""
    data = {
        'file_path': ['src/main.py', 'src/utils.py'],
        'lines_of_code': [120, 45]
    }
    df = pd.DataFrame(data)
    
    engineer = FeatureEngineer()
    df_result = engineer.calculate_churn(df)
    
    assert 'churn' in df_result.columns
    assert all(0 <= val <= 100 for val in df_result['churn'])


def test_feature_engineer_count_authors():
    """Test count_authors method."""
    data = {
        'file_path': ['src/main.py', 'src/utils.py'],
        'lines_of_code': [120, 45]
    }
    df = pd.DataFrame(data)
    
    engineer = FeatureEngineer()
    df_result = engineer.count_authors(df)
    
    assert 'num_authors' in df_result.columns
    assert all(1 <= val <= 10 for val in df_result['num_authors'])


def test_feature_engineer_days_since_bugfix():
    """Test days_since_bugfix method."""
    data = {
        'file_path': ['src/main.py', 'src/utils.py'],
        'lines_of_code': [120, 45]
    }
    df = pd.DataFrame(data)
    
    engineer = FeatureEngineer()
    df_result = engineer.days_since_bugfix(df)
    
    assert 'bug_fix_proximity' in df_result.columns
    assert all(0 <= val <= 365 for val in df_result['bug_fix_proximity'])


def test_feature_engineer_preserves_original_columns():
    """Test that transform preserves original columns."""
    data = {
        'file_path': ['src/main.py', 'src/utils.py'],
        'lines_of_code': [120, 45]
    }
    df = pd.DataFrame(data)
    original_columns = set(df.columns)
    
    engineer = FeatureEngineer()
    engineer.fit(df)
    df_transformed = engineer.transform(df)
    
    assert original_columns.issubset(set(df_transformed.columns))

