"""
Tests for the balancer module.
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from preprocessing.balancer import Balancer


def test_balancer_init():
    """Test Balancer initialization."""
    balancer = Balancer()
    assert balancer is not None


def test_balancer_balance():
    """Test data balancing."""
    data = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'target': [0, 0, 0, 1, 1]
    })
    
    balancer = Balancer()
    balanced_data = balancer.balance(data, target_column='target')
    
    assert balanced_data is not None
    assert isinstance(balanced_data, pd.DataFrame)


def test_balancer_balance_with_imbalanced_data():
    """Test balancing with imbalanced data."""
    data = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'target': [0, 0, 0, 0, 0, 0, 0, 0, 1, 1]  # Highly imbalanced
    })
    
    balancer = Balancer()
    balanced_data = balancer.balance(data, target_column='target')
    
    assert balanced_data is not None
    # After balancing, should have more balanced classes
    assert len(balanced_data) >= len(data)


def test_balancer_balance_empty_data():
    """Test balancing with empty data."""
    data = pd.DataFrame()
    
    balancer = Balancer()
    # Should handle empty data gracefully
    try:
        balanced_data = balancer.balance(data, target_column='target')
        assert balanced_data is not None
    except (ValueError, KeyError):
        # Expected if target column doesn't exist
        pass

