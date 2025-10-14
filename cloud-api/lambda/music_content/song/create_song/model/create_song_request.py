from typing import List, Optional

from pydantic import BaseModel


class CreateSongRequest(BaseModel):
    title: str
    genres: List[str] = []
    artists: List[str] = []
    album_id: Optional[str] = ""
    description: Optional[str] = ""
    cover_type: str
    audio_type: str