from pydantic import BaseModel, Field


class SubscriptionRequest(BaseModel):
    content_id: str = Field(..., min_length=1, description="The content identifier.")
    name: str = Field(..., min_length=1, max_length=100, description="The name of the subscriber.")
    username: str = Field(..., min_length=1, max_length=50, description="The username of the subscriber.")
