"""Tests for regex helper functionality."""

from unittest.mock import Mock

import pytest

from immich_janitor.models import Asset
from immich_janitor.regex_helper import RegexHelper, RegexSuggestion


@pytest.fixture
def sample_assets():
    """Create sample assets for testing."""
    return [
        Asset(
            id="1",
            original_file_name="IMG_001.jpg",
            type="IMAGE",
            created_at="2024-01-01T12:00:00Z",
            is_favorite=False,
            is_archived=False,
            is_trashed=False,
        ),
        Asset(
            id="2",
            original_file_name="IMG_002.jpg",
            type="IMAGE",
            created_at="2024-01-01T12:00:00Z",
            is_favorite=False,
            is_archived=False,
            is_trashed=False,
        ),
        Asset(
            id="3",
            original_file_name="DSC_1234.jpg",
            type="IMAGE",
            created_at="2024-01-01T12:00:00Z",
            is_favorite=False,
            is_archived=False,
            is_trashed=False,
        ),
        Asset(
            id="4",
            original_file_name="VID_001.mp4",
            type="VIDEO",
            created_at="2024-01-01T12:00:00Z",
            is_favorite=False,
            is_archived=False,
            is_trashed=False,
        ),
        Asset(
            id="5",
            original_file_name="photo.png",
            type="IMAGE",
            created_at="2024-01-01T12:00:00Z",
            is_favorite=False,
            is_archived=False,
            is_trashed=False,
        ),
    ]


def test_regex_helper_initialization():
    """Test RegexHelper initialization."""
    examples = ["IMG_001.jpg", "IMG_002.jpg"]
    helper = RegexHelper(examples)
    
    assert helper.examples == examples
    assert helper.suggestions == []


def test_extract_prefixes():
    """Test prefix extraction from filenames."""
    examples = ["IMG_001.jpg", "IMG_002.jpg", "DSC_1234.jpg"]
    helper = RegexHelper(examples)
    
    prefixes = helper._extract_prefixes()
    
    assert "IMG" in prefixes or "IMG_" in prefixes
    # Should find common prefixes


def test_extract_extensions():
    """Test extension extraction from filenames."""
    examples = ["IMG_001.jpg", "IMG_002.jpg", "photo.png"]
    helper = RegexHelper(examples)
    
    extensions = helper._extract_extensions()
    
    assert "jpg" in extensions  # Most common
    # png might not be included if threshold not met


def test_check_for_numbers():
    """Test number detection in filenames."""
    examples_with_numbers = ["IMG_001.jpg", "IMG_002.jpg"]
    helper_yes = RegexHelper(examples_with_numbers)
    assert helper_yes._check_for_numbers() is True
    
    examples_without_numbers = ["photo.jpg", "image.png"]
    helper_no = RegexHelper(examples_without_numbers)
    assert helper_no._check_for_numbers() is False


def test_extract_date_patterns():
    """Test date pattern detection."""
    examples_with_dates = [
        "IMG_2024-01-15.jpg",
        "photo_2024-01-16.jpg",
        "20240117_event.jpg",
    ]
    helper = RegexHelper(examples_with_dates)
    
    date_patterns = helper._extract_date_patterns()
    
    # Should detect YYYY-MM-DD format
    assert "YYYY-MM-DD" in date_patterns
    # Might detect YYYYMMDD
    assert len(date_patterns) > 0


def test_analyze_patterns_with_prefix_numbers_extension():
    """Test pattern analysis with prefix, numbers, and extension."""
    examples = ["IMG_001.jpg", "IMG_002.jpg", "IMG_999.jpg"]
    helper = RegexHelper(examples)
    
    suggestions = helper.analyze_patterns()
    
    assert len(suggestions) > 0
    # Should suggest pattern like ^IMG_\d+\.jpg$
    patterns = [s.pattern for s in suggestions]
    assert any("IMG" in p and r"\d+" in p and "jpg" in p for p in patterns)


