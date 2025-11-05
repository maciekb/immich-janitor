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


class AssetBulkDeleteRequest(BaseModel):
    """Request model for bulk delete operation."""

    ids: list[str]
    force: bool = False
