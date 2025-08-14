from fastapi import FastAPI , Depends , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app import auth, models, config , captcha
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from app.models import User
from app.config import get_db
from sqlalchemy.orm import Session
# In your main.py or wherever you initialize FastAPI
# from app.website import router as website_router



app = FastAPI()

#  CORS CONFIG HERE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["captcha-id"],  # <-- 🔥 this is important!
)

# DB setup
models.Base.metadata.create_all(bind=config.engine)


# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Routers
app.include_router(auth.router)
app.include_router(captcha.router)
# app.include_router(website_router, prefix="/api", tags=["websites"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# dashboard

# def get_current_user(token : str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token,os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
#         username = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401,detail="invalid token")
#         return username
#     except JWTError:
#         raise HTTPException(status_code=401,detail="token verification failed")

from app.config import Base, engine
Base.metadata.create_all(bind=engine)




