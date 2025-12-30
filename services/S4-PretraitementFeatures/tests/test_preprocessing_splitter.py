"""
Tests for the splitter module.
"""
import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from preprocessing.splitter import DataSplitter


def test_data_splitter_init():
    """Test DataSplitter initialization."""
    splitter = DataSplitter()
    assert splitter is not None


def test_data_splitter_split():
    """Test data splitting."""
    data = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'target': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    })
    
    splitter = DataSplitter()
    train, test = splitter.split(data, test_size=0.2)
    
    assert train is not None
    assert test is not None
    assert len(train) + len(test) == len(data)
    assert len(test) == pytest.approx(len(data) * 0.2, abs=1)


def test_data_splitter_split_with_different_sizes():
    """Test data splitting with different test sizes."""
    data = pd.DataFrame({
        'feature1': range(100),
        'target': [i % 2 for i in range(100)]
    })
    
    splitter = DataSplitter()
    train, test = splitter.split(data, test_size=0.3)
    
    assert len(test) == pytest.approx(len(data) * 0.3, abs=1)


def test_data_splitter_split_empty_data():
    """Test splitting with empty data."""
    data = pd.DataFrame()
    
    splitter = DataSplitter()
    # Should handle empty data gracefully
    try:
        train, test = splitter.split(data, test_size=0.2)
        assert train is not None
        assert test is not None
    except (ValueError, IndexError):
        # Expected if data is empty
        pass

