from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: int
    username: str
    email: str


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=25)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=25)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)
