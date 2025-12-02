from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class URLBase(BaseModel):
    original_url: HttpUrl

class URLCreate(URLBase):
    pass

class URLResponse(URLBase):
    short_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True

class URLStatsResponse(BaseModel):
    total_clicks: int
    browsers: dict
    countries: dict
    os: dict
    referrers: dict
