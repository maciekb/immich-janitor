"""Utility functions for immich-janitor."""

from datetime import datetime, timedelta
from typing import Optional


def format_size(bytes_size: Optional[int]) -> str:
    """Format bytes to human-readable size.
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 GB", "256 MB")
    """
    if bytes_size is None:
        return "Unknown"
    
    if bytes_size == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(bytes_size)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.2f} {units[unit_index]}"


def parse_time_delta(time_str: str) -> timedelta:
    """Parse time delta string like '30d', '7d', '1h'.
    
    Args:
        time_str: Time string (e.g., "30d", "7d", "24h")
        
    Returns:
        timedelta object
        
    Raises:
        ValueError: If format is invalid
    """
    time_str = time_str.strip().lower()
    
    if time_str.endswith("d"):
        days = int(time_str[:-1])
        return timedelta(days=days)
    elif time_str.endswith("h"):
        hours = int(time_str[:-1])
        return timedelta(hours=hours)
    elif time_str.endswith("m"):
        minutes = int(time_str[:-1])
        return timedelta(minutes=minutes)
    else:
        raise ValueError(f"Invalid time format: {time_str}. Use format like '30d', '24h', '60m'")


def is_older_than(date: datetime, delta: timedelta) -> bool:
    """Check if a date is older than given time delta.
    
    Args:
        date: Date to check
        delta: Time delta to compare against
        
    Returns:
        True if date is older than now - delta
    """
    return date < (datetime.now(date.tzinfo) - delta)
