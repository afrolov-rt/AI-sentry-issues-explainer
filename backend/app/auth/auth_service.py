from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.settings import settings
from app.models.schemas import User, UserResponse
from app.models.database import get_database
from bson import ObjectId
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by username and password"""
        db = get_database()
        user_data = await db.users.find_one({"username": username})
        
        if not user_data:
            return None
        
        if not self.verify_password(password, user_data["hashed_password"]):
            return None
        
        # Convert ObjectId to string
        if "_id" in user_data:
            user_data["id"] = str(user_data["_id"])
            del user_data["_id"]
        
        return User(**user_data)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    async def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token and return user"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            
            db = get_database()
            user_data = await db.users.find_one({"_id": ObjectId(user_id)})
            
            if user_data is None:
                return None
            
            # Convert ObjectId to string
            user_data["id"] = str(user_data["_id"])
            del user_data["_id"]
            
            return User(**user_data)
            
        except JWTError:
            return None
    
    async def create_user(self, username: str, email: str, password: str, full_name: str = None, role: str = "developer") -> User:
        """Create new user"""
        db = get_database()
        
        # Check if user already exists
        existing_user = await db.users.find_one({
            "$or": [
                {"username": username},
                {"email": email}
            ]
        })
        
        if existing_user:
            if existing_user["username"] == username:
                raise HTTPException(status_code=400, detail="Username already exists")
            else:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        # Hash password
        hashed_password = self.get_password_hash(password)
        
        # Create user data
        user_data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "hashed_password": hashed_password,
            "role": role,
            "is_active": True,
            "workspace_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert user
        result = await db.users.insert_one(user_data)
        user_data["id"] = str(result.inserted_id)
        if "_id" in user_data:
            del user_data["_id"]
        
        return User(**user_data)

# Global auth service instance
auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency to get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    user = await auth_service.verify_token(token)
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """Optional authentication dependency"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = await auth_service.verify_token(token)
        return user if user and user.is_active else None
    except Exception:
        return None

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
