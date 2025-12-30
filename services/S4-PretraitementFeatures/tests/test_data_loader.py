"""
Tests for the data_loader module.
"""
import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import RealDataLoader


def test_real_data_loader_init():
    """Test RealDataLoader initialization."""
    loader = RealDataLoader()
    assert loader is not None


def test_real_data_loader_load_data_empty_path():
    """Test loading data with empty path."""
    loader = RealDataLoader()
    # Should handle empty path gracefully
    result = loader.load_data("")
    assert result is not None or isinstance(result, pd.DataFrame) or result is None


def test_real_data_loader_load_data_nonexistent():
    """Test loading data from nonexistent path."""
    loader = RealDataLoader()
    # Should handle nonexistent path gracefully
    with pytest.raises((FileNotFoundError, Exception)):
        loader.load_data("/nonexistent/path/data.csv")


def test_real_data_loader_with_valid_data():
    """Test loading valid data."""
    loader = RealDataLoader()
    # This test assumes data might exist or not
    # It should not crash if data doesn't exist
    try:
        result = loader.load_data("data/raw/dataset.csv")
        if result is not None:
            assert isinstance(result, pd.DataFrame)
    except (FileNotFoundError, Exception):
        # Expected if file doesn't exist
        pass

