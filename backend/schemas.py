from pydantic import BaseModel, HttpUrl, EmailStr
from typing import Optional
from datetime import datetime

class URLBase(BaseModel):
    original_url: HttpUrl

class URLCreate(URLBase):
    title: Optional[str] = None

class URLUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None

class URLResponse(URLBase):
    short_id: str
    title: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

class URLStatsResponse(BaseModel):
    total_clicks: int
    browsers: dict
    countries: dict
    os: dict
    referrers: dict

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
