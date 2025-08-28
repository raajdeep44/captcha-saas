from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app import utils
from . import admin_model, admin_schemas 
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

load_dotenv()
router = APIRouter()
admin_security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def get_current_admin(
      credentials : HTTPAuthorizationCredentials = Depends(admin_security),
      db : Session = Depends(get_db) 
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not an admin")
        username : str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401,detail="Invalid Token")
    except JWTError:
        raise HTTPException(status_code=401,detail="Invalid Token")
    
    admin = db.query(admin_model.Admin).filter(admin_model.Admin.username == username).first()
    if not admin:
        raise HTTPException(status_code=404,detail="admin not found")
    return admin



@router.post("/maalik/register")
def register_admin(admin : admin_schemas.AdminCreate, db : Session = Depends(get_db)):

    if db.query(admin_model.Admin).filter(admin_model.Admin.email == admin.email).first():
        raise HTTPException(status_code=400,detail="email already exists")
    if db.query(admin_model.Admin).filter(admin_model.Admin.username == admin.username).first():
        raise HTTPException(status_code=400,detail="username already exists")
    
    hashed_pwd = utils.hash_password(admin.password)
    db_admin = admin_model.Admin(
        username = admin.username,
        email = admin.email,
        password = hashed_pwd
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)

    return {"message": "admin registered successfully", "username": admin.username}
    
@router.post("/maalik/login")
def admin_login(admin : admin_schemas.AdminLogin, db : Session = Depends(get_db)):
    db_admin = db.query(admin_model.Admin).filter(admin_model.Admin.email == admin.email).first()
    if not db_admin or not utils.verify_password(admin.password,db_admin.password):
        raise HTTPException(status_code=400,detail="Invalid admin details")
    
    subject = f"{db_admin.username}"
    token = utils.create_access_token(data={"sub":subject, "role":"admin"})
    db_admin.admin_auth_token = token 
    db.commit()
    return {"message":"Admin login Successful","username":db_admin.username,"access_token": token,"email": db_admin.email}
