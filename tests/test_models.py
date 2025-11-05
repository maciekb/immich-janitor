"""Tests for data models."""

from datetime import datetime

import pytest

from immich_janitor.models import Asset, AssetBulkDeleteRequest


def test_asset_model():
    """Test Asset model creation."""
    asset_data = {
        "id": "test-123",
        "originalFileName": "IMG_001.jpg",
        "type": "IMAGE",
        "createdAt": "2024-01-01T12:00:00Z",
        "fileSizeInBytes": 1024,
        "isFavorite": False,
        "isArchived": False,
    }
    
    asset = Asset(**asset_data)
    
    assert asset.id == "test-123"
    assert asset.original_file_name == "IMG_001.jpg"
    assert asset.type == "IMAGE"
    assert isinstance(asset.created_at, datetime)
    assert asset.file_size_in_bytes == 1024
    assert asset.is_favorite is False
    assert asset.is_archived is False


def test_bulk_delete_request():
    """Test AssetBulkDeleteRequest model."""
    request = AssetBulkDeleteRequest(ids=["id1", "id2"], force=True)
    
    assert request.ids == ["id1", "id2"]
    assert request.force is True
    
    # Test default value
    request_default = AssetBulkDeleteRequest(ids=["id1"])
    assert request_default.force is False
