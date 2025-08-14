# # website.py (Corrected)

# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# import secrets
# import string

# # Removed redundant imports that are no longer needed here
# from app import schemas, models
# from app.config import get_db # Import get_db from config
# from app.auth import get_current_user # Import get_current_user from auth

# router = APIRouter()

# # Removed redundant get_db() function.
# # Removed redundant get_current_user() function.

# def generate_api_key() -> str:
#     """Generate a secure API key"""
#     prefix = "ck_"
#     random_part = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(32))
#     return f"{prefix}{random_part}"

# @router.post("/websites", response_model=schemas.WebsiteResponse)
# def create_website(
#     website: schemas.WebsiteCreate,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Create a new website for the current user"""
#     existing_website = db.query(models.Website).filter(
#         models.Website.user_id == current_user.id,
#         models.Website.website_url == website.website_url
#     ).first()
    
#     if existing_website:
#         raise HTTPException(
#             status_code=400,
#             detail="Website URL already exists for your account"
#         )
    
#     api_key = generate_api_key()
    
#     while db.query(models.Website).filter(models.Website.api_key == api_key).first():
#         api_key = generate_api_key()
    
#     db_website = models.Website(
#         user_id=current_user.id,
#         website_name=website.website_name,
#         website_url=website.website_url,
#         api_key=api_key
#     )
    
#     db.add(db_website)
#     db.commit()
#     db.refresh(db_website)
    
#     return db_website

# # ... (The rest of the CRUD endpoints remain the same) ...
# # They will now use the imported get_current_user and get_db dependencies.

# @router.get("/websites", response_model=List[schemas.WebsiteResponse])
# def get_user_websites(
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     websites = db.query(models.Website).filter(
#         models.Website.user_id == current_user.id
#     ).order_by(models.Website.created_at.desc()).all()
    
#     return websites

# @router.get("/websites/{website_id}", response_model=schemas.WebsiteResponse)
# def get_website(
#     website_id: int,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     website = db.query(models.Website).filter(
#         models.Website.id == website_id,
#         models.Website.user_id == current_user.id
#     ).first()
    
#     if not website:
#         raise HTTPException(status_code=404, detail="Website not found")
    
#     return website

# @router.put("/websites/{website_id}", response_model=schemas.WebsiteResponse)
# def update_website(
#     website_id: int,
#     website_update: schemas.WebsiteUpdate,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     website = db.query(models.Website).filter(
#         models.Website.id == website_id,
#         models.Website.user_id == current_user.id
#     ).first()
    
#     if not website:
#         raise HTTPException(status_code=404, detail="Website not found")
    
#     if website_update.website_name is not None:
#         website.website_name = website_update.website_name
#     if website_update.website_url is not None:
#         existing = db.query(models.Website).filter(
#             models.Website.user_id == current_user.id,
#             models.Website.website_url == website_update.website_url,
#             models.Website.id != website_id
#         ).first()
#         if existing:
#             raise HTTPException(status_code=400, detail="Website URL already exists")
#         website.website_url = website_update.website_url
#     if website_update.is_active is not None:
#         website.is_active = website_update.is_active
    
#     db.commit()
#     db.refresh(website)
    
#     return website

# @router.post("/websites/{website_id}/regenerate-key", response_model=schemas.WebsiteResponse)
# def regenerate_api_key(
#     website_id: int,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     website = db.query(models.Website).filter(
#         models.Website.id == website_id,
#         models.Website.user_id == current_user.id
#     ).first()
    
#     if not website:
#         raise HTTPException(status_code=404, detail="Website not found")
    
#     new_api_key = generate_api_key()
    
#     while db.query(models.Website).filter(models.Website.api_key == new_api_key).first():
#         new_api_key = generate_api_key()
    
#     website.api_key = new_api_key
#     db.commit()
#     db.refresh(website)
    
#     return website

# @router.delete("/websites/{website_id}")
# def delete_website(
#     website_id: int,
#     current_user: models.User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     website = db.query(models.Website).filter(
#         models.Website.id == website_id,
#         models.Website.user_id == current_user.id
#     ).first()
    
#     if not website:
#         raise HTTPException(status_code=404, detail="Website not found")
    
#     db.delete(website)
#     db.commit()
    
#     return {"message": "Website deleted successfully"}

# def validate_api_key(api_key: str, db: Session) -> models.Website:
#     website = db.query(models.Website).filter(
#         models.Website.api_key == api_key,
#         models.Website.is_active == True
#     ).first()
    
#     if not website:
#         raise HTTPException(status_code=403, detail="Invalid or inactive API key")
    
#     return website