import enum # создание фиксированных списков (перечислений)

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum, # ограниченный выбор значений
    Table
)
from sqlalchemy.orm import relationship # связи между таблицами (М:М, 1:1)
from sqlalchemy.sql import func # функции бд

from app.database import Base

class UserRole(enum.Enum):
    user = "user"
    admin = "admin"

class PostType(enum.Enum):
    recipe = "recipe"
    news = "news"

# промежуточная таблица
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    favorites = relationship("Favorite", back_populates="user")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    body = Column(Text, nullable=False)
    post_type = Column(Enum(PostType), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    favorites = relationship("Favorite", back_populates="post")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")

class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    user = relationship("User", back_populates="favorites")
    post = relationship("Post", back_populates="favorites")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    posts = relationship("Post", secondary=post_tags, back_populates="tags")