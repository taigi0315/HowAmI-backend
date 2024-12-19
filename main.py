# main.py
from fastapi import FastAPI, HTTPException, Request, Body
from firebase_admin import credentials, firestore, initialize_app
from fastapi.middleware.cors import CORSMiddleware
from model.user import User
from typing import Dict, Any
import os
import json

from fastapi.staticfiles import StaticFiles

def get_firebase_creds():
    # Base64로 인코딩된 private key를 디코드
    private_key_base64 = os.getenv('FIREBASE_PRIVATE_KEY_BASE64')
    if private_key_base64:
        private_key = base64.b64decode(private_key_base64).decode('utf-8')
    else:
        private_key = os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')

    cred_dict = {
        "type": "service_account",
        "project_id": os.getenv('FIREBASE_PROJECT_ID'),
        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
        "private_key": private_key,
        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
    }
    
    return credentials.Certificate(cred_dict)


# Initialize Firebase Admin SDK
cred = get_firebase_creds()
initialize_app(cred)
db = firestore.client()
user_ref = db.collection("users")

# Create a single FastAPI instance
app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.1.170:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Cross-Origin-Opener-Policy"],
    allow_origin_regex="https?://.*",
)

# Helper functions
def get_user_document(user_id: str):
    user_document = user_ref.document(user_id)
    user_snapshot = user_document.get()
    if not user_snapshot.exists:
        raise HTTPException(status_code=404, detail="User not found.")
    return user_document, user_snapshot.to_dict()

# ================ USER ROUTES ==========================
@app.get("/users")
async def get_users():
    try:
        users = [doc.to_dict() for doc in user_ref.stream()]
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users")
async def create_user(user: User):
    try:
        user_ref.document(user.id).set(user.dict())
        return {"message": "User added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}")
async def update_user(user_id: str, user: User):
    try:
        user_document, _ = get_user_document(user_id)
        user_document.update(user.dict())
        return {"message": "User updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/create-or-fetch")
async def create_or_fetch_user(user: User):
    try:
        existing_user = user_ref.document(user.id).get()
        if existing_user.exists:
            return existing_user.to_dict()
        user_ref.document(user.id).set(user.dict())
        return user.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= ITEM ROUTES =========================
@app.post("/users/{user_id}/add-item")
async def add_item(user_id: str, payload: Dict[str, Any] = Body(...)):
    key = payload.get("key")
    item = payload.get("item")

    if not key or not item:
        raise HTTPException(status_code=400, detail="Invalid data.")

    user_document, user_data = get_user_document(user_id)
    existing_items = user_data.get(key, [])
    if not isinstance(existing_items, list):
        existing_items = []

    updated_items = existing_items + [item]
    user_document.update({key: updated_items})

    return {"message": "Item added successfully"}

@app.put("/users/{user_id}/update-item")
async def update_item(user_id: str, payload: Dict[str, Any] = Body(...)):
    key = payload.get("key")
    items = payload.get("items")
    if not key or not items:
        raise HTTPException(status_code=400, detail="Invalid data.")

    user_document, _ = get_user_document(user_id)
    user_document.update({key: items})

    return {"message": "Items updated successfully."}

@app.post("/users/{user_id}/remove-item")
async def remove_item(user_id: str, key: str, item: str, result: str):
    try:
        user_document, user_data = get_user_document(user_id)
        if key not in user_data or item not in user_data[key]:
            raise HTTPException(status_code=400, detail="Item not found.")
        user_data[key].remove(item)
        user_document.update({key: user_data[key], "result": result})
        return {"message": "Item removed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= PROFILE ROUTES ======================
@app.put("/users/{user_id}/update-profile")
async def update_profile(user_id: str, data: Dict[str, Any] = Body(...)):
    try:
        user_document, _ = get_user_document(user_id)
        user_document.update({
            "profile_image": data.get("profile_image")
        })
        return {"message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= HEALTH CHECK ========================
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ================= OPTIONS ROUTE =======================
@app.options("/users/create-or-fetch")
async def options_handler(request: Request):
    return {}

