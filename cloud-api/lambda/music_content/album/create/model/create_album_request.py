from datetime import datetime

from pydantic import BaseModel, Field

from typing import List, Optional


class SongData(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    audio_type: str = Field(..., pattern="^audio/")
    duration: Optional[int] = Field(None, ge=0)
    description: Optional[str] = Field(None, min_length=1, max_length=200)


class CreateAlbumRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    artists: List[str] = Field(..., min_items=1)
    genres: List[str] = Field(..., min_items=1)
    year: int = Field(..., ge=1900, le=datetime.now().year)
    cover_type: str = Field(default="image/jpeg", pattern="^image/")
    description: Optional[str] = Field(None, max_length=1000)
    songs: List[SongData] = Field(..., min_items=1, max_items=50)