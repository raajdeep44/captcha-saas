from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models, utils
from app.config import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @router.post("/register", response_model=schemas.ShowUser)
@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = utils.hash_password(user.password)
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_pwd)
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

        token = utils.create_access_token(data={"sub": db_user.username})
        db_user.auth_token = token
        db.commit()
        return {"message": "Login Successful", "access_token": token, "token_type": "bearer","username":db_user.username , "email" : db_user.email}
    except Exception as e:
        print("Login Error:", e)
        raise HTTPException(status_code=500, detail="Internal server error")


