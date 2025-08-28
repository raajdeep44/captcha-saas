from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
# from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app import schemas, models, utils
from app.config import SessionLocal
from jose import JWTError, jwt
import secrets
import os,httpx
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

IPINFO_TOKEN = os.getenv("IPINFO_APIKEY")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
security = HTTPBearer()  # tells Swagger this API uses HTTP Bearer auth


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):  
    token = credentials.credentials
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("jwt token :",payload)
        # Extract user_id ("sub" claim from JWT)
        # id : int = payload.get("sub")
        username : str = payload.get("sub").split("_")[0]
        # print("user id :",user_id)
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    except JWTError:
        # If token invalid/expired
        raise HTTPException(status_code=401, detail="Invalid token")

    # Look up the user in DB
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Return the user → now endpoint has `current_user`
    return user



# @router.post("/register", response_model=schemas.ShowUser)
@router.post("/register")
def register(user: schemas.UserCreate,request: Request, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = utils.hash_password(user.password)
    
    user_ip = request.client.host
    # user_ip =  "122.176.125.107"
    print("ipinfo api key ",IPINFO_TOKEN)
    url = f"https://ipinfo.io/{user_ip}/json?token={IPINFO_TOKEN}"
    res = httpx.get(url)
   
    if res.status_code == 200:
        data = res.json()
        region = data.get("region")
        print("region",region)
        city = data.get("city")
        print("city ",city)
        country = data.get("country")
    else: 
        region = country = city = None
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd,
        role = 'user',
        ip_address = user_ip,
        region = region,
        city = city,
        country = country
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "user registered successfully"}

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if not db_user or not utils.verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        random_part = secrets.token_hex(5)
        subject = f"{db_user.username}_{random_part}"
        token = utils.create_access_token(data={"sub": subject })
        db_user.auth_token = token
        db.commit()
        return {"message": "Login Successful", "access_token": token, "token_type": "bearer","username":db_user.username , "email" : db_user.email}
    except Exception as e:
        print("Login Error:", e)
        raise HTTPException(status_code=500, detail="Internal server error")


