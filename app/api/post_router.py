from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.post import PostResponse
from app.services.post_service import PostService
import logging

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/get_last_posts", response_model=List[PostResponse])
def get_last_posts_api(tag: Optional[str] = Query(None), db: Session = Depends(get_db)):
    posts = PostService.get_last_posts(db)
    if tag:
        tag_lower = tag.lower()
        for post in posts:
            post.has_tag = any(tag_lower == t.lower() for t in post.tags)
    return posts
