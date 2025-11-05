"""Tests for utility functions."""

import pytest

from immich_janitor.utils import format_size


def test_format_size_bytes():
    """Test formatting bytes."""
    assert format_size(0) == "0 B"
    assert format_size(1) == "1 B"
    assert format_size(999) == "999 B"


def test_format_size_kilobytes():
    """Test formatting kilobytes."""
    assert format_size(1024) == "1.00 KB"
    assert format_size(1536) == "1.50 KB"
    assert format_size(10240) == "10.00 KB"


def test_format_size_megabytes():
    """Test formatting megabytes."""
    assert format_size(1048576) == "1.00 MB"  # 1024 * 1024
    assert format_size(5242880) == "5.00 MB"  # 5 * 1024 * 1024
    assert format_size(10485760) == "10.00 MB"


def test_format_size_gigabytes():
    """Test formatting gigabytes."""
    assert format_size(1073741824) == "1.00 GB"  # 1024^3
    assert format_size(5368709120) == "5.00 GB"  # 5 * 1024^3
    assert format_size(198660000000) == "185.02 GB"  # Real-world example


def test_format_size_terabytes():
    """Test formatting terabytes."""
    assert format_size(1099511627776) == "1.00 TB"  # 1024^4
    assert format_size(5497558138880) == "5.00 TB"


def test_format_size_edge_cases():
    """Test edge cases and rounding."""
    # Test rounding
    assert format_size(1500) == "1.46 KB"
    assert format_size(1536000) == "1.46 MB"
    
    # Test large numbers
    assert format_size(999999999999) == "931.32 GB"
    
    # Test None
    assert format_size(None) == "Unknown"


def test_format_size_precision():
    """Test decimal precision is consistent."""
    result = format_size(1536)
    assert "1.50" in result  # Should have 2 decimal places
    
    result_gb = format_size(1610612736)  # 1.5 GB
    assert "1.50" in result_gb
