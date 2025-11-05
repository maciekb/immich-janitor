"""Data models for Immich API responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Asset(BaseModel):
    """Represents an Immich asset (photo or video)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    original_file_name: str = Field(alias="originalFileName")
    type: str  # 'IMAGE' or 'VIDEO'
    created_at: datetime = Field(alias="createdAt")
    file_size_in_bytes: Optional[int] = Field(None, alias="fileSizeInBytes")
    is_favorite: bool = Field(False, alias="isFavorite")
    is_archived: bool = Field(False, alias="isArchived")
    is_trashed: bool = Field(False, alias="isTrashed")
    deleted_at: Optional[datetime] = Field(None, alias="deletedAt")


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
