"""Tests for data models."""

from datetime import datetime, timezone

import pytest

from immich_janitor.models import (
    Asset,
    AssetBulkDeleteRequest,
    DuplicateAsset,
    DuplicateGroup,
    ExifInfo,
)


def test_exif_info_model():
    """Test ExifInfo model with file size."""
    exif_data = {
        "fileSizeInByte": 5000000,
        "exifImageWidth": 1920,
        "exifImageHeight": 1080,
        "make": "Apple",
        "model": "iPhone 15 Pro",
    }
    
    exif = ExifInfo(**exif_data)
    
    assert exif.file_size_in_byte == 5000000
    assert exif.exif_image_width == 1920
    assert exif.exif_image_height == 1080
    assert exif.make == "Apple"
    assert exif.model == "iPhone 15 Pro"


def test_exif_info_optional_fields():
    """Test ExifInfo with only required fields."""
    exif = ExifInfo()
    
    assert exif.file_size_in_byte is None
    assert exif.exif_image_width is None


def test_asset_with_exif():
    """Test Asset model with EXIF information."""
    asset_data = {
        "id": "test-123",
        "originalFileName": "IMG_001.jpg",
        "type": "IMAGE",
        "createdAt": "2024-01-01T12:00:00Z",
        "exifInfo": {
            "fileSizeInByte": 5000000,
            "exifImageWidth": 1920,
            "exifImageHeight": 1080,
        },
        "isFavorite": False,
        "isArchived": False,
        "isTrashed": False,
    }
    
    asset = Asset(**asset_data)
    
    assert asset.id == "test-123"
    assert asset.original_file_name == "IMG_001.jpg"
    assert asset.type == "IMAGE"
    assert isinstance(asset.created_at, datetime)
    assert asset.exif_info is not None
    assert asset.file_size_in_bytes == 5000000  # Property from exifInfo
    assert asset.is_favorite is False


def test_asset_without_exif():
    """Test Asset model without EXIF information (old API format)."""
    asset_data = {
        "id": "test-456",
        "originalFileName": "IMG_002.jpg",
        "type": "IMAGE",
        "createdAt": "2024-01-01T12:00:00Z",
        "isFavorite": True,
        "isArchived": False,
        "isTrashed": False,
    }
    
    asset = Asset(**asset_data)
    
    assert asset.id == "test-456"
    assert asset.exif_info is None
    assert asset.file_size_in_bytes is None  # No EXIF, no size
    assert asset.is_favorite is True


def test_asset_trashed():
    """Test Asset model with trash status."""
    asset_data = {
        "id": "test-789",
        "originalFileName": "IMG_003.jpg",
        "type": "VIDEO",
        "createdAt": "2024-01-01T12:00:00Z",
        "isFavorite": False,
        "isArchived": False,
        "isTrashed": True,
        "deletedAt": "2024-01-02T12:00:00Z",
    }
    
    asset = Asset(**asset_data)
    
    assert asset.is_trashed is True
    assert asset.deleted_at is not None
    assert isinstance(asset.deleted_at, datetime)


def test_bulk_delete_request():
    """Test AssetBulkDeleteRequest model."""
    request = AssetBulkDeleteRequest(ids=["id1", "id2"], force=True)
    
    assert request.ids == ["id1", "id2"]
    assert request.force is True
    
    # Test default value
    request_default = AssetBulkDeleteRequest(ids=["id1"])
    assert request_default.force is False


def test_duplicate_asset():
    """Test DuplicateAsset model."""
    dup_data = {
        "id": "dup-123",
        "deviceAssetId": "device-456",
        "deviceId": "device-789",
        "originalPath": "/path/to/file.jpg",
        "originalFileName": "photo.jpg",
        "type": "IMAGE",
        "createdAt": "2024-01-01T12:00:00Z",
        "fileSizeInBytes": 2000000,
    }
    
    dup = DuplicateAsset(**dup_data)
    
    assert dup.id == "dup-123"
    assert dup.original_file_name == "photo.jpg"
    assert dup.file_size_in_bytes == 2000000


