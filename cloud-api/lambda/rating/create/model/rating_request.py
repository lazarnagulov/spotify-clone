from pydantic import BaseModel, conint


class RatingRequest(BaseModel):
    rating: conint(ge=1, le=5)
    content_id: str
    content_type: str