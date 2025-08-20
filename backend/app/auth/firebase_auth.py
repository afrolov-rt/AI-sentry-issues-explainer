import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.settings import settings
from app.models.schemas import User
from app.models.database import get_database
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        if not firebase_admin._apps:
            if settings.FIREBASE_ADMIN_SDK_PATH and os.path.exists(settings.FIREBASE_ADMIN_SDK_PATH):
                cred = credentials.Certificate(settings.FIREBASE_ADMIN_SDK_PATH)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully")
            else:
                logger.warning("Firebase Admin SDK path not found or not configured")
                return False
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        return False


security = HTTPBearer()

class FirebaseAuth:
    def __init__(self):
        self.initialized = initialize_firebase()
    
    async def verify_token(self, token: str) -> Optional[dict]:
        """Verify Firebase ID token"""
        if not self.initialized:
            raise HTTPException(status_code=500, detail="Firebase not initialized")
        
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except auth.InvalidIdTokenError:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        except auth.ExpiredIdTokenError:
            raise HTTPException(status_code=401, detail="Authentication token expired")
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    async def get_or_create_user(self, firebase_user: dict) -> User:
        """Get existing user or create new one"""
        db = get_database()
        

        existing_user = await db.users.find_one({"firebase_uid": firebase_user["uid"]})
        
        if existing_user:

            update_data = {}
            if existing_user.get("email") != firebase_user.get("email"):
                update_data["email"] = firebase_user.get("email")
            if existing_user.get("display_name") != firebase_user.get("name"):
                update_data["display_name"] = firebase_user.get("name")
            
            if update_data:
                await db.users.update_one(
                    {"firebase_uid": firebase_user["uid"]},
                    {"$set": update_data}
                )
                existing_user.update(update_data)
            
            return User(**existing_user)
        

        new_user = User(
            firebase_uid=firebase_user["uid"],
            email=firebase_user.get("email", ""),
            display_name=firebase_user.get("name"),
            role="developer"
        )
        
        user_dict = new_user.dict(exclude={"id"})
        result = await db.users.insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)
        
        return User(**user_dict)


firebase_auth = FirebaseAuth()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    firebase_user = await firebase_auth.verify_token(token)
    user = await firebase_auth.get_or_create_user(firebase_user)
    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """Optional authentication dependency"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        firebase_user = await firebase_auth.verify_token(token)
        user = await firebase_auth.get_or_create_user(firebase_user)
        return user
    except HTTPException:
        return None
