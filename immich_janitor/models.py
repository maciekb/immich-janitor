"""Data models for Immich API responses."""

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExifInfo(BaseModel):
    """EXIF information for an asset."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    file_size_in_byte: Optional[int] = Field(None, alias="fileSizeInByte")
    exif_image_width: Optional[int] = Field(None, alias="exifImageWidth")
    exif_image_height: Optional[int] = Field(None, alias="exifImageHeight")
    make: Optional[str] = None
    model: Optional[str] = None
    date_time_original: Optional[datetime] = Field(None, alias="dateTimeOriginal")


class Asset(BaseModel):
    """Represents an Immich asset (photo or video)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    original_file_name: str = Field(alias="originalFileName")
    type: str  # 'IMAGE' or 'VIDEO'
    created_at: datetime = Field(alias="createdAt")
    exif_info: Optional[ExifInfo] = Field(None, alias="exifInfo")
    is_favorite: bool = Field(False, alias="isFavorite")
    is_archived: bool = Field(False, alias="isArchived")
    is_trashed: bool = Field(False, alias="isTrashed")
    deleted_at: Optional[datetime] = Field(None, alias="deletedAt")

    @property
    def file_size_in_bytes(self) -> Optional[int]:
        """Get file size from exifInfo if available."""
        if self.exif_info:
            return self.exif_info.file_size_in_byte
        return None

    @property
    def photo_taken_at(self) -> datetime:
        """Get the date when photo was taken (from EXIF) or created date as fallback.
        
        Normalizes timezone-naive EXIF timestamps to UTC to ensure compatibility
        with timezone-aware created_at timestamps for comparison operations.
        """
        if self.exif_info and self.exif_info.date_time_original:
            exif_date = self.exif_info.date_time_original
            # If EXIF date is naive (no timezone), assume UTC
            if exif_date.tzinfo is None:
                return exif_date.replace(tzinfo=timezone.utc)
            return exif_date
        return self.created_at


class AssetBulkDeleteRequest(BaseModel):
    """Request model for bulk delete operation."""

    ids: list[str]
    force: bool = False


class DuplicateAsset(BaseModel):
    """Represents an asset in a duplicate group."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    device_asset_id: str = Field(alias="deviceAssetId")
    device_id: str = Field(alias="deviceId")
    original_path: str = Field(alias="originalPath")
    original_file_name: str = Field(alias="originalFileName")
    type: str
    created_at: datetime = Field(alias="createdAt")
    file_size_in_bytes: Optional[int] = Field(None, alias="fileSizeInBytes")


class DuplicateGroup(BaseModel):
    """Represents a group of duplicate assets."""

    id: str
    assets: list[DuplicateAsset]

    @property
    def asset_count(self) -> int:
        """Number of assets in this duplicate group."""
        return len(self.assets)

    @property
    def total_size(self) -> int:
        """Total size of all assets in bytes."""
        return sum(
            asset.file_size_in_bytes or 0 for asset in self.assets
        )


class TrashRestoreRequest(BaseModel):
    """Request model for restoring assets from trash."""

    ids: list[str]


class TrashEmptyRequest(BaseModel):
    """Request model for emptying trash."""

    ids: list[str]
