from pydantic import BaseModel, Field


class SubscriptionRequest(BaseModel):
    content_id: str = Field(..., min_length=1, description="The content identifier.")
    content_type: str = Field(..., min_length=1, description="The content type.")
