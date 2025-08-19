from pydantic import BaseModel, EmailStr
from datetime import datetime
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ShowUser(BaseModel):
    id: int
    username: str
    email: EmailStr


class WebsiteCreate(BaseModel):
    website_name: str
    website_url: str

class WebsiteResponse(BaseModel):
    id: int
    user_id: int
    website_name: str
    website_url: str
    api_key: str
    created_at: datetime
    is_active: bool

    class Config:
        orm_mode = True
