from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_id = Column(String, unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

class URLStats(Base):
    __tablename__ = "url_stats"

    id = Column(Integer, primary_key=True, index=True)
    short_id = Column(String, ForeignKey("urls.short_id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip = Column(String, nullable=True)
    country = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    os = Column(String, nullable=True)
    device = Column(String, nullable=True)
    referrer = Column(String, nullable=True)
