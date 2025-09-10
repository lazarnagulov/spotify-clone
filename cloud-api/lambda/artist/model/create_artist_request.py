from pydantic import BaseModel, StringConstraints
from typing import Annotated, List

class CreateArtistRequest(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    genres: List[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]]
    bio: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=1000)]
