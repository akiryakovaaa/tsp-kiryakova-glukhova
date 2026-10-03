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

from sqlalchemy.orm import relationship, Mapped, mapped_column # связи таблиц (М:М, 1:1) и типизация колонок
from sqlalchemy.sql import func # фиксация времени сервером
from typing import List, Optional # List для множественных связей, Optional для полей, допускающих NULL
from datetime import datetime # тип данных для хранения даты и времени

from database import Base

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    favorites: Mapped[List["Favorite"]] = relationship(back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    post_type: Mapped[PostType] = mapped_column(Enum(PostType))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    favorites: Mapped[List["Favorite"]] = relationship(back_populates="post") # у одного поста может быть много добавлений в избранное
    tags: Mapped[List["Tag"]] = relationship(secondary=post_tags, back_populates="posts") # у поста много тегов, один тег может принадлежать множеству постов

class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="favorites")
    post: Mapped["Post"] = relationship(back_populates="favorites")

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    posts: Mapped[List["Post"]] = relationship(secondary=post_tags, back_populates="tags")