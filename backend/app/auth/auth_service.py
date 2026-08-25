from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.settings import settings
from app.models.schemas import User, UserResponse
from app.models.database import (
    as_dict,
    create_user as create_user_record,
    find_user_by_id,
    find_user_by_username,
    find_user_by_username_or_email,
)
import logging
from typing import Optional

logger = logging.getLogger(__name__)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        record = await find_user_by_username(username)
        if not record:
            return None
        user_data = as_dict(record)
        
        if not self.verify_password(password, user_data["hashed_password"]):
            return None
        
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
            
            record = await find_user_by_id(user_id)
            if record is None:
                return None
            return User(**as_dict(record))
            
        except JWTError:
            return None
    
    async def create_user(self, username: str, email: str, password: str, full_name: str = None, role: str = "developer") -> User:
        """Create new user"""
        existing_user = await find_user_by_username_or_email(username, email)
        
        if existing_user:
            if existing_user.username == username:
                raise HTTPException(status_code=400, detail="Username already exists")
            else:
                raise HTTPException(status_code=400, detail="Email already exists")
        

        hashed_password = self.get_password_hash(password)
        

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
        

        record = await create_user_record(**user_data)
        return User(**as_dict(record))


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
