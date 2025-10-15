from typing import List, Optional
from pydantic import BaseModel, Field


class CreateSongRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    genres: List[str] = Field(default_factory=list)
    artists: List[str] = Field(default_factory=list)
    album_id: Optional[str] = None
    description: Optional[str] = None
    cover_type: str
    audio_type: str
