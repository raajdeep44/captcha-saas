from pydantic import BaseModel

class AdminCreate(BaseModel):
    username : str
    email : str
    password : str

class AdminLogin(BaseModel):
    email : str
    password : str

    