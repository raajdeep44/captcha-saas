# app/captcha.py

from fastapi import APIRouter, Query, Header, HTTPException
from pydantic import BaseModel
from captcha.image import ImageCaptcha
import random
import string
import io
from fastapi.responses import StreamingResponse

router = APIRouter()

# In-memory store (replace with Redis/DB in prod)
captcha_store = {}

# Dummy keys (for testing)
VALID_API_KEYS = {"abc123", "testkey","ck_jpbb8bo7rxf32kb4gh39u6"}

class CaptchaInput(BaseModel):
    captcha_id: str
    user_input: str

def valid_api_key(key: str) -> bool:
    return key in VALID_API_KEYS

@router.get("/generate-captcha")
def generate_captcha(api_key: str = Query(...)):
    if not valid_api_key(api_key):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    captcha_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    captcha_store[captcha_id] = captcha_text

    image = ImageCaptcha()
    image_bytes = io.BytesIO()
    image.write(captcha_text, image_bytes)
    image_bytes.seek(0)

    headers = {"captcha-id": captcha_id}
    return StreamingResponse(content=image_bytes, media_type="image/png", headers=headers)

@router.post("/verify-captcha")
def verify_captcha(data: CaptchaInput, x_api_key: str = Header(...)):
    if not valid_api_key(x_api_key):
        raise HTTPException(status_code=403, detail="Invalid API Key")

    stored_value = captcha_store.get(data.captcha_id)
    if not stored_value:
        raise HTTPException(status_code=404, detail="Captcha ID not found")

    if data.user_input.upper() == stored_value.upper():
        return {"success": True, "message": "CAPTCHA verified âœ…"}
    else:
        return {"success": False, "message": "CAPTCHA failed âŒ"}