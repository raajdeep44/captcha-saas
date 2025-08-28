import secrets
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app import models, schemas
from app.config import get_db
from app.auth import get_current_user
from typing import List
from app.models import Website

router = APIRouter()

@router.post("/websites", response_model=schemas.WebsiteResponse)
def create_website(
    data: schemas.WebsiteCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_site = models.Website(
        user_id=current_user.id,
        website_name=data.website_name,
        website_url=data.website_url,
        api_key=secrets.token_hex(16)
    )
    db.add(new_site)
    db.commit()
    db.refresh(new_site)
    return new_site

@router.get("/websites", response_model=List[schemas.WebsiteResponse])
def get_user_websites(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    websites = db.query(models.Website).filter(
        models.Website.user_id == current_user.id
    ).order_by(models.Website.created_at.asc()).all()

    return websites

@router.get("/websites/stats")
def get_stats(current_user :models.User = Depends(get_current_user),db:Session = Depends(get_db)):
    websites = db.query(models.Website).filter(models.Website.user_id == current_user.id).all()
    total_websites = len(websites)

    total_captchas = 0
    total_success = 0
    total_failed = 0
    for site in websites:
        stats = (
            db.query(models.CaptchaStats).filter(models.CaptchaStats.website_id == site.id).first()
        )
        if stats:
            total_captchas += stats.total_generated
            total_success += stats.total_verified_success
            total_failed += stats.total_verified_failed

    success_rate = 0
    if(total_success + total_failed > 0):
        success_rate = (total_success / (total_success + total_failed)) * 100


    return {
        "total_websites":total_websites,
        "total_captchas":total_captchas,
        "captchaSuccessRate": success_rate
    }
    

