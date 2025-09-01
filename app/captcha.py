# app/captcha.py

from fastapi import APIRouter, Query, Header, HTTPException , Depends,Request,Header
from pydantic import BaseModel
from captcha.image import ImageCaptcha
import random
import string
import io
from fastapi.responses import StreamingResponse
from app import models,schemas
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from app.config import SessionLocal
from datetime import datetime
from fastapi import Path
from app.models import Captcha, CaptchaAttempts
from app.auth import get_current_user
from datetime import datetime,timedelta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CaptchaInput(BaseModel):
    captcha_id: str
    user_input: str

def valid_api_key(api_key: str, db : Session):
    website = db.query(models.Website).filter(
        models.Website.api_key == api_key,
        models.Website.is_active == True
    ).first()
    if not website:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return website

def get_or_create_stats(db: Session,website_id : int) -> models.CaptchaStats:
    stats = db.query(models.CaptchaStats).filter(
        models.CaptchaStats.website_id == website_id
    ).first()
    if not stats:
        stats = models.CaptchaStats(website_id = website_id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
    return stats

@router.get("/generate-captcha")
def generate_captcha(api_key: str = Query(...),db : Session = Depends(get_db)):
    website = valid_api_key(api_key,db)
    
    # captcha stats

    stats = get_or_create_stats(db,website.id)
    stats.total_generated += 1  
    stats.last_used = datetime.utcnow()
    db.commit()
    
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    # storing captcha text in db
    captcha_db = Captcha(
        website_id = website.id,
        value = captcha_text
    )
    db.add(captcha_db)
    db.commit()
    db.refresh(captcha_db)

    # captcha_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    # captcha_store[captcha_id] = captcha_text

    image = ImageCaptcha()
    image_bytes = io.BytesIO()
    image.write(captcha_text, image_bytes)
    image_bytes.seek(0)

    # headers = {"captcha-id": captcha_id}
    headers = {"captcha-id": str(captcha_db.id)}
    return StreamingResponse(content=image_bytes, media_type="image/png", headers=headers)

@router.post("/verify-captcha")
def verify_captcha(data: CaptchaInput, request: Request, x_api_key: str = Header(...), db: Session = Depends(get_db)):
    website = valid_api_key(x_api_key, db)
        
    # stored_value = captcha_store.get(data.captcha_id)
    captcha = db.query(Captcha).filter(Captcha.id == data.captcha_id).first()
    if not captcha:
        raise HTTPException(status_code=404, detail="Captcha ID not found")
    
    stats = get_or_create_stats(db,website.id)
    success = data.user_input.upper() == captcha.value.upper()
    if success:
        stats.total_verified_success += 1
    else:
        stats.total_verified_failed += 1
    
    # Optional: store user attempt
    user_ip = request.client.host
    attempt = CaptchaAttempts(
        captcha_id=captcha.id,
        website_id = website.id,
        user_ip=user_ip,
        success=success
    )
    db.add(attempt)
    
    stats.last_used = datetime.utcnow()
    db.commit()
    
    return {"success": success, "message": "CAPTCHA verified" if success else "CAPTCHA failed"}




@router.get("/stats/{website_id}")
def get_stats(current_user :models.User = Depends(get_current_user), website_id: int = Path(...), db: Session = Depends(get_db)):
    stats = db.query(models.CaptchaStats).filter(models.CaptchaStats.website_id == website_id).first()
    if not stats:
        return {
            "website_id": website_id,
            "total_generated": 0,
            "total_verified_success": 0,
            "total_verified_failed": 0,
            "success_rate": 0.0,
            "last_used": None,
        }

    total_attempted = stats.total_verified_success + stats.total_verified_failed
    success_rate = (stats.total_verified_success / total_attempted * 100.0) if total_attempted else 0.0

    return {
        "website_id": website_id,
        "total_generated": stats.total_generated,
        "total_verified_success": stats.total_verified_success,
        "total_verified_failed": stats.total_verified_failed,
        "success_rate": round(success_rate, 2),
        "last_used": stats.last_used,
    }


@router.get("/recent-activity")
def get_recent_activity(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    websites = db.query(models.Website).filter(models.Website.user_id == current_user.id).all()
    website_ids = [w.id for w in websites]

    attempts = (
        db.query(models.CaptchaAttempts, models.Website.website_name)
        .join(models.Captcha, models.Captcha.id == models.CaptchaAttempts.captcha_id)
        .join(models.Website, models.Website.id == models.Captcha.website_id)
        .filter(models.Website.id.in_(website_ids))
        .order_by(models.CaptchaAttempts.verified_at.desc())
        .all()
    )

    results = []
    for attempt, website_name in attempts:
        results.append({
            "id": attempt.id,
            "website": website_name,
            "ip": attempt.user_ip,
            "status": attempt.success,
            "time": attempt.verified_at
        })

    return results

@router.get("/attempts/last-30-days/{website_id}")
def get_captcha_attempts_last_30_days(
    website_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # ensures only logged-in user
):
    # Verify that the website belongs to the current user
    website = db.query(models.Website).filter(
        models.Website.id == website_id,
        models.Website.user_id == current_user.id
    ).first()

    if not website:
        raise HTTPException(status_code=403, detail="Not authorized to view this website")

    # Calculate last 30 days window
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    count = db.query(models.CaptchaAttempts).filter(
        models.CaptchaAttempts.website_id == website_id,
        models.CaptchaAttempts.verified_at >= thirty_days_ago
    ).count()

    return {
        "website_id": website_id,
        "captcha_attempts_last_30_days": count
    }

@router.get("/attempts/daily/{website_id}")
def get_captcha_attempts_daily(
    website_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):  
    website = db.query(models.Website).filter(
        models.Website.id == website_id,
        models.Website.user_id == current_user.id
    ).first()

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    results = (
        db.query(
            func.date(models.CaptchaAttempts.verified_at).label("date"),
            func.count().label("total"),
            func.sum(case((models.CaptchaAttempts.success == True, 1), else_=0)).label("success"),
            func.sum(case((models.CaptchaAttempts.success == False, 1), else_=0)).label("failed"),
        )
        .filter(
            models.CaptchaAttempts.website_id == website_id,
            models.CaptchaAttempts.verified_at >= thirty_days_ago
        )
        .group_by(func.date(models.CaptchaAttempts.verified_at))
        .order_by(func.date(models.CaptchaAttempts.verified_at))
        .all()
    )

    daily_stats = []
    for row in results:
        success_rate = (row.success / row.total * 100) if row.total > 0 else 0
        daily_stats.append({
            "date": row.date,
            "total": row.total,
            "success": row.success,
            "failed": row.failed,
            "success_rate": f"{success_rate:.2f}%"
        })

    return {"website_id": website_id, "daily_statistics": daily_stats}


