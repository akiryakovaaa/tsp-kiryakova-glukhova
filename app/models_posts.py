import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Table, DateTime, Enum
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class PostType(enum.Enum):
    ARTICLE = "article"
    RECIPE = "recipe"
    NEWS = "news"


# связь Post <-> Tag
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('post_id', Integer, ForeignKey('posts.id', ondelete="CASCADE"), nullable=False),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"), nullable=False)
)

# Tag
class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    posts = relationship('Post', secondary=post_tags, back_populates='tags')

# Post
class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    body = Column(Text, nullable=False)
    post_type = Column(Enum(PostType), nullable=False)

    author_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    is_published = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    tags = relationship('Tag', secondary=post_tags, back_populates='posts')