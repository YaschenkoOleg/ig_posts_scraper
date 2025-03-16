# app/services/post_service.py
import logging
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import desc
from app.models.post import Post

logger = logging.getLogger(__name__)

class PostService:
    @staticmethod
    def get_post_by_id(db: Session, post_id: str) -> Optional[Post]:
        return db.query(Post).filter(Post.post_id == post_id).first()

    @staticmethod
    def create_post(db: Session, post_data: dict) -> Optional[Post]:

        # Перевіряємо, чи існує пост з таким post_id
        existing_post = PostService.get_post_by_id(db, post_data.get("post_id"))
        if existing_post:
            logger.info(f"Пост з id {post_data.get('post_id')} вже існує. Пропускаємо.")
            return existing_post

        try:
            post = Post(**post_data)
            db.add(post)
            db.commit()
            db.refresh(post)
            logger.info(f"Пост з id {post_data.get('post_id')} додано до бд")
            return post
        except Exception as e:
            db.rollback()
            logger.error(f"Помилка додавання поста: {str(e)}")
            raise ValueError(f"Помилка додавання поста: {str(e)}")

    @staticmethod
    def get_last_posts(db: Session, limit: int = 10, tag: Optional[str] = None):
        query = db.query(Post).order_by(desc(Post.date)).limit(limit).all()

        if tag:
            for post in query:
                post.has_tag = tag.lower() in [t.lower() for t in (post.tags or [])]
        return query