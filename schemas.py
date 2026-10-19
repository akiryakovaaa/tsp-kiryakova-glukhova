from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from models import PostType, UserRole

# входная схема для регистрации нового пользователя (POST /users/register).
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

# входная схема для аутентификации (POST /users/login)
class UserLogin(BaseModel):
    username: str
    password: str

# выходная схема для отправки данных пользователя клиенту
class UserResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

# входная схема для создания публикации (POST /posts)
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1)
    description: Optional[str] = None
    post_type: PostType = PostType.recipe
    is_published: bool = False
    tag_ids: Optional[list[int]] = None

# выходная схема для возврата данных о публикации клиенту
class PostResponse(BaseModel):
    id: int
    title: str
    body: str
    author_id: int

    model_config = ConfigDict(from_attributes=True)

# входная схема для создания тега (POST /tags)
class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

# выходная схема для возврата данных о теге клиенту
class TagResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)