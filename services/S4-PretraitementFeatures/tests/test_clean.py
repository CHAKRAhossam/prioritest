"""
Tests for the DataCleaner class.
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from preprocessing.clean import DataCleaner


def test_data_cleaner_fit():
    """Test DataCleaner fit method."""
    data = {
        'age': [25, 30, np.nan, 22, 35],
        'salary': [50000, 60000, 55000, np.nan, 70000],
        'city': ['Paris', 'London', 'Paris', np.nan, 'New York'],
        'purchased': ['Yes', 'No', 'Yes', 'No', 'Yes']
    }
    df = pd.DataFrame(data)
    
    cleaner = DataCleaner()
    cleaner.fit(df)
    
    assert cleaner.preprocessor is not None


def test_data_cleaner_transform():
    """Test DataCleaner transform method."""
    data = {
        'age': [25, 30, np.nan, 22, 35],
        'salary': [50000, 60000, 55000, np.nan, 70000],
        'city': ['Paris', 'London', 'Paris', np.nan, 'New York'],
        'purchased': ['Yes', 'No', 'Yes', 'No', 'Yes']
    }
    df = pd.DataFrame(data)
    
    cleaner = DataCleaner()
    cleaner.fit(df)
    df_transformed = cleaner.transform(df)
    
    assert df_transformed is not None
    assert isinstance(df_transformed, pd.DataFrame)
    assert len(df_transformed) == len(df)
    assert not df_transformed.isnull().any().any()


def test_data_cleaner_transform_before_fit():
    """Test DataCleaner transform before fit raises error."""
    cleaner = DataCleaner()
    df = pd.DataFrame({'col1': [1, 2, 3]})
    
    with pytest.raises(RuntimeError):
        cleaner.transform(df)


def test_data_cleaner_with_numeric_only():
    """Test DataCleaner with numeric data only."""
    data = {
        'age': [25, 30, np.nan, 22, 35],
        'salary': [50000, 60000, 55000, np.nan, 70000]
    }
    df = pd.DataFrame(data)
    
    cleaner = DataCleaner()
    cleaner.fit(df)
    df_transformed = cleaner.transform(df)
    
    assert df_transformed is not None
    assert len(df_transformed.columns) >= len(df.columns)


def test_data_cleaner_with_categorical_only():
    """Test DataCleaner with categorical data only."""
    data = {
        'city': ['Paris', 'London', 'Paris', np.nan, 'New York'],
        'purchased': ['Yes', 'No', 'Yes', 'No', 'Yes']
    }
    df = pd.DataFrame(data)
    
    cleaner = DataCleaner()
    cleaner.fit(df)
    df_transformed = cleaner.transform(df)
    
    assert df_transformed is not None
    assert len(df_transformed.columns) >= len(df.columns)