def test_analyze_patterns_multiple_prefixes():
    """Test pattern analysis with multiple prefixes."""
    examples = ["IMG_001.jpg", "DSC_001.jpg", "IMG_002.jpg", "DSC_002.jpg"]
    helper = RegexHelper(examples)
    
    suggestions = helper.analyze_patterns()
    
    assert len(suggestions) > 0
    # Should suggest pattern with (IMG|DSC)
    patterns = [s.pattern for s in suggestions]
    assert any("|" in p for p in patterns)  # OR pattern


def test_analyze_patterns_returns_max_five():
    """Test that analyze_patterns returns at most 5 suggestions."""
    examples = ["IMG_001.jpg", "IMG_002.jpg"]
    helper = RegexHelper(examples)
    
    suggestions = helper.analyze_patterns()
    
    assert len(suggestions) <= 5


def test_test_pattern_matching(sample_assets):
    """Test pattern matching against assets."""
    helper = RegexHelper(["IMG_001.jpg"])
    pattern = r"^IMG_\d+\.jpg$"
    
    matching, samples = helper.test_pattern(pattern, sample_assets)
    
    assert len(matching) == 2  # IMG_001.jpg and IMG_002.jpg
    assert len(samples) <= 10  # Should return sample of max 10
    assert all("IMG_" in s for s in samples)


def test_test_pattern_no_matches(sample_assets):
    """Test pattern that matches nothing."""
    helper = RegexHelper(["test.txt"])
    pattern = r"^NOMATCH_.*"
    
    matching, samples = helper.test_pattern(pattern, sample_assets)
    
    assert len(matching) == 0
    assert len(samples) == 0


def test_test_pattern_invalid_regex(sample_assets):
    """Test handling of invalid regex."""
    helper = RegexHelper(["test.jpg"])
    pattern = r"[invalid(regex"  # Invalid regex
    
    matching, samples = helper.test_pattern(pattern, sample_assets)
    
    # Should handle gracefully
    assert matching == []
    assert samples == []


def test_explain_regex_simple():
    """Test regex explanation for simple patterns."""
    helper = RegexHelper([])
    
    explanation = helper.explain_regex(r"^IMG_\d+\.jpg$")
    
    # Should contain key terms
    assert "IMG" in explanation or "start" in explanation.lower()


def test_explain_regex_with_or():
    """Test regex explanation with OR pattern."""
    helper = RegexHelper([])
    
    explanation = helper.explain_regex(r"^(IMG|DSC)_\d+\.jpg$")
    
    assert "OR" in explanation or "|" in explanation


def test_regex_suggestion_dataclass():
    """Test RegexSuggestion dataclass."""
    suggestion = RegexSuggestion(
        pattern=r"^IMG_\d+\.jpg$",
        description="Test pattern",
        priority=1,
        examples=["IMG_001.jpg"],
    )
    
    assert suggestion.pattern == r"^IMG_\d+\.jpg$"
    assert suggestion.description == "Test pattern"
    assert suggestion.priority == 1
    assert len(suggestion.examples) == 1


def test_analyze_patterns_removes_duplicates():
    """Test that duplicate patterns are removed."""
    examples = ["IMG_001.jpg", "IMG_002.jpg"]
    helper = RegexHelper(examples)
    
    suggestions = helper.analyze_patterns()
    
    # Check no duplicate patterns
    patterns = [s.pattern for s in suggestions]
    assert len(patterns) == len(set(patterns))


def test_analyze_patterns_ordered_by_priority():
    """Test that suggestions are ordered by priority."""
    examples = ["IMG_001.jpg", "IMG_002.jpg", "DSC_001.jpg"]
    helper = RegexHelper(examples)
    
    suggestions = helper.analyze_patterns()
    
    # Should be sorted by priority (lower is better)
    priorities = [s.priority for s in suggestions]
    assert priorities == sorted(priorities)
