from fastapi import Request, HTTPException
from firebase_admin import auth as firebase_auth, credentials, initialize_app
import os
import firebase_admin
from dotenv import load_dotenv
load_dotenv()

# 🔐 Set your allowed domain
ALLOWED_DOMAIN = "kaiko.com"

FIREBASE_JSON_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT")

if not FIREBASE_JSON_PATH:
    raise RuntimeError("Missing FIREBASE_SERVICE_ACCOUNT env variable")

cred = credentials.Certificate(FIREBASE_JSON_PATH)
initialize_app(cred)

# ✅ Token verification + domain restriction
async def verify_token(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.split("Bearer ")[-1]
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        email = decoded_token.get("email")

        if not email or not email.endswith(f"@{ALLOWED_DOMAIN}"):
            raise HTTPException(status_code=403, detail="Unauthorized domain")

        return decoded_token
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
