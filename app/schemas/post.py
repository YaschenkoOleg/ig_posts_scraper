from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class PostResponse(BaseModel):
    post_id: str
    comments: Optional[str] = None
    likes: Optional[str] = None
    description: Optional[str] = None
    tags: List[str]
    date: datetime
    has_tag: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)
