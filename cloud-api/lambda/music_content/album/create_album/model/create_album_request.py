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
    year: int = Field(..., ge=1900, le=2100)
    cover_type: str = Field(default="image/jpeg", pattern="^image/")
    description: Optional[str] = Field(None, max_length=1000)
    songs: List[SongData] = Field(..., min_items=1, max_items=50)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Greatest Hits",
                "artists": ["ARTIST#123"],
                "genres": ["Pop", "Rock"],
                "year": 2024,
                "cover_type": "image/jpeg",
                "description": "Best songs collection",
                "songs": [
                    {
                        "title": "Song One",
                        "audio_type": "audio/mpeg",
                        "duration": 180
                    },
                    {
                        "title": "Song Two",
                        "audio_type": "audio/mpeg",
                        "duration": 210
                    }
                ]
            }
        }