from fastapi import APIRouter,HTTPException , Depends
from sqlalchemy.orm import Session
from app.config import get_db
from app import models,schemas
from app.auth import get_current_user


router = APIRouter()


@router.get("/stats-admin/total-users-websites")
def get_total_users_for_admin(current_user : models.User = Depends(get_current_user),db : Session = Depends(get_db)):
    
    if current_user.role != "admin":
        raise HTTPException(status_code=401,detail="role is not valid")
    
    users = db.query(models.User).filter().all()
    total_users = len(users)
    
    websites = db.query(models.Website).filter().all()
    total_websites = len(websites)

    return {"total_users": total_users,"total_websites":total_websites}


@router.get("/stats-admin/catpcha")
def get_captcha_success_rate(current_user : models.User = Depends(get_current_user),db : Session = Depends(get_db)):

    if current_user.role != "admin":
        raise HTTPException(status_code=401,detail="role is not valid")
    
    websites = db.query(models.Website).filter().all()
    total_websites = len(websites)

    total_captchas = 0
    total_success = 0
    total_failed = 0
    data = []
    for site in websites:
        stats = db.query(models.CaptchaStats).filter(models.CaptchaStats.website_id == site.id).first()
        if stats: 
            data.append(stats.id)
            total_captchas += stats.total_generated
            total_success += stats.total_verified_success
            total_failed += stats.total_verified_failed

    success_rate = 0
    if(total_success + total_failed > 0):
        success_rate = (total_success / (total_success + total_failed)) * 100

    return {"success_rate": success_rate}


@router.get("/stats-admin/total-users-data")
def get_all_users_data(current_user : models.User = Depends(get_current_user), db : Session = Depends(get_db)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=401,detail="role not valid")
    
    users = db.query(models.User).filter().all()
    all_data = []
    for user in users:
        data = {
            "username" : user.username,
            "email" : user.email,
            "country": user.country,
            "region": user.region,
            "city":user.city,
            "ip": user.ip_address
        }
        all_data.append(data)

    return all_data

@router.get("/stats-admin/total-websites-data")
def get_all_sites_data(current_user : models.User = Depends(get_current_user), db : Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=401,detail="role is not valid")

    websites = db.query(models.Website).filter().all()
    websites_ids = [w.user_id  for w in websites]

    all_data = (
        db.query(models.Website,models.User)
        .join(models.User,models.User.id == models.Website.user_id)
        .filter(models.User.id.in_(websites_ids))
        .all()
    )

    results = []
    for website,user in all_data:
        data = {
            "username" : user.username,
            "website_name": website.website_name,
            "website_url": website.website_url
        }
        results.append(data)
    

    return results