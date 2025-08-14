from sqlalchemy import Column, Integer, String , Boolean , DateTime,ForeignKey
from app.config import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    auth_token = Column(String(500),nullable=False)

# class APIKey(Base):
#     __tablename__ = "api_keys"
#     id = Column(Integer, primary_key=True, index=True)
#     hashed_key = Column(String, unique=True, index=True, nullable=False)
#     owner = Column(String, nullable=True)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

class Website(Base):
    __tablename__ = "websites"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    website_name = Column(String(100), nullable=False)
    website_url = Column(String(200), nullable=False)
    api_key = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
