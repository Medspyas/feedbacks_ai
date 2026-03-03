from pydantic import BaseModel,  Field, ConfigDict
from datetime import datetime, timezone
from typing import Optional



class Feedback(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    content: str = Field(..., min_length=10)
    rating: int = Field(default=5, ge=1, le=5)


class FeedbackDB(Feedback):
    id : Optional[str] = None
    status: str = "pending"
    ai_analysis: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        )
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )