from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = ""


class CategoryOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""


class BlogCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    category: str
    tags: List[str] = []
    published: bool = True


class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    published: Optional[bool] = None


class BlogOut(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    author: str
    published: bool
    created_at: datetime
    updated_at: datetime
