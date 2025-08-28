from sqlalchemy import Column,Integer,String
from app.config import Base

class Admin(Base):

    __tablename__ = "admins"

    id = Column(Integer,primary_key=True,index=True)
    username = Column(String(100),unique=True,index=True)
    email = Column(String(100),unique=True,index=True)
    password = Column(String)   
    admin_auth_token = Column(String(255),unique=True,nullable=True,index=True)