from fastapi import APIRouter,HTTPException , Depends
from sqlalchemy.orm import Session
from admin import admin_model, admin_auth
from admin.admin_auth import get_current_admin
from app.config import get_db
from app import models,schemas





router = APIRouter()

@router.get("/stats/total-users")
def get_total_users(current_admin: admin_model.Admin = Depends(get_current_admin),db : Session = Depends(get_db)):
    # users = db.query(models.User).filter().all()
    # users = [1,2,3,4]
    # total_users = len(users)

    return {"total_users": 4}


