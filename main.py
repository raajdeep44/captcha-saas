from fastapi import FastAPI , Depends , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app import auth, models, config , captcha , admin
# from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os
from app.models import User
from app.config import get_db
from sqlalchemy.orm import Session
# In your main.py or wherever you initialize FastAPI
from app.website import router as website_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
from app.auth import get_current_user   
from fastapi.responses import FileResponse


app = FastAPI()

security = HTTPBearer()  # tells Swagger this API uses HTTP Bearer auth


#  CORS CONFIG HERE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # <-- 🔥 this is important!
)


# DB setup
models.Base.metadata.create_all(bind=config.engine)

# @app.get("/config.js")
# def config_js():
#     api_base = os.getenv("API_BASE", "http://127.0.0.1:8000")
#     js_content = f"const API_BASE = '{api_base}';"
#     return PlainTextResponse(js_content, media_type="application/javascript")


# Routers
app.include_router(auth.router,tags=["auth"])
app.include_router(captcha.router,tags=["captcha"])
app.include_router(website_router, prefix="/api", tags=["websites"])
app.include_router(admin.router,tags=["admin"])
# app.include_router(admin_auth.router,tags=["admin"])
# app.include_router(admin_routes.router,tags=["admin"])
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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




app.mount("/", StaticFiles(directory="frontend", html=True), name="user")

app.mount("/", StaticFiles(directory="admin_frontend", html=True), name="admin")

# app.mount("/user", StaticFiles(directory="frontend", html=True), name="user_dashboard")
# app.mount("/admin", StaticFiles(directory="admin_frontend", html=True), name="admin_dashboard")

# @app.get("/dashboard")
# def dashboard(current_user=Depends(get_current_user)):
#     if current_user.role == "admin":
#         return FileResponse("admin_frontend/index.html")
#     else:
#         return FileResponse("frontend/index.html")