def test_duplicate_group():
    """Test DuplicateGroup model with multiple assets."""
    group_data = {
        "id": "group-123",
        "assets": [
            {
                "id": "dup-1",
                "deviceAssetId": "dev-1",
                "deviceId": "device-1",
                "originalPath": "/path1.jpg",
                "originalFileName": "photo.jpg",
                "type": "IMAGE",
                "createdAt": "2024-01-01T12:00:00Z",
                "fileSizeInBytes": 1000000,
            },
            {
                "id": "dup-2",
                "deviceAssetId": "dev-2",
                "deviceId": "device-2",
                "originalPath": "/path2.jpg",
                "originalFileName": "photo.jpg",
                "type": "IMAGE",
                "createdAt": "2024-01-01T12:00:00Z",
                "fileSizeInBytes": 1000000,
            },
        ],
    }
    
    group = DuplicateGroup(**group_data)
    
    assert group.id == "group-123"
    assert group.asset_count == 2
    assert group.total_size == 2000000  # Sum of both assets


def test_asset_photo_taken_at_with_exif():
    """Test photo_taken_at property when EXIF dateTimeOriginal is available."""
    asset_data = {
        "id": "test-exif-date",
        "originalFileName": "IMG_001.jpg",
        "type": "IMAGE",
        "createdAt": "2024-01-10T12:00:00Z",  # Upload date
        "exifInfo": {
            "fileSizeInByte": 5000000,
            "dateTimeOriginal": "2024-01-05T10:30:00Z",  # Photo taken date
        },
        "isFavorite": False,
        "isArchived": False,
        "isTrashed": False,
    }
    
    asset = Asset(**asset_data)
    
    # Should use dateTimeOriginal from EXIF, not createdAt
    assert asset.photo_taken_at.strftime("%Y-%m-%d") == "2024-01-05"
    assert asset.created_at.strftime("%Y-%m-%d") == "2024-01-10"
    assert asset.photo_taken_at != asset.created_at


def test_asset_photo_taken_at_without_exif():
    """Test photo_taken_at property when EXIF dateTimeOriginal is not available."""
    asset_data = {
        "id": "test-no-exif-date",
        "originalFileName": "IMG_002.jpg",
        "type": "IMAGE",
        "createdAt": "2024-01-10T12:00:00Z",
        "isFavorite": False,
        "isArchived": False,
        "isTrashed": False,
    }
    
    asset = Asset(**asset_data)
    
    # Should fallback to createdAt when no EXIF date
    assert asset.photo_taken_at == asset.created_at
    assert asset.photo_taken_at.strftime("%Y-%m-%d") == "2024-01-10"


def test_asset_photo_taken_at_with_exif_but_no_date():
    """Test photo_taken_at property when EXIF exists but dateTimeOriginal is None."""
    asset_data = {
        "id": "test-exif-no-date",
        "originalFileName": "IMG_003.jpg",
        "type": "IMAGE",
        "createdAt": "2024-01-10T12:00:00Z",
        "exifInfo": {
            "fileSizeInByte": 5000000,
            # dateTimeOriginal not provided
        },
        "isFavorite": False,
        "isArchived": False,
        "isTrashed": False,
    }
    
    asset = Asset(**asset_data)
    
    # Should fallback to createdAt when EXIF exists but has no date
    assert asset.photo_taken_at == asset.created_at
    assert asset.photo_taken_at.strftime("%Y-%m-%d") == "2024-01-10"


def test_asset_photo_taken_at_naive_exif_normalized():
    """Test photo_taken_at normalizes timezone-naive EXIF dates to UTC.
    
    This regression test ensures we don't get TypeError when comparing
    naive EXIF dates with timezone-aware created_at timestamps.
    """
    # Create asset with timezone-naive EXIF date (common in EXIF metadata)
    naive_exif_date = datetime(2024, 1, 5, 10, 30, 0)  # No timezone
    
    asset_data = {
        "id": "test-naive-exif",
        "originalFileName": "IMG_004.jpg",
        "type": "IMAGE",
        "createdAt": "2024-01-10T12:00:00Z",  # Timezone-aware (UTC)
        "exifInfo": {
            "fileSizeInByte": 5000000,
            "dateTimeOriginal": naive_exif_date,
        },
        "isFavorite": False,
        "isArchived": False,
        "isTrashed": False,
    }
    
    asset = Asset(**asset_data)
    
    # photo_taken_at should be timezone-aware after normalization
    assert asset.photo_taken_at.tzinfo is not None
    assert asset.photo_taken_at.tzinfo == timezone.utc
    
    # Should be comparable with created_at without TypeError
    # This would fail before normalization fix
    assert asset.photo_taken_at < asset.created_at  # Photo taken before upload
    
    # Date should be preserved, only timezone added
    assert asset.photo_taken_at.strftime("%Y-%m-%d %H:%M:%S") == "2024-01-05 10:30:00"
