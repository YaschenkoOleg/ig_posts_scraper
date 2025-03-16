# models/post.py
from sqlalchemy import Column, Integer, String, DateTime, ARRAY, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True, index=True, nullable=False) # Instagram post ID
    comments = Column(String, nullable=True)
    likes = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    date = Column(DateTime(timezone=True), server_default=func.now())