from pydantic import BaseModel, Field, EmailStr, ConfigDict

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    author_id: int


class PostResponse(BaseModel):
    id: int
    title: str
    content: str = Field(validation_alias="body")
    author_id: int

    model_config = ConfigDict(from_attributes=True)

class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class TagResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)