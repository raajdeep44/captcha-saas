from sqlalchemy import Column, Integer, String , Boolean , DateTime,ForeignKey
from app.config import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    auth_token = Column(String(500),nullable=False)

    websites = relationship("Website", back_populates="user", cascade="all, delete-orphan")

class Website(Base):
    __tablename__ = "websites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    website_name = Column(String(100), nullable=False)
    website_url = Column(String(200), nullable=False)
    api_key = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="websites")
    stats = relationship("CaptchaStats", uselist=False, back_populates="website", cascade="all, delete-orphan")
    captchas = relationship("Captcha", back_populates="website", cascade="all, delete-orphan")

class CaptchaStats(Base):
    __tablename__ = "captcha_stats"

    id = Column(Integer, primary_key=True,index=True)
    website_id = Column(Integer,ForeignKey("websites.id"),nullable=False)
    total_generated = Column(Integer,nullable=False,default=0)
    total_verified_success = Column(Integer,nullable=False,default=0)
    total_verified_failed = Column(Integer,nullable=False,default=0)
    last_used = Column(DateTime, nullable=True)

    website = relationship("Website", back_populates="stats")


class CaptchaAttempts(Base):
    __tablename__ = "captcha_attempts"

    id = Column(Integer,primary_key=True,index=True)
    captcha_id = Column(Integer, ForeignKey("captchas.id"), nullable=False)
    user_ip = Column(String,nullable=False)
    success = Column(Boolean,default=False)
    verified_at = Column(DateTime, default=datetime.utcnow)

    captcha = relationship("Captcha", back_populates="attempts")
    


class Captcha(Base):
    __tablename__ = "captchas"
    id = Column(Integer, primary_key=True,index=True)
    website_id = Column(Integer, ForeignKey("websites.id"),nullable=False)
    value = Column(String,nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    website = relationship("Website", back_populates="captchas")
    attempts = relationship("CaptchaAttempts", back_populates="captcha", cascade="all, delete-orphan")
